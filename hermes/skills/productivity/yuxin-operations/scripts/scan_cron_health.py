#!/usr/bin/env python3
"""管理进化扫描 #1:cron 健康扫描(全局 + 9 profile,去重)。

用法: python3 scan_cron_health.py
输出: 总数/停摆/error/停用>7d/deliver 分布,直接可贴进日报。
口径来源: 2026-09-17 实测(112 job 去重、停摆判定 >24h 超期、(profile,id) 去重)。
"""
import glob
import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)

PATHS = ['/Users/hua/.hermes/cron/jobs.json'] + glob.glob(
    '/Users/hua/.hermes/profiles/*/cron/jobs.json')


def parse_ts(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s))
        return d if d.tzinfo else d.replace(tzinfo=TZ)
    except ValueError:
        return None


all_jobs = {}  # (profile, id) -> job  (dedup: 双读重复计数 Pitfall)
for path in PATHS:
    pf = 'default' if '/profiles/' not in path else path.split('/profiles/')[1].split('/')[0]
    try:
        data = json.load(open(path))
        for j in data.get('jobs', []):
            all_jobs[(pf, j.get('id'))] = j
    except Exception as e:
        print(f"ERR reading {path}: {e}")

enabled = {k: v for k, v in all_jobs.items() if v.get('enabled')}
print(f"=== TOTAL unique: {len(all_jobs)} | enabled: {len(enabled)} ===")

# --- stalled: enabled 但 next_run 超期 >24h(停摆可自愈,每轮重核) ---
print("\n--- [STALL] enabled, next_run >24h overdue ---")
for (pf, _), j in sorted(enabled.items()):
    nr = parse_ts(j.get('next_run_at'))
    if nr and (now - nr).total_seconds() > 86400:
        lr = parse_ts(j.get('last_run_at'))
        last = f"{(now - lr).total_seconds() / 86400:.1f}d ago" if lr else '?'
        print(f"  {pf} | {j.get('name', '?')[:45]} | last_run {last} | overdue {(now - nr).total_seconds() / 86400:.1f}d | status={j.get('last_status')}")

# --- error ---
print("\n--- [ERROR] enabled, last_status=error ---")
for (pf, _), j in sorted(enabled.items()):
    if j.get('last_status') == 'error':
        lr = parse_ts(j.get('last_run_at'))
        age = f"{(now - lr).total_seconds() / 86400:.1f}d ago" if lr else '?'
        print(f"  {pf} | {j.get('name', '?')[:45]} | last_run {age}")
        print(f"      err: {str(j.get('last_error'))[:150]}")

# --- disabled/paused >7d ---
print("\n--- [PAUSED>7d] unique ---")
seen = set()
rows = []
for (pf, _), j in all_jobs.items():
    if j.get('enabled'):
        continue
    pa = parse_ts(j.get('paused_at'))
    if pa and (now - pa).days > 7:
        rows.append(((now - pa).days, j.get('name', '?')))
for d, n in sorted(set(rows), key=lambda x: -x[0]):
    print(f"  {n} | {d}d")

# --- deliver distribution ---
print("\n--- deliver distribution ---")
dist = Counter()
for j in all_jobs.values():
    d = j.get('deliver')
    if isinstance(d, list):
        for x in d:
            dist[str(x.get('type', x))] += 1
    else:
        dist[str(d)] += 1
for k, v in dist.most_common():
    print(f"  {k}: {v}")

# --- chat ids referenced (存活判定跑 verify_deliver_targets.py,勿用 channel_directory.json) ---
used = set()
for j in all_jobs.values():
    used |= set(re.findall(r'oc_[a-f0-9]{16,}', json.dumps(j, ensure_ascii=False)))
print(f"\nchat ids referenced by jobs: {len(used)}  -> 跑 verify_deliver_targets.py 验证存活")
