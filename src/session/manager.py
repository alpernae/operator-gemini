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
        
        # Setup tools based on configuration
        tools = []
        if Config.ENABLE_GOOGLE_SEARCH:
            tools.append(types.Tool(google_search=types.GoogleSearch()))
        
        # Get initial prompt for system instruction
        initial_prompt = Config.get_initial_prompt() if Config.ENABLE_INITIAL_PROMPT else None
        
        # Live API Configuration
        config_kwargs = {
            "response_modalities": ["AUDIO"],
            "media_resolution": Config.MEDIA_RESOLUTION,
            "speech_config": types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Sadachbia")
                )
            ),
            "realtime_input_config": types.RealtimeInputConfig(
                turn_coverage=Config.TURN_COVERAGE
            ),
            "context_window_compression": types.ContextWindowCompressionConfig(
                trigger_tokens=25600,
                sliding_window=types.SlidingWindow(target_tokens=12800),
            ),
        }
        
        # Add system instruction if initial prompt is enabled
        if initial_prompt:
            config_kwargs["system_instruction"] = types.Content(
                parts=[types.Part.from_text(text=initial_prompt)],
                role="user"
            )
        
        # Add tools if available
        if tools:
            config_kwargs["tools"] = tools
            
        self.config = types.LiveConnectConfig(**config_kwargs)
        
        self.session = None
        self.audio_in_queue = None
        self.is_ai_speaking = False
        self.current_response = ""
        self.conversation_history = []
        self.search_enabled = Config.ENABLE_GOOGLE_SEARCH
        
    async def setup_session(self, session, audio_in_queue):
        """Initialize session and audio queue"""
        self.session = session
        self.audio_in_queue = audio_in_queue
        
    def toggle_search(self, enabled):
        """Toggle Google Search on/off"""
        self.search_enabled = enabled
        return self.search_enabled
        
    def add_to_conversation_history(self, role, content):
        """Add message to conversation history with memory management"""
        self.conversation_history.append({"role": role, "content": content})
        
        # Keep only recent messages to manage memory
        if len(self.conversation_history) > Config.CONVERSATION_MEMORY:
            self.conversation_history = self.conversation_history[-Config.CONVERSATION_MEMORY:]
    
    async def send_message_with_context(self, message, end_of_turn=True):
        """Send message with conversation context"""
        try:
            # Add user message to history
            self.add_to_conversation_history("user", message)
            
            # Send message with end_of_turn based on configuration
            await self.session.send(input=message, end_of_turn=end_of_turn)
            
        except Exception as e:
            print(f"❌ Error sending message: {e}")

    async def send_realtime(self, out_queue):
        """Send real-time data to the session"""
        while True:
            msg = await out_queue.get()
            await self.session.send(input=msg)

    async def receive_audio(self):
        """Receive audio and text from the session with real-time display and search support"""
        while True:
            if not self.session:
                await asyncio.sleep(0.1)  # Wait for session to be initialized
                continue

            try:
                turn = self.session.receive()
                self.current_response = ""
                response_started = False
                has_content = False
                search_results_shown = False
                code_execution_shown = False
                
                async for response in turn:
                    # Handle audio data
                    if data := response.data:
                        self.audio_in_queue.put_nowait(data)
                        continue
                    
                    # Handle tool calls (Google Search)
                    if hasattr(response, 'tool_call') and response.tool_call and self.search_enabled:
                        if not search_results_shown:
                            print(f"\n🔍 Performing Google Search...")
                            search_results_shown = True
                        continue
                    
                    # Handle executable code
                    if hasattr(response, 'executable_code') and response.executable_code:
                        if not code_execution_shown:
                            print(f"\n⚙️ Processing request...")
                            code_execution_shown = True
                        continue
                    
                    # Handle code execution results
                    if hasattr(response, 'code_execution_result') and response.code_execution_result:
                        # Code execution results are handled internally, just continue
                        continue
                        
                    # Handle text responses
                    if text := response.text:
                        # Start new AI response
                        if not response_started:
                            if not self.is_ai_speaking:
                                print(f"\n🤖 AI: ", end="", flush=True)
                                self.is_ai_speaking = True
                            response_started = True
                        
                        # Print text in real-time
                        print(text, end="", flush=True)
                        self.current_response += text
                        has_content = True

                # End of turn - finish the response
                if self.is_ai_speaking and has_content:
                    print("")  # New line after complete response
                    
                    # Add AI response to conversation history
                    self.add_to_conversation_history("assistant", self.current_response)
                    
                    self.is_ai_speaking = False
                    
                    # Show prompt again for next user input
                    await asyncio.sleep(0.1)  # Small delay for better UX
                
                # Clear audio queue on interruption
                while not self.audio_in_queue.empty():
                    self.audio_in_queue.get_nowait()
                    
            except Exception as e:
                print(f"\n❌ Error in receive_audio: {e}")
                await asyncio.sleep(0.5)  # Brief pause before retrying

    def get_conversation_summary(self):
        """Get a summary of recent conversation"""
        if not self.conversation_history:
            return "No conversation history"
        
        recent_messages = self.conversation_history[-10:]  # Last 10 messages
        user_messages = len([msg for msg in recent_messages if msg["role"] == "user"])
        ai_messages = len([msg for msg in recent_messages if msg["role"] == "assistant"])
        
        return f"Recent: {user_messages} user messages, {ai_messages} AI responses"

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
