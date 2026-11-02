#!/usr/bin/env python3
"""一次性解析全部 cron jobs.json(default + profiles),输出 8 项扫描第 1/8 项所需的三张清单。
用法: python3 scan_cron_health.py
输出: [1] disabled>7天清单 [2] enabled+error(含 last_error 摘要供假阳性判断) [3] delivery_error
"""
import json, glob, datetime, os

NOW = datetime.datetime.now()

def parse_dt(s):
    if not s: return None
    try:
        return datetime.datetime.fromisoformat(str(s).replace('Z','+00:00')).replace(tzinfo=None)
    except Exception:
        return None

files = ['/Users/hua/.hermes/cron/jobs.json'] + sorted(glob.glob('/Users/hua/.hermes/profiles/*/cron/jobs.json'))
total = enabled_cnt = 0
old_disabled, errors, deliv_errs = [], [], []

for f in files:
    profile = 'default' if f.endswith('/cron/jobs.json') and '/profiles/' not in f else f.split('/profiles/')[1].split('/')[0]
    try:
        data = json.load(open(f))
    except Exception as e:
        print(f'!! {profile}: parse error {e}'); continue
    jobs = data.get('jobs', data) if isinstance(data, dict) else data
    if isinstance(jobs, dict): jobs = list(jobs.values())
    total += len(jobs)
    for j in jobs:
        name = j.get('name','?')
        paused_at = parse_dt(j.get('paused_at'))
        days_paused = (NOW - paused_at).days if paused_at else None
        if not j.get('enabled', True):
            enabled_cnt += 1
            if days_paused is not None and days_paused > 7:
                old_disabled.append((profile, name, j.get('id','')[:12], days_paused, str(j.get('last_status'))))
        else:
            if j.get('last_status') == 'error':
                err = str(j.get('last_error',''))[:180].replace('\n',' ')
                errors.append((profile, name, j.get('id','')[:12], err))
            de = j.get('last_delivery_error')
            if de:
                deliv_errs.append((profile, name, j.get('deliver'), str(de)[:140]))

print(f'== 总计: {total} jobs, enabled={total-enabled_cnt}, disabled={enabled_cnt}')
print(f'\n== [1] disabled 且 paused>7 天({len(old_disabled)}):')
for t in old_disabled:
    print(f'  [{t[0]}] {t[1]} ({t[2]}) paused {t[3]}d last_status={t[4]}')
print(f'\n== [2] enabled+error({len(errors)}) — 读 err 判断真失败 vs 假阳性(报告包在 RuntimeError 里):')
for t in errors:
    print(f'  [{t[0]}] {t[1]} ({t[2]})\n      err: {t[3]}')
print(f'\n== [3] delivery_error({len(deliv_errs)}) — 232009=群解散需改 deliver, 230002=Bot不在群:')
for t in deliv_errs:
    print(f'  [{t[0]}] {t[1]} deliver={t[2]} | {t[3]}')
