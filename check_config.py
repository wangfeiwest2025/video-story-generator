#!/usr/bin/env python3
"""
创空间配置检查脚本
检查常见的配置错误
"""

import streamlit as st
import re

st.set_page_config(page_title="配置检查", page_icon="🔧", layout="wide")

st.title("🔧 创空间配置检查")

st.warning("⚠️ 请仔细检查以下配置，特别是端口号！")

# 获取用户配置
comfyui_url = st.text_input(
    "您在创空间中填写的 ComfyUI 地址",
    value="",
    placeholder="请填写您在侧边栏中配置的地址",
    help="填写您实际在创空间中使用的地址"
)

if st.button("🔍 检查配置", type="primary"):
    if not comfyui_url:
        st.error("❌ 请输入地址")
    else:
        st.markdown("---")

        # 1. 检查地址格式
        st.markdown("### 1️⃣ 地址格式检查")

        # 检查协议
        if not comfyui_url.startswith(('http://', 'https://')):
            st.error("❌ 地址缺少协议（http:// 或 https://）")
        else:
            st.success(f"✅ 协议正确: {comfyui_url.split('://')[0]}://")

        # 检查端口
        port_match = re.search(r':(\d+)', comfyui_url)
        if port_match:
            port = int(port_match.group(1))
            st.write(f"**检测到端口**: `{port}`")

            if port == 8501:
                st.error("""
                ❌ **端口错误！8501 是 Streamlit 端口**

                这是导致无法调用 ComfyUI 的原因！

                **正确配置**:
                - ComfyUI 端口: **8188**
                - 正确地址: `https://xxx-8188.cnb.run/`
                """)
            elif port == 8188:
                st.success("✅ 端口正确: 8188 (ComfyUI 默认端口)")
            else:
                st.warning(f"⚠️ 非标准端口: {port}")
        else:
            st.info("ℹ️ 未检测到明确端口（可能使用默认端口）")

        # 2. 测试连接
        st.markdown("### 2️⃣ 连接测试")

        import requests

        try:
            with st.spinner(f"正在连接 {comfyui_url}..."):
                response = requests.get(f"{comfyui_url}/system_stats", timeout=10)

                if response.status_code == 200:
                    st.success("✅ ComfyUI 连接成功")

                    data = response.json()
                    st.info(f"ComfyUI 版本: {data.get('system', {}).get('comfyui_version')}")

                    # 显示完整 URL
                    st.code(f"您配置的地址: {comfyui_url}", language="bash")

                    # 如果端口错误，显示正确地址
                    if port == 8501:
                        # 生成正确地址
                        correct_url = comfyui_url.replace(':8501', ':8188')
                        st.error(f"""
                        **请将地址修改为**: `{correct_url}`
                        """)
                else:
                    st.error(f"❌ 连接失败: HTTP {response.status_code}")

                    if port == 8501:
                        st.error("""
                        **问题**: 端口 8501 是 Streamlit Web 界面的端口
                        **解决**: 修改为端口 8188
                        """)

        except requests.exceptions.Timeout:
            st.error("❌ 连接超时")
            if port == 8501:
                st.error("端口 8501 不是 ComfyUI 端口，无法响应")
        except requests.exceptions.ConnectionError as e:
            st.error(f"❌ 连接失败: {e}")
            if port == 8501:
                st.error("端口 8501 是错误的端口")
        except Exception as e:
            st.error(f"❌ 错误: {e}")

        # 3. 正确配置示例
        st.markdown("### 3️⃣ 正确配置示例")

        st.markdown("""
        #### 魔搭创空间配置

        在侧边栏中填写：

        ```
        ComfyUI地址: https://xxx-8188.cnb.run/
        ComfyUI输出目录: (留空)
        ```

        ⚠️ **重要提示**:
        - 端口必须是 **8188**（ComfyUI 端口）
        - 不是 8501（8501 是 Streamlit 端口）
        - 输出目录必须留空（使用 API 下载）

        #### 常见错误

        | 错误 | 说明 | 后果 |
        |------|------|------|
        | `https://xxx-8501.cnb.run/` | ❌ 端口 8501 | 无法调用 ComfyUI |
        | `https://xxx-8188.cnb.run/` | ✅ 端口 8188 | 可以正常工作 |
        | `/workspace/output` | ❌ 填写路径 | 找不到文件 |
        | (留空) | ✅ 留空 | 使用 API 下载 |
        """)

# 显示诊断步骤
st.markdown("---")
st.markdown("## 📋 诊断步骤")

st.markdown("""
### 步骤 1: 检查当前配置

在创空间侧边栏中，查看您填写的 ComfyUI 地址：
- [ ] 是否以 `https://` 开头？
- [ ] 端口是否是 **8188**？
- [ ] 如果端口是 8501，这是错误的！

### 步骤 2: 修正配置

如果发现错误，请修改：
- **ComfyUI地址**: `https://xxx-8188.cnb.run/`
- **ComfyUI输出目录**: 留空

### 步骤 3: 测试连接

点击侧边栏的"🔌 测试连接"按钮：
- ✅ 应该显示"ComfyUI连接成功"
- ❌ 如果失败，检查地址是否正确

### 步骤 4: 重新生成

修改配置后，点击"开始生成"，查看进度监控

---

## 🎯 快速检查清单

- [ ] ComfyUI 地址端口是 8188（不是 8501）
- [ ] ComfyUI 输出目录留空
- [ ] 测试连接显示成功
- [ ] 进度监控显示"已提交 X 个任务"
""")

# 显示端口对比
st.markdown("---")
st.markdown("## 🔌 端口对比说明")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ❌ 错误配置 (端口 8501)

    ```
    ComfyUI地址: https://xxx-8501.cnb.run/
    ```

    **问题**:
    - 8501 是 Streamlit Web 界面的端口
    - 这是用户访问的地址
    - 不是 ComfyUI API 地址
    - 无法提交任务

    **结果**:
    - 无法调用 ComfyUI
    - 只能生成音频
    - 视频生成失败
    """)

with col2:
    st.markdown("""
    ### ✅ 正确配置 (端口 8188)

    ```
    ComfyUI地址: https://xxx-8188.cnb.run/
    ```

    **说明**:
    - 8188 是 ComfyUI API 的端口
    - 这是 ComfyUI 服务的地址
    - 可以提交任务
    - 可以下载视频

    **结果**:
    - ✅ 可以调用 ComfyUI
    - ✅ 可以生成视频
    - ✅ 流程完整
    """)

st.markdown("---")
st.info("💡 **提示**: 如果您发现配置错误，请立即修改并重新测试！")