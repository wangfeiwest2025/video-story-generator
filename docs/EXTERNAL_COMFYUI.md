# 🔌 配置外部ComfyUI服务器

AI短视频生成器支持连接外部ComfyUI服务器，无需在本地部署。

---

## 📋 前提条件

### 外部ComfyUI要求

1. **ComfyUI版本**: 0.34.0+
2. **必需模型**:
   - `minimax_h3_fl2va_int8_convrot.safetensors`
   - `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
   - `minimax_h3_video_vae_fp16.safetensors`
   - `minimax_h3_audio_vae_fp32.safetensors`

3. **网络访问**:
   - 服务器需要公网访问或VPN连接
   - 端口8188需要开放

4. **配置要求**:
   - GPU: NVIDIA RTX 3090+ (24GB+ VRAM)
   - 内存: 32GB+

---

## 🚀 使用方式

### 方式1: Web界面

1. 启动Web界面：
```bash
cd web/
bash start.sh
```

2. 在侧边栏配置：
   - 选择"远程URL"模式
   - 输入ComfyUI地址，例如：`https://yvkxlmr70c-8188.cnb.run/`
   - 点击"测试连接"验证

3. 开始生成：
   - 创建脚本
   - 调整参数
   - 点击"开始生成"

### 方式2: 命令行

```bash
# 使用外部ComfyUI
python scripts/auto_generate.py your_script.json \
    --comfyui-url https://yvkxlmr70c-8188.cnb.run/

# 完整参数示例
python scripts/auto_generate.py your_script.json \
    --comfyui-url https://your-server.com \
    --output my_output/ \
    --width 1344 \
    --height 768 \
    --steps 20 \
    --voice zh-CN-XiaoxiaoNeural \
    --narration-volume 1.2 \
    --ambient-volume 0.5
```

---

## 🔧 配置说明

### ComfyUI URL格式

| 类型 | URL格式 | 示例 |
|------|---------|------|
| 本地 | `http://127.0.0.1:8188` | 默认 |
| HTTP | `http://server-ip:8188` | `http://192.168.1.100:8188` |
| HTTPS | `https://server.com` | `https://your-server.com` |
| CNB | `https://xxx-8188.cnb.run/` | `https://yvkxlmr70c-8188.cnb.run/` |

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--comfyui-url` | `http://127.0.0.1:8188` | ComfyUI服务器地址 |
| `--width` | `1344` | 视频宽度 |
| `--height` | `768` | 视频高度 |
| `--steps` | `20` | 采样步数 |
| `--voice` | `zh-CN-XiaoxiaoNeural` | TTS语音 |
| `--narration-volume` | `1.2` | 解说词音量 |
| `--ambient-volume` | `0.5` | 环境音音量 |

---

## 🌐 常见外部服务

### CNB (CodeNB) 平台

**特点**:
- 一键部署ComfyUI
- 自动分配GPU
- 提供公网URL

**使用步骤**:
1. 在CNB创建ComfyUI项目
2. 安装必需模型
3. 获取访问URL（如：`https://xxx-8188.cnb.run/`）
4. 在生成器中配置URL

**示例**:
```bash
python scripts/auto_generate.py my_script.json \
    --comfyui-url https://yvkxlmr70c-8188.cnb.run/
```

### RunPod平台

**特点**:
- 按需GPU
- 灵活配置
- SSH访问

**使用步骤**:
1. 部署RunPod GPU Pod
2. 安装ComfyUI和模型
3. 配置端口转发
4. 使用公网URL或SSH隧道

### 自建服务器

**要求**:
- 公网IP或域名
- 开放8188端口
- 安装ComfyUI和模型

**配置**:
```bash
# 服务器端启动ComfyUI
python main.py --listen 0.0.0.0 --port 8188

# 客户端使用
python scripts/auto_generate.py my_script.json \
    --comfyui-url http://your-server-ip:8188
```

---

## 🔒 安全注意事项

