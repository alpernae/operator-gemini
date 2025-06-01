# Operator Gemini

A Python client for interacting with Google's Gemini Live API with real-time audio, video capabilities, and advanced configuration management.

## Features

- 🎤 **Real-time Audio**: Audio streaming with configurable sample rates
- 📷 **Video Support**: Camera and screen capture capabilities
- 🔧 **Flexible Configuration**: Environment-based configuration with validation
- 🛡️ **Error Handling**: Robust error handling with quota management
- 🚀 **Multiple Models**: Support for fallback models
- ⚙️ **Customizable Settings**: Audio, video, and timing configurations

## Requirements

- Python 3.8+
- Google Gemini API key
- Dependencies listed in requirements.txt

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/alpernae/operator-gemini.git
cd operator-gemini
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
ENABLE_GOOGLE_SEARCH=true
SEARCH_RESULTS_LIMIT=5
TURN_COVERAGE=TURN_INCLUDES_ALL_INPUT
AUTO_END_TURN=true
CONVERSATION_MEMORY=50
ENABLE_INITIAL_PROMPT=true
INITIAL_PROMPT="You are a helpful coding assistant specializing in Python development..."
CUSTOM_INITIAL_PROMPT_FILE=custom_prompt.txt
```

## Configuration

The project uses a comprehensive configuration system through the `Config` class in `src/config.py`.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Gemini API key (required) | None |
| `MODEL_NAME` | Gemini model to use | `models/gemini-2.5-flash-preview-native-audio-dialog` |
| `DEFAULT_VIDEO_MODE` | Default video mode | `screen` |
| `ENABLE_GOOGLE_SEARCH` | Enable Google Search integration | `true` |
| `SEARCH_RESULTS_LIMIT` | Maximum search results to include | `5` |
| `TURN_COVERAGE` | Conversation turn management | `TURN_INCLUDES_ALL_INPUT` |
| `AUTO_END_TURN` | Automatically end conversation turns | `true` |
| `CONVERSATION_MEMORY` | Number of messages to keep in memory | `50` |
| `ENABLE_INITIAL_PROMPT` | Enable initial prompt system | `true` |
| `INITIAL_PROMPT` | Custom initial prompt text | Default system prompt |
| `CUSTOM_INITIAL_PROMPT_FILE` | Path to custom prompt file | None |

### Configuration Categories

#### API Configuration
- Primary model: `models/gemini-2.5-flash-preview-native-audio-dialog`
- Fallback models for quota/availability issues
- Automatic API key validation

#### Audio Configuration
- Format: 16-bit PCM
- Channels: Mono (1 channel)
- Send sample rate: 16kHz
- Receive sample rate: 24kHz
- Chunk size: 1024 samples

#### Video Configuration
- Supported modes: camera, screen, both, none
- Multiple resolution options (LOW, MEDIUM, HIGH)
- Configurable image quality and compression
- Adjustable capture intervals

#### Advanced Features
- Google Search integration
- Conversation memory management
- Turn coverage options
- Real-time display configuration

## Initial Prompt System

The client supports configuring an initial prompt that sets up the AI assistant's behavior and capabilities:

### Using Environment Variables

```env
# Enable/disable initial prompt
ENABLE_INITIAL_PROMPT=true

# Custom initial prompt text
INITIAL_PROMPT="You are a helpful coding assistant specializing in Python development..."
```

### Using a Custom Prompt File

Create a text file with your custom prompt:

```bash
echo "You are an expert data scientist..." > custom_prompt.txt
```

Then reference it in your `.env` file:

```env
CUSTOM_INITIAL_PROMPT_FILE=custom_prompt.txt
```

### Interactive Commands

During runtime, you can:
- Type `prompt` to view the current initial prompt
- Type `status` to see if initial prompt is enabled
- The initial prompt is automatically sent when the session starts

## Project Structure

```
operator-gemini/
├── src/
│   └── config.py             # Configuration management and validation
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
└── README.md                # This file
```

## Error Handling

The configuration system includes comprehensive error handling:

### API Key Validation
```python
Config.validate()  # Automatically called on import
```

### Quota Management
- Detailed quota exceeded error messages
- Guidance for resolving billing and quota issues
- Automatic fallback model suggestions

### Configuration Validation
- Required environment variable checking
- Helpful error messages with setup instructions
- Links to relevant Google AI Studio pages

## Dependencies

- **google-genai**: Google Gemini API client (≥0.7.0)
- **opencv-python**: Camera capture and image processing (≥4.8.0)
- **pyaudio**: Audio input/output handling (≥0.2.11)
- **pillow**: Image manipulation and optimization (≥10.0.0)
- **mss**: Screen capture functionality (≥9.0.0)
- **python-dotenv**: Environment variable management (≥1.0.0)

## Getting Started

1. **Get your Gemini API key** from [Google AI Studio](https://aistudio.google.com/app/apikey)

2. **Create your `.env` file**:
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Test configuration**:
```python
from src.config import Config
Config.validate()  # Should pass without errors
```

## Troubleshooting

### Common Issues

1. **Missing API Key**:
   ```
   ❌ GEMINI_API_KEY environment variable is required!
   ```
   - Get your API key from https://aistudio.google.com/app/apikey
   - Add it to your `.env` file

2. **Quota Exceeded**:
   - Check billing at https://aistudio.google.com/
   - Wait for quota reset or upgrade your plan
   - The system will display detailed guidance

3. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.8+)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test your changes with the configuration system
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the configuration validation messages
3. Check Google's Gemini API documentation
4. Create an issue at https://github.com/alpernae/operator-gemini/issues

## Acknowledgments

- Google Gemini team for the Live API
- Python community for excellent libraries
- Contributors to the open-source packages used in this project

---

**Repository**: https://github.com/alpernae/operator-gemini