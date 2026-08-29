# 部署环境差异和解决方案

## 🔍 问题分析

本地测试成功但部署环境失败，通常是环境差异导致的。本文档帮助您诊断和解决这些问题。

---

## 📊 本地 vs 部署环境对比

### 本地环境（成功）
- ✅ FFmpeg 已安装
- ✅ 文件系统可写入
- ✅ 充足的磁盘空间
- ✅ 完整的系统权限

### 部署环境（失败）
- ❓ FFmpeg 是否可用？
- ❓ 文件系统权限如何？
- ❓ 磁盘空间是否充足？
- ❓ 是否有其他限制？

---

## 🎯 常见部署环境问题

### 1. FFmpeg 不可用

#### 症状
```
❌ ffmpeg 未安装
或
❌ ffmpeg: command not found
```

#### 检查方法
```bash
ffmpeg -version
which ffmpeg
```

#### 解决方案

**魔搭创空间**:
魔搭创空间通常已预装 FFmpeg，但可能版本不匹配。

**Streamlit Cloud**:
Streamlit Cloud **不支持 FFmpeg**！

这是关键问题！Streamlit Cloud 的限制：
- ❌ 不支持 FFmpeg
- ❌ 不支持自定义系统包
- ❌ 有磁盘空间限制
- ❌ 有执行时间限制

**解决方案**：
- 使用其他部署平台（Railway, Render, Fly.io）
- 使用 Docker 部署
- 使用魔搭创空间

---

### 2. 磁盘空间不足

#### 症状
```
No space left on device
```

#### 检查
使用诊断脚本检查磁盘空间。

#### 解决方案
```bash
# 清理旧文件
rm -rf output/20260829_*

# 检查磁盘使用
df -h
```

---

### 3. 文件系统权限

#### 症状
```
Permission denied
```

#### 解决方案
```bash
# 修改权限
chmod -R 755 /path/to/project
chown -R user:user /path/to/project
```

---

### 4. 视频文件未生成

#### 症状
```
❌ 没有找到混合后的视频文件
```

#### 可能原因
1. ComfyUI 生成失败
2. 视频下载失败
3. 文件保存失败

#### 诊断步骤

**步骤 1: 检查原始视频**
```
项目目录/output/时间戳/video/
```

**步骤 2: 检查混合视频**
```
项目目录/output/时间戳/final/
```

**步骤 3: 使用诊断工具**
运行 `diagnose_deployment.py` 检查详细情况。

---

### 5. 音频混合失败

#### 症状
```
❌ 失败: [ffmpeg错误]
```

#### 可能原因
- FFmpeg 不可用
- 视频文件损坏
- 编码器不支持

---

## 🛠️ 部署平台选择

### ✅ 推荐平台

#### 1. 魔搭创空间
- ✅ 支持 FFmpeg
- ✅ 充足的磁盘空间
- ✅ GPU 支持
- ⚠️ 需要正确配置 ComfyUI 地址

#### 2. Railway
- ✅ 支持 FFmpeg
- ✅ Docker 支持
- ✅ 自定义环境
- 💰 收费（有免费额度）

#### 3. Render
- ✅ 支持 FFmpeg
- ✅ Docker 支持
- ⏱️ 免费版有限制

#### 4. Fly.io
- ✅ 完全自定义
- ✅ Docker 支持
- 💰 收费（有免费额度）

### ❌ 不推荐平台

#### Streamlit Cloud
- ❌ 不支持 FFmpeg
- ❌ 无法安装系统包
- ❌ 有严格的限制
- ❌ **不适合视频处理应用**

---

## 🚀 部署最佳实践

### 1. 使用 Docker 部署

创建 `Dockerfile`:
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
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. 配置外部 ComfyUI

```
ComfyUI地址: https://your-comfyui-server:8188/
ComfyUI输出目录: (留空)
```

### 3. 监控资源使用

定期检查：
- 磁盘空间
- 内存使用
- GPU 使用率

---

## 📝 诊断清单

部署前请确认：

- [ ] FFmpeg 是否安装？运行 `ffmpeg -version`
- [ ] 磁盘空间是否充足？至少 5GB
- [ ] 文件系统可写入？创建测试文件
- [ ] ComfyUI 地址正确？端口是 8188 不是 8501
- [ ] ComfyUI 可访问？点击"测试连接"
- [ ] Python 依赖已安装？检查 `requirements.txt`
- [ ] 环境变量已设置？如需要

---

## 🔧 故障排查步骤

### 步骤 1: 运行诊断工具

修改启动文件为 `diagnose_deployment.py`，检查：
- FFmpeg 状态
- 文件系统权限
- 磁盘空间
- 输出目录内容

### 步骤 2: 检查日志

查看进度监控中的详细输出：
- 在哪一步失败？
- 具体的错误信息是什么？

### 步骤 3: 验证文件

在结果预览中检查：
- 原始视频是否存在？
- 混合视频是否存在？
- 文件大小是否正常？

### 步骤 4: 测试简单案例

使用单场景测试脚本：
```json
{
  "title": "Test",
  "scenes": [{"id": 1, "narration": "测试", "visual_prompt": "test", "audio": "test"}]
}
```

---

## 💡 临时解决方案

如果视频合成失败：

### 方案 1: 使用混合视频

单场景或合成失败时，直接使用：
```
output/时间戳/final/scene_01_mixed.mp4
```

### 方案 2: 使用原始视频

如果混合也失败，使用原始视频：
```
output/时间戳/video/scene_01_00001.mp4
```
（仅环境音，无解说词）

### 方案 3: 本地处理

从创空间下载视频和音频，在本地使用 FFmpeg 合成：
```bash
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4
```

---

## 📞 获取帮助

如果问题仍然存在：

1. 运行 `diagnose_deployment.py` 诊断工具
2. 导出诊断报告
3. 提供以下信息：
   - 部署平台（魔搭/Streamlit Cloud/其他）
   - 诊断报告
   - 进度监控中的错误信息
   - 输出目录的文件情况

---

## 🎉 推荐部署方案

**最佳选择**：魔搭创空间 + 外部 ComfyUI

**配置**：
```
ComfyUI地址: https://xxx-8188.cnb.run/
ComfyUI输出目录: (留空)
```

**优势**：
- ✅ 稳定可靠
- ✅ 支持 FFmpeg
- ✅ 免费使用
- ✅ GPU 支持
- ✅ 充足资源

**避免**：
- ❌ Streamlit Cloud（不支持 FFmpeg）
- ❌ 免费平台的各种限制