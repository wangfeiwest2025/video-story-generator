# 🚀 快速开始指南

## 5分钟快速上手

### 第1步：检查环境（1分钟）

```bash
cd video-story-generator
bash scripts/check_environment.sh
```

确保所有项都是 ✅

---

### 第2步：创建您的第一个脚本（2分钟）

复制模板：

```bash
cp templates/script_template.json my_first_video.json
```

编辑 `my_first_video.json`，修改以下内容：

```json
{
  "title": "我的第一个AI视频",
  "scenes": [
    {
      "id": 1,
      "narration": "你好，这是我的第一个AI生成的视频！",
      "visual_prompt": "Beautiful sunrise over mountains, golden light, peaceful nature scene, 4K quality",
      "audio": "gentle morning music, birds chirping"
    },
    {
      "id": 2,
      "narration": "AI技术正在改变我们的世界。",
      "visual_prompt": "Futuristic cityscape, flying cars, holographic displays, sci-fi atmosphere, cinematic lighting",
      "audio": "futuristic ambience, electronic music"
    }
  ]
}
```

---

### 第3步：一键生成（2分钟操作，自动运行）

```bash
python3 scripts/auto_generate.py my_first_video.json --output my_output/
```

**然后等待...**
- 音频生成: ~1分钟
- 视频生成: ~40-60分钟
- 最终合成: ~2分钟

---

## 📊 生成时间预估

| 场景数 | 总时长 | 生成时间 |
|--------|--------|----------|
| 2个 | 15-20秒 | ~45分钟 |
| 4个 | 30-40秒 | ~1.5小时 |
| 8个 | 1-1.5分钟 | ~2.5小时 |

---

## 🎨 快速示例

### 示例1: 使用现成的脚本

```bash
# 科幻动画
python3 scripts/auto_generate.py examples/scifi_story.json

# 自然纪录片
python3 scripts/auto_generate.py examples/nature_documentary.json
```

---

## 💡 实用技巧

### 技巧1: 快速测试

创建一个2场景的短脚本快速测试：

```json
{
  "title": "快速测试",
  "scenes": [
    {
      "id": 1,
      "narration": "测试场景1",
      "visual_prompt": "A simple test scene",
      "audio": "test audio"
    },
    {
      "id": 2,
      "narration": "测试场景2",
      "visual_prompt": "Another test scene",
      "audio": "test audio"
    }
  ]
}
```

生成时间约 **40-50分钟**

### 技巧2: 查看进度

```bash
# 查看ComfyUI队列
curl -s http://127.0.0.1:8188/queue | jq

# 查看生成的视频
ls -lh my_output/video/
```

### 技巧3: 提高质量

修改 `scripts/auto_generate.py` 中的参数：

```python
# 增加采样步数（更高质量，更慢）
"steps": 25  # 默认20

# 提高分辨率（更大文件，更慢）
"width": 1344,
"height": 768  # 或 960x544 更快
```

---

## 🎯 常见用途

### 用途1: 产品宣传视频
- 时长: 30-60秒
- 场景: 3-5个
- 风格: 科技、现代

### 用途2: 故事短片
- 时长: 1-3分钟
- 场景: 6-12个
- 风格: 电影级

### 用途3: 教育视频
- 时长: 2-5分钟
- 场景: 8-15个
- 风格: 清晰、专业

---

## 📞 获取帮助

遇到问题？查看：

1. **环境检查**: `bash scripts/check_environment.sh`
2. **完整文档**: `SKILL.md`
3. **示例项目**: `examples/` 目录

---

**🎉 开始创作您的AI视频吧！**