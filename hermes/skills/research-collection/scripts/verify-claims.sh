#!/bin/bash
# verify-claims.sh — 验证 subagent 报告里的具体 claim
# 用法：./verify-claims.sh "claim1" "claim2" ...
# 每个 claim 用 web_search 验证，最后输出 ✅/⚠️ 汇总

set -e

CLAIMS=("$@")

if [ ${#CLAIMS[@]} -eq 0 ]; then
  echo "用法: $0 \"<claim1>\" \"<claim2>\" ..."
  echo "示例: $0 '\"10.1038/s41467-026-70682-y\"' 'Moleaer Freya 2025'"
  exit 1
fi

echo "🔍 验证 ${#CLAIMS[@]} 个 claim..."
echo ""

VERIFIED=0
UNVERIFIED=0

for i in "${!CLAIMS[@]}"; do
  CLAIM="${CLAIMS[$i]}"
  NUM=$((i+1))

  echo "[$NUM/$NUM] ${CLAIM}"
  echo "---"
  echo "请人工检查 web_search 输出："
  echo ""
  read -p "通过验证？(y/n): " VERDICT

  if [ "$VERDICT" = "y" ] || [ "$VERDICT" = "Y" ]; then
    echo "✅ 已验证"
    VERIFIED=$((VERIFIED+1))
  else
    echo "⚠️ 存疑"
    UNVERIFIED=$((UNVERIFIED+1))
  fi
  echo ""
done

echo "================================"
echo "汇总：✅ $VERIFIED 已验证 ｜ ⚠️ $UNVERIFIED 存疑"
echo "================================"