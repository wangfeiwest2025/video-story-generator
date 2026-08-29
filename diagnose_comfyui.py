#!/usr/bin/env python3
"""
魔搭环境诊断 - 检查 ComfyUI 配置和连接
"""

import streamlit as st
import requests
from pathlib import Path
import json

st.set_page_config(page_title="环境诊断", page_icon="🔍", layout="wide")

st.title("🔍 魔搭环境诊断")

# 1. 基本环境信息
st.markdown("## 📋 环境信息")
st.write(f"**当前工作目录**: `{Path.cwd()}`")
st.write(f"**项目目录**: `{Path(__file__).parent}`")

# 检查项目输出目录
project_output = Path(__file__).parent / "output"
st.write(f"**项目输出目录**: `{project_output}`")
st.write(f"- 是否存在: {'✅' if project_output.exists() else '❌'}")
if project_output.exists():
    st.write(f"- 文件数: {len(list(project_output.rglob('*')))}")

# 2. ComfyUI 连接测试
st.markdown("## 🔌 ComfyUI 连接测试")

comfyui_url = st.text_input(
    "ComfyUI 地址",
    value="http://127.0.0.1:8188",
    help="请输入 ComfyUI 的完整地址，包括协议（http/https）和端口"
)

if st.button("测试连接"):
    st.markdown("### 测试结果")

    # 测试基本连接
    try:
        st.write(f"正在连接: `{comfyui_url}/system_stats`")
        response = requests.get(f"{comfyui_url}/system_stats", timeout=10)
        if response.status_code == 200:
            st.success(f"✅ ComfyUI 连接成功！")
            st.json(response.json())

            # 测试队列
            st.write("\n测试队列访问...")
            queue_response = requests.get(f"{comfyui_url}/queue", timeout=5)
            if queue_response.status_code == 200:
                st.success("✅ 队列访问正常")
            else:
                st.warning(f"⚠️ 队列访问异常: HTTP {queue_response.status_code}")

            # 测试历史记录
            st.write("\n测试历史记录访问...")
            hist_response = requests.get(f"{comfyui_url}/history", timeout=5)
            if hist_response.status_code == 200:
                st.success("✅ 历史记录访问正常")
            else:
                st.warning(f"⚠️ 历史记录访问异常: HTTP {hist_response.status_code}")

        else:
            st.error(f"❌ 连接失败: HTTP {response.status_code}")
            st.write("可能的原因:")
            st.write("1. ComfyUI 未启动")
            st.write("2. 地址或端口错误")
            st.write("3. 网络不通")
    except requests.exceptions.Timeout:
        st.error("❌ 连接超时")
        st.write("可能的原因:")
        st.write("1. ComfyUI 地址错误")
        st.write("2. 网络不通")
        st.write("3. 防火墙阻止")
    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ 连接错误: {e}")
        st.write("\n常见解决方案:")
        st.write("1. **ComfyUI 在本地**: 确认 ComfyUI 已启动")
        st.write("2. **ComfyUI 在外部服务器**: 使用外部 IP 或域名")
        st.write("3. **ComfyUI 在 CNB**: 使用 CNB 提供的 URL (如 `https://xxx-8188.cnb.run/`)")
    except Exception as e:
        st.error(f"❌ 未知错误: {e}")

# 3. ComfyUI 输出目录测试
st.markdown("## 📁 ComfyUI 输出目录测试")

comfyui_output = st.text_input(
    "ComfyUI 输出目录",
    value="/workspace/output",
    help="ComfyUI 保存视频的路径"
)

if st.button("检查目录"):
    output_path = Path(comfyui_output)

    st.write(f"**路径**: `{output_path}`")
    st.write(f"**是否存在**: {'✅' if output_path.exists() else '❌'}")

    if output_path.exists():
        # 列出文件
        files = list(output_path.glob("*.mp4"))
        st.write(f"**MP4 文件数**: {len(files)}")

        if files:
            st.write("**最新的视频文件**:")
            for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                st.write(f"- {f.name} ({f.stat().st_size / 1024 / 1024:.2f} MB)")

        # 检查 video 子目录
        video_dir = output_path / "video"
        if video_dir.exists():
            st.write(f"\n**video 子目录存在**: ✅")
            video_files = list(video_dir.glob("*.mp4"))
            st.write(f"**video 子目录中的 MP4 文件数**: {len(video_files)}")
        else:
            st.write(f"\n**video 子目录**: ❌ 不存在")
    else:
        st.error("❌ 目录不存在")
        st.write("\n可能的原因:")
        st.write("1. 路径错误")
        st.write("2. ComfyUI 输出目录不在此路径")
        st.write("3. 如果 ComfyUI 在远程服务器，创空间无法直接访问文件系统")

        st.write("\n**重要提示**:")
        st.warning("⚠️ 如果 ComfyUI 部署在远程服务器，创空间无法直接访问文件系统！")
        st.write("需要通过 ComfyUI API 下载视频，或配置共享存储。")

# 4. 配置建议
st.markdown("## 💡 配置建议")

st.markdown("""
### 魔搭创空间 + ComfyUI 的常见部署方式

#### 方式 1: ComfyUI 在外部 GPU 服务器（推荐）
- **ComfyUI 地址**: `https://your-gpu-server.com` 或 `https://xxx-8188.cnb.run/`
- **ComfyUI 输出目录**: 创空间无法直接访问，需要通过 API 下载

#### 方式 2: ComfyUI 和创空间在同一环境
- **ComfyUI 地址**: `http://127.0.0.1:8188`
- **ComfyUI 输出目录**: `/workspace/output` 或其他共享路径

#### 方式 3: ComfyUI 在本地，创空间在云端
- **ComfyUI 地址**: `http://your-local-ip:8188`（需要端口转发）
- **ComfyUI 输出目录**: 创空间无法访问，需要通过 API 下载

### ⚠️ 当前问题

如果诊断结果显示：
- ✅ ComfyUI 连接成功
- ❌ ComfyUI 输出目录不存在

这说明 **ComfyUI 在远程服务器**，创空间无法直接访问文件系统。

**解决方案**：需要修改代码，通过 ComfyUI API 下载视频，而不是文件复制。
""")

# 5. 生成测试任务
st.markdown("## 🧪 生成测试任务")

if st.button("生成测试任务"):
    test_workflow = {
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
            json={"prompt": test_workflow},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ 测试任务已提交: {result.get('prompt_id')}")
            st.write("请在 ComfyUI 界面查看任务状态")
        else:
            st.error(f"❌ 提交失败: HTTP {response.status_code}")
            st.write(response.text)
    except Exception as e:
        st.error(f"❌ 提交失败: {e}")

st.markdown("---")
st.markdown("""
**使用说明**:
1. 运行此诊断工具检查 ComfyUI 连接
2. 如果连接成功但无法访问输出目录，说明 ComfyUI 在远程服务器
3. 根据诊断结果调整 app.py 中的配置
""")