# 📥 媒体文件下载说明

由于视频和音频文件较大（约20MB），未包含在Git仓库中。

## 📊 已生成内容

### 视频文件 (4个场景)
- `scifi_scene_01_00001_.mp4` - 3.3MB
- `scifi_scene_02_00001_.mp4` - 3.2MB
- `scifi_scene_03_00001_.mp4` - 7.4MB
- `scifi_scene_04_00001_.mp4` - 4.6MB

**总大小**: 约19MB

### 音频文件 (8个场景)
- `narration_01.mp3` - `narration_08.mp3`

**总大小**: 约552KB

## 🔗 如何获取

### 方法1: 自己生成

使用提供的脚本自行生成：

```bash
# 1. 克隆仓库
git clone https://github.com/wangfeiwest2025/video-story-generator.git
cd video-story-generator

# 2. 运行生成脚本
python3 scripts/auto_generate.py examples/scifi_story.json

# 3. 等待生成完成（约2小时）
```

### 方法2: 查看生成日志

查看项目进度文档：
- `docs/PROJECT_STATUS.md` - 详细的生成进度

## 📝 生成配置

本项目使用以下配置生成：

- **模型**: MiniMax H3
- **分辨率**: 1344×768
- **帧率**: 24fps
- **总时长**: 91.49秒 (1.52分钟)
- **场景数**: 8个

## ⏱️ 生成时间

- **音频生成**: 约2分钟
- **视频生成**: 约40分钟/场景
- **总时间**: 约2小时（8个场景）

## 🎯 完成状态

- ✅ 场景1-4: 已完成
- 🔄 场景5-8: 生成中

---

**💡 提示**: 使用video-story-generator技能，您也可以创建自己的AI短视频！