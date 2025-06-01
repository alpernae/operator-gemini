"""
Gemini Live API Client Package

A comprehensive client for interacting with Google's Gemini Live API
with support for audio, video (camera/screen), and real-time communication.
"""

__version__ = "1.0.0"
__author__ = "Gemini Live Client"

from .core import LiveClient
from .config import Config

__all__ = ["LiveClient", "Config"]
