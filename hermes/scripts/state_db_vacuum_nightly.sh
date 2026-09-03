#!/bin/bash
# state.db 夜间安全瘦身 — VACUUM INTO 备份 → 校验 → 原子换库 → 重启gateway → 验证
# 失败自动回滚。日志: ~/.hermes/logs/state_db_vacuum.log
set -u
LOG=/Users/hua/.hermes/logs/state_db_vacuum.log
TS=$(date +%Y%m%d_%H%M%S)
BKDIR=/Users/hua/.hermes/backups
mkdir -p "$BKDIR"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

vacuum_one() {
  local DB="$1" GW="$2"
  local NAME=$(basename $(dirname "$DB"))
  log "==== 开始 $NAME ===="
  [ -f "$DB" ] || { log "跳过 $NAME: 库不存在"; return; }
  local BEFORE=$(stat -f%z "$DB")

  # 1. VACUUM INTO 产出压缩副本（同时就是备份）
  local VAC="$BKDIR/state-$NAME-vacuumed-$TS.db"
  if ! sqlite3 "$DB" "VACUUM INTO '$VAC';" >>"$LOG" 2>&1; then
    log "❌ $NAME VACUUM INTO 失败，放弃(原库未动)"; rm -f "$VAC"; return
  fi
  # 2. 完整性校验
  local CHK=$(sqlite3 "$VAC" "PRAGMA integrity_check;" 2>&1)
  if [ "$CHK" != "ok" ]; then
    log "❌ $NAME 副本 integrity_check=$CHK，放弃(原库未动)"; rm -f "$VAC"; return
  fi
  local AFTER_VAC=$(stat -f%z "$VAC")
  # 3. 消息数一致性抽查
  local C1=$(sqlite3 "$DB" "SELECT COUNT(*) FROM messages;" 2>/dev/null)
  local C2=$(sqlite3 "$VAC" "SELECT COUNT(*) FROM messages;" 2>/dev/null)
  if [ "$C1" != "$C2" ]; then
    log "❌ $NAME 消息数不一致($C1 vs $C2)，放弃(原库未动)"; rm -f "$VAC"; return
  fi
  # 4. 原子换库
  mv "$DB" "$DB.old-$TS" && mv "$VAC" "$DB" && rm -f "$DB-wal" "$DB-shm"
  # 5. 重启 gateway（如有）
  if [ -n "$GW" ]; then
    launchctl kickstart -k "gui/$(id -u)/$GW" >>"$LOG" 2>&1 \
      && log "$NAME gateway 已重启" || log "⚠️ $NAME gateway 重启指令失败(可能未安装)"
  fi
  sleep 5
  # 6. 换库后可读性验证
  local V=$(sqlite3 "$DB" "SELECT COUNT(*) FROM sessions;" 2>&1)
  case "$V" in
    ''|*[!0-9]*)
      log "❌ $NAME 换库后验证失败($V)，自动回滚"
      mv "$DB" "$DB.broken-$TS"; mv "$DB.old-$TS" "$DB"
      [ -n "$GW" ] && launchctl kickstart -k "gui/$(id -u)/$GW" >>"$LOG" 2>&1
      return ;;
    *) log "✅ $NAME 完成: $(echo $BEFORE | awk '{printf "%.1fG",$1/1073741824}') → $(echo $AFTER_VAC | awk '{printf "%.1fG",$1/1073741824}') sessions=$V" ;;
  esac
  # 7. 旧库保留 7 天后由下次运行清理
  find "$BKDIR" "$HOME/.hermes" -maxdepth 1 -name "*.old-*" -mtime +7 -delete 2>/dev/null
  find "$BKDIR" -name "state-*-vacuumed-*.db" -mtime +14 -delete 2>/dev/null
}

# 三个有 gateway 的主力库（其余 profile 库小，暂不动）
vacuum_one /Users/hua/.hermes/state.db "ai.hermes.gateway-default"
sleep 20
vacuum_one /Users/hua/.hermes/profiles/zhenglishi/state.db "ai.hermes.gateway-zhenglishi"
sleep 20
vacuum_one /Users/hua/.hermes/profiles/quant/state.db "ai.hermes.gateway-quant"

log "==== 全部结束 ===="
df -h /System/Volumes/Data | awk 'NR==2{print "磁盘可用: "$4}' | tee -a "$LOG"
