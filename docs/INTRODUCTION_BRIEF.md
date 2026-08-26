# 🎬 AI短视频自动化制作技能

**一键生成专业级AI短视频，从脚本到成片全自动化**

---

## ✨ 一句话介绍

让每个人都能创作电影级AI短视频的自动化工具。

---

## 🎯 核心优势

### 简单易用
- 🖥️ **Web界面操作** - 无需编程知识
- 📝 **三步完成** - 脚本→参数→生成
- 🎨 **可视化调整** - 参数实时预览

### 专业输出
- 🎬 **电影级画质** - 1344×768分辨率
- 🎵 **原生立体声** - MiniMax H3音频
- ⏱️ **精确同步** - 音频驱动视频

### 高效自动化
- 🤖 **一键生成** - 全流程自动化
- ⚡ **批量处理** - 支持多场景脚本
- 📊 **实时监控** - 进度一目了然

---

## 🚀 快速开始

### Web界面（推荐）

```bash
# 1. 进入项目
cd video-story-generator/web

# 2. 启动服务
bash start.sh

# 3. 浏览器访问
http://localhost:8501
```

### 命令行

```bash
# 使用示例脚本
python scripts/auto_generate.py examples/scifi_story.json
```

---

## 📊 性能数据

| 项目 | 数据 |
|------|------|
| 单场景生成时间 | 40-60分钟 |
| 8场景总时长 | 约2小时 |
| 输出分辨率 | 1344×768 |
| 音频格式 | AAC立体声 |
| 文件大小 | 4-7MB/场景 |

---

## 🎨 使用场景

### 个人创作
- YouTube短视频
- TikTok内容
- Instagram Reels
- 微博视频号

### 企业应用
- 产品宣传
- 企业介绍
- 培训视频
- 营销内容

### 教育领域
- 在线课程
- 教学演示
- 知识科普
- 学习资料

---

## 💡 功能特点

### 音频驱动生成
视频时长由解说词音频精确决定，完美同步。

### 多种TTS语音
- 🎀 温柔女声 - `zh-CN-XiaoxiaoNeural`
- 👦 年轻男声 - `zh-CN-YunxiNeural`
- 👨 成熟男声 - `zh-CN-YunjianNeural`

### 参数可调
- 📐 分辨率：960×544 / 1344×768 / 1920×1080
- 🎯 采样步数：15-30（质量vs速度）
- 🎚️ 音量控制：解说词 + 环境音独立调节

### Web界面
- 📝 在线脚本编辑
- 🎥 参数可视化调整
- 📊 实时进度监控
- 🎞️ 在线预览下载

---

## 🛠️ 技术栈

- **AI模型**: MiniMax H3
- **TTS服务**: edge-tts (Microsoft)
- **视频生成**: ComfyUI
- **Web框架**: Streamlit
- **音频处理**: ffmpeg

---

## 📁 项目结构

```
video-story-generator/
├── SKILL.md                 # 完整技能文档
├── README.md                # 项目说明
├── scripts/
│   └── auto_generate.py     # 自动化脚本
├── templates/
│   └── script_template.json # 脚本模板
├── examples/                # 示例项目
│   └── scifi_battle_journey/
└── web/                     # Web界面
    ├── app.py              # 主应用
    ├── start.sh            # 启动脚本
    └── README.md           # Web文档
```

---

## 🎬 示例项目

**星辰战斗与归途** - 科幻动画短片

- ⏱️ 时长：1.52分钟
- 🎭 场景：8个
- 🎨 风格：太空歌剧
- 📦 文件：约19MB视频

---

## ⚙️ 系统要求

### 硬件
- GPU: NVIDIA RTX 3090+ (24GB+ VRAM)
- 内存: 32GB+
- 存储: 100GB+

### 软件
- ComfyUI 0.34.0+
- Python 3.10+
- ffmpeg

---

## 📚 文档资源

- **完整文档**: `SKILL.md`
- **快速开始**: `QUICKSTART.md`
- **Web指南**: `WEB_QUICKSTART.md`
- **项目总结**: `PROJECT_SUMMARY.md`

---

## 🔗 获取方式

**GitHub**: https://github.com/wangfeiwest2025/video-story-generator

```bash
git clone https://github.com/wangfeiwest2025/video-story-generator.git
```

---

## 📄 许可证

MIT License - 可自由使用、修改和分发

---

## 🎉 开始创作

🎬 **让AI为您讲述故事！**

1. ⭐ Star GitHub仓库
2. 📖 阅读文档
3. 🚀 启动Web界面
4. 🎥 创作您的第一个AI短视频

---

**AI短视频自动化制作技能 - 专业级视频，人人可及**