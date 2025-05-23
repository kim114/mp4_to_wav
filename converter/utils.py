"""
工具函数模块

包含日志设置、文件验证等通用功能。
"""

import os
import sys
import logging
from pathlib import Path
from typing import List

# 支持的视频格式
SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.3gp'}

def setup_logging(log_file: str = 'conversion.log') -> logging.Logger:
    """
    设置日志记录
    
    Args:
        log_file: 日志文件名
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger('video_converter')
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def validate_file_extension(file_path: str, supported_formats: set = None) -> bool:
    """
    验证文件扩展名是否受支持
    
    Args:
        file_path: 文件路径
        supported_formats: 支持的格式集合
        
    Returns:
        bool: 是否支持该格式
    """
    if supported_formats is None:
        supported_formats = SUPPORTED_VIDEO_FORMATS
    
    file_ext = Path(file_path).suffix.lower()
    return file_ext in supported_formats

def get_video_files_from_directory(directory: str) -> List[str]:
    """
    从目录中获取所有支持的视频文件
    
    Args:
        directory: 目录路径
        
    Returns:
        List[str]: 视频文件路径列表
    """
    video_files = []
    
    if not os.path.exists(directory):
        return video_files
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if validate_file_extension(file_path):
                video_files.append(file_path)
    
    return sorted(video_files)

def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为可读格式
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化的文件大小
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def create_output_directory(output_path: str) -> bool:
    """
    创建输出目录
    
    Args:
        output_path: 输出路径
        
    Returns:
        bool: 是否创建成功
    """
    try:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        return True
    except Exception:
        return False

def get_file_info(file_path: str) -> dict:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        dict: 文件信息字典
    """
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'modified_time': stat.st_mtime,
            'exists': True
        }
    except (OSError, FileNotFoundError):
        return {
            'size': 0,
            'size_formatted': '0 B',
            'modified_time': 0,
            'exists': False
        } 