# 🎬 AI短视频自动化制作智能体

## 📖 项目概述

**AI短视频自动化制作智能体**是一个端到端的视频内容生成系统，能够从文字脚本自动生成专业级短视频。该系统集成了文本转语音（TTS）、AI视频生成、音频混合等先进技术，实现了从"创意"到"成片"的全自动化流程。

### 🎯 核心价值

- **一键生成**：只需提供文字脚本，即可自动生成包含解说词、环境音效、画面的完整视频
- **专业品质**：输出电影级画质视频（最高支持 1920x1080），原生立体声音频
- **灵活配置**：支持多种分辨率、采样步数、音量调节等参数
- **云端部署**：支持魔搭创空间、Docker、本地等多种部署方式

---

## ✨ 核心功能

### 1. 🎙️ 智能音频生成

#### 文字转语音（TTS）
- **引擎**：Microsoft Edge-TTS
- **支持语言**：中文（多种方言）
- **可选语音**：
  - `zh-CN-XiaoxiaoNeural` - 女声，温柔
  - `zh-CN-YunxiNeural` - 男声，年轻
  - `zh-CN-YunjianNeural` - 男声，成熟

#### 音频时长计算
- 自动计算音频时长
- 精确转换为视频帧数
- 符合 MiniMax H3 模型要求（帧数 ≡ 1 mod 17）

### 2. 🎨 AI 视频生成

#### 核心技术：MiniMax H3
- **模型类型**：文本到视频生成模型
- **分辨率支持**：
  - 960x544（低分辨率，速度快）
  - 1344x768（推荐，平衡质量和速度）
  - 1920x1080（高清，质量最佳）
- **帧率**：24 FPS
- **时长驱动**：视频时长由解说词音频精确决定

#### 模型组件
```
┌─────────────────────────────────────────┐
│         MiniMax H3 模型架构             │
├─────────────────────────────────────────┤
│ UNETLoader      - 主模型               │
│ CLIPLoader      - 文本编码器           │
│ VAELoader (视频) - 视频解码器          │
│ VAELoader (音频) - 音频解码器          │
└─────────────────────────────────────────┘
```

### 3. 🔊 智能音频混合

#### 混合策略
- **输入源**：
  - 原始视频音轨（环境音、背景音乐）
  - TTS 生成的解说词
- **混合方式**：使用 FFmpeg 进行多轨道混音
- **音量控制**：
  - 解说词音量：可调（默认 1.2x）
  - 环境音音量：可调（默认 0.5x）

#### 输出质量
- **音频编码**：AAC
- **声道**：立体声
- **比特率**：自适应

### 4. 🎬 视频合成

#### 多场景合成
- 自动拼接多个场景视频
- 使用 FFmpeg concat 协议
- 保持原始画质，无损合成

#### 单场景优化
- 单场景无需合成，直接输出
- 提高处理效率

---

## 🏗️ 技术架构

### 系统架构图

```
┌──────────────────────────────────────────────────────────┐
│                    用户界面层                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Streamlit   │  │ Web UI      │  │ 参数配置    │    │
│  │ Web界面     │  │ 标签页      │  │ 侧边栏      │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└───────────────────┬──────────────────────────────────────┘
                    │
┌───────────────────┴──────────────────────────────────────┐
│                    核心处理层                            │
│  ┌─────────────────────────────────────────────────┐    │
│  │         VideoStoryGenerator (主控制器)          │    │
│  │  ┌───────────┬───────────┬───────────┬───────┐│    │
│  │  │ 音频生成  │ 视频生成  │ 音频混合  │ 合成  ││    │
│  │  └───────────┴───────────┴───────────┴───────┘│    │
│  └─────────────────────────────────────────────────┘    │
└───────────────────┬──────────────────────────────────────┘
                    │
┌───────────────────┴──────────────────────────────────────┐
│                    外部服务层                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ ComfyUI     │  │ Edge-TTS    │  │ FFmpeg      │    │
│  │ (MiniMax)   │  │ API         │  │ 本地        │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### 工作流程

```
┌──────────────────────────────────────────────────────────┐
│                   完整生成流程                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  阶段1: 音频生成 (约1分钟)                               │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ 文字脚本 │ -> │ Edge-TTS│ -> │ MP3音频 │            │
│  └─────────┘    └─────────┘    └─────────┘            │
│                                                          │
│  阶段2: 视频生成 (20-45分钟/场景)                       │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ 提示词  │ -> │ MiniMax │ -> │ MP4视频 │            │
│  │ 音频时长│    │ H3 GPU  │    │ (环境音)│            │
│  └─────────┘    └─────────┘    └─────────┘            │
│                                                          │
│  阶段3: 音频混合 (约5分钟)                               │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ 视频音轨│ -> │ FFmpeg  │ -> │ 混合音频│            │
│  │ 解说词  │    │ amix    │    │ 视频文件│            │
│  └─────────┘    └─────────┘    └─────────┘            │
│                                                          │
│  阶段4: 视频合成 (约1分钟)                               │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ 多场景  │ -> │ FFmpeg  │ -> │ 最终视频│            │
│  │ 混合视频│    │ concat  │    │ 完整版  │            │
│  └─────────┘    └─────────┘    └─────────┘            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🛠️ 技术栈

