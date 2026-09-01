#!/bin/bash
# sync_portal_to_profile.sh — F3 双端同步手动 cp + 验证（v1.0 · 2026-09-01 08:00 第 51 档立）
#
# 用途：把 portal (default profile skills/) cp 到 afu profile 本地副本 + byte-identical 验证
# 触发：每次 afu-customer-service skill 升版后手动执行
# 9 月初 P0 待办（T3）：替换为 verify_evolution.py 自动调用

set -e

PORTAL="$HOME/.hermes/skills/afu-customer-service/SKILL.md"
PROFILE="$HOME/.hermes/profiles/afu/skills/afu-customer-service/SKILL.md"

# Step 1 · HOME 检查（F1 防劫持）
if [ "$HOME" != "/Users/hua" ]; then
  echo "⚠️ F1 HOME 劫持检测：HOME=$HOME（应 = /Users/hua），立即修复"
  export HOME=/Users/hua
  echo "✅ 已 export HOME=/Users/hua"
fi

# Step 2 · 文件存在性检查
if [ ! -f "$PORTAL" ]; then
  echo "❌ portal 不存在：$PORTAL"
  exit 1
fi

if [ ! -f "$PROFILE" ]; then
  echo "❌ profile 本地副本不存在：$PROFILE"
  exit 1
fi

# Step 3 · 读取双端 version
PORTAL_VERSION=$(grep "^version:" "$PORTAL" | awk '{print $2}')
PROFILE_VERSION=$(grep "^version:" "$PROFILE" | awk '{print $2}')

echo "📋 portal version:  $PORTAL_VERSION"
echo "📋 profile version: $PROFILE_VERSION"

# Step 4 · 检查版本号一致性
if [ "$PORTAL_VERSION" != "$PROFILE_VERSION" ]; then
  echo "⚠️ 双端不同步：portal v$PORTAL_VERSION ≠ profile v$PROFILE_VERSION"
  echo "🔧 执行 cp 同步..."
  cp "$PORTAL" "$PROFILE"
  echo "✅ cp 完成"

  # 重新读取验证
  PROFILE_VERSION=$(grep "^version:" "$PROFILE" | awk '{print $2}')
  if [ "$PROFILE_VERSION" = "$PORTAL_VERSION" ]; then
    echo "✅ 同步后双端一致：v$PORTAL_VERSION"
  else
    echo "❌ cp 后仍不同步：portal v$PORTAL_VERSION ≠ profile v$PROFILE_VERSION"
    exit 1
  fi
else
  echo "✅ 双端已同步：v$PORTAL_VERSION"
fi

# Step 5 · byte-identical 验证（最终检查）
if diff -q "$PORTAL" "$PROFILE" > /dev/null 2>&1; then
  echo "✅ byte-identical 验证通过"
  echo ""
  echo "📊 文件统计："
  echo "  portal:  $(wc -l < "$PORTAL") 行 / $(wc -c < "$PORTAL") bytes"
  echo "  profile: $(wc -l < "$PROFILE") 行 / $(wc -c < "$PROFILE") bytes"
  exit 0
else
  echo "❌ byte-identical 验证失败：双端内容有差异"
  echo "🔍 diff 输出："
  diff "$PORTAL" "$PROFILE" | head -20
  exit 1
fi