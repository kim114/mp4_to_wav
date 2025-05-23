"""
核心转换逻辑模块

包含视频到音频转换的主要功能。
"""

import os
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from moviepy import VideoFileClip

from .utils import (
    setup_logging, 
    validate_file_extension, 
    get_video_files_from_directory,
    create_output_directory,
    get_file_info
)

class VideoToAudioConverter:
    """视频转音频转换器类"""
    
    def __init__(self, log_file: str = 'conversion.log'):
        """
        初始化转换器
        
        Args:
            log_file: 日志文件路径
        """
        self.logger = setup_logging(log_file)
        self.current_clip = None
    
    def validate_input_file(self, input_path: str) -> bool:
        """
        验证输入文件是否有效
        
        Args:
            input_path: 输入文件路径
            
        Returns:
            bool: 文件是否有效
        """
        if not os.path.exists(input_path):
            self.logger.error(f"文件不存在: {input_path}")
            return False
        
        if not validate_file_extension(input_path):
            self.logger.error(f"不支持的视频格式: {input_path}")
            return False
            
        return True
    
    def generate_output_path(self, input_path: str, output_dir: Optional[str] = None, 
                           output_format: str = 'wav') -> str:
        """
        生成输出文件路径
        
        Args:
            input_path: 输入文件路径
            output_dir: 输出目录（可选）
            output_format: 输出格式（默认wav）
            
        Returns:
            str: 输出文件路径
        """
        input_file = Path(input_path)
        output_filename = input_file.stem + f'.{output_format}'
        
        if output_dir:
            create_output_directory(os.path.join(output_dir, output_filename))
            return os.path.join(output_dir, output_filename)
        else:
            return os.path.join(input_file.parent, output_filename)
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        获取视频文件信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            Dict[str, Any]: 视频信息字典
        """
        info = get_file_info(video_path)
        
        try:
            clip = VideoFileClip(video_path)
            info.update({
                'duration': clip.duration,
                'fps': clip.fps,
                'has_audio': clip.audio is not None,
                'resolution': (clip.w, clip.h) if hasattr(clip, 'w') else None
            })
            clip.close()
        except Exception as e:
            self.logger.error(f"无法读取视频信息 {video_path}: {str(e)}")
            info.update({
                'duration': 0,
                'fps': 0,
                'has_audio': False,
                'resolution': None
            })
        
        return info
    
    def convert_single_file(self, input_path: str, output_path: Optional[str] = None, 
                          audio_params: Optional[dict] = None, 
                          progress_callback: Optional[callable] = None) -> bool:
        """
        转换单个视频文件为音频
        
        Args:
            input_path: 输入视频文件路径
            output_path: 输出音频文件路径（可选）
            audio_params: 音频参数（可选）
            progress_callback: 进度回调函数（可选）
            
        Returns:
            bool: 转换是否成功
        """
        try:
            # 验证输入文件
            if not self.validate_input_file(input_path):
                return False
            
            # 生成输出路径
            if output_path is None:
                output_path = self.generate_output_path(input_path)
            
            # 确保输出目录存在
            if not create_output_directory(output_path):
                self.logger.error(f"无法创建输出目录: {output_path}")
                return False
            
            self.logger.info(f"开始转换: {input_path} -> {output_path}")
            
            # 检查文件是否已存在
            if os.path.exists(output_path):
                self.logger.warning(f"输出文件已存在，将被覆盖: {output_path}")
            
            # 加载视频文件
            video_clip = VideoFileClip(input_path)
            self.current_clip = video_clip
            
            # 检查是否有音频轨道
            if video_clip.audio is None:
                self.logger.error(f"视频文件没有音频轨道: {input_path}")
                video_clip.close()
                self.current_clip = None
                return False
            
            # 设置默认音频参数
            default_params = {
                'codec': 'pcm_s16le',  # WAV格式的PCM编码
                'logger': None
            }
            
            if audio_params:
                # MoviePy 2.2.1 write_audiofile支持的参数
                supported_params = ['codec', 'fps', 'bitrate', 'nbytes', 'buffersize', 'ffmpeg_params', 'write_logfile']
                filtered_params = {k: v for k, v in audio_params.items() 
                                 if k in supported_params}
                default_params.update(filtered_params)
                
                # 处理声道数参数 - 通过ffmpeg_params设置
                if 'channels' in audio_params:
                    channels = audio_params['channels']
                    if 'ffmpeg_params' not in default_params:
                        default_params['ffmpeg_params'] = []
                    if channels == 1:
                        default_params['ffmpeg_params'].extend(['-ac', '1'])
                    elif channels == 2:
                        default_params['ffmpeg_params'].extend(['-ac', '2'])
            
            # 添加进度回调
            if progress_callback:
                # MoviePy的logger参数问题较多，暂时禁用内置进度显示
                # 在转换前后手动调用进度回调
                progress_callback(phase='converting', t=0, duration=video_clip.duration if video_clip.duration else 0)
                # 设置logger为None避免iter_bar错误
                default_params['logger'] = None
            else:
                # 没有自定义回调时使用默认进度条
                default_params['logger'] = 'bar'
            
            # 提取并保存音频
            video_clip.audio.write_audiofile(output_path, **default_params)
            
            # 转换完成后的进度回调
            if progress_callback:
                progress_callback(phase='completed', t=video_clip.duration if video_clip.duration else 0, 
                                duration=video_clip.duration if video_clip.duration else 0)
            
            # 关闭视频对象
            video_clip.close()
            self.current_clip = None
            
            # 验证输出文件
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                self.logger.info(f"转换完成: {output_path}")
                return True
            else:
                self.logger.error(f"转换失败，输出文件无效: {output_path}")
                return False
            
        except Exception as e:
            self.logger.error(f"转换失败 {input_path}: {str(e)}")
            if self.current_clip:
                try:
                    self.current_clip.close()
                except:
                    pass
                self.current_clip = None
            return False
    
    def convert_batch(self, input_dir: str, output_dir: Optional[str] = None, 
                     audio_params: Optional[dict] = None,
                     progress_callback: Optional[callable] = None) -> Tuple[int, int]:
        """
        批量转换目录中的所有视频文件
        
        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径（可选）
            audio_params: 音频参数（可选）
            progress_callback: 进度回调函数（可选）
            
        Returns:
            Tuple[int, int]: (成功转换数量, 总文件数量)
        """
        if not os.path.exists(input_dir):
            self.logger.error(f"输入目录不存在: {input_dir}")
            return 0, 0
        
        # 查找所有视频文件
        video_files = get_video_files_from_directory(input_dir)
        
        if not video_files:
            self.logger.warning(f"在目录中未找到支持的视频文件: {input_dir}")
            return 0, 0
        
        self.logger.info(f"找到 {len(video_files)} 个视频文件")
        
        success_count = 0
        total_count = len(video_files)
        
        for i, video_file in enumerate(video_files, 1):
            self.logger.info(f"正在处理 ({i}/{total_count}): {os.path.basename(video_file)}")
            
            # 通知总体进度
            if progress_callback:
                progress_callback(
                    file_index=i,
                    total_files=total_count,
                    current_file=video_file,
                    phase='processing'
                )
            
            # 生成输出路径
            if output_dir:
                # 保持相对目录结构
                rel_path = os.path.relpath(video_file, input_dir)
                output_path = self.generate_output_path(
                    rel_path, 
                    os.path.join(output_dir, os.path.dirname(rel_path))
                )
            else:
                output_path = self.generate_output_path(video_file)
            
            # 单文件进度回调
            def file_progress_callback(**kwargs):
                if progress_callback:
                    progress_callback(
                        file_index=i,
                        total_files=total_count,
                        current_file=video_file,
                        phase='converting',
                        **kwargs
                    )
            
            if self.convert_single_file(video_file, output_path, audio_params, file_progress_callback):
                success_count += 1
            
            # 通知单文件完成
            if progress_callback:
                progress_callback(
                    file_index=i,
                    total_files=total_count,
                    current_file=video_file,
                    phase='completed'
                )
        
        self.logger.info(f"批量转换完成: {success_count}/{total_count} 成功")
        
        # 通知批量转换完成
        if progress_callback:
            progress_callback(
                file_index=total_count,
                total_files=total_count,
                current_file=None,
                phase='finished',
                success_count=success_count
            )
        
        return success_count, total_count
    
    def stop_conversion(self):
        """停止当前转换"""
        if self.current_clip:
            try:
                self.current_clip.close()
                self.current_clip = None
                self.logger.info("转换已停止")
            except Exception as e:
                self.logger.error(f"停止转换时出错: {str(e)}")
    
    def __del__(self):
        """析构函数，确保资源清理"""
        if self.current_clip:
            try:
                self.current_clip.close()
            except:
                pass 