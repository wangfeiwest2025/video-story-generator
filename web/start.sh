#!/bin/bash

echo "🎬 启动AI短视频生成器 Web界面..."
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
fi

# 激活虚拟环境
source venv/bin/activate

# 检查ComfyUI
echo "🔍 检查ComfyUI连接..."
if curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
    echo "✅ ComfyUI连接正常"
else
    echo "⚠️  ComfyUI未运行在 http://localhost:8188"
    echo "   请确保ComfyUI正在运行"
    echo ""
fi

# 启动Streamlit
echo ""
echo "🚀 启动Streamlit服务..."
echo "📱 访问地址: http://localhost:8501"
echo "🌐 网络访问: http://$(hostname -I | awk '{print $1}'):8501"
echo ""

streamlit run app.py --server.port 8501 --server.address 0.0.0.0