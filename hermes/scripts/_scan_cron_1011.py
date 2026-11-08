#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 玉芬管理进化扫描 2026-10-11 cron 健康扫描
import json, datetime, os, glob

NOW = datetime.datetime.now().astimezone()

def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None

def days_since(ts):
    if ts is None:
        return None
    return (NOW - ts).total_seconds() / 86400.0

def load_jobs(path):
    try:
        with open(path) as f:
            d = json.load(f)
    except Exception as e:
        return None, str(e)
    jobs = d if isinstance(d, list) else d.get('jobs', [])
    return jobs, None

def scan(domain, path):
    jobs, err = load_jobs(path)
    if err:
        print(f"[{domain}] LOAD ERROR: {err}")
        return
    print(f"\n===== {domain} ({path}) =====")
    print(f"TOTAL jobs: {len(jobs)}")
    enabled = [j for j in jobs if j.get('enabled')]
    disabled = [j for j in jobs if not j.get('enabled')]
    print(f"enabled={len(enabled)} disabled={len(disabled)}")

    # paused > 7d
    print(f"\n--- paused/disabled >7d (决策:删 vs 保留) ---")
    for j in sorted(disabled, key=lambda x: days_since(parse_ts(x.get('paused_at'))) or 0, reverse=True):
        pa = parse_ts(j.get('paused_at'))
        d = days_since(pa)
        if d is not None and d > 7:
            print(f"  [>{d:.0f}d] {j.get('name')} (id={j.get('id','')[:6]}) paused_at={j.get('paused_at','')[:10]}")

    # error jobs
    print(f"\n--- last_status=error ---")
    for j in jobs:
        if j.get('last_status') == 'error':
            lr = parse_ts(j.get('last_run_at'))
            lrd = days_since(lr)
            err_txt = (j.get('last_error') or '')[:160].replace('\n',' ')
            print(f"  [enabled={j.get('enabled')}] last_run {lrd if lrd is None else round(lrd,1)}d ago | {j.get('name')} (id={j.get('id','')[:6]})")
            print(f"      err: {err_txt}")

    # deliver / origin chat_ids
    print(f"\n--- deliver/origin 形态 ---")
    seen = {}
    for j in jobs:
        dv = j.get('deliver') or 'null'
        og = (j.get('origin') or {}).get('chat_id') if isinstance(j.get('origin'), dict) else None
        key = (dv, og)
        seen.setdefault(key, []).append(j.get('name',''))
    for (dv, og), names in seen.items():
        print(f"  deliver={dv} origin_chat={og} :: {len(names)} jobs e.g. {names[0][:40]}")

def main():
    scan("main", "/Users/hua/.hermes/cron/jobs.json")
    for p in sorted(glob.glob("/Users/hua/.hermes/profiles/*/cron/jobs.json")):
        prof = p.split('/')[-3]
        scan(prof, p)

if __name__ == '__main__':
    main()
