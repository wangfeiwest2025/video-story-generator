---
name: video-story-generator
description: AI驱动的短视频自动化制作技能 - 从脚本到成片，支持音频驱动视频生成
version: 1.0.0
tags: [video, ai, storytelling, automation, minimax]
---

# 🎬 Video Story Generator - AI短视频自动化制作

## 概述

这是一个完整的短视频自动化制作技能，将复杂的视频生成流程简化为**3个步骤**：

1. **📝 撰写分镜脚本** - 定义场景、解说词、视觉提示
2. **🎙️ 生成解说词音频** - 使用TTS自动生成
3. **🎬 自动生成视频** - AI生成视频+环境音，自动合成

**核心特性**:
- ✅ 音频驱动 - 视频时长由音频决定
- ✅ 原生音频生成 - MiniMax H3自动生成环境音效和音乐
- ✅ 批量生成 - 自动处理多个场景
- ✅ 端到端自动化 - 从脚本到成片无需手动干预

---

## 使用方法

### 快速开始

```
/video-story-generator --title "我的故事" --duration 90 --style "科幻动画"
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--title` | 短片标题 | "AI生成短片" |
| `--duration` | 目标时长（秒） | 60 |
| `--style` | 视觉风格 | "电影级" |
| `--resolution` | 分辨率 | "1344x768" |
| `--fps` | 帧率 | 24 |
| `--voice` | TTS语音 | "zh-CN-XiaoxiaoNeural" |
| `--scenes` | 场景配置文件 | 自动生成 |

---

## 工作流程

### 阶段1: 脚本准备

创建分镜脚本JSON文件：

```json
{
  "title": "我的故事",
  "style": "科幻动画",
  "scenes": [
    {
      "id": 1,
      "narration": "解说词文本...",
      "visual_prompt": "Visual description in English...",
      "audio": "audio description: music, sfx"
    }
  ]
}
```

### 阶段2: 音频生成

```bash
python generate_narration.py --script script.json --output audio/
```

- 使用 edge-tts（免费）或其他TTS服务
- 自动计算每个音频时长
- 生成音频清单和时长信息

### 阶段3: 视频生成

```bash
python generate_videos.py --audio audio/ --output video/
```

- MiniMax H3生成视频+环境音
- 根据音频时长自动调整视频长度
- 批量提交到队列

### 阶段4: 自动合成

```bash
python compose_final.py --scenes scenes/ --output final.mp4
```

- 混合解说词和环境音
- 拼接所有场景
- 生成最终视频

---

## 完整示例

### 示例1: 科幻动画短片（1.5分钟）

```python
# 定义脚本
script = {
    "title": "星辰战斗与归途",
    "style": "科幻动画，太空歌剧",
    "scenes": [
        {
            "id": 1,
            "narration": "在银河边缘，星际战役即将开始...",
            "visual_prompt": "Epic space battle, countless battleships...",
            "audio": "dramatic orchestral music, engine roar"
        },
        # ... 更多场景
    ]
}

# 一键生成
python auto_generate.py --script script.json
```

**输出**:
- 8个场景视频（每个10-12秒）
- 解说词音频（8个）
- 最终合成视频（1.5分钟）

---

## 技术细节

### 视频参数

**MiniMax H3 模型**:
- 模型: `minimax_h3_fl2va_int8_convrot.safetensors`
- 文本编码器: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- 视频VAE: `minimax_h3_video_vae_fp16.safetensors`
- 音频VAE: `minimax_h3_audio_vae_fp32.safetensors`

**视频规格**:
- 分辨率: 1344×768 (16:9宽屏)
- 帧率: 24fps
- 单场景时长: 8-15秒（MiniMax H3限制）
- 音频: 原生立体声（自动生成环境音+音乐）

### 帧数计算公式

MiniMax H3 要求帧数符合特定规律：

```python
frames_needed = round(duration_seconds * 24)
length = max(5, frames_needed) + (5 - (max(5, frames_needed) % 17)) % 17
```

### 音频混合策略

```python
# 环境音音量: 50% (背景)
# 解说词音量: 120% (突出)
ffmpeg -i video.mp4 -i narration.mp3 \
       -filter_complex "[0:a]volume=0.5[env];[1:a]volume=1.2[narr];[env][narr]amix=inputs=2:duration=first[aout]" \
       -map 0:v -map "[aout]" output.mp4
```

---

## 文件结构

