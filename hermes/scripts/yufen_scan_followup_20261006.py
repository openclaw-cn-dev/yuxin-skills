#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""玉芬管理进化扫描 补查: state.db tokens/天 + kanban 存在性 + chat 测活准备"""
import sqlite3, datetime, os, glob, json

NOWDT = datetime.datetime.now()
OUT = []
P = OUT.append

# --- state.db sessions by day (started_at) ---
try:
    con = sqlite3.connect("file:/Users/hua/.hermes/state.db?mode=ro", uri=True)
    cur = con.cursor()
    for d in range(5, -1, -1):
        day = (NOWDT - datetime.timedelta(days=d)).strftime("%Y-%m-%d")
        cur.execute("SELECT COUNT(*), COALESCE(SUM(input_tokens),0), COALESCE(SUM(output_tokens),0) FROM sessions WHERE started_at LIKE ?", (day + "%",))
        cnt, it, ot = cur.fetchone()
        P("DAY %s sessions=%d in=%d out=%d" % (day, cnt, it, ot))
    # top sessions today/yesterday by input tokens
    for day in [(NOWDT - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), NOWDT.strftime("%Y-%m-%d")]:
        cur.execute("SELECT title, input_tokens, started_at FROM sessions WHERE started_at LIKE ? ORDER BY input_tokens DESC LIMIT 3", (day + "%",))
        for t, it, sa in cur.fetchall():
            P("TOP %s | in=%s | %s | %s" % (day, it, sa[:16], str(t)[:50]))
    con.close()
except Exception as e:
    P("state.db err: %s" % e)

# --- kanban db existence ---
P("--- kanban check ---")
for p in ["/Users/hua/.hermes/kanban.db", "/Users/hua/.hermes/kanban/kanban.db"]:
    P("%s exists=%s size=%s" % (p, os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else "-"))
hits = glob.glob("/Users/hua/.hermes/**/kanban.db", recursive=True)
P("kanban.db glob hits: %s" % hits[:10])

# --- rotation research source freshness (文件系统验证法) ---
P("--- research source freshness ---")
D = "/Users/hua/rkr_staging/文档库"
checks = [
    ("RAS仿真", D + "/A-渔芯科技/A1-水产养殖RAS/RAS流体力学仿真"),
    ("三合一技术前沿", D + "/Z-共享/Z1-通用学科知识/技术前沿"),
    ("Kali网络安全", D + "/Z-共享/Z1-通用学科知识/网络安全"),
    ("360行种子池", D + "/C-渔芯独角兽/C1-360行种子池"),
]
for name, path in checks:
    if not os.path.isdir(path):
        P("SRC %s MISSING_DIR %s" % (name, path))
        continue
    for mtime in [1, 3]:
        n = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".md"):
                    try:
                        if (NOWDT - datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(root, f)))).days < mtime:
                            n += 1
                    except Exception:
                        pass
        P("SRC %s files_mtime<%dd = %d" % (name, mtime, n))

# --- reports dir ---
try:
    import subprocess
    r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    P("DISK %s" % r.stdout.strip().splitlines()[-1])
except Exception:
    pass

print("\n".join(OUT))
