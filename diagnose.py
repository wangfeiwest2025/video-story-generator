#!/usr/bin/env python3
"""
诊断工具 - 检查视频生成状态和文件位置
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import json

st.set_page_config(page_title="视频生成诊断", page_icon="🔍", layout="wide")

st.title("🔍 视频生成诊断工具")

# 1. 检查项目输出目录
st.markdown("## 📁 项目输出目录检查")
project_root = Path(__file__).parent
output_base = project_root / "output"

st.write(f"**项目根目录**: `{project_root}`")
st.write(f"**输出目录**: `{output_base}`")
st.write(f"**输出目录存在**: {output_base.exists()}")

if output_base.exists():
    # 列出所有子目录
    output_dirs = sorted([d for d in output_base.iterdir() if d.is_dir()],
                        reverse=True)

    st.write(f"**找到项目数量**: {len(output_dirs)}")

    if output_dirs:
        for project_dir in output_dirs[:5]:  # 显示最新的5个
            st.markdown(f"### 📂 项目: {project_dir.name}")

            # 检查子目录
            audio_dir = project_dir / "audio"
            video_dir = project_dir / "video"
            final_dir = project_dir / "final"

            st.write(f"- **audio目录**: {'✅ 存在' if audio_dir.exists() else '❌ 不存在'}")
            if audio_dir.exists():
                audio_files = list(audio_dir.glob("*.mp3"))
                st.write(f"  - 音频文件数: {len(audio_files)}")
                if audio_files:
                    st.write(f"  - 文件列表: {[f.name for f in audio_files[:5]]}")

            st.write(f"- **video目录**: {'✅ 存在' if video_dir.exists() else '❌ 不存在'}")
            if video_dir.exists():
                video_files = list(video_dir.glob("*.mp4"))
                st.write(f"  - 视频文件数: {len(video_files)}")
                if video_files:
                    st.write(f"  - 文件列表: {[f.name for f in video_files[:5]]}")

            st.write(f"- **final目录**: {'✅ 存在' if final_dir.exists() else '❌ 不存在'}")
            if final_dir.exists():
                final_files = list(final_dir.glob("*.mp4"))
                st.write(f"  - 最终视频数: {len(final_files)}")
                if final_files:
                    st.write(f"  - 文件列表: {[f.name for f in final_files[:5]]}")

            st.markdown("---")
    else:
        st.warning("没有找到项目目录")
else:
    st.error("输出目录不存在")

# 2. 检查 ComfyUI 输出目录
st.markdown("## 📂 ComfyUI 输出目录检查")

comfyui_output_dir = st.text_input(
    "ComfyUI 输出目录路径",
    value="/workspace/output",
    help="请输入 ComfyUI 的 output 目录路径"
)

if st.button("检查 ComfyUI 输出"):
    comfyui_output = Path(comfyui_output_dir)

    st.write(f"**路径**: `{comfyui_output}`")
    st.write(f"**存在**: {comfyui_output.exists()}")

    if comfyui_output.exists():
        # 查找所有视频文件
        all_videos = list(comfyui_output.rglob("*.mp4"))
        st.write(f"**视频文件总数**: {len(all_videos)}")

        if all_videos:
            st.markdown("### 最新的视频文件")
            for video in sorted(all_videos, key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                size_mb = video.stat().st_size / 1024 / 1024
                mtime = datetime.fromtimestamp(video.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                st.write(f"- `{video.relative_to(comfyui_output)}` ({size_mb:.2f} MB) - {mtime}")

        # 检查是否有 video 子目录
        video_subdir = comfyui_output / "video"
        if video_subdir.exists():
            st.write(f"**video子目录存在**: ✅")
            videos_in_subdir = list(video_subdir.glob("*.mp4"))
            st.write(f"**video子目录中的视频数**: {len(videos_in_subdir)}")
            if videos_in_subdir:
                st.write("文件列表:")
                for v in videos_in_subdir[:10]:
                    st.write(f"  - {v.name}")
    else:
        st.error("ComfyUI 输出目录不存在")

# 3. 检查生成状态文件
st.markdown("## 📊 生成状态检查")
status_file = Path("/tmp/video_generation_status.json")
if status_file.exists():
    with open(status_file, 'r') as f:
        status = json.load(f)
    st.json(status)
else:
    st.info("状态文件不存在")

# 4. 检查场景时序文件
st.markdown("## ⏱️ 场景时序检查")
if output_base.exists():
    output_dirs = sorted([d for d in output_base.iterdir() if d.is_dir()],
                        reverse=True)
    if output_dirs:
        timing_file = output_dirs[0] / "audio" / "scene_timing.json"
        if timing_file.exists():
            with open(timing_file, 'r') as f:
                timing = json.load(f)
            st.json(timing)
        else:
            st.warning("场景时序文件不存在")

# 5. 提交记录检查
st.markdown("## 📝 提交记录检查")
if output_base.exists():
    output_dirs = sorted([d for d in output_base.iterdir() if d.is_dir()],
                        reverse=True)
    if output_dirs:
        submission_file = output_dirs[0] / "submissions.json"
        if submission_file.exists():
            with open(submission_file, 'r') as f:
                submissions = json.load(f)
            st.json(submissions)
        else:
            st.warning("提交记录文件不存在")

st.markdown("---")
st.markdown("""
**使用说明**:
1. 此工具帮助诊断视频生成问题
2. 检查文件是否正确生成到指定目录
3. 查看生成状态和进度
4. 确认 ComfyUI 输出路径是否正确
""")