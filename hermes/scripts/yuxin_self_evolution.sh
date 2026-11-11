#!/bin/bash
# 玉芬自进化守护 - 每 2 小时执行一次信号扫描 + 行动
# Windows 迁移版（2026-11-10）：KB 容器 yuxin-kb-db-1/yuxin_kb、内存用 ctypes、gateway 改端口探活
HERMES_HOME="${HERMES_HOME:-/d/yuxin/hermes}"
LOG="$HERMES_HOME/logs/yva-self-evolution.log"
STATE_DIR="$HERMES_HOME/state"
mkdir -p "$HERMES_HOME/logs" "$STATE_DIR"

PY="/c/Program Files/Python311/python.exe"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 玉芬自进化扫描开始 ===" | tee -a "$LOG"

# 1. KB 待复核积压（新版 schema：needs_review + archived，无 processing_status）
NEEDS_REVIEW=$(timeout 20 docker exec yuxin-kb-db-1 psql -U postgres -d yuxin_kb -t -c \
  "SELECT COUNT(*) FROM documents WHERE needs_review=true;" 2>/dev/null | tr -d ' \r' )
NEEDS_REVIEW="${NEEDS_REVIEW:-0}"
ARCHIVED=$(timeout 20 docker exec yuxin-kb-db-1 psql -U postgres -d yuxin_kb -t -c \
  "SELECT COUNT(*) FROM documents WHERE status='archived';" 2>/dev/null | tr -d ' \r' )
ARCHIVED="${ARCHIVED:-0}"
echo "[$(date '+%H:%M:%S')] KB 积压 needs_review=$NEEDS_REVIEW archived=$ARCHIVED" | tee -a "$LOG"

# 2. cron 失败
FAIL_CRON=$(hermes cron list 2>/dev/null | grep -c "error" || true)
echo "[$(date '+%H:%M:%S')] cron 失败任务数: $FAIL_CRON" | tee -a "$LOG"

# 3. Hermes Gateway 探活（端口 18888，2s 超时）
GW_OK=$("$PY" -c "
import urllib.request
try:
    urllib.request.urlopen('http://localhost:18888/health', timeout=2)
    print('up')
except Exception:
    print('down')
" 2>/dev/null)
echo "[$(date '+%H:%M:%S')] Hermes Gateway(18888): $GW_OK" | tee -a "$LOG"

# 4. 内存（ctypes GlobalMemoryStatusEx，KB 单位）
FREE_MEM_MB=$("$PY" -c "
import ctypes, ctypes.wintypes
class MS(ctypes.Structure):
    _fields_=[('dwLength',ctypes.wintypes.DWORD),('dwMemoryLoad',ctypes.wintypes.DWORD),
    ('ullTotalPhys',ctypes.c_ulonglong),('ullAvailPhys',ctypes.c_ulonglong),
    ('ullTotalPageFile',ctypes.c_ulonglong),('ullAvailPageFile',ctypes.c_ulonglong),
    ('ullTotalVirtual',ctypes.c_ulonglong),('ullAvailVirtual',ctypes.c_ulonglong),
    ('ullAvailExtendedVirtual',ctypes.c_ulonglong)]
m=MS(); m.dwLength=ctypes.sizeof(MS)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
print(int(m.ullAvailPhys//1048576))
" 2>/dev/null)
echo "[$(date '+%H:%M:%S')] 内存可用: ${FREE_MEM_MB:-?} MB" | tee -a "$LOG"

# 5. 写状态
cat > "$STATE_DIR/yva-self-evolution.json" <<EOF
{
  "ts": "$(date -Iseconds)",
  "kb_needs_review": ${NEEDS_REVIEW:-0},
  "kb_archived": ${ARCHIVED:-0},
  "cron_failed": ${FAIL_CRON:-0},
  "gateway_18888": "${GW_OK:-unknown}",
  "free_mem_mb": ${FREE_MEM_MB:-0}
}
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 扫描完成,状态已保存 ===" | tee -a "$LOG"

# 静默退出 (除非有需要立即处理的紧急情况)
exit 0
