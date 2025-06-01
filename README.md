# Gemini Live API Client

A comprehensive Python client for interacting with Google's Gemini Live API with real-time audio, video (camera/screen capture), and multimodal communication capabilities.

## Features

- 🎤 **Real-time Audio**: Bidirectional audio streaming with microphone input and speaker output
- 📷 **Camera Integration**: Live camera feed processing and transmission
- 🖥️ **Screen Sharing**: Real-time screen capture and sharing
- 🔄 **Multimodal Support**: Simultaneous camera and screen sharing
- 💬 **Text Chat**: Interactive text-based communication
- 🚀 **Live Controls**: Dynamic toggling of camera and screen sharing during sessions
- 🛡️ **Error Handling**: Robust error handling with quota management and fallback models
- ⚡ **Async Architecture**: High-performance asynchronous implementation

## Requirements

- Python 3.8+
- Google Gemini API key
- Microphone and speakers (for audio)
- Camera (optional, for camera mode)
- Display (for screen sharing mode)

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd live
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
Create a `.env` file in the project root:
```env
# Get your API key from https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Optional configurations
MODEL_NAME=models/gemini-2.5-flash-preview-native-audio-dialog
DEFAULT_VIDEO_MODE=screen
```

## Usage

### Basic Usage

```bash
# Start with screen sharing (default)
python client.py

# Start with camera only
python client.py --mode camera

# Start with both camera and screen
python client.py --mode both

# Start with audio only (no video)
python client.py --mode none
```

### Interactive Commands

Once the application is running, you can use these commands:

- **Text input**: Type any message and press Enter
- **Exit**: Type `q` or `quit`
- **Camera control**: 
  - `camera on` - Enable camera
  - `camera off` - Disable camera
- **Screen control**:
  - `screen on` - Enable screen sharing
  - `screen off` - Disable screen sharing
- **Status check**: `status` - View current settings

### Video Modes

| Mode | Description |
|------|-------------|
| `camera` | Camera feed only |
| `screen` | Screen capture only |
| `both` | Both camera and screen capture |
| `none` | Audio and text only |

## Project Structure

```
live/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── core.py               # Main LiveClient orchestration
│   ├── audio/
│   │   ├── __init__.py
│   │   └── manager.py        # Audio input/output handling
│   ├── video/
│   │   ├── __init__.py
│   │   └── manager.py        # Camera and screen capture
│   └── session/
│       ├── __init__.py
│       └── manager.py        # Gemini API session management
├── client.py                 # Main entry point
├── requirements.txt          # Dependencies
├── .env                      # Environment variables
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Gemini API key (required) | None |
| `MODEL_NAME` | Gemini model to use | `models/gemini-2.5-flash-preview-native-audio-dialog` |
| `DEFAULT_VIDEO_MODE` | Default video mode | `screen` |

### Advanced Configuration

The [`Config`](src/config.py) class contains detailed settings for:

- **Audio**: Sample rates, chunk sizes, audio format
- **Video**: Image quality, resolution limits, capture intervals
- **API**: Model selection, fallback models, error handling

## Architecture

### Core Components

1. **[`LiveClient`](src/core.py)**: Main orchestrator that manages all components
2. **[`AudioManager`](src/audio/manager.py)**: Handles microphone input and speaker output
3. **[`VideoManager`](src/video/manager.py)**: Manages camera and screen capture
4. **[`SessionManager`](src/session/manager.py)**: Handles Gemini API communication

### Key Features

- **Asynchronous Design**: Uses `asyncio.TaskGroup` for concurrent operations
- **Queue-based Communication**: Efficient data flow between components
- **Error Recovery**: Automatic fallback to alternative models on quota exceeded
- **Resource Management**: Proper cleanup of audio/video resources

## Error Handling

The client includes comprehensive error handling:

- **Quota Exceeded**: Automatic fallback to alternative models
- **Connection Issues**: Retry logic and detailed error messages
- **Resource Cleanup**: Proper cleanup of audio/video resources on exit
- **User Interruption**: Graceful handling of Ctrl+C

## Troubleshooting

### Common Issues

1. **API Key Missing**:
   ```
   ❌ GEMINI_API_KEY environment variable is required!
   ```
   - Get your API key from https://aistudio.google.com/app/apikey
   - Add it to your `.env` file

2. **Quota Exceeded**:
   ```
   🚨 QUOTA EXCEEDED ERROR
   ```
   - Check your billing at https://aistudio.google.com/
   - Wait for quota reset or upgrade your plan

3. **Audio Issues**:
   - Ensure microphone permissions are granted
   - Check audio device availability

4. **Video Issues**:
   - Verify camera permissions
   - Ensure camera is not in use by other applications

### Debug Mode

For detailed error information, run with Python's debug mode:
```bash
python -u client.py --mode your_mode
```

## Dependencies

- **google-genai**: Google Gemini API client
- **opencv-python**: Camera capture and image processing
- **pyaudio**: Audio input/output handling
- **pillow**: Image manipulation and optimization
- **mss**: Screen capture functionality
- **python-dotenv**: Environment variable management

## API Reference

### LiveClient

```python
from src.core import LiveClient

client = LiveClient(video_mode="both")
await client.run()
```

### Configuration

```python
from src.config import Config

# Access configuration values
print(Config.MODEL_NAME)
print(Config.GEMINI_API_KEY)
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Google's Gemini API documentation
3. Create an issue in this repository

## Acknowledgments

- Google Gemini team for the Live API
- OpenCV community for computer vision tools
- PyAudio team for audio processing capabilities