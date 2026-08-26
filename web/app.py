"""
AI短视频自动化制作智能体 - Streamlit Web界面
"""

import streamlit as st
import json
import os
import sys
import asyncio
import time
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.auto_generate import VideoStoryGenerator

# 页面配置
st.set_page_config(
    page_title="AI短视频生成器",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #4CAF50;
        color: white;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        padding: 1rem;
        background-color: #2196F3;
        color: white;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        padding: 1rem;
        background-color: #FF9800;
        color: white;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .progress-box {
        padding: 1rem;
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'generator' not in st.session_state:
    st.session_state.generator = None
if 'script' not in st.session_state:
    st.session_state.script = None
if 'status' not in st.session_state:
    st.session_state.status = 'idle'
if 'progress' not in st.session_state:
    st.session_state.progress = {}
if 'output_dir' not in st.session_state:
    st.session_state.output_dir = None

# 侧边栏
with st.sidebar:
    st.image("https://img.shields.io/badge/version-1.0.0-blue", width=100)
    st.markdown("### 🎬 AI短视频生成器")
    st.markdown("---")

    # TTS语音选择
    voice = st.selectbox(
        "解说员声音",
        [
            "zh-CN-XiaoxiaoNeural (女声-温柔)",
            "zh-CN-YunxiNeural (男声-年轻)",
            "zh-CN-YunjianNeural (男声-成熟)"
        ],
        index=0
    )
    voice_id = voice.split()[0]

    # 视频参数
    st.markdown("### 🎥 视频参数")
    resolution = st.select_slider(
        "分辨率",
        options=["960x544", "1344x768", "1920x1080"],
        value="1344x768"
    )
    width, height = map(int, resolution.split('x'))

    steps = st.slider(
        "采样步数（质量⬆️ 速度⬇️）",
        min_value=15,
        max_value=30,
        value=20,
        step=1
    )

    # 音频参数
    st.markdown("### 🎵 音频参数")
    narration_volume = st.slider(
        "解说词音量",
        min_value=80,
        max_value=150,
        value=120
    ) / 100.0

    ambient_volume = st.slider(
        "环境音音量",
        min_value=20,
        max_value=80,
        value=50
    ) / 100.0

    st.markdown("---")
    st.markdown("""
    ### 📚 使用说明
    1. 创建或上传脚本
    2. 点击"开始生成"
    3. 等待自动完成
    4. 预览和下载视频
    """)

# 主界面
st.markdown('<h1 class="main-header">🎬 AI短视频自动化制作</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">从脚本到成片，一键完成</p>', unsafe_allow_html=True)

# 标签页
tab1, tab2, tab3, tab4 = st.tabs(["📝 脚本编辑", "🚀 生成控制", "📊 进度监控", "🎥 结果预览"])

# 脚本编辑标签
with tab1:
    st.markdown('<h2 class="sub-header">📝 脚本编辑</h2>', unsafe_allow_html=True)

    # 选择输入方式
    input_method = st.radio(
        "选择输入方式",
        ["在线编辑", "上传JSON文件", "使用示例模板"],
        horizontal=True
    )

    if input_method == "在线编辑":
        # 项目信息
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("视频标题", value="我的AI短视频")
        with col2:
            style = st.text_input("视频风格", value="电影级")

        # 场景数量
        num_scenes = st.number_input("场景数量", min_value=1, max_value=20, value=2)

        # 场景编辑
        scenes = []
        for i in range(num_scenes):
            with st.expander(f"场景 {i+1}", expanded=(i == 0)):
                col1, col2, col3 = st.columns(3)
                with col1:
                    narration = st.text_area(
                        "解说词",
                        value=f"这是场景{i+1}的解说词",
                        height=100,
                        key=f"narration_{i}"
                    )
                with col2:
                    visual_prompt = st.text_area(
                        "视觉描述（英文）",
                        value=f"Scene {i+1} visual description, cinematic lighting",
                        height=100,
                        key=f"visual_{i}"
                    )
                with col3:
                    audio = st.text_area(
                        "音频描述",
                        value=f"ambient sounds, background music",
                        height=100,
                        key=f"audio_{i}"
                    )

                scenes.append({
                    "id": i + 1,
                    "narration": narration,
                    "visual_prompt": visual_prompt,
                    "audio": audio
                })

        # 生成脚本
        if st.button("📝 生成脚本", type="primary"):
            script = {
                "title": title,
                "style": style,
                "scenes": scenes
            }
            st.session_state.script = script
            st.success("✅ 脚本已生成！")

            # 显示脚本
            st.json(script)

            # 下载按钮
            st.download_button(
                label="📥 下载脚本JSON",
                data=json.dumps(script, ensure_ascii=False, indent=2),
                file_name=f"{title}.json",
                mime="application/json"
            )

    elif input_method == "上传JSON文件":
        uploaded_file = st.file_uploader("上传脚本JSON文件", type=["json"])
        if uploaded_file:
            try:
                script = json.load(uploaded_file)
                st.session_state.script = script
                st.success(f"✅ 已加载脚本：{script.get('title', '未命名')}")
                st.json(script)
            except Exception as e:
                st.error(f"❌ 脚本解析失败：{str(e)}")

    else:  # 使用示例模板
        examples_dir = Path(__file__).parent.parent / "examples"
        if examples_dir.exists():
            example_files = list(examples_dir.glob("*.json"))
            selected_example = st.selectbox(
                "选择示例模板",
                [f.name for f in example_files]
            )

            if st.button("加载示例"):
                example_path = examples_dir / selected_example
                with open(example_path, 'r', encoding='utf-8') as f:
                    script = json.load(f)
                st.session_state.script = script
                st.success(f"✅ 已加载示例：{script.get('title', selected_example)}")
                st.json(script)

# 生成控制标签
with tab2:
    st.markdown('<h2 class="sub-header">🚀 生成控制</h2>', unsafe_allow_html=True)

    # 显示当前脚本
    if st.session_state.script:
        st.info(f"📋 当前脚本：{st.session_state.script.get('title', '未命名')}")

        # 生成参数确认
        st.markdown("### ⚙️ 生成参数")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("分辨率", f"{width}x{height}")
        with col2:
            st.metric("采样步数", steps)
        with col3:
            st.metric("场景数", len(st.session_state.script.get('scenes', [])))

        # 生成按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 开始生成", type="primary", use_container_width=True):
                if st.session_state.status == 'running':
                    st.warning("⚠️ 已有生成任务正在运行")
                else:
                    st.session_state.status = 'running'
                    st.rerun()

        with col2:
            if st.session_state.status == 'running':
                if st.button("⏹️ 停止生成", type="secondary", use_container_width=True):
                    st.session_state.status = 'stopped'
                    st.info("⏹️ 已停止生成")
                    st.rerun()
    else:
        st.warning("⚠️ 请先在"脚本编辑"标签页创建或加载脚本")

# 进度监控标签
with tab3:
    st.markdown('<h2 class="sub-header">📊 进度监控</h2>', unsafe_allow_html=True)

    if st.session_state.status == 'running':
        # 模拟进度显示
        st.markdown('<div class="progress-box">', unsafe_allow_html=True)

        # 总体进度
        st.markdown("### 📊 总体进度")
        total_scenes = len(st.session_state.script.get('scenes', []))

        # 阶段进度
        stages = [
            ("音频生成", 0.1),
            ("视频生成", 0.7),
            ("音频混合", 0.1),
            ("最终合成", 0.1)
        ]

        for stage, weight in stages:
            st.markdown(f"**{stage}**")
            progress = st.progress(0)
            status = st.empty()

        # ComfyUI队列状态
        st.markdown("### 🎬 ComfyUI队列")
        queue_status = st.empty()
        queue_status.info("🔄 正在检查队列...")

        # 自动刷新
        if st.checkbox("自动刷新进度", value=True):
            time.sleep(2)
            st.rerun()

    elif st.session_state.status == 'completed':
        st.success("✅ 生成完成！请到"结果预览"标签查看结果")

    else:
        st.info("ℹ️ 尚未开始生成，请在"生成控制"标签页点击开始")

# 结果预览标签
with tab4:
    st.markdown('<h2 class="sub-header">🎥 结果预览</h2>', unsafe_allow_html=True)

    if st.session_state.output_dir and Path(st.session_state.output_dir).exists():
        output_path = Path(st.session_state.output_dir)

        # 最终视频
        final_video = output_path / "final" / f"{st.session_state.script['title']}_final.mp4"
        if final_video.exists():
            st.markdown("### 🎬 最终视频")
            st.video(str(final_video))

            # 下载按钮
            with open(final_video, 'rb') as f:
                st.download_button(
                    label="📥 下载最终视频",
                    data=f,
                    file_name=final_video.name,
                    mime="video/mp4"
                )

        # 单个场景视频
        st.markdown("### 🎞️ 单场景视频")
        video_dir = output_path / "video"
        if video_dir.exists():
            videos = list(video_dir.glob("*.mp4"))
            for video in sorted(videos):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.video(str(video))
                with col2:
                    st.markdown(f"**{video.name}**")
                    st.metric("文件大小", f"{video.stat().st_size / (1024*1024):.2f} MB")

                    with open(video, 'rb') as f:
                        st.download_button(
                            label="下载",
                            data=f,
                            file_name=video.name,
                            mime="video/mp4",
                            key=f"dl_{video.name}"
                        )
    else:
        st.info("ℹ️ 尚未生成任何内容")

# 实际生成逻辑
if st.session_state.status == 'running' and st.session_state.script:
    with st.spinner("正在生成中..."):
        try:
            # 初始化生成器
            output_dir = f"output/streamlit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            generator = VideoStoryGenerator(
                script_path=None,  # 直接传脚本
                output_dir=output_dir,
                voice=voice_id,
                width=width,
                height=height,
                steps=steps,
                narration_volume=narration_volume,
                ambient_volume=ambient_volume
            )
            generator.script = st.session_state.script

            # 执行生成
            asyncio.run(generator.run_full_pipeline())

            # 更新状态
            st.session_state.status = 'completed'
            st.session_state.output_dir = output_dir
            st.success("✅ 生成完成！")
            st.rerun()

        except Exception as e:
            st.error(f"❌ 生成失败：{str(e)}")
            st.session_state.status = 'error'

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🎬 AI短视频自动化制作智能体 | 基于MiniMax H3模型</p>
    <p>💡 技术支持：ComfyUI + edge-tts + ffmpeg</p>
</div>
""", unsafe_allow_html=True)