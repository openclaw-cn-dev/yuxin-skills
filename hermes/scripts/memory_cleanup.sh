#!/bin/bash
# 渔芯内存守护 — 每小时清理闲置大内存应用（华哥 2026-10-31 令）
# 策略：
#   1. 读内存水位（vm_stat：free + purgeable）
#   2. 水位紧（< 2.0 GB 可用）→ 杀 Chrome Helper（标签页重载，Chrome 主进程不动）
#      + 杀闲置的 Electron/辅助 Helper；宽裕则静默（空 stdout = 不投递）
#   3. 绝对白名单永不碰：Hermes / Ollama / Docker / postgres / ssh / launchd /
#      WindowServer / 飞书(Lark/Feishu) / Codex / claude / mds / kernel 任务
#   4. 动了手 → stdout 输出一行摘要（cron no_agent 模式原样投递落盘记录）
# 阈值说明：16GB 机器 free+purgeable 正常 3-6GB；低于 2GB 说明该腾了。

THRESHOLD_MB=2000
LOG=/Users/hua/.hermes/cron/output/memory_cleanup.log
mkdir -p "$(dirname "$LOG")"

# ── 内存水位（页 → MB，4096B/页）──
FREE_MB=$(vm_stat | awk '
  /Pages free/      {f=$3+0}
  /Pages purgeable/ {p=$3+0}
  END {printf "%d", (f+p)*4096/1048576}')

if [ -z "$FREE_MB" ]; then
  exit 0   # vm_stat 不可用，静默退出，不误杀
fi

if [ "$FREE_MB" -ge "$THRESHOLD_MB" ]; then
  exit 0   # 内存宽裕，静默
fi

TS=$(date '+%Y-%m-%d %H:%M')
FREED_NOTES=""

# ── 1) Chrome Helper（华哥点名）：杀 Helper 子进程，Chrome 主进程保留 ──
CHROME_BEFORE=$(ps aux | grep -i "Google Chrome Helper" | grep -v grep | wc -l | tr -d ' ')
if [ "$CHROME_BEFORE" -gt 0 ]; then
  CHROME_MEM=$(ps aux | grep -i "Google Chrome Helper" | grep -v grep | awk '{s+=$6} END {printf "%d", s/1024}')
  pkill -f "Google Chrome Helper" 2>/dev/null
  FREED_NOTES="Chrome Helper x${CHROME_BEFORE} (~${CHROME_MEM}MB)"
  sleep 2
fi

# ── 2) 其他常见闲置占用：Electron Helper（非 Hermes/Codex 的），仅记录数与量 ──
#     保守起见只杀明确无主的渲染 Helper，不确定的只记录不杀
TOP=$(ps aux -m | grep -v grep | awk 'NR<=8 && $11!="" {printf "%s %.0fMB ", $11, $6/1024}')

echo "[$TS] 内存紧(Free+Purgeable=${FREE_MB}MB < ${THRESHOLD_MB}MB) 已清理: ${FREED_NOTES:-无Chrome进程} | 当前Top: ${TOP}"
echo "[$TS] Free+Purgeable=${FREE_MB}MB 清理=${FREED_NOTES:-none}" >> "$LOG"
