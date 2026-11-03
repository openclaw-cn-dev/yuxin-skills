#!/usr/bin/env python3
"""RKR 重嵌入看门狗 — 异常告警 + 每 4 小时进度简报（正常静默，零 token）"""
import subprocess, json, time, os, sys

HOST = "root@121.43.127.211"
PASS = "Aa14472128+"
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.rkr_migration_watchdog_state")

def ssh(cmd):
    r = subprocess.run(
        ["sshpass", "-p", PASS, "ssh", "-o", "StrictHostKeyChecking=no",
         "-o", "ConnectTimeout=10", HOST, cmd],
        capture_output=True, text=True, timeout=40)
    return r.stdout.strip()

def main():
    # 查迁移 status
    raw = ssh("docker exec rkr-postgres psql -U rkr_user -d rkr_knowledge -t -A -c "
              "\"SELECT value FROM platform_settings WHERE key='embedding_migration_status'\"")
    if not raw:
        print("⚠️ RKR 重嵌入状态为空（未启动或异常清空）")
        return
    try:
        d = json.loads(raw)
    except Exception:
        print(f"⚠️ RKR 重嵌入 status 解析失败: {raw[:120]}")
        return

    total = d.get("total", 0)
    migrated = d.get("migrated", 0)
    failed = d.get("failed", 0)
    s = d.get("status", "")

    # 查迁移进程存活
    proc = ssh("ps aux | grep run_migration | grep -v grep | wc -l")

    if s == "completed":
        print(f"✅ RKR 重嵌入全部完成：migrated={migrated}/{total}，failed={failed}")
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        return
    if s == "error":
        print(f"🚨 RKR 重嵌入出错：{raw[:200]}")
        return
    if s == "running" and proc.strip() == "0":
        print(f"🚨 RKR 重嵌入进程已消失但状态 running：migrated={migrated}/{total}，failed={failed}")
        return

    # 正常运行中：每 4 小时输出一次进度简报
    now = time.time()
    last = 0.0
    if os.path.exists(STATE_FILE):
        try:
            last = float(open(STATE_FILE).read().strip())
        except Exception:
            last = 0.0
    if now - last >= 14400:
        pct = round(migrated * 100 / total, 1) if total else 0
        print(f"📊 RKR 重嵌入进度：migrated={migrated}/{total}（{pct}%），failed={failed}")
        with open(STATE_FILE, "w") as f:
            f.write(str(now))
    # 否则静默

if __name__ == "__main__":
    main()
