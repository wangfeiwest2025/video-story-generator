#!/bin/bash
# AI短视频生成技能 - 环境检查脚本

echo "=========================================="
echo "🔍 AI短视频生成技能 - 环境检查"
echo "=========================================="
echo ""

# 检查Python
echo "📌 检查 Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Python 未安装"
    exit 1
fi

# 检查ffmpeg
echo ""
echo "📌 检查 ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1)
    echo "   ✅ $FFMPEG_VERSION"
else
    echo "   ❌ ffmpeg 未安装"
    echo "   安装: apt install ffmpeg 或 brew install ffmpeg"
fi

# 检查ComfyUI
echo ""
echo "📌 检查 ComfyUI..."
if pgrep -f "main.py" > /dev/null; then
    echo "   ✅ ComfyUI 正在运行"
    curl -s http://127.0.0.1:8188/system_stats > /dev/null && echo "   ✅ API 可访问" || echo "   ⚠️  API 不可访问"
else
    echo "   ⚠️  ComfyUI 未运行"
    echo "   启动: cd ComfyUI && python main.py"
fi

# 检查MiniMax H3模型
echo ""
echo "📌 检查 MiniMax H3 模型..."
MODELS=(
    "minimax_h3_fl2va_int8_convrot.safetensors"
    "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
    "minimax_h3_video_vae_fp16.safetensors"
    "minimax_h3_audio_vae_fp32.safetensors"
)

MODEL_DIRS=(
    "ComfyUI/models/diffusion_models"
    "ComfyUI/models/text_encoders"
    "ComfyUI/models/vae"
    "ComfyUI/models/vae"
)

ALL_MODELS_OK=true
for i in "${!MODELS[@]}"; do
    MODEL="${MODELS[$i]}"
    DIR="${MODEL_DIRS[$i]}"

    if [ -f "$DIR/$MODEL" ]; then
        echo "   ✅ $MODEL"
    else
        echo "   ❌ $MODEL (未找到)"
        ALL_MODELS_OK=false
    fi
done

# 检查Python包
echo ""
echo "📌 检查 Python 包..."
PACKAGES=("edge-tts" "mutagen" "requests")
for PKG in "${PACKAGES[@]}"; do
    if python3 -c "import $PKG" 2>/dev/null; then
        echo "   ✅ $PKG"
    else
        echo "   ❌ $PKG (未安装)"
        echo "      安装: pip install $PKG"
    fi
done

# GPU检查
echo ""
echo "📌 检查 GPU..."
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -n1)
    VRAM_FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -n1)
    echo "   ✅ GPU: $GPU_INFO"
    echo "   ✅ 可用VRAM: ${VRAM_FREE}MB"
else
    echo "   ⚠️  nvidia-smi 未找到"
fi

echo ""
echo "=========================================="
if [ "$ALL_MODELS_OK" = true ]; then
    echo "✅ 环境检查完成 - 准备就绪！"
else
    echo "⚠️  环境检查完成 - 请安装缺失的模型"
fi
echo "=========================================="