### 前端技术
- **框架**：Streamlit 1.30+
- **特性**：
  - 响应式布局
  - 实时进度监控
  - 文件预览和下载
  - 参数可视化调节

### 后端技术
- **语言**：Python 3.10+
- **核心库**：
  - `edge-tts` - 文本转语音
  - `mutagen` - 音频元数据处理
  - `requests` - HTTP 请求
  - `asyncio` - 异步处理

### AI 模型
- **视频生成**：MiniMax H3
  - `minimax_h3_fl2va_int8_convrot.safetensors` - 主模型
  - `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` - 文本编码器
  - `minimax_h3_video_vae_fp16.safetensors` - 视频解码器
  - `minimax_h3_audio_vae_fp32.safetensors` - 音频解码器

### 多媒体处理
- **工具**：FFmpeg 7.1+
- **功能**：
  - 音频混合
  - 视频拼接
  - 格式转换
  - 编码优化

### 推理引擎
- **平台**：ComfyUI 0.34.0+
- **特性**：
  - 图形化工作流
  - 节点式处理
  - 支持远程部署
  - RESTful API

---

## 💻 部署方式

### 1. 魔搭创空间（推荐）

#### 优势
- ✅ 免费使用
- ✅ GPU 支持
- ✅ 免配置环境
- ✅ 支持外部 ComfyUI

#### 配置步骤
```
1. Fork 项目到魔搭创空间
2. 配置外部 ComfyUI 地址
3. 启动应用
4. 通过 Web 界面使用
```

#### 正确配置
```
ComfyUI地址: https://xxx-8188.cnb.run/
ComfyUI输出目录: (留空)
```

### 2. Docker 部署

#### Dockerfile
```dockerfile
FROM python:3.10-slim

# 安装 FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用
COPY . /app
WORKDIR /app

# 启动
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
```

### 3. 本地开发

#### 环境准备
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 FFmpeg
sudo apt-get install ffmpeg

# 启动 ComfyUI
cd ComfyUI
python main.py --listen 0.0.0.0 --port 8188

