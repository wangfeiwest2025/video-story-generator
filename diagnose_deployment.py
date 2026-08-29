#!/usr/bin/env python3
"""
部署环境诊断脚本
检查视频合成失败的具体原因
"""

import streamlit as st
import subprocess
import os
import sys
from pathlib import Path
import json

st.set_page_config(page_title="部署环境诊断", page_icon="🔍", layout="wide")

st.title("🔍 部署环境诊断 - 视频合成问题")

# 1. 环境信息
st.markdown("## 1️⃣ 环境信息")

st.write("### Python 环境")
st.write(f"- Python 版本: `{sys.version}`")
st.write(f"- 工作目录: `{Path.cwd()}`")
st.write(f"- 项目目录: `{Path(__file__).parent}`")
st.write(f"- 用户: `{os.getenv('USER', 'unknown')}`")

# 2. FFmpeg 检查
st.markdown("## 2️⃣ FFmpeg 检查")

try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        st.success("✅ FFmpeg 已安装")
        version_line = result.stdout.split('\n')[0]
        st.write(f"版本: `{version_line}`")
    else:
        st.error("❌ FFmpeg 执行失败")
except FileNotFoundError:
    st.error("❌ FFmpeg 未安装")
    st.markdown("""
    **解决方案**:
    ```bash
    apt-get update
    apt-get install -y ffmpeg
    ```
    """)
except Exception as e:
    st.error(f"❌ FFmpeg 检查失败: {e}")

# 3. 文件系统检查
st.markdown("## 3️⃣ 文件系统检查")

project_root = Path(__file__).parent
output_dir = project_root / "output"

st.write(f"**项目目录**: `{project_root}`")
st.write(f"- 是否存在: {'✅' if project_root.exists() else '❌'}")
st.write(f"- 可读取: {'✅' if os.access(project_root, os.R_OK) else '❌'}")
st.write(f"- 可写入: {'✅' if os.access(project_root, os.W_OK) else '❌'}")

st.write(f"\n**输出目录**: `{output_dir}`")
st.write(f"- 是否存在: {'✅' if output_dir.exists() else '❌'}")

# 测试文件创建
test_file = project_root / "test_write.tmp"
try:
    test_file.write_text("test")
    test_file.unlink()
    st.write(f"- 写入测试: ✅ 成功")
except Exception as e:
    st.write(f"- 写入测试: ❌ {e}")
    st.error("❌ 无法在项目目录创建文件")

# 4. 磁盘空间
st.markdown("## 4️⃣ 磁盘空间")

try:
    import shutil
    total, used, free = shutil.disk_usage(project_root)
    st.write(f"- 总空间: {total / (1024**3):.2f} GB")
    st.write(f"- 已使用: {used / (1024**3):.2f} GB")
    st.write(f"- 剩余: {free / (1024**3):.2f} GB")

    if free < 1024**3:  # 小于 1GB
        st.warning("⚠️ 磁盘空间不足（小于 1GB）")
except Exception as e:
    st.error(f"❌ 无法获取磁盘空间: {e}")

# 5. 检查输出目录内容
st.markdown("## 5️⃣ 输出目录检查")

if output_dir.exists():
    # 查找最新的项目
    projects = sorted([d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith("202")],
                     reverse=True)

    if projects:
        st.write(f"找到 {len(projects)} 个生成项目")

        latest = projects[0]
        st.markdown(f"### 最新项目: `{latest.name}`")

        # 检查目录结构
        for subdir in ['audio', 'video', 'final']:
            path = latest / subdir
            if path.exists():
                files = list(path.glob("*"))
                st.write(f"- `{subdir}/`: {len(files)} 个文件")

                if subdir == 'video':
                    mp4_files = list(path.glob("*.mp4"))
                    st.write(f"  - MP4 文件: {len(mp4_files)} 个")
                    for f in mp4_files[:3]:
                        st.write(f"    - {f.name} ({f.stat().st_size / 1024 / 1024:.2f} MB)")

                if subdir == 'final':
                    mixed_files = list(path.glob("*_mixed.mp4"))
                    final_files = list(path.glob("*_final.mp4"))
                    st.write(f"  - 混合视频: {len(mixed_files)} 个")
                    st.write(f"  - 最终视频: {len(final_files)} 个")

                    if mixed_files:
                        for f in mixed_files[:3]:
                            st.write(f"    - {f.name} ({f.stat().st_size / 1024 / 1024:.2f} MB)")

        # 检查场景时序文件
        timing_file = latest / "audio" / "scene_timing.json"
        if timing_file.exists():
            with open(timing_file, 'r') as f:
                timing = json.load(f)
            st.markdown("#### 场景时序信息")
            st.json(timing)

        # 检查提交记录
        submission_file = latest / "submissions.json"
        if submission_file.exists():
            with open(submission_file, 'r') as f:
                submissions = json.load(f)
            st.markdown("#### 提交记录")
            st.json(submissions)
    else:
        st.info("没有找到生成项目")
