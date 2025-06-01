"""
Gemini Live API Client - Main Entry Point

Usage:
    python main.py --mode camera
    python main.py --mode screen  
    python main.py --mode both
    python main.py --mode none
"""

import asyncio
import argparse
import traceback
from src.core import LiveClient
from src.config import Config

def main():
    parser = argparse.ArgumentParser(description="Gemini Live API with screen/camera sharing")
    parser.add_argument(
        "--mode",
        type=str,
        default=Config.DEFAULT_VIDEO_MODE,
        help="Video input mode",
        choices=["camera", "screen", "both", "none"],
    )

    args = parser.parse_args()

    try:
        client = LiveClient(video_mode=args.mode)
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
