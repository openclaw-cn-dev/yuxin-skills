#!/bin/bash
# 协作者持续调研目录监控脚本 v2.0（trap F 第 4 次实测 2026-08-18 沉淀）
#
# 用法：bash check-collaborator-research.sh [协作者名]
# 默认：[协作者名] = 老莫
#
# 背景：协作者的"持续调研"子目录路径已发生多次迁移（陷阱 F 第 4 次实测）
#   老莫当前主路径：3-公司项目资料/301-智能体/学习笔记/持续调研/
#   历史归档路径：1-公共知识/114-项目开发与调研/持续调研/
#
# 输出：所有候选"持续调研"目录的最新文件 + 时间戳 + 距今天数
# 退出码：
#   0 = 找到 ≥1 个目录 + 最新调研 ≤ 14 天
#   1 = 最新调研 > 14 天（需启动催办 SOP）

set -e

COLLABORATOR="${1:-老莫}"
TODAY=$(date +%s)
THRESHOLD_DAYS=14

echo "=== 协作者调研目录监控 v2.0（$COLLABORATOR）==="
echo ""

# 1. 发现所有候选路径
DIRS=$(find /Users/hua/rkr_staging -name "持续调研" -type d 2>/dev/null)

if [ -z "$DIRS" ]; then
  echo "❌ 未找到任何'持续调研'目录"
  exit 1
fi

echo "📂 发现的候选路径："
echo "$DIRS" | while read -r d; do
  echo "  - $d"
done
echo ""

# 2. 检查每个路径的最新文件
NEWEST_FILE=""
NEWEST_TIME=0
NEWEST_DIR=""

for d in $DIRS; do
  echo "--- $d ---"
  LATEST=$(ls -t "$d"/*.md 2>/dev/null | head -1 || true)
  if [ -z "$LATEST" ]; then
    echo "  (无 .md 文件)"
    continue
  fi
  MTIME=$(stat -f %m "$LATEST" 2>/dev/null || echo 0)
  AGE_DAYS=$(( (TODAY - MTIME) / 86400 ))
  echo "  最新: $(basename "$LATEST")"
  echo "  时间: $(stat -f '%Sm' "$LATEST")"
  echo "  距今: ${AGE_DAYS} 天"

  if [ "$MTIME" -gt "$NEWEST_TIME" ]; then
    NEWEST_TIME="$MTIME"
    NEWEST_FILE="$LATEST"
    NEWEST_DIR="$d"
  fi
done

echo ""
echo "=== 全局最新调研 ==="
if [ -z "$NEWEST_FILE" ]; then
  echo "❌ 未找到任何调研文件"
  exit 1
fi

AGE_DAYS=$(( (TODAY - NEWEST_TIME) / 86400 ))
echo "📄 文件: $(basename "$NEWEST_FILE")"
echo "📁 目录: $NEWEST_DIR"
echo "📅 时间: $(stat -f '%Sm' "$NEWEST_FILE")"
echo "⏱️  距今: ${AGE_DAYS} 天"
echo ""

# 3. 阈值判定
if [ "$AGE_DAYS" -le "$THRESHOLD_DAYS" ]; then
  echo "✅ $COLLABORATOR 活跃（${AGE_DAYS} 天 ≤ ${THRESHOLD_DAYS} 天阈值）"
  exit 0
else
  echo "⚠️ $COLLABORATOR 调研超时（${AGE_DAYS} 天 > ${THRESHOLD_DAYS} 天阈值）—— 启动催办 SOP"
  exit 1
fi