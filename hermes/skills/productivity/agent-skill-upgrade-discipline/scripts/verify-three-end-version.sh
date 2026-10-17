#!/bin/bash
# verify-three-end-version.sh
# 用法: ./verify-three-end-version.sh <profile> <umbrella-skill-name>
# 示例: ./verify-three-end-version.sh afu afu-customer-service
# 输出: 三处 version + 一致性布尔值
# 退出码: 0 = 三方一致; 1 = 有漂移

set -e

PROFILE="${1:?用法: $0 <profile> <umbrella-skill-name>}"
UMBRELLA="${2:?用法: $0 <profile> <umbrella-skill-name>}"

PROFILE_DIR="/Users/hua/.hermes/profiles/${PROFILE}/skills"
FILES=(
  "${PROFILE_DIR}/productivity/${UMBRELLA}/SKILL.md"
  "${PROFILE_DIR}/${UMBRELLA}/SKILL.md"
)

echo "=== ${PROFILE}/${UMBRELLA} 三处版本号 ==="
VERSIONS=()
for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    v=$(grep -m1 '^version:' "$f" | awk '{print $2}')
    echo "$(basename $(dirname "$f"))/SKILL.md → v${v}"
    VERSIONS+=("$v")
  else
    echo "⚠️ 缺失: $f"
    VERSIONS+=("MISSING")
  fi
done

# 三方一致性判定
if [ "${VERSIONS[0]}" == "${VERSIONS[1]}" ] && [ "${VERSIONS[0]}" != "MISSING" ]; then
  echo "✅ 三方一致: v${VERSIONS[0]}"
  exit 0
else
  echo "❌ 三方不一致: ${VERSIONS[*]}"
  exit 1
fi