```
video-story-generator/
├── SKILL.md                      # 技能文档
├── templates/
│   ├── script_template.json      # 脚本模板
│   ├── workflow_template.json    # ComfyUI工作流模板
│   └── config_template.json      # 配置模板
├── scripts/
│   ├── generate_narration.py     # 音频生成脚本
│   ├── generate_videos.py        # 视频生成脚本
│   ├── batch_generate.py         # 批量生成脚本
│   ├── mix_audio.sh             # 音频混合脚本
│   ├── compose_final.py         # 最终合成脚本
│   └── automate_everything.py   # 全自动化脚本
├── examples/
│   ├── scifi_story.json         # 科幻动画示例
│   ├── nature_documentary.json  # 自然纪录片示例
│   └── product_ad.json          # 产品广告示例
└── utils/
    ├── timing_calculator.py     # 时长计算工具
    ├── prompt_enhancer.py       # 提示词增强工具
    └── quality_checker.py       # 质量检查工具
```

---

## TTS选项

### 免费: Microsoft Edge TTS

```python
# 安装
pip install edge-tts

# 支持的中文语音
voices = [
    "zh-CN-XiaoxiaoNeural",   # 女声，温柔
    "zh-CN-YunxiNeural",      # 男声，年轻
    "zh-CN-YunjianNeural",    # 男声，成熟
    "zh-CN-XiaoyiNeural"      # 女声，活泼
]
```

### 高级: OpenAI TTS

```python
# 需要API key
from openai import OpenAI

client = OpenAI()
response = client.audio.speech.create(
    model="tts-1",
    voice="onyx",  # alloy, echo, fable, onyx, nova, shimmer
    input="解说词文本"
)
```

---

## 性能优化

### 缩短生成时间

1. **减少单场景时长**: 从10-12秒降至6-8秒
2. **降低分辨率**: 从1344×768降至960×544
3. **减少采样步数**: 从20步降至15步（质量略微下降）

**时间对比**:
- 标准配置（10-12秒/场景）: ~45分钟/场景
- 优化配置（6-8秒/场景）: ~25分钟/场景

### 批量生成优化

- 使用队列系统自动调度
- 每个场景独立随机种子
- 自动清理GPU内存

---

## 常见问题

### Q: 为什么生成速度慢？

A: MiniMax H3生成高质量视频+音频需要较长时间：
- 模型加载: ~30秒
- 视频采样: ~15-40分钟（取决于时长）
- 音频生成: ~30秒
- 解码: ~30秒

### Q: 如何提高质量？

A: 调整以下参数：
- 增加采样步数（`steps: 20-30`）
- 提高分镜脚本的详细程度
- 优化视觉提示词（英文更准确）
- 使用高质量TTS语音

### Q: 支持哪些视频风格？

A: MiniMax H3支持多种风格：
- 科幻/太空
- 动画/动漫
- 自然/风景
- 人物/动作
- 抽象/艺术

### Q: 如何添加背景音乐？

A: 两种方式：
1. MiniMax H3自动生成环境音（推荐）
2. 后期添加自定义音乐（需要音频文件）

---

## 最佳实践

### 1. 分镜脚本设计

- **单场景时长**: 8-15秒最佳
- **总场景数**: 5-12个
- **总时长**: 1-3分钟
- **叙事节奏**: 开头铺垫 → 高潮 → 结尾升华

### 2. 视觉提示词优化

```markdown
✅ 好的提示词：
"Commander Ayla piloting her fighter jet, intense space battle, 
dramatic lighting, cinematic slow motion, 4K quality"

❌ 差的提示词：
"A woman in a spaceship fighting"
```

### 3. 音频同步

- 解说词时长决定视频时长
- 留出0.5秒停顿时间
- 环境音自动匹配场景氛围

### 4. 自动化工作流

```bash
# 一键完整流程
python automate_everything.py --script my_story.json
```

---

## 示例项目

### 项目1: 科幻动画《星辰战斗与归途》
- 时长: 1分31秒
- 场景: 8个
- 风格: 太空歌剧
- 生成时间: 约1.5小时

### 项目2: 自然纪录片《深海探秘》
- 时长: 2分钟
- 场景: 10个
- 风格: 自然纪录片
- 生成时间: 约2小时

### 项目3: 产品广告《智能手表》
- 时长: 30秒
- 场景: 4个
- 风格: 科技产品
- 生成时间: 约40分钟

---

## 许可证

MIT License - 自由使用、修改、分发

---

## 贡献

欢迎提交：
- 新的脚本模板
- 优化建议
- Bug修复
- 文档改进

---

## 更新日志

### v1.0.0 (2026-08-26)
- ✅ 初始版本
- ✅ 支持MiniMax H3模型
- ✅ 集成edge-tts
- ✅ 全自动化流程
- ✅ 音频驱动视频生成

---

## 支持

- 📧 Issues: GitHub Issues
- 📖 文档: `/docs`
- 💬 讨论: GitHub Discussions

---

**🎬 让AI为您讲故事！**