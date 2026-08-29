# 快速故障排查指南

## ❌ 错误: "argument should be a str or an os.PathLike object..."

### 原因
这个错误发生在 `comfyui_output_dir` 为 `None` 时尝试创建 `Path` 对象。

### ✅ 已修复
最新提交 `d1ddc8a` 已修复此问题。

---

## 配置说明

### 场景 1: ComfyUI 在外部服务器（最常见）

**正确配置**:
```
ComfyUI地址: https://your-gpu-server.com
ComfyUI输出目录: (留空)
```

**工作原理**:
- 系统检测到输出目录为空
- 自动使用 API 下载视频
- 无需文件系统访问

---

### 场景 2: ComfyUI 和创空间在同一环境

**正确配置**:
```
ComfyUI地址: http://127.0.0.1:8188
ComfyUI输出目录: /workspace/output
```

**工作原理**:
- 系统检测到目录存在
- 使用文件系统复制
- 速度更快

---

## 验证步骤

### 1. 检查 ComfyUI 连接

在侧边栏点击"🔌 测试连接"：
- ✅ 应显示"ComfyUI 连接成功"
- 显示 ComfyUI 版本信息

### 2. 查看生成日志

在"📊 进度监控"中查看：

**成功模式** (API 下载):
```
📁 ComfyUI输出目录: 未指定（将通过 API 下载视频）
   💡 这通常发生在 ComfyUI 部署在远程服务器时
...
📋 获取视频文件到项目目录...
   ℹ️ ComfyUI 输出目录未配置
   💡 将通过 API 下载视频
   正在从 https://your-server 下载视频...
   ✅ 已下载: scene_01_00001.mp4
```

**成功模式** (文件复制):
```
📁 ComfyUI输出目录: /workspace/output (自动检测)
...
📋 获取视频文件到项目目录...
   ✅ 使用文件系统复制方式
   ✅ 场景 01: scene_01_00001.mp4
```

---

## 常见错误

### ❌ "无法连接 ComfyUI"

**检查**:
```bash
curl https://your-comfyui-server/system_stats
```

**解决**:
- 确认 ComfyUI 正在运行
- 检查地址和端口
- 检查网络连通性

### ❌ "视频下载失败"

**原因**: ComfyUI 的 `/view` API 无法访问

**检查**:
```bash
curl "https://your-comfyui-server/view?filename=test.mp4&type=output"
```

**解决**:
- ComfyUI 默认支持 `/view` 端点
- 检查是否有访问限制

---

## 最新更新

| 提交 | 修复内容 |
|------|---------|
| `d1ddc8a` | 修复 None 路径处理错误 |
| `9dbfb52` | 改进 UI 提示信息 |
| `b7dec61` | 添加 API 下载功能 |

---

## 获取帮助

如果问题仍然存在：
1. 运行 `diagnose_comfyui.py` 诊断工具
2. 提供错误日志
3. 说明您的部署架构