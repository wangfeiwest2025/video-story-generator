# 🚀 使用外部ComfyUI快速开始

## 示例URL
`https://yvkxlmr70c-8188.cnb.run/`

---

## 快速测试

### 步骤1: 测试连接

```bash
# 测试ComfyUI服务器是否可用
curl https://yvkxlmr70c-8188.cnb.run/system_stats
```

### 步骤2: 准备脚本

创建测试脚本 `test.json`:

```json
{
  "title": "测试视频",
  "style": "电影级",
  "scenes": [
    {
      "id": 1,
      "narration": "这是一个测试场景",
      "visual_prompt": "A beautiful sunset over mountains, golden light, cinematic, 4K quality",
      "audio": "gentle wind, ambient music"
    }
  ]
}
```

### 步骤3: 生成视频

```bash
# 使用外部ComfyUI生成
python scripts/auto_generate.py test.json \
    --comfyui-url https://yvkxlmr70c-8188.cnb.run/ \
    --output test_output/
```

---

## Web界面使用

### 步骤1: 启动Web界面

```bash
cd web/
bash start.sh
```

### 步骤2: 配置ComfyUI

1. 访问 `http://localhost:8501`
2. 在侧边栏选择"远程URL"
3. 输入: `https://yvkxlmr70c-8188.cnb.run/`
4. 点击"测试连接"

### 步骤3: 创建并生成

1. 在"脚本编辑"标签创建脚本
2. 调整参数
3. 点击"开始生成"

---

## 命令行完整示例

```bash
# 完整参数示例
python scripts/auto_generate.py my_story.json \
    --comfyui-url https://yvkxlmr70c-8188.cnb.run/ \
    --output my_videos/ \
    --width 1344 \
    --height 768 \
    --steps 20 \
    --voice zh-CN-XiaoxiaoNeural \
    --narration-volume 1.2 \
    --ambient-volume 0.5
```

---

## 预期输出

```
🔌 ComfyUI地址: https://yvkxlmr70c-8188.cnb.run/
================================================================================
🎙️ 阶段1: 生成解说词音频
================================================================================
...
✅ 音频生成完成
================================================================================
🎬 阶段2: 生成视频
================================================================================
...
✅ 视频生成完成
================================================================================
✨ 完成！
```

---

## 查看结果

```bash
# 查看生成的视频
ls my_videos/video/*.mp4

# 播放视频
vlc my_videos/video/scene_01_00001_.mp4
```

---

## 注意事项

1. ✅ 确保外部ComfyUI服务器已安装MiniMax H3模型
2. ✅ 检查网络连接稳定性
3. ✅ 视频生成需要较长时间（约40-60分钟/场景）
4. ✅ 建议先用简单脚本测试

---

**🎬 现在就开始使用外部ComfyUI生成AI视频！**