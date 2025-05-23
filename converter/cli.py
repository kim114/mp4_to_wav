"""
命令行界面模块

提供命令行参数解析和交互功能。
"""

import sys
import argparse
from typing import Optional, Dict, Any

from .core import VideoToAudioConverter

def create_argument_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Returns:
        argparse.ArgumentParser: 配置好的参数解析器
    """
    parser = argparse.ArgumentParser(
        description='MP4视频转WAV音频转换器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 转换单个文件
  python -m converter.cli -i video.mp4
  
  # 转换单个文件并指定输出路径
  python -m converter.cli -i video.mp4 -o output.wav
  
  # 批量转换目录中的所有视频
  python -m converter.cli -d /path/to/videos
  
  # 批量转换并指定输出目录
  python -m converter.cli -d /path/to/videos -od /path/to/output
  
  # 设置音频质量参数
  python -m converter.cli -i video.mp4 --sample-rate 48000 --channels 2
        """
    )
    
    # 输入选项
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '-i', '--input',
        metavar='FILE',
        help='输入视频文件路径'
    )
    input_group.add_argument(
        '-d', '--directory',
        metavar='DIR',
        help='输入目录路径（批量转换）'
    )
    
    # 输出选项
    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='输出音频文件路径（仅用于单文件转换）'
    )
    parser.add_argument(
        '-od', '--output-dir',
        metavar='DIR',
        help='输出目录路径'
    )
    
    # 音频质量选项
    parser.add_argument(
        '--sample-rate',
        type=int,
        default=44100,
        metavar='RATE',
        help='音频采样率 (默认: 44100 Hz)'
    )
    
    parser.add_argument(
        '--channels',
        type=int,
        choices=[1, 2],
        metavar='N',
        help='音频声道数 (1=单声道, 2=立体声)'
    )
    
    parser.add_argument(
        '--format',
        choices=['wav', 'mp3', 'flac', 'aac'],
        default='wav',
        help='输出音频格式 (默认: wav)'
    )
    
    parser.add_argument(
        '--bitrate',
        metavar='RATE',
        help='音频比特率 (例如: 320k, 256k)'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='覆盖已存在的输出文件'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细转换信息'
    )
    
    parser.add_argument(
        '--log-file',
        metavar='FILE',
        default='conversion.log',
        help='日志文件路径 (默认: conversion.log)'
    )
    
    return parser

def prepare_audio_parameters(args: argparse.Namespace) -> Dict[str, Any]:
    """
    根据命令行参数准备音频参数
    
    Args:
        args: 解析后的命令行参数
        
    Returns:
        Dict[str, Any]: 音频参数字典
    """
    audio_params = {}
    
    # 采样率
    if args.sample_rate != 44100:
        audio_params['fps'] = args.sample_rate
    
    # 声道数
    if args.channels:
        if args.channels == 1:
            audio_params['channels'] = 1
        elif args.channels == 2:
            audio_params['channels'] = 2
    
    # 比特率
    if args.bitrate:
        audio_params['bitrate'] = args.bitrate
    
    # 输出格式相关的编码器设置
    if args.format == 'wav':
        audio_params['codec'] = 'pcm_s16le'
    elif args.format == 'mp3':
        audio_params['codec'] = 'libmp3lame'
    elif args.format == 'flac':
        audio_params['codec'] = 'flac'
    elif args.format == 'aac':
        audio_params['codec'] = 'aac'
    
    # 注意：verbose参数已移除，因为MoviePy 2.2.1不支持
    
    return audio_params

def create_progress_display():
    """创建进度显示函数"""
    last_percentage = -1
    
    def progress_callback(**kwargs):
        nonlocal last_percentage
        
        phase = kwargs.get('phase', '')
        
        if phase == 'processing':
            file_index = kwargs.get('file_index', 0)
            total_files = kwargs.get('total_files', 0)
            current_file = kwargs.get('current_file', '')
            print(f"\n正在处理文件 {file_index}/{total_files}: {current_file}")
        
        elif phase == 'converting':
            # MoviePy的进度信息
            if 't' in kwargs:
                progress = kwargs.get('t', 0)
                duration = kwargs.get('duration', 0)
                if duration > 0:
                    percentage = int((progress / duration) * 100)
                    if percentage != last_percentage and percentage % 5 == 0:
                        print(f"转换进度: {percentage}%")
                        last_percentage = percentage
        
        elif phase == 'completed':
            print("✓ 转换完成")
        
        elif phase == 'finished':
            success_count = kwargs.get('success_count', 0)
            total_files = kwargs.get('total_files', 0)
            print(f"\n🎉 批量转换完成: {success_count}/{total_files} 成功")
    
    return progress_callback

def main():
    """命令行主函数"""
    try:
        # 解析命令行参数
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # 创建转换器实例
        converter = VideoToAudioConverter(log_file=args.log_file)
        
        # 准备音频参数
        audio_params = prepare_audio_parameters(args)
        
        # 创建进度显示
        progress_callback = create_progress_display() if not args.verbose else None
        
        if args.input:
            # 单文件转换
            print(f"开始转换文件: {args.input}")
            
            # 生成输出路径
            output_path = args.output
            if output_path is None:
                output_path = converter.generate_output_path(
                    args.input, 
                    args.output_dir, 
                    args.format
                )
            
            # 检查输出文件是否存在
            import os
            if os.path.exists(output_path) and not args.overwrite:
                response = input(f"输出文件已存在: {output_path}\n是否覆盖? (y/N): ")
                if response.lower() not in ['y', 'yes', '是']:
                    print("转换已取消")
                    sys.exit(0)
            
            success = converter.convert_single_file(
                args.input, 
                output_path, 
                audio_params,
                progress_callback
            )
            
            if success:
                print(f"✅ 转换成功: {output_path}")
                sys.exit(0)
            else:
                print("❌ 转换失败")
                sys.exit(1)
        
        elif args.directory:
            # 批量转换
            print(f"开始批量转换目录: {args.directory}")
            
            success_count, total_count = converter.convert_batch(
                args.directory,
                args.output_dir,
                audio_params,
                progress_callback
            )
            
            if success_count == total_count:
                print(f"✅ 所有文件转换成功！")
                sys.exit(0)
            else:
                print(f"⚠️ 部分文件转换失败: {success_count}/{total_count} 成功")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断转换")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 程序错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 