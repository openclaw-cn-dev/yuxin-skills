#!/bin/bash
# generate-decision-matrix.sh
# ai-tech-scheme-consolidation SOP 辅助工具
# 用法：bash generate-decision-matrix.sh <议题 1> <议题 2> ...
# 输出 Markdown 共识区/分歧区矩阵骨架到 stdout
# 复制到 docs/NN_consolidated_v{N}.md 的"共识区/分歧区"段填写

set -e

if [ $# -eq 0 ]; then
    echo "用法: $0 <议题 1> <议题 2> ..."
    echo "示例: $0 '1D 水柱模型' 'DO 平衡' '塘形支持' 'ML 路线'"
    exit 1
fi

echo "## 共识区/分歧区矩阵"
echo ""
echo "| 议题 | {vendor 1} | {vendor 2} | {vendor 3} | 渔芯判断 | 决策依据 |"
echo "|------|------------|------------|------------|---------|---------|"

for topic in "$@"; do
    # 转义 | 字符（防止破坏表格）
    safe_topic=$(echo "$topic" | sed 's/|/\\|/g')
    echo "| $safe_topic | ✅/⚠️/❌ | ✅/⚠️/❌ | ✅/⚠️/❌ | ✅/⚠️/❌ | {一句话} |"
done

echo ""
echo "## 填写说明"
echo ""
echo "- ✅ = 该方案已采纳此议题（直接引用 §X.Y）"
echo "- ⚠️ = 该方案思路对但需砍改（见 docs/NN_*_review.md）"
echo "- ❌ = 该方案无此议题或反对此议题"
echo "- 渔芯判断 = 综合 3 份方案 + 渔芯约束（M4 16GB / 团队人数 / 时间 / 商业化）"
echo "- 决策依据 = 一句话说明为什么这么判断"
echo ""
echo "## 下一步"
echo ""
echo "1. 把每行填充完毕"
echo "2. 共识区（多数 ✅）直接进决策稿；分歧区（结论不同）单独列"
echo "3. 不做的项进\"不做什么清单\"段"
