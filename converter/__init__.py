"""
MP4视频转WAV音频转换器包

这个包提供了视频到音频的转换功能，支持单文件转换和批量转换。
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

from .core import VideoToAudioConverter
from .utils import setup_logging, validate_file_extension

__all__ = [
    'VideoToAudioConverter',
    'setup_logging', 
    'validate_file_extension'
] 