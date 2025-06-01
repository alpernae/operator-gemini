import asyncio
import pyaudio
from ..config import Config

class AudioManager:
    """Manages audio input/output for the Live API session"""
    
    def __init__(self):
        self.pya = pyaudio.PyAudio()
        self.audio_stream = None
        self.output_stream = None
        self.audio_in_queue = None
        self.out_queue = None
        
    async def setup_audio_queues(self, audio_in_queue, out_queue):
        """Initialize audio queues"""
        self.audio_in_queue = audio_in_queue
        self.out_queue = out_queue
        
    async def listen_audio(self):
        """Capture audio from microphone and send to output queue"""
        mic_info = self.pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            self.pya.open,
            format=getattr(pyaudio, Config.FORMAT),
            channels=Config.CHANNELS,
            rate=Config.SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=Config.CHUNK_SIZE,
        )
        
        kwargs = {"exception_on_overflow": False} if __debug__ else {}
        
        while True:
            data = await asyncio.to_thread(
                self.audio_stream.read, Config.CHUNK_SIZE, **kwargs
            )
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def play_audio(self):
        """Play audio from input queue"""
        self.output_stream = await asyncio.to_thread(
            self.pya.open,
            format=getattr(pyaudio, Config.FORMAT),
            channels=Config.CHANNELS,
            rate=Config.RECEIVE_SAMPLE_RATE,
            output=True,
        )
        
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(self.output_stream.write, bytestream)

    def cleanup(self):
        """Clean up audio resources"""
        try:
            if self.audio_stream:
                self.audio_stream.close()
            if self.output_stream:
                self.output_stream.close()
            self.pya.terminate()
        except Exception as e:
            print(f"❌ Error during audio cleanup: {e}")
