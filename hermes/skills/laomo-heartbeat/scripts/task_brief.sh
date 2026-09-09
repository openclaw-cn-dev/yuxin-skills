#!/usr/bin/env bash
# task_brief.sh — task #11 安全详情查询 (Pitfall: SELECT * 全量 dump description)
#
# 根因: tasks.db task #11 的 description 是 ~45KB 的 R 轮次追踪日志,
#       开场 triage 若用 `SELECT * FROM tasks WHERE id=11` 会把 ~45KB 吞进 context 窗口。
#       该违规在 R 日志累计记录 6+ 次 (R315/R323/R325/R326/R328/R330),
#       根因同族: "违规总发生在读到规则之前" — 防线必须是脚本, 不能只靠纪律。
#
# 用法:
#   bash task_brief.sh              # 安全行 + desc 统计 + 尾部 1200 chars
#   bash task_brief.sh 3000         # 尾部切片加长
#
# 铁律: 任何 sqlite 查询的 SELECT 列表一律不含 description;
#       desc 详情只走本脚本 / status_probe.sh / substr() 尾部切片三通道。
set -euo pipefail
DB="${TASKS_DB:-/Users/hua/.hermes/tasks.db}"
TAIL="${1:-1200}"

echo "=== 老莫 pending/in_progress 任务 (SELECT 列表不含 description) ==="
sqlite3 "$DB" "SELECT id||'|'||title||'|'||priority||'|'||status FROM tasks WHERE assigned_to='老莫' AND status IN ('pending','in_progress') ORDER BY CASE priority WHEN 'P0' THEN 0 WHEN 'P1' THEN 1 ELSE 2 END;"

echo "=== desc 统计 (chars 口径, R237 教训: bytes 会 ~1.4x 膨胀) ==="
sqlite3 "$DB" "SELECT 'chars='||length(description) FROM tasks WHERE id=11;"

echo "=== last R 编号 (从尾部 80 chars 提取) ==="
sqlite3 "$DB" "SELECT substr(description, -80) FROM tasks WHERE id=11;" | grep -o 'R[0-9]\+' | tail -1

echo "=== desc 尾部切片 (last ${TAIL} chars) ==="
sqlite3 "$DB" "SELECT substr(description, -${TAIL}) FROM tasks WHERE id=11;"
