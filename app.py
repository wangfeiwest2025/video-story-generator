"""
AI短视频自动化制作智能体 - Streamlit Web界面（简化版）
使用文件系统跟踪状态，避免 session_state 的线程问题
"""

import streamlit as st
import json
import os
import sys
import asyncio
import time
import threading
from pathlib import Path
from datetime import datetime
import subprocess

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
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
</style>
""", unsafe_allow_html=True)

# 状态文件路径
STATUS_FILE = Path("/tmp/video_generation_status.json")

def get_status():
    """从文件读取状态"""
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"status": "idle", "message": "", "error": ""}
    return {"status": "idle", "message": "", "error": ""}

def set_status(status, message="", error=""):
    """写入状态到文件"""
    with open(STATUS_FILE, 'w') as f:
        json.dump({"status": status, "message": message, "error": error}, f)

# 初始化session state
if 'script' not in st.session_state:
    st.session_state.script = None

# 侧边栏
with st.sidebar:
    st.markdown("### 🎬 AI短视频生成器")
    st.markdown("---")

    # ComfyUI设置
    st.markdown("### 🔌 ComfyUI设置")
    comfyui_url = st.text_input(
        "ComfyUI地址",
        value="http://127.0.0.1:8188"
    )

    comfyui_output_dir = st.text_input(
        "ComfyUI输出目录",
        value="/workspace/output",
        help="ComfyUI 生成的视频保存路径（通常在 ComfyUI 的 output 目录）"
    )

    # 测试连接
    if st.button("🔌 测试连接", use_container_width=True):
        try:
            import requests
            response = requests.get(f"{comfyui_url}/system_stats", timeout=5)
            if response.status_code == 200:
                st.success("✅ ComfyUI连接成功！")
            else:
                st.error(f"❌ 连接失败: HTTP {response.status_code}")
        except Exception as e:
            st.error(f"❌ 连接失败: {str(e)}")

    st.markdown("---")

    # 视频参数
    st.markdown("### 🎨 视频参数")

    voice = st.selectbox(
        "TTS语音",
        ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-YunjianNeural"]
    )

    resolution = st.select_slider(
        "分辨率",
        options=["960x544", "1344x768", "1920x1080"],
        value="1344x768"
    )
    width, height = map(int, resolution.split('x'))

    steps = st.slider("采样步数", min_value=15, max_value=30, value=20)

    # 音频参数
    st.markdown("---")
    st.markdown("### 🔊 音频参数")

    narration_volume = st.slider(
        "解说词音量",
        min_value=0.5,
        max_value=2.0,
        value=1.2,
        step=0.1,
        help="解说词相对于原始音量的倍数"
    )

    ambient_volume = st.slider(
        "环境音音量",
        min_value=0.1,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="环境音相对于原始音量的倍数"
    )

# 主界面
st.markdown('<h1 class="main-header">🎬 AI短视频生成器</h1>', unsafe_allow_html=True)
st.markdown("---")

# 创建标签页
tab1, tab2, tab3, tab4 = st.tabs(["📝 脚本编辑", "🚀 生成控制", "📊 进度监控", "🎥 结果预览"])

# 脚本编辑标签
with tab1:
    st.markdown('<h2 class="sub-header">📝 脚本编辑</h2>', unsafe_allow_html=True)

    edit_mode = st.radio("编辑模式", ["在线编辑", "加载示例"])

    if edit_mode == "在线编辑":
        title = st.text_input("视频标题", value="我的AI视频")
        style = st.text_input("视频风格", value="电影级")

        st.markdown("### 场景列表")
        num_scenes = st.number_input("场景数量", min_value=1, max_value=5, value=1)

        scenes = []
        for i in range(num_scenes):
            with st.expander(f"场景 {i+1}", expanded=(i==0)):
                narration = st.text_area(
                    f"解说词 {i+1}",
                    value=f"这是第{i+1}个场景的解说词。",
                    key=f"narration_{i}"
                )
                visual_prompt = st.text_area(
                    f"视觉描述 {i+1} (英文)",
                    value="A beautiful scene",
                    key=f"visual_{i}"
                )
                audio = st.text_input(
                    f"音频描述 {i+1}",
                    value="ambient music",
                    key=f"audio_{i}"
                )

                scenes.append({
                    "id": i+1,
                    "narration": narration,
                    "visual_prompt": visual_prompt,
                    "audio": audio
                })

        if st.button("生成脚本", type="primary"):
            script = {
                "title": title,
                "style": style,
                "voice": voice,
                "scenes": scenes
            }
            st.session_state.script = script
            st.success("✅ 脚本已生成！")
            st.json(script)

    else:  # 加载示例
        example_dir = Path(__file__).parent / "examples"
        examples = list(example_dir.glob("*.json"))

        if examples:
            selected_example = st.selectbox(
                "选择示例脚本",
                [ex.name for ex in examples]
            )

            if st.button("加载示例"):
                example_path = example_dir / selected_example
                with open(example_path, 'r', encoding='utf-8') as f:
                    script = json.load(f)
                st.session_state.script = script
                st.success(f"✅ 已加载脚本：{script.get('title', selected_example)}")
                st.json(script)
        else:
            st.warning("暂无示例脚本")

# 生成控制标签
with tab2:
    st.markdown('<h2 class="sub-header">🚀 生成控制</h2>', unsafe_allow_html=True)

    if st.session_state.script:
        st.info(f"📋 当前脚本：{st.session_state.script.get('title', '未命名')}")

        # 显示参数
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
                # 检查状态
                current_status = get_status()
                if current_status["status"] == "running":
                    st.warning("⚠️ 已有生成任务正在运行")
                else:
                    # 准备生成
                    set_status("running", "正在初始化...")

                    # 保存脚本
                    temp_script = Path("/tmp/current_script.json")
                    with open(temp_script, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.script, f, ensure_ascii=False, indent=2)

                    # 创建输出目录 - 使用项目目录内的相对路径
                    project_root = Path(__file__).parent
                    output_dir = project_root / "output" / datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_dir.mkdir(parents=True, exist_ok=True)

                    # 后台生成函数
                    def run_generation():
                        try:
                            set_status("running", "创建生成器...")

                            gen = VideoStoryGenerator(
                                script_file=str(temp_script),
                                output_dir=str(output_dir),
                                comfyui_url=comfyui_url,
                                comfyui_output_dir=comfyui_output_dir,
                                voice=voice,
                                width=width,
                                height=height,
                                steps=steps,
                                narration_volume=narration_volume,
                                ambient_volume=ambient_volume
                            )

                            # 运行完整流程
                            set_status("running", "生成音频...")
                            asyncio.run(gen.generate_narration_audio())

                            # 检查模型
                            set_status("running", "检查 MiniMax H3 模型...")
                            gen.check_minimax_models()

                            # 获取音频时长
                            set_status("running", "计算音频时长...")
                            scene_timing = gen.get_audio_durations()

                            # 提交视频生成任务
                            set_status("running", "提交视频生成任务到 ComfyUI...")
                            prompt_ids = gen.submit_all_videos(scene_timing)

                            if not prompt_ids:
                                set_status("error", "", "未能提交任何视频生成任务，请检查 ComfyUI 连接")
                                return

                            set_status("running", f"已提交 {len(prompt_ids)} 个任务到 ComfyUI，等待完成...")

                            # 等待完成
                            gen.wait_for_completion(prompt_ids, check_interval=60)

                            # 混合音频
                            set_status("running", "混合音频...")
                            gen.mix_audio()

                            # 合成最终视频
                            set_status("running", "合成最终视频...")
                            final_video = gen.compose_final_video()

                            if final_video:
                                set_status("completed", f"视频已生成到: {output_dir}")
                            else:
                                set_status("error", "", "视频合成失败")

                        except Exception as e:
                            import traceback
                            error_msg = f"{str(e)}\n{traceback.format_exc()}"
                            set_status("error", "", error_msg)

                    # 启动线程
                    thread = threading.Thread(target=run_generation, daemon=True)
                    thread.start()

                    st.success("✅ 生成任务已启动！")
                    time.sleep(1)
                    st.rerun()

        with col2:
            if st.button("⏹️ 重置状态", type="secondary", use_container_width=True):
                set_status("idle", "已重置")
                st.info("✅ 状态已重置")
                st.rerun()

    else:
        st.warning("⚠️ 请先在\"脚本编辑\"标签页创建或加载脚本")

# 进度监控标签
with tab3:
    st.markdown('<h2 class="sub-header">📊 进度监控</h2>', unsafe_allow_html=True)

    status = get_status()

    if status["status"] == "running":
        st.markdown('<div class="info-box">🔄 正在生成...</div>', unsafe_allow_html=True)

        if status["message"]:
            st.info(f"**当前状态**: {status['message']}")

        # 显示 ComfyUI 队列
        try:
            import requests
            response = requests.get(f"{comfyui_url}/queue", timeout=5)
            if response.status_code == 200:
                queue_data = response.json()
                running = len(queue_data.get('queue_running', []))
                pending = len(queue_data.get('queue_pending', []))
                st.metric("ComfyUI 队列", f"{running} 运行中 / {pending} 等待")
        except:
            pass

        # 自动刷新
        if st.checkbox("自动刷新", value=True):
            time.sleep(3)
            st.rerun()

    elif status["status"] == "completed":
        st.markdown('<div class="success-box">✅ 生成完成！</div>', unsafe_allow_html=True)
        if status["message"]:
            st.success(status["message"])

    elif status["status"] == "error":
        st.error(f"❌ 生成失败")
        if status["error"]:
            with st.expander("查看错误详情"):
                st.code(status["error"])

    else:
        st.info("ℹ️ 尚未开始生成")

# 结果预览标签
with tab4:
    st.markdown('<h2 class="sub-header">🎥 结果预览</h2>', unsafe_allow_html=True)

    # 使用项目目录内的相对路径
    project_root = Path(__file__).parent
    output_base = project_root / "output"

    st.info(f"📁 输出目录: `{output_base}`")

    if output_base.exists():
        # 找到所有项目目录
        output_dirs = sorted([d for d in output_base.iterdir() if d.is_dir() and d.name.startswith("202")],
                            reverse=True)

        if output_dirs:
            st.write(f"找到 {len(output_dirs)} 个生成项目")

            # 检查最新的完整项目
            for project_dir in output_dirs[:5]:  # 检查最新的5个项目
                final_dir = project_dir / "final"
                video_dir = project_dir / "video"
                audio_dir = project_dir / "audio"

                # 检查是否有文件
                final_videos = list(final_dir.glob("*.mp4")) if final_dir.exists() else []
                mixed_videos = list(final_dir.glob("*_mixed.mp4")) if final_dir.exists() else []
                scene_videos = list(video_dir.glob("*.mp4")) if video_dir.exists() else []
                audio_files = list(audio_dir.glob("*.mp3")) if audio_dir.exists() else []

                if final_videos or mixed_videos or scene_videos or audio_files:
                    st.markdown(f"### 📁 项目: {project_dir.name}")

                    # 显示文件统计
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("最终视频", len(final_videos))
                    with col2:
                        st.metric("场景视频", len(scene_videos))
                    with col3:
                        st.metric("音频文件", len(audio_files))

                    # 显示最终视频
                    if final_videos:
                        st.markdown("#### 🎬 最终完整视频")
                        for video in sorted(final_videos):
                            size_mb = video.stat().st_size / 1024 / 1024
                            mtime = datetime.fromtimestamp(video.stat().st_mtime).strftime("%H:%M:%S")

                            with st.expander(f"✅ {video.name} ({size_mb:.2f} MB) - {mtime}", expanded=(video == final_videos[0])):
                                st.success("✅ 包含完整解说词和环境音")

                                col1, col2 = st.columns(2)
                                with col1:
                                    st.video(str(video))
                                with col2:
                                    try:
                                        with open(video, 'rb') as f:
                                            st.download_button(
                                                f"📥 下载最终视频",
                                                f,
                                                file_name=video.name,
                                                mime="video/mp4",
                                                key=f"download_{project_dir.name}_{video.name}"
                                            )
                                    except Exception as e:
                                        st.error(f"下载失败: {e}")

                    # 显示混合视频（含解说词）
                    if mixed_videos:
                        st.markdown("#### 🎵 场景视频（含解说词）")
                        for video in sorted(mixed_videos):
                            size_mb = video.stat().st_size / 1024 / 1024

                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**{video.name}** ({size_mb:.2f} MB)")
                            with col2:
                                try:
                                    with open(video, 'rb') as f:
                                        st.download_button(
                                            "📥",
                                            f,
                                            file_name=video.name,
                                            mime="video/mp4",
                                            key=f"dl_{project_dir.name}_{video.name}"
                                        )
                                except Exception as e:
                                    st.error(f"下载失败: {e}")

                    # 显示原始视频
                    if scene_videos:
                        with st.expander(f"📹 原始场景视频 ({len(scene_videos)} 个)"):
                            st.info("这些是从 ComfyUI 生成的原始视频（仅含环境音）")
                            for video in sorted(scene_videos):
                                size_mb = video.stat().st_size / 1024 / 1024
                                st.write(f"- **{video.name}** ({size_mb:.2f} MB)")

                    # 显示解说词音频
                    if audio_files:
                        with st.expander(f"🎙️ 解说词音频 ({len(audio_files)} 个)"):
                            for audio in sorted(audio_files):
                                size_kb = audio.stat().st_size / 1024
                                st.write(f"- {audio.name} ({size_kb:.1f} KB)")
                                st.audio(str(audio))

                    st.markdown("---")
        else:
            st.warning("没有找到生成项目")
    else:
        st.warning("输出目录不存在，请先生成视频")

    # 显示 ComfyUI 原始输出
    if comfyui_output_dir:
        st.markdown("### 📂 ComfyUI 原始输出")
        comfyui_output = Path(comfyui_output_dir)

        st.info(f"ComfyUI 输出目录: `{comfyui_output}`")

        if comfyui_output.exists():
            # 查找视频文件
            all_videos = list(comfyui_output.rglob("*.mp4"))
            if all_videos:
                st.write(f"找到 {len(all_videos)} 个视频文件")

                # 显示最新的视频
                for video in sorted(all_videos, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                    size_mb = video.stat().st_size / 1024 / 1024
                    mtime = datetime.fromtimestamp(video.stat().st_mtime).strftime("%m/%d %H:%M")

                    with st.expander(f"{video.name} ({size_mb:.2f} MB) - {mtime}"):
                        st.info("ℹ️ 原始生成的视频（仅含环境音，无解说词）")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.video(str(video))
                        with col2:
                            try:
                                with open(video, 'rb') as f:
                                    st.download_button(
                                        f"📥 下载原始视频",
                                        f,
                                        file_name=video.name,
                                        mime="video/mp4",
                                        key=f"dl_comfyui_{video.name}"
                                    )
                            except Exception as e:
                                st.error(f"下载失败: {e}")
            else:
                st.info("ComfyUI 输出目录中没有找到视频文件")
        else:
            st.warning(f"ComfyUI 输出目录不存在: {comfyui_output}")
            st.markdown("""
            **提示**:
            - 如果使用外部 ComfyUI，请确保输出目录路径正确
            - 如果 ComfyUI 在同一环境中，默认路径通常是 `/workspace/output`
            """)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🎬 AI短视频自动化制作智能体 | Powered by MiniMax H3</p>
</div>
""", unsafe_allow_html=True)