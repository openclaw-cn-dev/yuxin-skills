#!/bin/bash
# 黑豆 self-evolve cron · 下次 cron 启动自检脚本(沿用 9-6 16 时档首测)
# 用途:在周日/周末收口档出"bin/<date>_cron_startup_v1.0.sh",供下周一/下个关键时刻
#      cron 启动时 30 秒完成 §0 五确认 + 必带件 N 件校验 + 启动路径连通性自检。
# 触发条件:沿用 heidou-self-evolve-cron SKILL §0 步骤 F(骨架→实体检测)的延伸——
#      任何"下个 cron 节点必到"的关键时刻(周一衔接 / 整合窗口 / 月末 / 季末 / 重大 deadline 前 N 天)
#      都应在上一档出本类自检脚本,下档直接执行。
# 沿用:坑 #AH 周末高频出档防护 + 坑 #AI 索引卡 v1.x 升级模式 + 9-6 16 时档实测。

# === 模板参数(实际生成时按目标时刻替换) ===
# TARGET_LABEL="9-7 周一早 cron"
# REQUIRED_FILES=(
#   "memory/sop/<必带件 1>_v<x>_<date>.md"
#   "memory/sop/<必带件 2>_v<x>_<date>.md"
#   ...
# )
# PROFILE_BASE="/Users/hua/.hermes/profiles/heidou"
# CHECK_CANBAN_SQL="SELECT COUNT(*) FROM tasks WHERE assignee='黑豆' AND status IN ('pending','in_progress')"

set -euo pipefail

# === 0. 30 秒启动横幅 ===
echo "============================================"
echo " ${TARGET_LABEL:-下次 cron} 启动自检 v1.0"
echo " 维护:黑豆 · 沿用 heidou-self-evolve-cron SKILL"
echo " 出档时间:$(date '+%Y-%m-%d %H:%M')"
echo "============================================"
echo ""

# === 1. HOME 漂移自检(沿用坑 #G) ===
echo "[Step 1/5] HOME 漂移自检:"
echo "  HOME=$HOME"
if [ "${HOME}" = "/Users/hua" ]; then
    echo "  ✅ HOME 正常"
else
    echo "  ⚠️ HOME 漂移(目标 /Users/hua,实际 $HOME)"
    echo "  应对:本自检后续全程用绝对路径,不依赖 \$HOME"
fi
echo ""

# === 2. heartbeat 空任务自检(沿用 SKILL §0 步骤 B) ===
echo "[Step 2/5] heartbeat 自检:"
HEARTBEAT_OUT=$(python3 ~/.hermes/scripts/heartbeat_check.py 黑豆 2>&1 || echo "ERROR")
HEARTBEAT_EXIT=$?
if [ "$HEARTBEAT_EXIT" = "0" ] && [ -z "$HEARTBEAT_OUT" ]; then
    echo "  ✅ heartbeat 空 + exit 0(真无任务)"
elif [ "$HEARTBEAT_EXIT" = "0" ]; then
    echo "  ⚠️ heartbeat exit 0 但有 stdout: $HEARTBEAT_OUT"
    echo "  应对:沿用 SKILL §0 步骤 C 二次验证 kanban.db"
else
    echo "  ❌ heartbeat 异常 exit=$HEARTBEAT_EXIT: $HEARTBEAT_OUT"
fi
echo ""

# === 3. kanban.db 直查(沿用坑 #Q + SKILL §0 步骤 C) ===
echo "[Step 3/5] kanban.db 黑豆待办直查:"
KANBAN_PATH="${PROFILE_BASE:-/Users/hua/.hermes/profiles/heidou}/kanban.db"
TASK_COUNT=$(sqlite3 "$KANBAN_PATH" "${CHECK_CANBAN_SQL:-SELECT COUNT(*) FROM tasks WHERE assignee='黑豆' AND status IN ('pending','in_progress')}" 2>/dev/null || echo "ERR")
echo "  黑豆待办 = $TASK_COUNT"
if [ "$TASK_COUNT" = "0" ]; then
    echo "  ✅ 无任务,可继续自检"
elif [ "$TASK_COUNT" = "ERR" ]; then
    echo "  ⚠️ sqlite3 查询失败(检查 KANBAN_PATH + SQL)"
else
    echo "  ⚠️ 有 $TASK_COUNT 件待办,先交付任务再回自检"
fi
echo ""

# === 4. 必带件 N 件校验(沿用 SKILL §0 步骤 F + 周末收口卡 §X 必带件清单) ===
echo "[Step 4/5] 必带件校验(${#REQUIRED_FILES[@]:-0} 件):"
MISSING=0
if [ "${#REQUIRED_FILES[@]:-0}" -gt 0 ]; then
    for FILE in "${REQUIRED_FILES[@]}"; do
        FULLPATH="${PROFILE_BASE:-/Users/hua/.hermes/profiles/heidou}/$FILE"
        if [ -f "$FULLPATH" ]; then
            SIZE=$(wc -c < "$FULLPATH")
            echo "  ✅ $FILE ($SIZE bytes)"
        else
            echo "  ❌ MISSING: $FILE"
            MISSING=$((MISSING+1))
        fi
    done
else
    echo "  (无 REQUIRED_FILES 配置 — 模板未实例化)"
fi

if [ "$MISSING" -gt 0 ]; then
    echo ""
    echo "  ❌ $MISSING 件必带件缺失,启动失败"
    exit 3
fi
echo ""

# === 5. 沿用预演字段定义 + 必出 N 件清单 ===
echo "[Step 5/5] 沿用预演 + 必出 N 件:"
echo "  (沿用 SKILL §0 五确认 + §三 周末收口卡 §X 字段定义)"
echo "  必出 N 件清单:"
echo "    1. evolution/<date>_<HH>.md"
echo "    2. memory/sop/<必出件 1>_v<x>_<date>.md"
echo "    3. ..."
echo "    N. 飞书通知玉芬: <时刻> 黑豆到达 + 已带 N 件"
echo ""

echo "============================================"
echo " ✅ ${TARGET_LABEL:-下次 cron} 启动自检 v1.0 执行完毕"
echo " 下一步:按预演 §X ~ §Y 填实衔接卡实体"
echo "============================================"
