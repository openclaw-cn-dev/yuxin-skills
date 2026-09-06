#!/usr/bin/env bash
# 老莫心跳 R 轮状态一键采集 (laomo-heartbeat skill)
# 用法: bash ~/.hermes/skills/laomo-heartbeat/scripts/status_probe.sh
# 覆盖 R 轮标准流程第 3 步全部采集项, 输出分节即 R 轮 entry 的状态素材。
set -u
DOCKER_SOCK="${DOCKER_SOCK:-/Users/hua/.docker/run/docker.sock}"
TASKS_DB="${TASKS_DB:-/Users/hua/.hermes/tasks.db}"

echo "=== daemon ping (200=UP) ==="
curl -s -o /dev/null -w "%{http_code}\n" --max-time 5 --unix-socket "$DOCKER_SOCK" http://localhost/_ping

echo "=== docker ps -a ==="
# R253 教训: cron session $HOME 可能被劫持到某 profile home (如实测 xiaobao), docker CLI 会静默解析
# <劫持HOME>/.docker/run/docker.sock 并返回【空列表】且无报错 — 空列表≠无容器≠daemon DOWN。
# 必须显式 DOCKER_HOST 绝对路径; 若 daemon ping=200 而 ps 输出为空, 一律视为假象并告警。
export DOCKER_HOST="unix://${DOCKER_SOCK}"
ps_out="$(docker ps -a --format '{{.Names}}\t{{.Status}}' 2>&1 | sort)"
if [ -z "$ps_out" ]; then
  echo "(⚠️ docker ps 输出为空 — 若上方 daemon ping=200, 这是 HOME 劫持/DOCKER_HOST 假象, 空列表≠无容器; 核对 DOCKER_SOCK=$DOCKER_SOCK 是否存在)"
else
  echo "$ps_out"
fi

echo "=== port probes ==="
for p in "18888/health" "11434/api/version" "8000/api/health" "5173"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://localhost:${p}" 2>/dev/null)
  echo ":${p} = ${code}"
done

echo "=== :8006 multi-endpoint (R248 防御: / 与 /api/health=200 但 /openapi.json 与 /docs=404 ⇒ SPA DevPlan 占端口, 非真 uvicorn API) ==="
for ep in "/" "/api/health" "/openapi.json" "/docs"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://localhost:8006${ep}" 2>/dev/null)
  echo "8006${ep} = ${code}"
done

echo "=== msg GW launchctl (ai.hermes.gateway-laomo 缺失 = R178+ 已知阻塞) ==="
launchctl list 2>/dev/null | grep -i -E "hermes|gateway|laomo" || echo "(no matches)"

echo "=== .env fingerprints (R240 方法论: python 全变量名 regex, bash grep 输出会被净化层改写不可信) ==="
python3 - <<'PY'
import re, hashlib, os
paths = ["/Users/hua/.hermes/.env", "/Users/hua/.hermes/profiles/laomo/.env"]
seen = set()
for p in paths:
    if p in seen or not os.path.exists(p):
        continue
    seen.add(p)
    try:
        txt = open(p, encoding="utf-8", errors="ignore").read()
    except Exception as e:
        print(p, "READ_ERR", e); continue
    m = re.search(r"^VOLC_ARK_API_KEY\s*=\s*(\S+)", txt, re.M)
    if m:
        k = m.group(1).strip().strip('"').strip("'")
        print(f"{p}: LEN={len(k)} prefix={k[:12]} md5={hashlib.md5(k.encode()).hexdigest()[:8]}")
    else:
        print(f"{p}: NO VOLC_ARK_API_KEY")
PY

echo "=== desc size & last_r (chars 口径, R237 教训: bytes 会 ~1.4x 膨胀) ==="
python3 - "$TASKS_DB" <<'PY'
import sqlite3, re, sys
row = sqlite3.connect(sys.argv[1]).execute("SELECT description FROM tasks WHERE id=11").fetchone()
if not row:
    print("task #11 not found"); sys.exit(1)
desc = row[0]
rs = re.findall(r"\[R(\d+)", desc)
print(f"chars: {len(desc)} = {len(desc)/1024:.1f} KB chars | last_r: {rs[-1] if rs else '-'} | entries: {len(rs)} | range: {rs[0] if rs else '-'}..{rs[-1] if rs else '-'}")
PY
