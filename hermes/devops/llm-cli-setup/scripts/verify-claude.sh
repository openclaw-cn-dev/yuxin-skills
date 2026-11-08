#!/bin/bash
# Claude Code 装机验收脚本 — 跑完 4 步全绿才算装好
# 用法：bash verify-claude.sh

set -e
echo "=========================================="
echo " Claude Code 装机验收"
echo "=========================================="

# [1] Node 版本
echo -n "[1/4] Node 版本（需 ≥18）: "
NODE_VER=$(node --version 2>/dev/null | sed 's/v//')
NODE_MAJOR=$(echo "$NODE_VER" | cut -d. -f1)
if [ "$NODE_MAJOR" -ge 18 ]; then
  echo "✅ v$NODE_VER"
else
  echo "❌ v$NODE_VER 太老，请升级 Node"
  exit 1
fi

# [2] claude 可执行
echo -n "[2/4] claude 可执行: "
if command -v claude >/dev/null 2>&1; then
  CLAUDE_PATH=$(which claude)
  echo "✅ $CLAUDE_PATH"
else
  echo "❌ 找不到 claude（可能需要重开终端或检查 PATH）"
  exit 1
fi

# [3] 版本号
echo -n "[3/4] claude --version: "
CLAUDE_VER=$(claude --version 2>&1)
echo "✅ $CLAUDE_VER"

# [4] 最小对话（不传 Key 会失败但能验证 CLI 本身工作）
echo "[4/4] 最小对话测试（这一步会尝试调 API，无 Key 正常会失败）: "
if claude -p "say 'pong' only" 2>&1 | head -5; then
  echo "✅ 调通"
else
  echo "⚠️  调 API 失败（可能没设 Key 或 Key 错，CLI 本身是好的）"
fi

echo "=========================================="
echo " 装机部分完成，配置 Key 见 templates/claude-code-env.bat"
echo "=========================================="
