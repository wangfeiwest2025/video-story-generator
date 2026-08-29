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
        example_dir = Path(__file__).parent.parent / "examples"
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

                    # 创建输出目录
                    output_dir = Path("/workspace/output") / datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_dir.mkdir(parents=True, exist_ok=True)

                    # 后台生成函数
                    def run_generation():
                        try:
                            set_status("running", "创建生成器...")

                            gen = VideoStoryGenerator(
                                script_file=str(temp_script),
                                output_dir=str(output_dir),
                                comfyui_url=comfyui_url,
                                voice=voice,
                                width=width,
                                height=height,
                                steps=steps
                            )

                            set_status("running", "生成音频...")
                            asyncio.run(gen.generate_narration_audio())

                            set_status("running", "提交视频生成任务...")
                            scene_timing = gen.get_audio_durations()
                            prompt_ids = gen.submit_all_videos(scene_timing)

                            set_status("running", f"已提交 {len(prompt_ids)} 个任务到 ComfyUI")

                            # 等待完成
                            gen.wait_for_completion(prompt_ids, check_interval=60)

                            set_status("running", "混合音频...")
                            gen.mix_audio()

                            set_status("running", "合成最终视频...")
                            gen.compose_final_video()

                            set_status("completed", f"视频已生成到: {output_dir}")

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

    # 1. 检查 ComfyUI 输出目录
    comfyui_output = Path("/workspace/ComfyUI/output")
    if comfyui_output.exists():
        # 查找所有 MP4 文件
        all_videos = list(comfyui_output.rglob("*.mp4"))
        if all_videos:
            st.markdown("### 🎬 生成的视频")
            for video in sorted(all_videos, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                size_mb = video.stat().st_size / 1024 / 1024
                mtime = datetime.fromtimestamp(video.stat().st_mtime).strftime("%H:%M:%S")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{video.name}** ({size_mb:.2f} MB) - {mtime}")
                with col2:
                    if st.button(f"▶️ 预览", key=f"preview_{video.name}"):
                        st.video(str(video))
                    with open(video, 'rb') as f:
                        st.download_button(
                            f"📥 下载",
                            f,
                            file_name=video.name,
                            mime="video/mp4",
                            key=f"download_{video.name}"
                        )

    # 2. 检查项目输出目录
    output_base = Path("/workspace/output")
    if output_base.exists():
        output_dirs = sorted([d for d in output_base.iterdir() if d.is_dir()], reverse=True)
        if output_dirs:
            latest_output = output_dirs[0]
            st.markdown("### 📂 项目输出目录")
            st.info(f"最新输出: `{latest_output.name}`")

            # 查找音频文件
            audio_files = list((latest_output / "audio").glob("*.mp3")) if (latest_output / "audio").exists() else []
            if audio_files:
                st.markdown(f"**音频文件**: {len(audio_files)} 个")
                for audio in audio_files[:3]:
                    st.audio(str(audio))

            # 查找视频文件
            video_files = list(latest_output.rglob("*.mp4"))
            if video_files:
                st.markdown(f"**视频文件**: {len(video_files)} 个")
                for video in video_files[:3]:
                    st.video(str(video))
            else:
                st.info("视频正在生成中...")

    # 3. 显示帮助信息
    if not (comfyui_output.exists() or output_base.exists()):
        st.info("ℹ️ 暂无输出文件")
        st.markdown("""
        **提示**：
        - 生成的视频保存在 ComfyUI 的输出目录
        - 点击"开始生成"后会自动创建输出文件
        - 视频生成需要 5-10 分钟，请耐心等待
        """)

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🎬 AI短视频自动化制作智能体 | Powered by MiniMax H3</p>
</div>
""", unsafe_allow_html=True)