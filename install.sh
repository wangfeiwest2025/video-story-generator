#!/bin/bash
# 安装AI短视频生成技能

SKILL_NAME="video-story-generator"
SKILL_DIR="$(pwd)"

echo "=========================================="
echo "🎬 安装 AI短视频生成技能"
echo "=========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "SKILL.md" ]; then
    echo "❌ 错误: 请在技能根目录运行此脚本"
    exit 1
fi

# 安装Python依赖
echo "📌 安装 Python 依赖..."
pip3 install -q edge-tts mutagen requests
echo "   ✅ 依赖安装完成"

# 设置脚本权限
echo ""
echo "📌 设置脚本权限..."
chmod +x scripts/*.sh
echo "   ✅ 权限设置完成"

# 检查环境
echo ""
echo "📌 检查环境..."
bash scripts/check_environment.sh

echo ""
echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "📖 快速开始:"
echo ""
echo "   1. 创建脚本文件:"
echo "      cp templates/script_template.json my_story.json"
echo ""
echo "   2. 编辑脚本文件:"
echo "      修改 scenes 数组，添加您的场景"
echo ""
echo "   3. 运行生成:"
echo "      python3 scripts/auto_generate.py my_story.json"
echo ""
echo "📖 完整文档: SKILL.md"
echo "📖 示例项目: examples/"
echo "=========================================="