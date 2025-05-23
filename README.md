# MP4视频转WAV音频转换器

一个功能强大且易用的视频转音频转换工具，支持将MP4等多种视频格式转换为WAV等音频格式。

## 功能特点

- 🎥 **多格式支持**: 支持MP4, AVI, MOV, MKV, FLV, WMV等常见视频格式
- 🎵 **音频格式**: 支持输出WAV, MP3, FLAC, AAC等音频格式
- 📁 **批量转换**: 支持单文件转换和目录批量转换
- 🖥️ **双界面模式**: 提供图形界面(GUI)和命令行界面(CLI)
- 📊 **实时进度**: 显示转换进度和详细日志
- ⚙️ **自定义设置**: 可调节采样率、声道数、比特率等参数
- 🛡️ **错误处理**: 完善的错误处理和日志记录

## 系统要求

- Python 3.8 或更高版本
- FFmpeg (MoviePy会自动下载)
- Windows/macOS/Linux

## 安装步骤

### 1. 克隆项目
```bash
git clone <项目地址>
cd autogen_demo
```

### 2. 创建虚拟环境 (推荐)
```bash
# 使用uv (推荐)
uv venv --python 3.11 .venv

# 或使用标准方法
python -m venv .venv
```

### 3. 激活虚拟环境
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 4. 安装依赖
```bash
# 使用uv
uv pip install -r requirements.txt

# 或使用pip
pip install -r requirements.txt
```

## 使用方法

### 图形界面模式 (推荐新手)

启动图形界面：
```bash
python main.py
# 或
python main.py gui
```

图形界面功能：
- 选择单个视频文件或整个目录
- 设置输出目录和音频参数
- 实时查看转换进度和日志
- 支持中途停止转换

### 命令行模式

#### 基本用法

```bash
# 转换单个文件
python main.py cli -i video.mp4

# 转换单个文件并指定输出路径
python main.py cli -i video.mp4 -o output.wav

# 批量转换目录中的所有视频
python main.py cli -d /path/to/videos

# 批量转换并指定输出目录
python main.py cli -d /path/to/videos -od /path/to/output
```

#### 高级参数

```bash
# 设置音频质量参数
python main.py cli -i video.mp4 --sample-rate 48000 --channels 2

# 转换为不同音频格式
python main.py cli -i video.mp4 --format mp3

# 设置比特率
python main.py cli -i video.mp4 --format mp3 --bitrate 320k

# 覆盖已存在的文件
python main.py cli -i video.mp4 --overwrite

# 显示详细转换信息
python main.py cli -i video.mp4 --verbose
```

#### 所有命令行参数

```
必需参数:
  -i FILE, --input FILE        输入视频文件路径
  -d DIR, --directory DIR      输入目录路径（批量转换）

可选参数:
  -o FILE, --output FILE       输出音频文件路径（仅用于单文件转换）
  -od DIR, --output-dir DIR    输出目录路径
  --format {wav,mp3,flac,aac}  输出音频格式 (默认: wav)
  --sample-rate RATE           音频采样率 (默认: 44100 Hz)
  --channels {1,2}             音频声道数 (1=单声道, 2=立体声)
  --bitrate RATE               音频比特率 (例如: 320k, 256k)
  --overwrite                  覆盖已存在的输出文件
  --verbose                    显示详细转换信息
  --log-file FILE              日志文件路径 (默认: conversion.log)
  -h, --help                   显示帮助信息
```

## 使用示例

### 示例1: 转换单个MP4文件为WAV
```bash
python main.py cli -i "我的视频.mp4"
```

### 示例2: 批量转换并设置高质量音频
```bash
python main.py cli -d "C:\Videos" -od "C:\Audio" --sample-rate 48000 --channels 2
```

### 示例3: 转换为MP3格式
```bash
python main.py cli -i video.mp4 --format mp3 --bitrate 320k
```

### 示例4: 使用图形界面
```bash
python main.py gui
```

## 项目结构

```
autogen_demo/
├── converter/              # 转换器包
│   ├── __init__.py        # 包初始化
│   ├── core.py            # 核心转换逻辑
│   ├── cli.py             # 命令行界面
│   ├── gui.py             # 图形界面
│   └── utils.py           # 工具函数
├── main.py                # 主程序入口
├── requirements.txt       # 项目依赖
├── README.md             # 项目说明
└── conversion.log        # 转换日志文件
```

## 支持的格式

### 输入视频格式
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- FLV (.flv)
- WMV (.wmv)
- M4V (.m4v)
- 3GP (.3gp)

### 输出音频格式
- WAV (.wav) - 无损格式，推荐
- MP3 (.mp3) - 压缩格式，体积小
- FLAC (.flac) - 无损压缩格式
- AAC (.aac) - 高效压缩格式

## 常见问题

### Q: 转换失败，提示找不到FFmpeg？
A: MoviePy会在首次使用时自动下载FFmpeg，请确保网络连接正常。如果问题持续，可以手动安装FFmpeg。

### Q: 转换后的音频文件很大？
A: WAV是无损格式，文件较大是正常的。如需较小文件，建议使用MP3或AAC格式。

### Q: 批量转换时部分文件失败？
A: 检查转换日志文件（conversion.log），通常是因为视频文件损坏或没有音频轨道。

### Q: 图形界面无法启动？
A: 确保系统安装了tkinter库。在某些Linux发行版中需要单独安装：
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
```

### Q: 如何设置音频质量？
A: 使用参数调节：
- `--sample-rate`: 采样率越高音质越好（44100/48000/96000）
- `--channels`: 2为立体声，1为单声道
- `--bitrate`: MP3格式的比特率（128k/256k/320k）

## 技术支持

如果遇到问题，请：
1. 查看conversion.log日志文件
2. 使用`--verbose`参数获取详细信息
3. 确保视频文件包含音频轨道
4. 检查文件路径是否正确

## 许可证

本项目基于MIT许可证开源。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持多种视频格式转音频
- 提供GUI和CLI两种界面
- 支持批量转换
- 完善的错误处理和日志记录

---

**享受使用！如果觉得有用，请给个Star ⭐** 