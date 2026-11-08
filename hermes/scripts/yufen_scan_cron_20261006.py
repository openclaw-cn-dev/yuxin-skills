#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""玉芬管理进化扫描 1/3: cron 健康 + 任务队列 + 调研增量 (合并脚本, 2026-10-06)"""
import json, os, glob, sqlite3, datetime, collections

NOW = datetime.datetime.now().astimezone()
OUT = []
P = OUT.append

# ============ PART 1: cron health ============
P("### PART1 cron health ###")
main_jobs_path = "/Users/hua/.hermes/cron/jobs.json"
all_jobs = []
sources = [("main", main_jobs_path)]
for pj in glob.glob("/Users/hua/.hermes/profiles/*/cron/jobs.json"):
    prof = pj.split("/profiles/")[1].split("/cron/")[0]
    sources.append((prof, pj))

for src, path in sources:
    try:
        with open(path) as f:
            data = json.load(f)
        jobs = data.get("jobs", data) if isinstance(data, dict) else data
        for j in jobs:
            j["_src"] = src
        all_jobs.extend(jobs)
    except Exception as e:
        P("ERR reading %s: %s" % (path, e))

P("total_jobs_all_sources=%d (main=%d)" % (
    len(all_jobs), len([j for j in all_jobs if j.get("_src") == "main"])))

enabled = [j for j in all_jobs if j.get("enabled")]
disabled = [j for j in all_jobs if not j.get("enabled")]
P("enabled=%d disabled=%d" % (len(enabled), len(disabled)))

# --- error jobs (enabled only, last_status=error) ---
P("--- error enabled jobs ---")
for j in enabled:
    if j.get("last_status") == "error":
        lr = j.get("last_run_at", "")
        le = (j.get("last_error") or "")[:220].replace("\n", " | ")
        P("ERR[%s] %s | last_run=%s | err=%s" % (j.get("_src"), j.get("name"), lr, le))

# --- error but disabled (for diff vs last round) ---
err_disabled = [j for j in disabled if j.get("last_status") == "error"]
P("disabled_with_error_count=%d" % len(err_disabled))

# --- paused > 7 days ---
P("--- paused>7d disabled jobs ---")
paused7d = []
for j in disabled:
    pt = j.get("paused_at")
    if not pt:
        continue
    try:
        pt_dt = datetime.datetime.fromisoformat(pt)
        days = (NOW - pt_dt).days
        if days > 7:
            paused7d.append((days, j.get("name"), j.get("_src"), pt[:10]))
    except Exception as e:
        P("ERR parse paused_at %s: %s" % (pt, e))
paused7d.sort(reverse=True)
for days, name, src, pt in paused7d:
    P("PAUSED %dd [%s] %s (paused_at=%s)" % (days, src, name, pt))
P("paused7d_total=%d" % len(paused7d))

# --- enabled jobs stale (last_run > 48h) ---
P("--- enabled last_run stale >48h ---")
for j in enabled:
    lr = j.get("last_run_at")
    if not lr:
        P("NEVER-RUN [%s] %s" % (j.get("_src"), j.get("name")))
        continue
    try:
        lr_dt = datetime.datetime.fromisoformat(lr)
        hrs = (NOW - lr_dt).total_seconds() / 3600
        if hrs > 48:
            P("STALE %.0fh [%s] %s last=%s" % (hrs, j.get("_src"), j.get("name"), lr[:16]))
    except Exception as e:
        P("ERR parse last_run %s: %s" % (lr, e))

# --- deliver chat_id census ---
P("--- deliver chat_id census ---")
chat_counter = collections.Counter()
for j in all_jobs:
    d = j.get("deliver") or ""
    if d.startswith("feishu:"):
        chat_counter[d.split(":", 1)[1]] += 1
    o = j.get("origin") or {}
    if isinstance(o, dict) and o.get("chat_id"):
        chat_counter[o["chat_id"]] += 1
for cid, cnt in chat_counter.most_common():
    P("CHAT %s x%d" % (cid, cnt))

# --- delivery errors ---
P("--- last_delivery_error jobs ---")
for j in all_jobs:
    de = j.get("last_delivery_error")
    if de:
        P("DELIV_ERR [%s] %s | %s" % (j.get("_src"), j.get("name"), str(de)[:150]))

