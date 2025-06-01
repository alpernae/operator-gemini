import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "models/gemini-2.5-flash-preview-native-audio-dialog")
    
    # Fallback models (in order of preference) Implement later
    # These models are used if the primary model is not available or quota is exceeded
    FALLBACK_MODELS = [
        "models/gemini-2.5-flash-exp-native-audio-thinking-dialog",
        "models/gemini-2.0-flash-live-001"
    ]
    
    # Audio Configuration
    FORMAT = "paInt16"
    CHANNELS = 1
    SEND_SAMPLE_RATE = 16000
    RECEIVE_SAMPLE_RATE = 24000
    CHUNK_SIZE = 1024
    
    # Video Configuration
    DEFAULT_VIDEO_MODE = os.getenv("DEFAULT_VIDEO_MODE", "screen")
    MEDIA_RESOLUTION = "MEDIA_RESOLUTION_MEDIUM"  # Options: LOW, MEDIUM, HIGH
    
    # Image Processing
    IMAGE_QUALITY = 85
    SCREEN_QUALITY = 75
    MAX_IMAGE_SIZE = (1024, 1024)
    MAX_SCREEN_SIZE = (1920, 1080)

    # Timing
    CAMERA_CAPTURE_INTERVAL = 2.0
    SCREEN_CAPTURE_INTERVAL = 3.0
    
    # Error handling
    QUOTA_ERROR_MESSAGE = """
🚨 API Quota Exceeded!

The Gemini API quota has been exceeded. This could mean:
1. You've reached your free tier limit
2. Billing issues with your Google Cloud account
3. Daily/monthly quota limits reached

Solutions:
1. Check your Google AI Studio billing: https://aistudio.google.com/
2. Wait for quota reset (if daily limit)
3. Upgrade your plan if needed
4. Try using a different API key

Error details: You exceeded your current quota, please check your plan and billing details.
"""
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("""
❌ GEMINI_API_KEY environment variable is required!

To fix this:
1. Get your API key from: https://aistudio.google.com/app/apikey
2. Create a .env file in this directory with:
   GEMINI_API_KEY=your_api_key_here
3. Or set the environment variable:
   set GEMINI_API_KEY=your_api_key_here
""")
        return True
    
    @classmethod
    def get_quota_error_message(cls):
        """Get formatted quota error message"""
        return cls.QUOTA_ERROR_MESSAGE

# Validate configuration on import
Config.validate()
