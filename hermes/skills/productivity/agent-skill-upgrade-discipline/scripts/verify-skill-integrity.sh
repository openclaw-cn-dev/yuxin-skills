#!/bin/bash
# verify-skill-integrity.sh
# 配套 ***SECRET*** §14(2026-08-25 新增)
# 用法: ./verify-skill-integrity.sh <profile> <skill-name>
# 示例: ./verify-skill-integrity.sh afu afu-customer-service
# 退出码: 0 = 全部 5 项通过 / 1 = 有失败项
#
# 5 项检查:
#   [1] frontmatter version 字段与 changelog 最新条目一致
#   [2] changelog 版本号无重复
#   [3] changelog 同日期条目 ≤ 1
#   [4] 三方版本号一致(主索引 + 顶层 portal + 分支 skill)
#   [5] changelog 版本号单调递增(无跳跃)
#
# 2026-08-25 阿福 cron 实证:
#   8/25 04:00 用老 verify-three-end-version.sh 返回 ✅
#   但顶层门户 changelog 实际有 v1.37.0/v1.38.0 同日期双条目
#   新脚本的检查 [3] 会立即报错

set -e

PROFILE="${1:?用法: $0 <profile> <skill-name>}"
SKILL="${2:?用法: $0 <profile> <skill-name>}"

PROFILE_DIR="/Users/hua/.hermes/profiles/${PROFILE}/skills"
TARGET="${PROFILE_DIR}/${SKILL}/SKILL.md"

if [ ! -f "$TARGET" ]; then
  echo "❌ 顶层 SKILL.md 不存在: $TARGET"
  exit 1
fi

echo "=== ${PROFILE}/${SKILL} 完整性核验 ==="

PASS=true

# ---- 检查 [1]: frontmatter version 与 changelog 最新条目一致 ----
FM_VERSION=$(grep -m1 '^version:' "$TARGET" | awk '{print $2}' | tr -d "'\"" | tr -d 'v')
echo ""
echo "  [1] frontmatter ↔ changelog 一致性"
echo "      frontmatter version: v${FM_VERSION}"

CL_LATEST=$(grep -E '^\s*-\s+["'"'"']?[0-9]+\.[0-9]+\.[0-9]+' "$TARGET" | head -1 | \
            grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
echo "      changelog 最新条目: v${CL_LATEST}"

if [ "$FM_VERSION" = "$CL_LATEST" ]; then
  echo "      ✅ 通过"
else
  echo "      ❌ 失败: frontmatter v${FM_VERSION} ≠ changelog v${CL_LATEST}"
  PASS=false
fi

# ---- 检查 [2]: changelog 无重复版本号 ----
echo ""
echo "  [2] changelog 版本号无重复"
DUPES=$(grep -oE '[0-9]+\.[0-9]+\.[0-9]+' "$TARGET" | sort | uniq -d)
if [ -z "$DUPES" ]; then
  echo "      ✅ 通过: 无重复版本号"
else
  echo "      ❌ 失败: 重复版本号: $DUPES"
  PASS=false
fi

# ---- 检查 [3]: 同日期条目 ≤ 1 ----
echo ""
echo "  [3] changelog 重复日期检查"
DUP_DATES=$(grep -oE '\(20[0-9]{2}-[0-9]{2}-[0-9]{2}\)' "$TARGET" | sort | uniq -c | awk '$1>1{print}')
if [ -z "$DUP_DATES" ]; then
  echo "      ✅ 通过: 无重复日期条目"
else
  echo "      ❌ 失败: 同日期多条目:"
  echo "$DUP_DATES" | sed 's/^/         /'
  echo "      💡 修复: 合并为单条目,或加 (上午/下午/晚上) 时间后缀"
  PASS=false
fi

# ---- 检查 [4]: 三方版本号一致 ----
echo ""
echo "  [4] 三方版本号一致(主索引 + 顶层 portal)"
INDEX_FILE="${PROFILE_DIR}/productivity/${SKILL}/SKILL.md"
if [ -f "$INDEX_FILE" ]; then
  INDEX_V=$(grep -m1 '^version:' "$INDEX_FILE" | awk '{print $2}' | tr -d "'\"" | tr -d 'v')
  if [ "$INDEX_V" = "$FM_VERSION" ]; then
    echo "      ✅ 通过: 主索引 v${INDEX_V} == 顶层 v${FM_VERSION}"
  else
    echo "      ❌ 失败: 主索引 v${INDEX_V} ≠ 顶层 v${FM_VERSION}"
    PASS=false
  fi
else
  echo "      ⚠️ 主索引不存在,跳过(§13)"
fi

# ---- 检查 [5]: changelog 版本号单调递增 ----
echo ""
echo "  [5] changelog 版本号单调性(从最早到最新)"
# 提取 changelog 段的所有版本号(按文件顺序)
ALL_VERSIONS=$(awk '/^changelog:/{flag=1; next} flag && /^[a-zA-Z]/{flag=0} flag' "$TARGET" | \
               grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
PREV=""
VIOLATIONS=""
while IFS= read -r v; do
  if [ -n "$PREV" ]; then
    # 比较 v >= PREV(用 sort -V)
    if ! printf "%s\n%s\n" "$PREV" "$v" | sort -V -C; then
      VIOLATIONS="${VIOLATIONS} ${PREV}→${v}"
    fi
  fi
  PREV="$v"
done <<< "$ALL_VERSIONS"

if [ -z "$VIOLATIONS" ]; then
  echo "      ✅ 通过: 版本号单调递增"
else
  echo "      ❌ 失败: 版本号跳跃:$VIOLATIONS"
  PASS=false
fi

echo ""
if $PASS; then
  echo "=== ✅ 全部 5 项通过 ==="
  exit 0
else
  echo "=== ❌ 有失败项,必须修复后再提交 ==="
  exit 1
fi
