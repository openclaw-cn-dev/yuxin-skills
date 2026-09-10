import json, os, datetime, glob, sqlite3

HOME = "/Users/hua/.hermes"
now = datetime.datetime(2026, 8, 27, 23, 5, 0)

def parse_jobs(path):
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get("jobs", []), None
    except Exception as e:
        return None, str(e)

main_jobs, err = parse_jobs(f"{HOME}/cron/jobs.json")
print("="*70)
print("MAIN CRON JOBS:", len(main_jobs) if main_jobs else f"ERR {err}")

paused_old = []
error_jobs = []
deliver_targets = {}
enabled_count = 0
for j in main_jobs:
    name = j.get("name","?")
    enabled = j.get("enabled", False)
    state = j.get("state")
    paused_at = j.get("paused_at")
    last_status = j.get("last_status")
    last_error = j.get("last_error")
    last_run = j.get("last_run_at")
    deliver = j.get("deliver")
    origin = j.get("origin") or {}
    chat_id = origin.get("chat_id")
    if enabled:
        enabled_count += 1
    if (not enabled) and paused_at:
        try:
            pt = datetime.datetime.fromisoformat(paused_at)
            if (now - pt).days > 7:
                paused_old.append((name, paused_at[:10], state, last_run[:10] if last_run else None))
        except: pass
    if last_status == "error":
        error_jobs.append((name, enabled, last_run[:10] if last_run else None, (last_error or "")[:100]))
    if deliver and deliver != "local":
        key = deliver
        if deliver == "origin":
            key = f"origin:{chat_id}"
        deliver_targets[key] = deliver_targets.get(key, 0) + 1

print(f"\nEnabled jobs: {enabled_count} / {len(main_jobs)}")
print(f"\n[1a] PAUSED >7 days (共{len(paused_old)}):")
for n, pa, st, lr in paused_old:
    print(f"  - {n} | paused {pa} | state={st} | last_run={lr}")

print(f"\n[1b] ERROR jobs (共{len(error_jobs)}):")
for n, en, lr, le in error_jobs:
    print(f"  - {n} | enabled={en} | last_run={lr} | {le}")

print(f"\n[1c] deliver targets (非local):")
for d, c in sorted(deliver_targets.items(), key=lambda x:-x[1]):
    print(f"  {d}  x{c}")

# Also profile cron jobs
print("\n" + "="*70)
print("PROFILE CRON JOBS:")
for prof in ["zhenglishi","quant","default","xiaobao","maodou","laomo","heidou","afu","community"]:
    p = f"{HOME}/profiles/{prof}/cron/jobs.json"
    if os.path.exists(p):
        jobs, e = parse_jobs(p)
        if jobs is not None:
            en = sum(1 for j in jobs if j.get("enabled"))
            er = sum(1 for j in jobs if j.get("last_status")=="error")
            pa = sum(1 for j in jobs if (not j.get("enabled")) and j.get("paused_at"))
            print(f"  {prof}: {len(jobs)} jobs | enabled={en} | error={er} | paused={pa}")
        else:
            print(f"  {prof}: ERR {e}")