else:
    st.warning("输出目录不存在")

# 6. 测试 FFmpeg 合成
st.markdown("## 6️⃣ FFmpeg 合成测试")

if st.button("🧪 测试 FFmpeg 合成"):
    test_dir = project_root / "test_ffmpeg"
    test_dir.mkdir(exist_ok=True)

    try:
        # 创建测试视频（黑色画面）
        create_cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=320x240:d=1",
            "-c:v", "libx264",
            str(test_dir / "test1.mp4")
        ]

        result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            st.success("✅ 创建测试视频成功")

            # 测试合成
            list_file = test_dir / "list.txt"
            list_file.write_text(f"file '{test_dir / 'test1.mp4'}'\n")

            concat_cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(list_file),
                "-c", "copy",
                str(test_dir / "output.mp4")
            ]

            result = subprocess.run(concat_cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                st.success("✅ FFmpeg 合成成功")
                output_file = test_dir / "output.mp4"
                if output_file.exists():
                    st.write(f"输出文件大小: {output_file.stat().st_size} bytes")
            else:
                st.error(f"❌ FFmpeg 合成失败")
                st.code(result.stderr)
        else:
            st.error(f"❌ 创建测试视频失败")
            st.code(result.stderr)

        # 清理
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)

    except subprocess.TimeoutExpired:
        st.error("❌ FFmpeg 执行超时")
    except Exception as e:
        st.error(f"❌ 测试失败: {e}")

# 7. 检查编码器
st.markdown("## 7️⃣ 视频编码器检查")

try:
    result = subprocess.run(
        ["ffmpeg", "-encoders"],
        capture_output=True, text=True, timeout=5
    )

    if result.returncode == 0:
        encoders = result.stdout

        # 检查关键编码器
        important_encoders = ['libx264', 'aac', 'mp3']
        for encoder in important_encoders:
            if encoder in encoders:
                st.write(f"✅ {encoder}")
            else:
                st.write(f"❌ {encoder} - 缺失")
except Exception as e:
    st.error(f"❌ 无法检查编码器: {e}")

# 8. 常见问题和解决方案
st.markdown("## 💡 常见问题和解决方案")

st.markdown("""
### 问题 1: FFmpeg 未安装

**症状**: "ffmpeg: command not found"

**解决方案**:
```bash
apt-get update
apt-get install -y ffmpeg
```

### 问题 2: 磁盘空间不足

**症状**: "No space left on device"

**解决方案**:
- 清理旧文件: `rm -rf output/20260829_*`
- 检查磁盘使用: `df -h`

### 问题 3: 权限问题

**症状**: "Permission denied"

**解决方案**:
```bash
chmod -R 755 /path/to/project
chown -R user:user /path/to/project
```

### 问题 4: 文件名编码问题

**症状**: 中文文件名导致错误

**解决方案**:
- 使用英文文件名
- 设置环境变量: `export LANG=en_US.UTF-8`

### 问题 5: Streamlit Cloud 限制

**症状**: 在 Streamlit Cloud 上失败

**原因**:
- Streamlit Cloud 不支持 ffmpeg
- 有磁盘空间限制
- 有执行时间限制

**解决方案**:
- 使用其他部署平台（如 Railway, Render）
- 或使用 Docker 部署
""")

# 9. 导出诊断信息
st.markdown("## 📋 导出诊断信息")

if st.button("📄 导出完整诊断报告"):
    report = f"""
# 部署环境诊断报告

## 环境信息
- Python: {sys.version}
- 工作目录: {Path.cwd()}
- 项目目录: {Path(__file__).parent}

## FFmpeg
- 已安装: {'是' if subprocess.run(['which', 'ffmpeg'], capture_output=True).returncode == 0 else '否'}

## 文件系统
- 项目目录可写入: {'是' if os.access(project_root, os.W_OK) else '否'}
- 输出目录存在: {'是' if output_dir.exists() else '否'}

## 磁盘空间
- 总空间: {total / (1024**3):.2f} GB
- 剩余: {free / (1024**3):.2f} GB
"""

    st.download_button(
        "下载诊断报告",
        report,
        file_name="deployment_diagnosis.txt",
        mime="text/plain"
    )

st.markdown("---")
st.info("请运行此诊断工具，并将结果发送给我，我可以帮您定位具体问题。")