# --- schedule expr census for rotation research line ---
P("--- rotation research jobs status ---")
rot_kw = ["轮换", "调研", "滚动", "research"]
for j in all_jobs:
    nm = j.get("name") or ""
    if any(k in nm for k in rot_kw) and j.get("_src") == "main":
        st = "ON" if j.get("enabled") else "OFF"
        P("ROT %s %s last=%s status=%s" % (st, nm, (j.get("last_run_at") or "")[:16], j.get("last_status")))

# ============ PART 2: task queue ============
P("### PART2 task queue ###")
NOWDT = datetime.datetime.now()
# kanban.db
try:
    con = sqlite3.connect("file:/Users/hua/.hermes/kanban.db?mode=ro", uri=True)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    P("kanban_tables=%s" % [r[0] for r in cur.fetchall()])
    try:
        cur.execute("SELECT id, title, status, priority, assignee, created_at, updated_at FROM tasks ORDER BY updated_at DESC")
        rows = cur.fetchall()
        P("kanban_tasks=%d" % len(rows))
        for r in rows:
            tid, title, status, prio, asg, ca, ua = r
            age_d = ""
            if ua:
                try:
                    ua_dt = datetime.datetime.fromtimestamp(ua) if isinstance(ua, (int, float)) else datetime.datetime.fromisoformat(str(ua))
                    age_d = "%.1fd" % ((NOWDT - ua_dt).total_seconds() / 86400)
                except Exception:
                    age_d = "?"
            P("KB id=%s [%s] prio=%s asg=%s upd=%s(%s) %s" % (tid, status, prio, asg, ua, age_d, str(title)[:60]))
    except Exception as e:
        P("kanban tasks query err: %s" % e)
    con.close()
except Exception as e:
    P("kanban.db err: %s" % e)

# tasks.db
try:
    con = sqlite3.connect("file:/Users/hua/.hermes/tasks.db?mode=ro", uri=True)
    cur = con.cursor()
    cur.execute("SELECT id, status, priority, assigned_to, created_at, updated_at, substr(description,1,80) FROM tasks ORDER BY updated_at DESC")
    rows = cur.fetchall()
    P("tasksdb_total=%d" % len(rows))
    for r in rows:
        tid, status, prio, asg, ca, ua, desc = r
        age_d = ""
        if ua:
            if isinstance(ua, (int, float)):
                ua_dt = datetime.datetime.fromtimestamp(ua)
            else:
                ua_dt = datetime.datetime.fromisoformat(str(ua))
            age_d = "%.1fd" % ((NOWDT - ua_dt).total_seconds() / 86400)
        P("TD id=%s [%s] prio=%s asg=%s upd=%s(%s) %s" % (tid, status, prio, asg, ua, age_d, str(desc)[:70]))
    con.close()
except Exception as e:
    P("tasks.db err: %s" % e)

# ============ PART 3: research increment (tokens by day) ============
P("### PART3 research increment ###")
try:
    con = sqlite3.connect("file:/Users/hua/.hermes/state.db?mode=ro", uri=True)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    P("state_tables=%s" % tables[:20])
    sess_tbl = None
    for t in tables:
        if "session" in t.lower():
            sess_tbl = t
            break
    if sess_tbl:
        cur.execute("PRAGMA table_info(%s)" % sess_tbl)
        cols = [r[1] for r in cur.fetchall()]
        P("sessions_cols=%s" % cols)
        # try common shape: created_at + input tokens
        tcol = "input_tokens" if "input_tokens" in cols else ("tokens_in" if "tokens_in" in cols else None)
        ccol = "created_at" if "created_at" in cols else None
        if tcol and ccol:
            for d in range(3, -1, -1):
                day = (NOWDT - datetime.timedelta(days=d)).strftime("%Y-%m-%d")
                cur.execute(
                    "SELECT COUNT(*), COALESCE(SUM(%s),0) FROM %s WHERE %s LIKE ?" % (tcol, sess_tbl, ccol),
                    (day + "%",))
                cnt, tok = cur.fetchone()
                P("DAY %s sessions=%d input_tokens=%d" % (day, cnt, tok))
    con.close()
except Exception as e:
    P("state.db err: %s" % e)

print("\n".join(OUT))
