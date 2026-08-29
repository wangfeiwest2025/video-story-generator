#!/usr/bin/env python3
"""
完整诊断脚本 - 检查所有可能的问题
"""

import streamlit as st
import requests
from pathlib import Path
import json
import sys
import os

st.set_page_config(page_title="完整诊断", page_icon="🔍", layout="wide")

st.title("🔍 视频生成完整诊断")

# 1. 环境检查
st.markdown("## 1️⃣ 环境检查")

st.write("### Python 环境")
st.write(f"- Python 版本: {sys.version}")
st.write(f"- 工作目录: {Path.cwd()}")
st.write(f"- 项目目录: {Path(__file__).parent}")

st.write("### 依赖包检查")
required_packages = ['streamlit', 'requests', 'edge_tts', 'mutagen']
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
        st.write(f"✅ {package}")
    except ImportError:
        st.write(f"❌ {package} - 未安装")
        missing_packages.append(package)

if missing_packages:
    st.error(f"缺少依赖包: {', '.join(missing_packages)}")
    st.code(f"pip install {' '.join(missing_packages)}")

# 2. 文件系统检查
st.markdown("## 2️⃣ 文件系统检查")

project_root = Path(__file__).parent
output_dir = project_root / "output"

st.write(f"**项目输出目录**: `{output_dir}`")
st.write(f"- 是否存在: {'✅' if output_dir.exists() else '❌'}")

if output_dir.exists():
    st.write(f"- 可写入: {'✅' if os.access(output_dir, os.W_OK) else '❌'}")

# 尝试创建测试文件
test_file = project_root / "test_write.tmp"
try:
    test_file.write_text("test")
    test_file.unlink()
    st.write(f"- 写入测试: ✅ 成功")
except Exception as e:
    st.write(f"- 写入测试: ❌ {e}")

# 3. ComfyUI 配置
st.markdown("## 2️⃣ ComfyUI 连接检查")

col1, col2 = st.columns(2)

with col1:
    comfyui_url = st.text_input(
        "ComfyUI 地址",
        value="http://127.0.0.1:8188",
        key="diag_url"
    )

with col2:
    comfyui_output = st.text_input(
        "ComfyUI 输出目录",
        value="",
        key="diag_output"
    )

