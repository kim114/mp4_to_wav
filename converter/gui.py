"""
图形用户界面模块

提供简单易用的图形界面来进行视频转音频转换。
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional

from .core import VideoToAudioConverter
from .utils import get_file_info, format_file_size

class VideoConverterGUI:
    """视频转换器图形界面"""
    
    def __init__(self):
        """初始化GUI界面"""
        self.root = tk.Tk()
        self.root.title("MP4视频转WAV音频转换器 v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置界面样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 初始化变量
        self.converter = VideoToAudioConverter()
        self.current_conversion_thread = None
        self.is_converting = False
        
        # 创建界面
        self.create_widgets()
        self.create_menu()
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="选择文件", command=self.select_file)
        file_menu.add_command(label="选择目录", command=self.select_directory)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 输入选择区域
        input_frame = ttk.LabelFrame(main_frame, text="输入选择", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # 单文件选择
        ttk.Label(input_frame, text="视频文件:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(input_frame, textvariable=self.file_var, state="readonly")
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(input_frame, text="浏览", command=self.select_file).grid(row=0, column=2)
        
        # 目录选择
        ttk.Label(input_frame, text="视频目录:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.dir_var = tk.StringVar()
        dir_entry = ttk.Entry(input_frame, textvariable=self.dir_var, state="readonly")
        dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(input_frame, text="浏览", command=self.select_directory).grid(row=1, column=2)
        
        # 输出设置区域
        output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="10")
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        # 输出目录
        ttk.Label(output_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.output_dir_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))
        ttk.Button(output_frame, text="浏览", command=self.select_output_dir).grid(row=0, column=2)
        
        # 音频设置
        audio_frame = ttk.Frame(output_frame)
        audio_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        audio_frame.columnconfigure(1, weight=1)
        audio_frame.columnconfigure(3, weight=1)
        
        ttk.Label(audio_frame, text="格式:").grid(row=0, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value="wav")
        format_combo = ttk.Combobox(audio_frame, textvariable=self.format_var, 
                                  values=["wav", "mp3", "flac", "aac"], state="readonly", width=8)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(audio_frame, text="采样率:").grid(row=0, column=2, sticky=tk.W)
        self.sample_rate_var = tk.StringVar(value="44100")
        sample_combo = ttk.Combobox(audio_frame, textvariable=self.sample_rate_var,
                                  values=["22050", "44100", "48000", "96000"], state="readonly", width=8)
        sample_combo.grid(row=0, column=3, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(audio_frame, text="声道:").grid(row=0, column=4, sticky=tk.W)
        self.channels_var = tk.StringVar(value="2")
        channels_combo = ttk.Combobox(audio_frame, textvariable=self.channels_var,
                                    values=["1", "2"], state="readonly", width=5)
        channels_combo.grid(row=0, column=5, sticky=tk.W, padx=(5, 0))
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        self.convert_button = ttk.Button(control_frame, text="开始转换", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止转换", command=self.stop_conversion, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="清除日志", command=self.clear_log).pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, sticky=tk.W)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="转换日志", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 文本框和滚动条
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        main_frame.rowconfigure(5, weight=1)
    
    def select_file(self):
        """选择单个视频文件"""
        filename = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v *.3gp"),
                ("MP4文件", "*.mp4"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.file_var.set(filename)
            self.dir_var.set("")  # 清除目录选择
            self.log_message(f"选择文件: {filename}")
            
            # 显示文件信息
            info = get_file_info(filename)
            if info['exists']:
                video_info = self.converter.get_video_info(filename)
                duration = video_info.get('duration', 0)
                duration_str = f"{duration:.1f}秒" if duration > 0 else "未知"
                self.log_message(f"文件大小: {info['size_formatted']}, 时长: {duration_str}")
    
    def select_directory(self):
        """选择视频目录"""
        dirname = filedialog.askdirectory(title="选择视频目录")
        if dirname:
            self.dir_var.set(dirname)
            self.file_var.set("")  # 清除文件选择
            self.log_message(f"选择目录: {dirname}")
            
            # 统计视频文件数量
            from .utils import get_video_files_from_directory
            video_files = get_video_files_from_directory(dirname)
            self.log_message(f"找到 {len(video_files)} 个视频文件")
    
    def select_output_dir(self):
        """选择输出目录"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_dir_var.set(dirname)
            self.log_message(f"输出目录: {dirname}")
    
    def start_conversion(self):
        """开始转换"""
        if self.is_converting:
            return
        
        # 验证输入
        input_file = self.file_var.get().strip()
        input_dir = self.dir_var.get().strip()
        
        if not input_file and not input_dir:
            messagebox.showerror("错误", "请选择要转换的视频文件或目录")
            return
        
        # 设置转换状态
        self.is_converting = True
        self.convert_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_var.set(0)
        
        # 准备音频参数
        audio_params = self.get_audio_params()
        
        # 在新线程中执行转换
        if input_file:
            self.current_conversion_thread = threading.Thread(
                target=self.convert_file_thread,
                args=(input_file, audio_params)
            )
        else:
            self.current_conversion_thread = threading.Thread(
                target=self.convert_directory_thread,
                args=(input_dir, audio_params)
            )
        
        self.current_conversion_thread.daemon = True
        self.current_conversion_thread.start()
    
    def stop_conversion(self):
        """停止转换"""
        if self.converter:
            self.converter.stop_conversion()
        self.conversion_finished(interrupted=True)
    
    def get_audio_params(self):
        """获取音频参数"""
        params = {}
        
        # 格式和编码
        format_type = self.format_var.get()
        if format_type == 'wav':
            params['codec'] = 'pcm_s16le'
        elif format_type == 'mp3':
            params['codec'] = 'libmp3lame'
        elif format_type == 'flac':
            params['codec'] = 'flac'
        elif format_type == 'aac':
            params['codec'] = 'aac'
        
        # 采样率
        sample_rate = int(self.sample_rate_var.get())
        if sample_rate != 44100:
            params['fps'] = sample_rate
        
        # 声道数
        channels = int(self.channels_var.get())
        if channels:
            params['channels'] = channels
        
        return params
    
    def convert_file_thread(self, input_file, audio_params):
        """单文件转换线程"""
        try:
            output_dir = self.output_dir_var.get().strip() or None
            output_path = self.converter.generate_output_path(
                input_file, output_dir, self.format_var.get()
            )
            
            self.update_status("转换中...")
            
            success = self.converter.convert_single_file(
                input_file, 
                output_path, 
                audio_params,
                self.progress_callback
            )
            
            if success:
                self.log_message(f"✅ 转换成功: {output_path}")
                self.update_status("转换完成")
            else:
                self.log_message("❌ 转换失败")
                self.update_status("转换失败")
        
        except Exception as e:
            self.log_message(f"❌ 转换错误: {str(e)}")
            self.update_status("转换错误")
        
        finally:
            self.root.after(0, self.conversion_finished)
    
    def convert_directory_thread(self, input_dir, audio_params):
        """目录转换线程"""
        try:
            output_dir = self.output_dir_var.get().strip() or None
            
            self.update_status("批量转换中...")
            
            success_count, total_count = self.converter.convert_batch(
                input_dir,
                output_dir,
                audio_params,
                self.progress_callback
            )
            
            if success_count == total_count:
                self.log_message(f"✅ 批量转换完成: 所有 {total_count} 个文件转换成功")
                self.update_status("批量转换完成")
            else:
                self.log_message(f"⚠️ 批量转换完成: {success_count}/{total_count} 成功")
                self.update_status(f"部分成功: {success_count}/{total_count}")
        
        except Exception as e:
            self.log_message(f"❌ 批量转换错误: {str(e)}")
            self.update_status("批量转换错误")
        
        finally:
            self.root.after(0, self.conversion_finished)
    
    def progress_callback(self, **kwargs):
        """进度回调函数"""
        phase = kwargs.get('phase', '')
        
        if phase == 'processing':
            file_index = kwargs.get('file_index', 0)
            total_files = kwargs.get('total_files', 0)
            current_file = kwargs.get('current_file', '')
            
            filename = os.path.basename(current_file)
            self.root.after(0, lambda: self.log_message(f"正在处理 ({file_index}/{total_files}): {filename}"))
            
            if total_files > 0:
                overall_progress = (file_index - 1) / total_files * 100
                self.root.after(0, lambda: self.progress_var.set(overall_progress))
        
        elif phase == 'converting':
            # MoviePy的进度信息
            if 't' in kwargs:
                progress = kwargs.get('t', 0)
                duration = kwargs.get('duration', 0)
                if duration > 0:
                    percentage = (progress / duration) * 100
                    self.root.after(0, lambda: self.progress_var.set(percentage))
        
        elif phase == 'completed':
            self.root.after(0, lambda: self.log_message("✓ 文件转换完成"))
        
        elif phase == 'finished':
            self.root.after(0, lambda: self.progress_var.set(100))
    
    def conversion_finished(self, interrupted=False):
        """转换完成处理"""
        self.is_converting = False
        self.convert_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        if interrupted:
            self.update_status("转换已停止")
            self.log_message("⚠️ 转换已被用户停止")
        
        self.progress_var.set(0)
    
    def update_status(self, status):
        """更新状态"""
        self.root.after(0, lambda: self.status_var.set(status))
    
    def log_message(self, message):
        """记录日志消息"""
        def update_log():
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
        
        if threading.current_thread() == threading.main_thread():
            update_log()
        else:
            self.root.after(0, update_log)
    
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)
    
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            "MP4视频转WAV音频转换器 v1.0\n\n"
            "基于MoviePy库构建\n"
            "支持多种视频格式转换为音频\n\n"
            "作者: AI Assistant"
        )
    
    def on_closing(self):
        """窗口关闭处理"""
        if self.is_converting:
            if messagebox.askokcancel("退出", "转换正在进行中，确定要退出吗？"):
                self.stop_conversion()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """运行GUI应用"""
        self.root.mainloop()

def main():
    """GUI主函数"""
    app = VideoConverterGUI()
    app.run()

if __name__ == "__main__":
    main() 