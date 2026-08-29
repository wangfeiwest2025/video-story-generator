# 魔搭创空间部署指南

## 问题分析

在魔搭创空间中无法调用 ComfyUI 的主要原因是：

### 典型部署架构

```
┌─────────────────┐         ┌──────────────────┐
│  魔搭创空间      │         │  ComfyUI 服务     │
│  (Web应用)      │  HTTP   │  (GPU推理服务器)  │
│                 │◄───────►│                  │
│  - Streamlit UI │         │  - MiniMax H3    │
│  - Python环境   │         │  - 视频生成      │
│                 │         │                  │
│  /app/output/   │         │  /workspace/     │
│  (项目输出)     │         │  output/         │
└─────────────────┘         └──────────────────┘
        ▲                            ▲
        │                            │
        └──────────── 文件系统隔离 ───┘
```

### 核心问题

1. **文件系统隔离**: 魔搭创空间和 ComfyUI 在不同的容器/服务器中
2. **无法直接访问**: 创空间无法访问 ComfyUI 的 `/workspace/output` 目录
3. **只能通过 API**: 需要通过 ComfyUI HTTP API 下载视频

---

## 解决方案

### ✅ 最新更新（提交 b7dec61）

已添加两种视频获取方式：

1. **文件系统复制**: 当 ComfyUI 输出目录可访问时
2. **API 下载**: 当 ComfyUI 在远程服务器时（自动选择）

---

## 配置指南

### 场景 1: ComfyUI 在外部 GPU 服务器（最常见）

#### 步骤 1: 配置 ComfyUI 地址

在 Web 界面侧边栏：

```
ComfyUI地址: https://your-gpu-server.com
            或 https://xxx-8188.cnb.run/  (CNB GPU节点)

ComfyUI输出目录: (留空)
```

#### 步骤 2: 测试连接

点击"🔌 测试连接"按钮，确认：
- ✅ ComfyUI 连接成功
- 显示 ComfyUI 版本信息

#### 工作原理

```
1. 提交任务 → ComfyUI API
2. 等待生成完成
3. 通过 /view API 下载视频
4. 保存到创空间的 /app/output/
```

### 场景 2: ComfyUI 和创空间在同一环境

#### 配置

```
ComfyUI地址: http://127.0.0.1:8188

ComfyUI输出目录: /workspace/output
```

#### 工作原理

```
1. 提交任务 → ComfyUI API
2. 等待生成完成
3. 文件系统复制 → /app/output/
```

### 场景 3: ComfyUI 在本地，创空间在云端

#### 配置

```
ComfyUI地址: http://your-public-ip:8188
            (需要端口转发或公网IP)

ComfyUI输出目录: (留空)
```

---

## 部署步骤

### 1. 准备 ComfyUI 服务器

确保 ComfyUI：
- ✅ 已安装 MiniMax H3 模型
- ✅ 正在运行并监听正确端口
- ✅ 网络可从创空间访问

测试命令：
```bash
curl https://your-comfyui-server.com/system_stats
```

### 2. 部署魔搭创空间

#### 方式 1: 通过 Git

```bash
# 克隆仓库
git clone https://www.modelscope.cn/studios/wangbaozhen/video-story-generator.git
cd video-story-generator

# 创空间会自动安装 requirements.txt 中的依赖
```

#### 方式 2: 手动上传

1. 在创空间文件页上传所有文件
2. 确保包含：
   - `app.py` (启动文件)
   - `requirements.txt` (依赖)
   - `scripts/` (核心脚本)

### 3. 配置创空间

在创空间设置中：
- 启动文件: `app.py`
- 环境变量: (如需要)

### 4. 启动并测试

1. 打开创空间 Web 界面
2. 在侧边栏配置 ComfyUI 地址
3. 点击"测试连接"
4. 创建测试脚本并生成

---

## 故障排查

### 使用诊断工具

访问诊断页面：

```
方式 1: 修改启动文件
在创空间设置中，将 entry_file 改为 diagnose_comfyui.py

方式 2: 直接访问
在浏览器中打开: https://your-space.modelscope.cn/diagnose_comfyui.py
```

#### 诊断项目

1. **ComfyUI 连接测试**
   - 检查地址是否正确
   - 检查网络是否连通
   - 检查 API 是否可访问

2. **输出目录检查**
   - 检查文件系统是否可访问
   - 确认是否需要使用 API 下载

3. **生成测试任务**
   - 提交简单测试任务
   - 验证 ComfyUI 工作流

### 常见错误

#### ❌ "无法连接到 ComfyUI"

**原因**:
- ComfyUI 未启动
- 地址错误
- 网络不通

**解决**:
```bash
# 在 ComfyUI 服务器上检查
curl http://localhost:8188/system_stats

# 检查防火墙
sudo ufw status
sudo ufw allow 8188
```

#### ❌ "视频文件未找到"

**原因**:
- ComfyUI 输出目录配置错误
- 文件系统不可访问

**解决**:
- 将"ComfyUI输出目录"留空
- 系统会自动通过 API 下载

#### ❌ "下载视频失败"

**原因**:
- ComfyUI 的 `/view` API 不可访问
- 权限问题

**解决**:
```bash
# 检查 ComfyUI 配置
# ComfyUI 需要允许 /view 端点

# 测试下载
curl "http://your-comfyui-server.com/view?filename=test.mp4&type=output"
```

---

## 性能优化

### 网络优化

1. **使用内网地址**: 如果 ComfyUI 和创空间在同一区域
2. **启用 CDN**: 加速视频下载
3. **压缩传输**: 减少带宽使用

### 存储优化

1. **定期清理**: 删除旧的输出文件
2. **对象存储**: 将视频上传到 OSS/S3
3. **增量下载**: 仅下载需要的视频

---

## 示例配置

### CNB GPU 节点 + 魔搭创空间

```yaml
# ComfyUI (CNB GPU节点)
地址: https://xxx-8188.cnb.run/
输出目录: /workspace/output (创空间无法访问)

# 魔搭创空间
ComfyUI地址: https://xxx-8188.cnb.run/
ComfyUI输出目录: (留空，使用API下载)

# 工作流程
1. 创空间提交任务 → CNB ComfyUI
2. ComfyUI 生成视频
3. 创空间通过 API 下载视频
4. 用户在创空间预览和下载
```

---

## 技术细节

### 视频获取流程

```python
# 1. 尝试文件系统访问
if comfyui_output_dir and Path(comfyui_output_dir).exists():
    # 文件系统复制
    shutil.copy(video_path, project_output)
else:
    # API 下载
    response = requests.get(
        f"{comfyui_url}/view",
        params={
            'filename': video_filename,
            'type': 'output',
            'subfolder': 'video'
        }
    )
    # 保存到项目输出
    with open(project_output / video_filename, 'wb') as f:
        f.write(response.content)
```

### ComfyUI API 端点

| 端点 | 用途 |
|------|------|
| `/system_stats` | 系统状态检查 |
| `/prompt` | 提交工作流 |
| `/queue` | 查看队列 |
| `/history/{prompt_id}` | 查看任务历史 |
| `/view` | 下载生成的文件 |

---

## 联系支持

如果问题仍然存在：

1. 运行诊断工具 `diagnose_comfyui.py`
2. 提供诊断结果
3. 说明部署架构（ComfyUI 位置、网络配置）
4. 提供错误日志

GitHub Issues: https://github.com/wangfeiwest2025/video-story-generator/issues