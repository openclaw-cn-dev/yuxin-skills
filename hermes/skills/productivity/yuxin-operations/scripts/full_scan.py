#!/usr/bin/env python3
"""玉芬每日管理进化扫描 — 一键跑第 1/3/4/5 项 (cron健康 / 任务队列 / 调研增量 / agent心跳)

用法: python3 full_scan.py [YYYY-MM-DD]   # 日期参数默认今天, 用于 state.db 当日大户查询

实测注意 (2026-09-29 固化):
- jobs.json 必须扫 root + 全部 profiles/*/cron/jobs.json (root 的 job.profile 字段多为 null,
  归属按文件域统计), 按 id 去重; 全量约 124 任务
- state.db sessions 表无 profile 列, user_id 多为 None → per-profile 心跳只能看 user_id 维度
- 全部 SQL 避免 || 字符串拼接 (触发 tirith:confusable_text 审批挂死), 用 printf()/多列
- kanban.db 表名是 tasks (列: id/title/assignee/status/priority)
"""
import json, sqlite3, os, glob, re, sys
from datetime import datetime, timezone, timedelta
from collections import Counter

tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
H = os.path.expanduser('~')
TODAY = sys.argv[1] if len(sys.argv) > 1 else now.strftime('%Y-%m-%d')
WEEK_AGO = (now - timedelta(days=7)).strftime('%Y-%m-%d')


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def age_str(dt):
    if not dt:
        return 'never'
    d = now - dt
    if d < timedelta(days=1):
        return f'{d.seconds // 3600}h ago'
    return f'{d.days}d ago'


# ---------- 1. CRON (全 profile 文件域, id 去重) ----------
def load_jobs():
    allj = []
    files = [f'{H}/.hermes/cron/jobs.json'] + sorted(glob.glob(f'{H}/.hermes/profiles/*/cron/jobs.json'))
    for f in files:
        prof = 'default' if f.endswith('/.hermes/cron/jobs.json') else f.split('/profiles/')[1].split('/')[0]
        try:
            for j in json.load(open(f)).get('jobs', []):
                j['_file_profile'] = prof
                allj.append(j)
        except Exception as e:
            print(f'WARN {f}: {e}')
    seen, out = set(), []
    for j in allj:
        if j.get('id') not in seen:
            seen.add(j.get('id'))
            out.append(j)
    return out


print('### 1. CRON HEALTH (文件域, id 去重) ###')
jobs = load_jobs()
enabled = [j for j in jobs if j.get('enabled')]
print(f'total={len(jobs)} enabled={len(enabled)} disabled={len(jobs) - len(enabled)}')
print('enabled_by_file_domain:', dict(Counter(j['_file_profile'] for j in enabled)))

print('\n-- stalled (enabled, next_run 超期 >24h) --')
for j in enabled:
    nr = parse_ts(j.get('next_run_at'))
    if nr and nr < now - timedelta(hours=24):
        lr = parse_ts(j.get('last_run_at'))
        lrs = lr.strftime('%m-%d %H:%M') if lr else 'never'
        print(f"  [{j['_file_profile']}] {j['name']} | last_run={lrs} | overdue {(now - nr).days}d")

print('\n-- error (enabled & last_status=error) --')
for j in enabled:
    if j.get('last_status') == 'error':
        print(f"  [{j['_file_profile']}] {j['name']} | last_run={age_str(parse_ts(j.get('last_run_at')))} | err={str(j.get('last_error'))[:120]}")

zn, rec = [], []
for j in jobs:
    if not j.get('enabled'):
        pa = parse_ts(j.get('paused_at'))
        if pa:
            (zn if (now - pa) > timedelta(days=7) else rec).append((j, pa))
print(f'\n-- zombies (disabled, paused>7d): {len(zn)} --')
print(f'-- 观察期 (paused<=7d): {len(rec)} --')
for j, pa in rec:
    print(f"  [{j['_file_profile']}] {j['name']} | paused {(now - pa).days}d ago ({pa.strftime('%m-%d')})")

cids = set()
for j in enabled:
    cids |= set(re.findall(r'oc_[a-f0-9]{8,}', json.dumps(j.get('deliver', '')) + str(j.get('origin', ''))))
print(f'\n-- deliver chat_ids (enabled, dedup): {len(cids)} --')
for c in sorted(cids):
    print(' ', c)

# ---------- 3. TASK QUEUE ----------
print('\n### 3. TASK QUEUE ###')
try:
    con = sqlite3.connect(f'{H}/.hermes/tasks.db')
    con.row_factory = sqlite3.Row
    rows = list(con.execute(
        "SELECT id,title,priority,status,assigned_to,updated_at FROM tasks "
        "WHERE status NOT IN ('done','cancelled','archived','completed') ORDER BY updated_at"))
    print(f'tasks.db open={len(rows)}')
    for r in rows:
        print(f"  id{r['id']} [{r['priority']}] {r['status']} owner={r['assigned_to']} "
              f"upd={r['updated_at']} | {str(r['title'])[:48]}")
    con.close()
except Exception as e:
    print('tasks.db error:', e)

try:
    con = sqlite3.connect(f'{H}/.hermes/kanban.db')
    con.row_factory = sqlite3.Row
    open_rows = [dict(r) for r in con.execute(
        "SELECT id,title,assignee,status,priority FROM tasks WHERE status IN ('pending','in_progress')")]
    print(f'kanban open={len(open_rows)}')
    for r in open_rows:
        print(f"  {str(r['id'])[:20]} [{r['priority']}] {r['status']} owner={r['assignee']} | {str(r['title'])[:44]}")
    con.close()
except Exception as e:
    print('kanban error:', e)

# ---------- 4 + 5. STATE.DB ----------
print(f'\n### 4. RESEARCH INCREMENT (cron sessions/day, since {WEEK_AGO}) ###')
try:
    con = sqlite3.connect(f'{H}/.hermes/state.db')
    cur = con.cursor()
    q = ("SELECT date(started_at,'unixepoch','localtime') d, COUNT(*), printf('%.1fM', SUM(input_tokens)/1e6) "
         "FROM sessions WHERE source='cron' AND started_at >= strftime('%s',?) GROUP BY d ORDER BY d")
    for d, c, tk in cur.execute(q, (WEEK_AGO,)):
        print(f'  {d}: {c} sessions, {tk} input')
    print(f'\n-- {TODAY} cron top sessions --')
    q2 = ('SELECT input_tokens + output_tokens, user_id, title FROM sessions '
          "WHERE source='cron' AND started_at >= strftime('%s',?) ORDER BY 1 DESC LIMIT 10")
    for tk, u, t in cur.execute(q2, (TODAY,)):
        print(f'  {tk:>9,} [{u}] {str(t)[:56]}')
    print('\n### 5. AGENT HEARTBEAT (per user_id; sessions 表无 profile 列) ###')
    latest = {}
    for u, s, ts in cur.execute('SELECT user_id, source, MAX(started_at) FROM sessions GROUP BY user_id, source'):
        latest.setdefault(u, []).append((s, ts))
    for u in sorted(latest, key=str):
        items = sorted(latest[u], key=lambda x: -x[1])[:2]
        parts = [f"{s}:{datetime.fromtimestamp(ts, tz).strftime('%m-%d %H:%M')}" for s, ts in items]
        print(f'  {u}: ' + ' | '.join(parts))
    con.close()
except Exception as e:
    print('state.db error:', e)
