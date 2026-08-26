# 🚀 快速启动指南

## 方式1: 直接启动（推荐）

```bash
cd /workspace/video-story-generator/web/
bash start.sh
```

浏览器访问：`http://localhost:8501`

## 方式2: 手动启动

```bash
cd /workspace/video-story-generator/web/

# 激活虚拟环境
source venv/bin/activate

# 启动Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📱 网络访问

如果需要从其他设备访问，使用服务器的IP地址：

```
http://<服务器IP>:8501
```

例如：`http://192.168.1.100:8501`

## ⚙️ 前置条件

### 必须运行ComfyUI

Web界面需要ComfyUI运行在 `http://localhost:8188`

启动ComfyUI：

```bash
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0
```

### 检查ComfyUI状态

```bash
curl http://localhost:8188/system_stats
```

## 🎯 使用流程

### 1. 创建脚本

- 选择"在线编辑"
- 输入视频标题和风格
- 添加场景（解说词、视觉描述、音频描述）
- 点击"生成脚本"

### 2. 调整参数

在侧边栏调整：
- TTS语音（温柔女声/年轻男声/成熟男声）
- 分辨率（960x544 / 1344x768 / 1920x1080）
- 采样步数（15-30）
- 音量比例

### 3. 开始生成

- 切换到"生成控制"标签
- 确认参数
- 点击"开始生成"

### 4. 监控进度

- 查看总体进度
- 查看各阶段状态
- 自动刷新进度

### 5. 预览下载

- 在线预览视频
- 下载最终视频
- 下载单场景视频

## 🐛 故障排除

### Q: 页面无法访问？

检查端口是否开放：

```bash
netstat -tlnp | grep 8501
```

### Q: ComfyUI连接失败？

确保ComfyUI正在运行：

```bash
curl http://localhost:8188/queue
```

### Q: 依赖缺失？

重新安装依赖：

```bash
cd web/
source venv/bin/activate
pip install -r requirements.txt
```

## 📞 获取帮助

- 详细文档：`web/README.md`
- 技能文档：`SKILL.md`
- 示例项目：`examples/`

---

**🎉 开始创作您的AI短视频！**