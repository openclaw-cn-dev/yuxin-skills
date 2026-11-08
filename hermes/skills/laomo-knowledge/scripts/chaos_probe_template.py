#!/usr/bin/env python3
"""
老莫 chaos-engineering probe template (R483 实战沉淀).
复制后修改 PROBES 列表即可用于任何 cron round 的稳态探活.

Usage:
    cp ~/.hermes/skills/laomo-knowledge/scripts/chaos_probe_template.py /tmp/test_chaos_probe_R<n>.py
    python3 /tmp/test_chaos_probe_R<n>.py

输出: ~/.hermes/profiles/laomo/evolution/chaos_probe_R<n>.json

Pitfall #78 防御: OpenAlex 探活必双端点, 默认 PROBES 已包含
- openalex_per_page (无 search 端点)
- openalex_search (有 search 端点)
两探针一致 UP 才能判 "OpenAlex 全 UP".

R<n> 改动 checklist:
1. 修改 PROBES 列表添加新探针 (e.g. 新加的 chromadb 8003 端口)
2. 必带 HOME=/Users/hua 前缀 (Pitfall #61 防御 a)
3. 跑完看 stdout up/down 计数, 落 JSON
4. 与上周 R<n-1> 的 chaos_probe JSON diff, 报警新增 DOWN 项

L1 manual (R483) → L2 scripted (R486+): 用 launchd / cron schedule 周自动跑.
"""
import subprocess
import time
import json
import os
from datetime import datetime, timezone, timedelta

# 老莫 cron mode HOME 污染防御 (Pitfall #61)
os.environ["HOME"] = "/Users/hua"

CST = timezone(timedelta(hours=8))

# 默认 11 探针 (R483 实测); R<n> 可加新探针 (L2 升级目标 20+)
PROBES = [
    ("docker_daemon",       "lsof /Users/hua/.docker/run/docker.sock"),
    ("openalex_per_page",   "curl -s -m 5 -o /dev/null -w '%{http_code}' https://api.openalex.org/works?per_page=1&mailto=laomo@yuxin.ai"),
    ("openalex_search",     "curl -s -m 5 -o /dev/null -w '%{http_code}' 'https://api.openalex.org/works?search=aquaculture%20recirculating&per_page=1&mailto=laomo@yuxin.ai'"),
    ("chromadb_8000",       "curl -s -m 3 -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/heartbeat"),
    ("chromadb_8001",       "curl -s -m 3 -o /dev/null -w '%{http_code}' http://localhost:8001/api/v1/heartbeat"),
    ("chromadb_8002",       "curl -s -m 3 -o /dev/null -w '%{http_code}' http://localhost:8002/api/v1/heartbeat"),
    ("hermes_gateway_8765", "curl -s -m 3 -o /dev/null -w '%{http_code}' http://localhost:8765/health"),
    ("cron_writer",         "launchctl list | grep com.hermes.writer.c6391079131e | awk '{print $1}' | head -1"),
    ("cron_lanmo",          "launchctl list | grep com.hermes.cron.laomo | awk '{print $1}' | head -1"),
    ("tasks_db_writable",   "python3 -c \"import sqlite3; sqlite3.connect('/Users/hua/.hermes/tasks.db').close(); print('OK')\""),
    ("rkr_staging_dir",     "ls /Users/hua/rkr_staging/ 2>&1 | head -1"),
    ("disk_space",          "df -h /Users/hua | tail -1 | awk '{print $5}'"),
]


def run_with_timeout(cmd, timeout=10):
    """单命令独立超时 (R144 第四态防御), 避免整脚本 hang."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"exit": r.returncode, "stdout": r.stdout.strip()[:200], "stderr": r.stderr.strip()[:200]}
    except subprocess.TimeoutExpired:
        return {"exit": -1, "stdout": "", "stderr": "TIMEOUT"}
    except Exception as e:
        return {"exit": -2, "stdout": "", "stderr": str(e)[:200]}


def classify(probe_name, result):
    """根据探针名判定 OK/DOWN. 不同探针 OK 标准不同."""
    exit_ok = result["exit"] == 0
    stdout = result["stdout"]
    if probe_name.startswith("chromadb") or probe_name.startswith("openalex") or probe_name.startswith("hermes_gateway"):
        return exit_ok and stdout in ("200", "OK")
    if probe_name == "tasks_db_writable":
        return stdout == "OK"
    if probe_name.startswith("cron_"):
        # cron_writer / cron_lanmo: launchctl list 有输出即视为 OK (PID 可能为空也算 scheduled)
        return exit_ok
    if probe_name == "docker_daemon":
        return exit_ok  # lsof 返 0 表示 socket 存在
    if probe_name == "rkr_staging_dir":
        return exit_ok and stdout != ""
    if probe_name == "disk_space":
        return exit_ok
    return exit_ok


def main():
    t0 = time.time()
    results = []
    ts = datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S CST")
    print(f"=== chaos probe @ {ts} ===")
    for name, cmd in PROBES:
        r = run_with_timeout(cmd)
        ok = classify(name, r)
        status = "UP " if ok else "DOWN"
        results.append({"probe": name, "ok": ok, **r})
        print(f"  {status} {name:22s} exit={r['exit']:3d} out={r['stdout'][:60]}")

    up_count = sum(1 for r in results if r["ok"])
    down_count = len(results) - up_count
    elapsed = time.time() - t0
    summary = {
        "ts": ts,
        "elapsed_sec": round(elapsed, 2),
        "up_count": up_count,
        "down_count": down_count,
        "results": results,
    }
    out_path = os.path.expanduser("~/.hermes/profiles/laomo/evolution/chaos_probe.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nUp: {up_count}/{len(results)}  Down: {down_count}/{len(results)}  Saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())