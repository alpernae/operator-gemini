import asyncio
import websockets.exceptions
from google import genai
from google.genai import types
from ..config import Config

class SessionManager:
    """Manages Gemini Live API session and communication"""
    
    def __init__(self):
        # Initialize Gemini client
        self.client = genai.Client(
            http_options={"api_version": "v1beta"},
            api_key=Config.GEMINI_API_KEY,
        )
        
        # Live API Configuration
        self.config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            media_resolution=Config.MEDIA_RESOLUTION,
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
                )
            ),
            context_window_compression=types.ContextWindowCompressionConfig(
                trigger_tokens=25600,
                sliding_window=types.SlidingWindow(target_tokens=12800),
            ),
        )
        
        self.session = None
        self.audio_in_queue = None
        
    async def setup_session(self, session, audio_in_queue):
        """Initialize session and audio queue"""
        self.session = session
        self.audio_in_queue = audio_in_queue
        
    async def send_realtime(self, out_queue):
        """Send real-time data to the session"""
        while True:
            msg = await out_queue.get()
            await self.session.send(input=msg)

    async def receive_audio(self):
        """Receive audio from the session"""
        while True:
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue
                if text := response.text:
                    print(text, end="")

            # Clear audio queue on interruption
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def try_connect_with_fallbacks(self):
        """Try to connect with fallback models if quota exceeded"""
        models_to_try = [Config.MODEL_NAME] + Config.FALLBACK_MODELS
        
        for model in models_to_try:
            try:
                print(f"🔄 Trying to connect with model: {model}")
                return self.client.aio.live.connect(model=model, config=self.config)
            except websockets.exceptions.ConnectionClosedError as e:
                if "quota" in str(e).lower() or "1011" in str(e):
                    print(f"❌ Quota exceeded for model: {model}")
                    if model == models_to_try[-1]:
                        print(Config.get_quota_error_message())
                        raise Exception("All models exhausted due to quota limits")
                    continue
                else:
                    raise e
            except Exception as e:
                print(f"❌ Failed to connect with {model}: {e}")
                if model == models_to_try[-1]:
                    error_msg = f"""
🚨 CRITICAL ERROR: All Models Failed!

Error Type: {type(e).__name__}
Error Message: {str(e)}

This error suggests a fundamental issue with the API connection.
Common causes:
1. Invalid API key
2. Network connectivity issues  
3. API service temporarily down
4. Incorrect model names
5. Package version incompatibility

Troubleshooting steps:
1. Verify your API key at: https://aistudio.google.com/app/apikey
2. Check internet connection
3. Try updating the google-genai package: pip install --upgrade google-genai
4. Check API status: https://status.cloud.google.com/

Exiting application...
"""
                    print(error_msg)
                    raise Exception("All available models failed to connect")
                continue
        
        raise Exception("Failed to connect with any available model")
