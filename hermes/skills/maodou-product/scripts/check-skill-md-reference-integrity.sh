#!/usr/bin/env bash
# check-skill-md-reference-integrity.sh
# 用途: SKILL.md 引用完整性自检(陷阱 AC 配套脚本,2026-08-20_12 实测抽取)
# 触发: 每次心跳步骤 5「技能检查与同步」时,或 W3+ 启动门槛 5/5 自检时
# 防护: 始终用绝对路径(陷阱 AC.2 — $HOME 异常时 ~/.hermes/... 静默找错位置)

set -uo pipefail

SKILL_DIR="/Users/hua/.hermes/skills/maodou-product"
SKILL_MD="$SKILL_DIR/SKILL.md"
REFERENCES_DIR="$SKILL_DIR/references"

# 第 1 步: HOME 自检(陷阱 AC.2 防护)
echo "=== HOME 自检(陷阱 AC.2 防护)==="
echo "HOME=$HOME"
if [[ "$HOME" == "/Users/hua/.hermes/profiles/"* ]]; then
    echo "⚠️  警告: \$HOME 异常指向其他 profile home,可能导致路径解析错位"
    echo "   脚本继续使用绝对路径,绕开此问题"
fi
echo ""

# 第 2 步: 提取 SKILL.md 中所有 `references/...` 引用
echo "=== SKILL.md 中所有 references/... 引用 ==="
REFERENCES_IN_SKILL=$(grep -oE "references/[^\`\"]+" "$SKILL_MD" 2>/dev/null | sort -u)
if [[ -z "$REFERENCES_IN_SKILL" ]]; then
    echo "❌ 未找到任何 references/... 引用"
    exit 1
fi

# 过滤掉「§节形式引用」(同一文件内的 § 锚点不需要独立文件)
FILE_REFERENCES=$(echo "$REFERENCES_IN_SKILL" | grep -v "§" | sort -u)
SECTION_REFERENCES=$(echo "$REFERENCES_IN_SKILL" | grep "§" | sort -u)

FILE_COUNT=$(echo "$FILE_REFERENCES" | grep -c .)
SECTION_COUNT=$(echo "$SECTION_REFERENCES" | grep -c .)

echo "文件形式引用($FILE_COUNT):"
echo "$FILE_REFERENCES" | sed 's/^/  - /'
echo ""
echo "§节形式引用($SECTION_COUNT)(不检查,锚点):"
echo "$SECTION_REFERENCES" | sed 's/^/  - /'
echo ""

# 第 3 步: 列出 references/ 目录实际存在的文件
echo "=== references/ 目录实际文件(绝对路径)==="
ACTUAL_FILES=$(ls "$REFERENCES_DIR" 2>/dev/null | sort)
if [[ -z "$ACTUAL_FILES" ]]; then
    echo "❌ references/ 目录为空或不存在: $REFERENCES_DIR"
    exit 2
fi
ACTUAL_COUNT=$(echo "$ACTUAL_FILES" | grep -c .)
echo "$ACTUAL_FILES" | sed 's/^/  - /'
echo ""

# 第 4 步: 计算缺失文件(SKILL.md 引用了但实际未创建)
echo "=== 缺失 reference 文件清单(SKILL.md 引用 vs 实际存在)==="
MISSING=0
while IFS= read -r ref; do
    # ref 形如 "references/xxx.md" 或 "references/xxx.sh"
    FILENAME=$(basename "$ref")
    # 检查两种形式(直接文件 + 同名 .md 形式)
    if [[ ! -f "$REFERENCES_DIR/$FILENAME" ]]; then
        echo "  ❌ 缺失: $FILENAME (SKILL.md 引用形式: \`$ref\`)"
        MISSING=$((MISSING + 1))
    fi
done <<< "$FILE_REFERENCES"

echo ""
echo "=== 汇总 ==="
echo "SKILL.md 引用文件数: $FILE_COUNT"
echo "实际存在文件数: $ACTUAL_COUNT"
echo "缺失文件数: $MISSING"

# 退出码: 0 = 全部存在, 1 = 有缺失
if [[ $MISSING -gt 0 ]]; then
    echo ""
    echo "⚠️  W3+ 启动门槛 5/5 第 5 项判定:"
    echo "    缺失 ≥ 1 个 → ❌ 启动门槛未就绪"
    echo "    缺失 = 0    → ✅ 启动门槛就绪"
    exit 1
fi

echo ""
echo "✅ 全部引用文件已存在"
exit 0