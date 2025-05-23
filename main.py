#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MP4视频转WAV音频转换器 - 主程序

支持命令行界面和图形界面两种模式。
"""

import sys
import argparse

def main():
    """主程序入口"""
    # 创建主参数解析器
    parser = argparse.ArgumentParser(
        description='MP4视频转WAV音频转换器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用模式:
  python main.py gui           # 启动图形界面 (默认)
  python main.py cli [参数]    # 使用命令行界面
  
GUI模式示例:
  python main.py gui
  python main.py              # 默认启动GUI
  
CLI模式示例:
  python main.py cli -i video.mp4
  python main.py cli -d /path/to/videos -od /path/to/output
        """
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='mode', help='运行模式')
    
    # GUI模式
    gui_parser = subparsers.add_parser('gui', help='启动图形界面')
    
    # CLI模式
    cli_parser = subparsers.add_parser('cli', help='使用命令行界面')
    
    # 为CLI模式添加所有参数
    from converter.cli import create_argument_parser
    cli_arg_parser = create_argument_parser()
    
    # 复制CLI参数到子解析器
    for action in cli_arg_parser._actions:
        if action.dest in ['help']:
            continue
        try:
            if action.dest in ['input', 'directory']:
                # 输入选项组
                if not hasattr(cli_parser, '_input_group'):
                    cli_parser._input_group = cli_parser.add_mutually_exclusive_group(required=True)
                
                if action.dest == 'input':
                    cli_parser._input_group.add_argument(
                        '-i', '--input', metavar='FILE',
                        help='输入视频文件路径'
                    )
                elif action.dest == 'directory':
                    cli_parser._input_group.add_argument(
                        '-d', '--directory', metavar='DIR',
                        help='输入目录路径（批量转换）'
                    )
            else:
                # 其他参数
                kwargs = {
                    'dest': action.dest,
                    'help': action.help
                }
                
                # 添加类型信息
                if action.type is not None:
                    kwargs['type'] = action.type
                if action.choices is not None:
                    kwargs['choices'] = action.choices
                if action.default is not None:
                    kwargs['default'] = action.default
                if action.metavar is not None:
                    kwargs['metavar'] = action.metavar
                
                # 处理store_true类型的参数
                if isinstance(action, argparse._StoreTrueAction):
                    kwargs['action'] = 'store_true'
                elif isinstance(action, argparse._StoreFalseAction):
                    kwargs['action'] = 'store_false'
                
                cli_parser.add_argument(*action.option_strings, **kwargs)
        except argparse.ArgumentError:
            # 忽略重复参数
            pass
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有指定模式，默认使用GUI
    if args.mode is None:
        args.mode = 'gui'
    
    # 根据模式启动相应界面
    if args.mode == 'gui':
        try:
            from converter.gui import main as gui_main
            print("启动图形界面...")
            gui_main()
        except ImportError as e:
            print(f"无法启动图形界面: {e}")
            print("可能缺少tkinter库，请使用命令行模式:")
            print("python main.py cli -h")
            sys.exit(1)
    
    elif args.mode == 'cli':
        # 重新解析参数给CLI模块
        cli_args = sys.argv[2:]  # 去掉 'main.py' 和 'cli'
        
        # 临时替换sys.argv来让CLI模块正确解析参数
        original_argv = sys.argv
        sys.argv = ['cli'] + cli_args
        
        try:
            from converter.cli import main as cli_main
            cli_main()
        finally:
            sys.argv = original_argv

def show_usage():
    """显示使用说明"""
    print("""
MP4视频转WAV音频转换器

使用方法:
  python main.py [gui|cli] [参数]

模式说明:
  gui  - 图形界面模式 (默认)
  cli  - 命令行界面模式

示例:
  python main.py                    # 启动图形界面
  python main.py gui               # 启动图形界面
  python main.py cli -i video.mp4  # 命令行转换单个文件
  python main.py cli -h            # 查看命令行帮助

首次使用建议选择图形界面模式。
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行错误: {e}")
        show_usage()
        sys.exit(1) 