if st.button("🔍 完整诊断", type="primary"):
    st.markdown("---")

    # 步骤 1: 测试基本连接
    st.markdown("### 📡 步骤 1: 测试网络连接")

    try:
        st.write(f"正在连接: `{comfyui_url}/system_stats`")
        response = requests.get(f"{comfyui_url}/system_stats", timeout=10)

        if response.status_code == 200:
            st.success("✅ ComfyUI 连接成功")

            data = response.json()
            st.write(f"- ComfyUI 版本: {data.get('system', {}).get('comfyui_version')}")
            st.write(f"- Python 版本: {data.get('system', {}).get('python_version')}")
        else:
            st.error(f"❌ HTTP {response.status_code}")
            st.write("可能的原因:")
            st.write("1. ComfyUI 未启动")
            st.write("2. 地址错误")
            st.write("3. 端口被占用")

    except requests.exceptions.Timeout:
        st.error("❌ 连接超时")
        st.write("**诊断**: ComfyUI 可能未启动或地址错误")
        st.write("**解决方案**: 检查 ComfyUI 是否运行，确认地址正确")

    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ 连接失败: {e}")
        st.write("**诊断**: 网络不通")
        st.write("**解决方案**: 检查网络连接，确认 ComfyUI 正在运行")

    except Exception as e:
        st.error(f"❌ 错误: {e}")

    # 步骤 2: 测试 API 端点
    st.markdown("### 🔌 步骤 2: 测试 API 端点")

    endpoints = [
        ('/queue', '队列'),
        ('/history', '历史记录'),
        ('/object_info', '节点信息')
    ]

    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{comfyui_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                st.write(f"✅ {name} ({endpoint})")
            else:
                st.write(f"❌ {name} ({endpoint}): HTTP {response.status_code}")
        except Exception as e:
            st.write(f"❌ {name} ({endpoint}): {e}")

    # 步骤 3: 检查模型
    st.markdown("### 🎨 步骤 3: 检查 MiniMax H3 模型")

    try:
        response = requests.get(f"{comfyui_url}/object_info", timeout=10)
        if response.status_code == 200:
            data = response.json()

            required = {
                'UNETLoader': 'minimax_h3_fl2va_int8_convrot.safetensors',
                'CLIPLoader': 'qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors',
                'VAELoader': [
                    'minimax_h3_video_vae_fp16.safetensors',
                    'minimax_h3_audio_vae_fp32.safetensors'
                ]
            }

            all_ok = True
            for node_type, model_names in required.items():
                if node_type in data:
                    key = 'unet_name' if node_type == 'UNETLoader' else 'clip_name' if node_type == 'CLIPLoader' else 'vae_name'
                    available = data[node_type]['input']['required'][key][0]

                    if isinstance(model_names, list):
                        for m in model_names:
                            status = '✅' if m in available else '❌'
                            st.write(f"{status} {m}")
                            if m not in available:
                                all_ok = False
                    else:
                        status = '✅' if model_names in available else '❌'
                        st.write(f"{status} {model_names}")
                        if model_names not in available:
                            all_ok = False
                else:
                    st.write(f"❌ {node_type} 节点不存在")
                    all_ok = False

            if all_ok:
                st.success("✅ 所有模型检查通过")
            else:
                st.error("❌ 部分模型缺失")
        else:
            st.error(f"❌ 无法获取模型信息: HTTP {response.status_code}")

    except Exception as e:
        st.error(f"❌ 模型检查失败: {e}")

    # 步骤 4: 测试提交任务
    st.markdown("### 🚀 步骤 4: 测试提交任务")

    simple_test = {
        "1": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            }
        }
    }

    try:
        response = requests.post(
            f"{comfyui_url}/prompt",
            json={"prompt": simple_test},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get('prompt_id')
            st.success(f"✅ 测试任务提交成功")
            st.write(f"任务 ID: `{prompt_id}`")

            # 检查任务状态
            st.write("检查任务状态...")
            try:
                hist_response = requests.get(f"{comfyui_url}/history/{prompt_id}", timeout=5)
                if hist_response.status_code == 200:
                    st.write("✅ 可以查询任务状态")
                else:
                    st.write(f"⚠️ 无法查询任务状态: HTTP {hist_response.status_code}")
            except:
                st.write("⚠️ 查询任务状态失败")

        else:
            st.error(f"❌ 任务提交失败: HTTP {response.status_code}")
            st.write("响应内容:")
            st.code(response.text[:500])

    except Exception as e:
        st.error(f"❌ 提交失败: {e}")

    # 步骤 5: 检查输出目录
    st.markdown("### 📁 步骤 5: 检查输出目录")

    if comfyui_output:
        output_path = Path(comfyui_output)
        st.write(f"**ComfyUI 输出目录**: `{output_path}`")
        st.write(f"- 是否存在: {'✅' if output_path.exists() else '❌'}")

        if output_path.exists():
            videos = list(output_path.rglob("*.mp4"))
            st.write(f"- 视频文件数: {len(videos)}")
    else:
        st.info("ℹ️ ComfyUI 输出目录未配置（将使用 API 下载）")

# 4. 配置建议
st.markdown("## 💡 配置建议")

st.markdown("""
### 正确配置示例

#### 方式 1: ComfyUI 在外部服务器（推荐）

```
ComfyUI 地址: https://your-gpu-server.com
ComfyUI 输出目录: (留空)
```

**工作原理**:
- 通过 API 下载视频
- 无需文件系统访问

#### 方式 2: ComfyUI 在同一环境

```
ComfyUI 地址: http://127.0.0.1:8188
ComfyUI 输出目录: /workspace/output
```

**工作原理**:
- 文件系统复制
- 速度更快

---

### 常见问题

#### ❌ "无法连接 ComfyUI"

**检查清单**:
- [ ] ComfyUI 是否正在运行？
- [ ] 地址是否正确？
- [ ] 端口是否正确？
- [ ] 网络是否连通？

**测试命令**:
```bash
curl http://your-comfyui-server:8188/system_stats
```

#### ❌ "提交任务失败"

**可能原因**:
- ComfyUI 版本不兼容
- 内存不足
- 工作流格式错误

**解决方案**:
- 查看 ComfyUI 控制台日志
- 检查 ComfyUI 版本 (需要 0.34.0+)

#### ❌ "模型缺失"

**解决方案**:
- 下载 MiniMax H3 模型
- 放到 ComfyUI models 目录
""")

st.markdown("---")
st.markdown("""
**使用说明**:
1. 填写 ComfyUI 地址
2. 点击"完整诊断"
3. 查看每个步骤的结果
4. 根据提示修复问题
""")