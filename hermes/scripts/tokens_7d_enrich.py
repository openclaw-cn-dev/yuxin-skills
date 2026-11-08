#!/usr/bin/env python3
import sqlite3, os
from datetime import datetime, timedelta
from collections import defaultdict

HOME = "/Users/hua"
HERMES_HOME = os.path.join(HOME, ".hermes")

dbs = [("default", os.path.join(HERMES_HOME, "state.db"))]
profiles_dir = os.path.join(HERMES_HOME, "profiles")
if os.path.exists(profiles_dir):
    for p in sorted(os.listdir(profiles_dir)):
        if p == "default":
            continue
        db = os.path.join(profiles_dir, p, "state.db")
        if os.path.exists(db):
            dbs.append((p, db))

today = datetime.now()
since_ts = (today - timedelta(days=7)).timestamp()

agent_7d = defaultdict(int)
model_7d = defaultdict(int)
for agent, dbp in dbs:
    try:
        conn = sqlite3.connect(dbp)
        cur = conn.cursor()
        cur.execute("SELECT model, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, reasoning_tokens FROM sessions WHERE started_at IS NOT NULL AND started_at > ?", (since_ts,))
        for model, inp, out, cr, cw, reason in cur.fetchall():
            total = sum(x for x in (inp, out, cr, cw, reason) if x)
            if total <= 0:
                continue
            agent_7d[agent] += total
            m = (model or "unknown")
            if "deepseek" in m:
                m = "deepseek"
            elif "minimax" in m.lower():
                m = "minimax"
            elif "claude" in m.lower():
                m = "claude"
            elif "gpt" in m.lower():
                m = "gpt"
            elif "glm" in m.lower():
                m = "glm"
            elif "doubao" in m.lower():
                m = "doubao"
            else:
                m = m[:16]
            model_7d[m] += total
        conn.close()
    except Exception as e:
        pass

print("=== 7天 Top Agents ===")
for a, t in sorted(agent_7d.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {a}: {t/1e6:,.1f}M")
print("=== 7天 模型分布 ===")
total = sum(model_7d.values())
for m, t in sorted(model_7d.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {m}: {t/total*100:.0f}% ({t/1e6:,.1f}M)")
print("=== profiles ===")
for a, dbp in dbs:
    sz = os.path.getsize(dbp) / 1e9 if os.path.exists(dbp) else 0
    print(f"  {a}: {sz:.2f}GB")