### 1. 网络安全
- ✅ 使用HTTPS加密连接
- ✅ 设置访问密钥或认证
- ✅ 限制访问IP范围
- ❌ 避免在公共网络暴露未保护的ComfyUI

### 2. 数据安全
- ✅ 视频数据通过HTTPS传输
- ✅ 脚本内容不包含敏感信息
- ✅ 定期清理服务器数据

### 3. 访问控制
```python
# ComfyUI服务器端配置
# 设置访问密钥
API_KEY = "your-secret-key"

# 在生成器中添加
headers = {"Authorization": f"Bearer {API_KEY}"}
```

---

## 🧪 测试连接

### 方法1: Web界面测试

1. 在Web界面侧边栏
2. 输入ComfyUI URL
3. 点击"测试连接"
4. 查看连接状态

### 方法2: 命令行测试

```bash
# 测试连接
curl https://your-server.com/system_stats

# 预期返回
{
  "system": {
    "os": "Linux",
    "python": "3.10.0",
    ...
  }
}
```

### 方法3: Python测试

```python
import requests

url = "https://your-server.com"
response = requests.get(f"{url}/system_stats", timeout=10)

if response.status_code == 200:
    print("✅ 连接成功")
    print(response.json())
else:
    print("❌ 连接失败")
```

---

## ⚠️ 故障排除

### 问题1: 连接超时

**原因**: 网络问题或服务器未启动

**解决**:
1. 检查网络连接
2. 确认服务器正在运行
3. 检查防火墙设置
4. 增加超时时间

```python
# 增加超时时间
requests.get(url, timeout=30)
```

### 问题2: 403 Forbidden

**原因**: 访问权限问题

**解决**:
1. 检查访问密钥
2. 确认IP白名单
3. 联系服务器管理员

### 问题3: 模型未找到

**原因**: 服务器缺少必需模型

**解决**:
```bash
# 在ComfyUI服务器上
cd ComfyUI/models/checkpoints/
# 下载MiniMax H3模型
```

### 问题4: GPU内存不足

**原因**: 服务器GPU资源不足

**解决**:
1. 降低分辨率（`--width 960 --height 544`）
2. 减少采样步数（`--steps 15`）
3. 联系服务器管理员增加资源

---

## 📊 性能对比

| 部署方式 | 优点 | 缺点 | 推荐场景 |
|---------|------|------|---------|
| **本地** | 低延迟、完全控制 | 需要本地GPU | 开发测试 |
| **CNB** | 一键部署、公网访问 | 按时计费 | 快速测试 |
| **RunPod** | 灵活配置、高性能 | 需要配置 | 生产环境 |
| **自建** | 完全控制、无限制 | 运维成本高 | 企业应用 |

---

## 💡 最佳实践

### 1. 开发阶段
- 使用本地ComfyUI
- 快速迭代测试
- 低分辨率验证

### 2. 生产阶段
- 使用高性能外部服务器
- 高分辨率输出
- 批量处理任务

### 3. 成本优化
- 选择合适的GPU规格
- 使用按需计费
- 批量处理减少空闲

---

## 📝 配置示例

### 完整配置文件

```json
{
  "title": "我的视频",
  "style": "电影级",
  "scenes": [...],
  "comfyui": {
    "url": "https://yvkxlmr70c-8188.cnb.run/",
    "timeout": 30,
    "api_key": "your-key"
  },
  "video": {
    "width": 1344,
    "height": 768,
    "steps": 20,
    "fps": 24
  },
  "audio": {
    "voice": "zh-CN-XiaoxiaoNeural",
    "narration_volume": 1.2,
    "ambient_volume": 0.5
  }
}
```

---

## 🔗 相关链接

- **ComfyUI文档**: https://github.com/comfyanonymous/ComfyUI
- **CNB平台**: https://cnb.cool/
- **RunPod**: https://www.runpod.io/
- **项目GitHub**: https://github.com/wangfeiwest2025/video-story-generator

---

**🔌 使用外部ComfyUI，随时随地生成AI视频！**