# 启动 Web 界面
cd web
bash start.sh
```

---

## 📂 项目结构

```
video-story-generator/
├── 📁 web/                    # Web 界面
│   ├── app.py                 # Streamlit 主程序
│   ├── requirements.txt       # Python 依赖
│   ├── start.sh              # 启动脚本
│   └── Dockerfile            # Docker 配置
│
├── 📁 scripts/               # 核心脚本
│   └── auto_generate.py      # 主生成流程
│
├── 📁 examples/              # 示例项目
│   ├── scifi_story.json      # 科幻脚本示例
│   ├── nature_documentary.json # 自然纪录片示例
│   └── scifi_battle_journey/ # 完整示例项目
│
├── 📁 templates/             # 模板文件
│   └── script_template.json  # 脚本模板
│
├── 📁 docs/                  # 文档
│   ├── ModelScope_DEPLOYMENT.md  # 魔搭部署指南
│   ├── DEPLOYMENT_ISSUES.md      # 部署问题排查
│   ├── TROUBLESHOOTING.md        # 故障排查
│   └── PATH_LOGIC_FIX_REPORT.md  # 路径修复报告
│
├── 📄 README.md              # 项目说明
├── 📄 SKILL.md              # 技能文档
├── 📄 requirements.txt      # Python 依赖
├── 📄 test_simple.json      # 测试脚本
│
├── 🔧 diagnose_deployment.py    # 部署诊断工具
├── 🔧 diagnose_comfyui.py       # ComfyUI 诊断
├── 🔧 check_config.py           # 配置检查工具
└── 🔧 full_diagnose.py          # 完整诊断
```

---

## 🎬 使用场景

### 1. 📚 教育培训
- 在线课程视频制作
- 知识科普短片
- 教学演示视频

**示例**：
```json
{
  "title": "Python编程入门",
  "scenes": [
    {
      "id": 1,
      "narration": "欢迎来到Python编程入门课程...",
      "visual_prompt": "A modern computer screen showing Python code",
      "audio": "soft background music"
    }
  ]
}
```

### 2. 📰 新闻资讯
- 新闻简报
- 行业动态
- 产品介绍

**示例**：
```json
{
  "title": "科技新闻简报",
  "scenes": [
    {
      "id": 1,
      "narration": "今日科技要闻...",
      "visual_prompt": "News studio with technology theme",
      "audio": "news broadcast music"
    }
  ]
}
```

### 3. 🎨 创意内容
- 短片故事
- 艺术创作
- 概念展示

**示例**：
```json
{
  "title": "星空之旅",
  "style": "电影级",
  "scenes": [
    {
      "id": 1,
      "narration": "在遥远的星系中...",
      "visual_prompt": "Beautiful galaxy with colorful nebula",
      "audio": "epic space music"
    }
  ]
}
```

### 4. 📊 商业应用
- 产品演示
- 品牌宣传
- 营销视频

**示例**：
```json
{
  "title": "产品发布",
  "scenes": [
    {
      "id": 1,
      "narration": "隆重推出我们的新产品...",
      "visual_prompt": "Sleek product showcase on dark background",
      "audio": "upbeat corporate music"
    }
  ]
}
```

---

## ⚡ 性能指标

### 生成时间

| 场景时长 | 单场景生成时间 | 总体预估（8场景） |
|----------|----------------|-------------------|
| 6-8秒    | 20-25分钟      | 约 1.5小时        |
| 10-12秒  | 40-45分钟      | 约 2.5小时        |

### 资源占用

| 资源类型 | 最低要求 | 推荐配置 |
|----------|----------|----------|
| GPU      | RTX 3090 (24GB) | RTX 4090 (24GB+) |
| 内存     | 32GB     | 64GB     |
| 存储     | 100GB    | 200GB+   |

### 输出质量

| 参数 | 规格 |
|------|------|
| 分辨率 | 最高 1920x1080 |
| 帧率 | 24 FPS |
| 音频 | AAC 立体声 |
| 编码 | H.264 |

---

## 🌟 项目特色

### 1. 音频驱动生成
- 视频时长由解说词音频精确决定
- 自动计算最佳帧数
- 无需手动调整

### 2. 智能路径处理
- 自动检测远程/本地 ComfyUI
- API 下载或文件复制自动选择
- 支持多种部署架构

### 3. 完善的错误处理
- 详细的错误诊断
- 清晰的解决方案提示
- 多个诊断工具

### 4. 用户友好界面
- 可视化参数调节
- 实时进度监控
- 在线预览下载

### 5. 灵活部署选项
- 魔搭创空间（推荐）
- Docker 容器
- 本地开发
- 云端部署

---

## 🔧 故障排查

### 常见问题

#### 1. 无法调用 ComfyUI
**症状**：只生成音频，视频生成失败

**原因**：
- ComfyUI 地址端口错误（常见：填了 8501 而非 8188）
- ComfyUI 未启动
- 网络不通

**解决方案**：
```
✅ 检查 ComfyUI 地址端口是否为 8188
✅ 点击"测试连接"验证
✅ 确认 ComfyUI 正在运行
```

#### 2. 视频合成失败
**症状**：显示"视频合成失败"

**原因**：
- FFmpeg 未安装
- 磁盘空间不足
- 文件权限问题

**解决方案**：
```bash
# 安装 FFmpeg
apt-get install ffmpeg

# 检查磁盘空间
df -h

# 检查权限
ls -la output/
```

#### 3. 视频文件未找到
**症状**：显示"未找到视频文件"

**原因**：
- ComfyUI 输出目录配置错误
- 视频生成未完成

**解决方案**：
```
✅ 将 ComfyUI 输出目录留空（使用 API 下载）
✅ 等待视频生成完成
✅ 检查 ComfyUI 队列状态
```

---

## 📚 相关文档

- **快速开始**: `QUICKSTART.md`
- **完整文档**: `SKILL.md`
- **外部 ComfyUI**: `docs/EXTERNAL_COMFYUI.md`
- **魔搭部署**: `docs/ModelScope_DEPLOYMENT.md`
- **故障排查**: `docs/TROUBLESHOOTING.md`
- **路径修复报告**: `docs/PATH_LOGIC_FIX_REPORT.md`

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/wangfeiwest2025/video-story-generator.git

# 安装依赖
pip install -r requirements.txt

# 运行测试
python scripts/auto_generate.py test_simple.json
```

### 代码规范
- Python 代码遵循 PEP 8
- 提交信息清晰描述改动
- 添加必要的注释和文档

---

## 📄 许可证

MIT License

---

## 📞 联系方式

- **GitHub**: https://github.com/wangfeiwest2025/video-story-generator
- **魔搭创空间**: https://www.modelscope.cn/studios/wangbaozhen/video-story-generator
- **问题反馈**: GitHub Issues

---

## 🎉 结语

**AI短视频自动化制作智能体**让视频创作变得简单高效。从文字到视频，只需几分钟的等待，即可获得专业品质的视频内容。无论您是内容创作者、教育工作者还是企业营销人员，这个工具都能帮助您快速实现视频内容的自动化生产。

**🎬 让 AI 为您讲述故事！**