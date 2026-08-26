# 🎬 AI短视频自动化制作技能

快速生成专业级AI短视频，从脚本到成片全自动化。

## ✨ 特性

- 🎯 **音频驱动** - 视频时长由解说词音频精确决定
- 🎨 **原生音频生成** - MiniMax H3自动生成环境音效和音乐
- 🤖 **全自动化** - 一键从脚本到成片
- 📊 **批量处理** - 自动处理多个场景
- 🎬 **专业输出** - 电影级画质，原生立体声

## 🚀 快速开始

### 1. 准备脚本

创建分镜脚本 `my_story.json`:

```json
{
  "title": "我的故事",
  "style": "电影级",
  "scenes": [
    {
      "id": 1,
      "narration": "解说词文本...",
      "visual_prompt": "Visual description in English...",
      "audio": "ambient sounds description"
    }
  ]
}
```

### 2. 一键生成

```bash
python scripts/auto_generate.py my_story.json --output output/
```

### 3. 获取结果

生成完成后，您将得到：
- `output/final/我的故事_final.mp4` - 最终视频

## 📋 完整流程

```
脚本 → 音频生成 → 视频生成 → 音频混合 → 最终合成
(1分钟)  (5分钟)    (30-60分钟)  (5分钟)    (1分钟)
```

## 🎨 示例项目

查看 `examples/` 目录：

1. **科幻动画《星辰战斗与归途》** - `scifi_battle_journey/` ⭐
   - 时长: 1.5分钟
   - 场景: 8个 (4个已完成)
   - 风格: 太空歌剧
   - **状态**: 实际生成项目，包含脚本、音频和进度文档
   - 📁 查看: `examples/scifi_battle_journey/`

2. **科幻动画脚本** - `scifi_story.json`
   - 时长: 1.5分钟
   - 场景: 8个
   - 风格: 太空歌剧
   - 可直接使用的脚本模板

3. **自然纪录片** - `nature_documentary.json`
   - 时长: 2分钟
   - 场景: 4个
   - 风格: 水下摄影

## 🛠️ 配置要求

### 软件要求
- ComfyUI 0.34.0+
- Python 3.10+
- ffmpeg
- edge-tts

### 硬件要求
- GPU: NVIDIA RTX 3090或更高（24GB+ VRAM推荐）
- 内存: 32GB+
- 存储: 100GB+

### MiniMax H3 模型

确保已安装以下模型：
- `minimax_h3_fl2va_int8_convrot.safetensors`
- `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- `minimax_h3_video_vae_fp16.safetensors`
- `minimax_h3_audio_vae_fp32.safetensors`

## 📚 文档

- **完整文档**: `SKILL.md`
- **脚本模板**: `templates/script_template.json`
- **工具脚本**: `scripts/`

## ⏱️ 性能

| 场景时长 | 单场景生成时间 | 总体预估 |
|----------|----------------|----------|
| 6-8秒 | 20-25分钟 | 1.5小时（8场景） |
| 10-12秒 | 40-45分钟 | 2.5小时（8场景） |

## 🎯 最佳实践

### 分镜脚本
- 单场景时长: 8-15秒最佳
- 总场景数: 5-12个
- 总时长: 1-3分钟

### 视觉提示词
- 使用英文描述
- 包含光线、镜头、风格
- 详细描述主体和动作

### 音频描述
- 描述环境音效
- 指定音乐类型
- 增强场景氛围

## 🔧 高级用法

### 自定义TTS语音

```json
{
  "voice": "zh-CN-YunxiNeural"
}
```

可选语音：
- `zh-CN-XiaoxiaoNeural` - 女声，温柔
- `zh-CN-YunxiNeural` - 男声，年轻
- `zh-CN-YunjianNeural` - 男声，成熟

### 调整视频参数

编辑 `scripts/auto_generate.py` 中的参数：
- `steps`: 采样步数（质量vs速度）
- `resolution`: 分辨率
- `audio_volume`: 音频音量比例

## 🐛 故障排除

### Q: 生成速度慢？
A: 降低场景时长或分辨率

### Q: 音频不同步？
A: 检查音频文件是否完整生成

### Q: 视频质量差？
A: 增加采样步数，优化视觉提示词

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**🎬 让AI为您讲述故事！**