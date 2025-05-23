#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MP4视频转WAV音频转换器 - 演示脚本

这个脚本演示了如何使用转换器的各种功能。
"""

import os
import sys
from converter import VideoToAudioConverter

def demo_converter():
    """演示转换器功能"""
    print("🎬 MP4视频转WAV音频转换器演示")
    print("=" * 50)
    
    # 创建转换器实例
    converter = VideoToAudioConverter()
    
    print("\n✅ 转换器创建成功！")
    print(f"📝 日志文件将保存在: conversion.log")
    
    # 检查支持的格式
    from converter.utils import SUPPORTED_VIDEO_FORMATS
    print(f"\n🎥 支持的视频格式: {', '.join(SUPPORTED_VIDEO_FORMATS)}")
    
    # 提示用户如何使用
    print("\n🚀 使用方法:")
    print("1. 图形界面模式: python main.py gui")
    print("2. 命令行模式示例:")
    print("   python main.py cli -i video.mp4")
    print("   python main.py cli -d /path/to/videos")
    
    # 检查当前目录是否有视频文件
    print("\n🔍 检查当前目录中的视频文件...")
    from converter.utils import get_video_files_from_directory
    video_files = get_video_files_from_directory(".")
    
    if video_files:
        print(f"找到 {len(video_files)} 个视频文件:")
        for i, file in enumerate(video_files[:5], 1):  # 最多显示5个
            print(f"   {i}. {os.path.basename(file)}")
        if len(video_files) > 5:
            print(f"   ... 还有 {len(video_files) - 5} 个文件")
        
        print("\n💡 您可以选择以下任一文件进行转换测试：")
        print(f"   python main.py cli -i \"{video_files[0]}\"")
    else:
        print("❌ 当前目录中没有找到视频文件")
        print("💡 请将一些MP4视频文件放在当前目录，或指定其他目录")
    
    print("\n" + "=" * 50)
    print("✨ 演示完成！程序已准备就绪。")

def test_import():
    """测试所有模块是否可以正常导入"""
    print("🔧 测试模块导入...")
    
    try:
        # 测试核心模块
        from converter.core import VideoToAudioConverter
        print("✅ 核心模块导入成功")
        
        # 测试工具模块
        from converter.utils import setup_logging, validate_file_extension
        print("✅ 工具模块导入成功")
        
        # 测试CLI模块
        from converter.cli import create_argument_parser
        print("✅ CLI模块导入成功")
        
        # 测试GUI模块（可能失败）
        try:
            from converter.gui import VideoConverterGUI
            print("✅ GUI模块导入成功")
        except ImportError as e:
            print(f"⚠️  GUI模块导入失败: {e}")
            print("   这通常是因为缺少tkinter库，但不影响CLI使用")
        
        # 测试MoviePy
        from moviepy import VideoFileClip
        print("✅ MoviePy导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def main():
    """主函数"""
    print("🎭 MP4视频转WAV音频转换器 - 演示程序")
    print("=" * 60)
    
    # 测试导入
    if not test_import():
        print("\n❌ 某些模块导入失败，请检查安装：")
        print("   uv pip install -r requirements.txt")
        return
    
    print("\n")
    
    # 演示功能
    demo_converter()
    
    # 显示启动选项
    print("\n🎮 现在您可以：")
    print("1. 启动图形界面: python main.py")
    print("2. 查看CLI帮助: python main.py cli --help")
    print("3. 阅读README: README.md")

if __name__ == "__main__":
    main() 