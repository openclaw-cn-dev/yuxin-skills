import json, os, datetime

HOME = "/Users/hua/.hermes"
now = datetime.datetime(2026, 8, 27, 23, 5, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=8)))

def parse_jobs(path):
    with open(path) as f:
        return json.load(f).get("jobs", []), None

main_jobs, _ = parse_jobs(f"{HOME}/cron/jobs.json")

print("="*70)
print("ALL DISABLED/PAUSED jobs in main cron (含暂停天数):")
print("="*70)
for j in main_jobs:
    if j.get("enabled"):
        continue
    name = j.get("name","?")
    paused_at = j.get("paused_at")
    last_run = j.get("last_run_at")
    state = j.get("state")
    days = None
    if paused_at:
        try:
            pt = datetime.datetime.fromisoformat(paused_at)
            if pt.tzinfo is None:
                pt = pt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
            days = (now - pt).days
        except Exception as e:
            days = f"ERR {e}"
    print(f"  [{days}d] {name} | state={state} | paused={paused_at} | last_run={last_run}")

print("\n" + "="*70)
print("ERROR jobs detail (main cron):")
print("="*70)
for j in main_jobs:
    if j.get("last_status") == "error":
        print(f"\n### {j.get('name')} (id={j.get('id')})")
        print(f"  enabled={j.get('enabled')} state={j.get('state')}")
        print(f"  last_run={j.get('last_run_at')}")
        print(f"  error={j.get('last_error')}")
        print(f"  deliver={j.get('deliver')} origin={j.get('origin')}")

print("\n" + "="*70)
print("enabled jobs with error in PROFILE crons:")
print("="*70)
for prof in ["zhenglishi","quant","xiaobao","maodou","laomo","heidou","afu","community","default"]:
    p = f"{HOME}/profiles/{prof}/cron/jobs.json"
    if not os.path.exists(p):
        continue
    jobs, _ = parse_jobs(p)
    for j in jobs:
        if j.get("last_status") == "error" or j.get("last_error"):
            print(f"  {prof}: {j.get('name')} | enabled={j.get('enabled')} | last_run={j.get('last_run_at')} | err={(j.get('last_error') or '')[:100]}")
