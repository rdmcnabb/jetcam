"""
jetcam - USB camera and microphone library for Linux.
Works with any V4L2 camera and ALSA audio device.

Usage:
    from jetcam import Camera, Microphone
"""

from jetcam.camera import Camera
from jetcam.microphone import Microphone

__all__ = ["Camera", "Microphone"]
__version__ = "0.1.0"
