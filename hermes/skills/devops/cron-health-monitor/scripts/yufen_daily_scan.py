#!/usr/bin/env python3
"""
玉芬每日管理进化扫描 — 一键数据采集（纯 stdlib，全绝对路径）

用法: python3 <本skill目录>/scripts/yufen_daily_scan.py
输出: stdout 分节文本（0-8 节），cron 会话直接解读，只对异常项人工深挖。
来源: 2026-09-06 玉芬 cron 实测三轮脚本 (scan/scan2/scan3) 合并固化。
坑位依据: references/***SECRET***.md
  - 死群判定必须双信号（目录缺失 + last_delivery_error 含 232009），目录本身可能不完整
  - 子 profile cron 卡死的根因优先查 gateway 存活（launchctl）
  - hermes cron CLI 与 jobs.json 脱节时，处置走直编文件（本脚本只读不写，无此风险）
各节独立 try/except，单节失败不影响其余。
"""
import glob
import json
import os
import re
import sqlite3
import subprocess
import time
from datetime import datetime

NOW = time.time()
OUT = []


def p(s=''):
    OUT.append(str(s))


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace('Z', '+00:00')).timestamp()
    except Exception:
        return None


def human_ts_mixed(v):
    """tasks.db timestamp 列混有 unix int 与 'YYYY-MM-DD HH:MM' 字符串，统一处理"""
    if v is None:
        return '?', None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v).strftime('%m-%d %H:%M'), float(v)
    s = str(v)
    try:
        ts = datetime.fromisoformat(s.replace(' ', 'T')).timestamp()
        return s[:16], ts
    except Exception:
        return s[:16], None


def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or '') + (r.stderr or '')
    except Exception as e:
        return -1, str(e)


CRON_FILES = ['/Users/hua/.hermes/cron/jobs.json'] + sorted(
    glob.glob('/Users/hua/.hermes/profiles/*/cron/jobs.json'))

# ---------- 0. ENV ----------
p('=== 0. ENV CHECK (Pitfall #37: HOME 可能指向嵌套 profile home) ===')
p(f'HOME={os.environ.get("HOME")}  pwd={os.getcwd()}  (本脚本全绝对路径，输出不受影响)')

# ---------- 1. CRON HEALTH ----------
ALL_JOBS = []
p('')
p('=== 1. CRON HEALTH (default + 子 profile) ===')
for cf in CRON_FILES:
    prof = 'default' if '/profiles/' not in cf else cf.split('/profiles/')[1].split('/')[0]
    try:
        data = json.load(open(cf))
        for j in data.get('jobs', []):
            j['_profile'] = prof
            ALL_JOBS.append(j)
    except Exception as e:
        p(f'!! parse fail {cf}: {e}')
p(f'total jobs: {len(ALL_JOBS)}')

p('-- 1a. enabled=False 且 paused_at > 7d (删/留决策清单) --')
n = 0
for j in ALL_JOBS:
    if not j.get('enabled') and j.get('state') == 'paused':
        pt = parse_ts(j.get('paused_at'))
        if pt and (NOW - pt) / 86400 > 7:
            n += 1
            lr = str(j.get('last_run_at') or '?')[:10]
            p(f"  [{j['_profile']}] {j['id']} {j['name']} | paused {(NOW - pt) / 86400:.0f}d | last_run={lr} | last_status={j.get('last_status')}")
if n == 0:
    p('  (none)')

p('-- 1b. last_status=error --')
n = 0
for j in ALL_JOBS:
    if j.get('last_status') == 'error':
        n += 1
        lr = parse_ts(j.get('last_run_at'))
        age = f'{(NOW - lr) / 86400:.1f}d ago' if lr else '?'
        err = re.sub(r'\s+', ' ', (j.get('last_error') or ''))[:150]
        p(f"  [{j['_profile']}] {j['id']} {j['name']} | enabled={j.get('enabled')} state={j.get('state')} | last_run={age} | err: {err}")
if n == 0:
    p('  (none)')

p('-- 1c. enabled+scheduled 但 next_run_at 落后 >30min (卡死) --')
stuck_by_prof = {}
for j in ALL_JOBS:
    if j.get('enabled') and j.get('state') == 'scheduled':
        nt = parse_ts(j.get('next_run_at'))
        if nt and (NOW - nt) / 60 > 30:
            stuck_by_prof.setdefault(j['_profile'], []).append(j['id'])
            p(f"  [{j['_profile']}] {j['id']} {j['name']} | 卡 {(NOW - nt) / 3600:.1f}h | last_run={str(j.get('last_run_at') or '?')[:16]}")
if not stuck_by_prof:
    p('  (none)')

p('-- 1d. 死群双信号判定 (目录缺失+232009 才判死；仅目录缺失=疑目录不完整) --')
try:
    d = json.load(open('/Users/hua/.hermes/channel_directory.json'))
    known = set(re.findall(r'oc_[a-f0-9]{20,}', json.dumps(d)))
    usage = {}
    for j in ALL_JOBS:
        blob = (j.get('deliver') or '') + ((j.get('origin') or {}).get('chat_id') or '')
        lde = j.get('last_delivery_error') or ''
        for cid in set(re.findall(r'oc_[a-f0-9]{20,}', blob)):
            usage.setdefault(cid, []).append(
                (j['_profile'], j['id'], j['name'], bool(j.get('enabled')), '232009' in lde))
    for cid in sorted(usage):
        users = usage[cid]
        in_dir = cid in known
        has_232009 = any(u[4] for u in users)
        if not in_dir and has_232009:
            verdict = '*** CONFIRMED DISSOLVED (双信号) ***'
        elif not in_dir:
            verdict = '(目录缺失但无投递错，疑目录不完整，勿判死)'
        else:
            verdict = 'alive'
        if verdict != 'alive':
            p(f'  {verdict} {cid}')
            for u in users:
                p(f"     [{u[0]}] {u[1]} {u[2][:30]} enabled={u[3]}")
except Exception as e:
    p(f'  !! {e}')

p('-- 1e. GATEWAY 存活 (launchctl) — 子 profile cron 卡死先查这里 --')
gw_labels = {}
rc, out = run(['launchctl', 'list'], 30)
if rc == 0:
    for line in out.splitlines():
        if 'ai.hermes.gateway' in line:
            parts = line.split('\t')
            if len(parts) >= 3:
                gw_labels[parts[2]] = parts[0]
    for prof in sorted({j['_profile'] for j in ALL_JOBS}):
        if prof == 'default':
            pid = next((gw_labels[k] for k in ('ai.hermes.gateway', 'ai.hermes.gateway-default')
                        if gw_labels.get(k, '-').isdigit()), '-')
        else:
            pid = gw_labels.get(f'ai.hermes.gateway-{prof}', '-')
            if not pid.isdigit():
                pid = '-'
        mark = 'OK' if pid.isdigit() else 'DOWN'
        stuck_n = len(stuck_by_prof.get(prof, []))
        extra = f' | cron卡死{stuck_n}个' if stuck_n else ''
        p(f'  {prof}: gateway={mark} (pid={pid}){extra}')
else:
    p(f'  !! launchctl failed: {out[:100]}')

# ---------- 2. SKILL CAPACITY ----------
p('')
p('=== 2. SKILL CAPACITY AUDIT ===')


def count_skills(root):
    return [f for f in glob.glob(root + '/**/SKILL.md', recursive=True)
            if '.archive' not in f and '.curator_backups' not in f]


try:
    main_files = count_skills('/Users/hua/.hermes/skills')
    main_bytes = sum(os.path.getsize(f) for f in main_files)
    p(f'default profile: {len(main_files)} SKILL.md, {main_bytes / 1024:.0f} KB, ~{main_bytes / 3 / 1000:.0f}K tok(est)')
    all_files = list(main_files)
    for pf in sorted(glob.glob('/Users/hua/.hermes/profiles/*/skills')):
        prof = pf.split('/profiles/')[1].split('/')[0]
        files = count_skills(pf)
        if files:
            b = sum(os.path.getsize(f) for f in files)
            p(f'  profile {prof}: {len(files)} SKILL.md, {b / 1024:.0f} KB')
        all_files += files
    all_bytes = sum(os.path.getsize(f) for f in all_files)
    p(f'TOTAL: {len(all_files)} SKILL.md, {all_bytes / 1024 / 1024:.1f} MB, ~{all_bytes / 3 / 1000:.0f}K tok(est)')
    tot_bak = 0
    for d in (glob.glob('/Users/hua/.hermes/skills/.curator_backups')
              + glob.glob('/Users/hua/.hermes/profiles/*/skills/.curator_backups')):
        rc, out = run(['du', '-sk', d])
        try:
            kb = int(out.split()[0]) if rc == 0 else 0
        except Exception:
            kb = 0
        tot_bak += kb
    p(f'  .curator_backups 总量: {tot_bak / 1024:.0f} MB (归档候选，处置需批准且只 mv 不 rm)')
    top = sorted(((os.path.getsize(f), f) for f in main_files), reverse=True)[:8]
    p('-- default 最大 skill top8 --')
    for b, f in top:
        p(f'  {f.replace("/Users/hua/.hermes/skills/", "").split("/")[0]}: {b / 1024:.0f} KB')
except Exception as e:
    p(f'  !! {e}')

# ---------- 3. TASK QUEUE ----------
p('')
p('=== 3. TASK QUEUE ===')
p('-- kanban.db (无 updated_at 列! created_at/started_at 是 unix epoch int) --')
try:
    conn = sqlite3.connect('/Users/hua/.hermes/kanban.db')
    cur = conn.cursor()
    cur.execute('SELECT status, COUNT(*) FROM tasks GROUP BY status')
    p('  status: ' + ', '.join(f'{r[0]}={r[1]}' for r in cur.fetchall()))
    cur.execute("""SELECT id, title, assignee, status, priority, created_at
                   FROM tasks WHERE status IN ('blocked','ready','running','pending')
                   ORDER BY priority ASC, created_at ASC LIMIT 40""")
    for r in cur.fetchall():
        ca_s = datetime.fromtimestamp(r[5]).strftime('%m-%d') if r[5] else '?'
        p(f'  [{r[3]}|P{r[4]}] #{r[0]} {str(r[1])[:50]} | asg={r[2]} | created={ca_s}')
    cur.execute("""SELECT id, title, assignee, priority FROM tasks
                   WHERE status='blocked' AND priority<=1
                   AND COALESCE(started_at, created_at) < ?""", (NOW - 86400,))
    blk = cur.fetchall()
    p(f'  -- blocked>24h P0/P1: {len(blk)} (命中即触发 1 行提醒) --')
    conn.close()
except Exception as e:
    p(f'  !! kanban.db: {e}')

p('-- tasks.db (团队池；priority 是 TEXT P0/P1，时间列混 int/str) --')
try:
    conn = sqlite3.connect('/Users/hua/.hermes/tasks.db')
    cur = conn.cursor()
    cur.execute("""SELECT id, title, assigned_to, priority, status, updated_at
                   FROM tasks WHERE status IN ('pending','in_progress') ORDER BY updated_at ASC""")
    rows = cur.fetchall()
    p(f'  active rows: {len(rows)}')
    for r in rows:
        ua_s, ua_ts = human_ts_mixed(r[5])
        stale = f' ⚠STALE {(NOW - ua_ts) / 86400:.0f}d' if ua_ts and (NOW - ua_ts) > 7 * 86400 else ''
        p(f'  [{r[4]}|{r[3]}] #{r[0]} {str(r[1])[:48]} | asg={r[2]} | upd={ua_s}{stale}')
    conn.close()
except Exception as e:
    p(f'  !! tasks.db: {e}')

# ---------- 4. RESEARCH INCREMENT ----------
p('')
p('=== 4. RESEARCH INCREMENT (last 7d: LLM 触发 vs [SILENT] 跳过) ===')
RESEARCH_JOBS = {
    '6da61cd7ad11': 'ai-cad-research-daily',      # 2026-09-06 时已不存在
    '847438a1b08d': 'ai-3d-model-research-daily',  # 2026-09-06 时已不存在
    '29c08e9341ca': 'RAS持续调研',
    '51335637e254': '微表情调研',
    'a9756718a86e': '四技术-网络(旧,已并入三合一)',
    'ceabf877e787': '四技术-AI(旧,已并入三合一)',
    '9c6856bad954': '四技术-爬虫(旧,已并入三合一)',
    'a5f2061c110c': '360行调研',
}
week_ago = NOW - 7 * 86400
trig = skip = 0
try:
    for jid, name in RESEARCH_JOBS.items():
        d = f'/Users/hua/.hermes/cron/output/{jid}'
        if not os.path.isdir(d):
            p(f'  {name}({jid}): NO OUTPUT DIR (job 可能已删/已合并)')
            continue
        files = sorted(glob.glob(d + '/*.md'), key=os.path.getmtime, reverse=True)
        t = s = 0
        for f in files:
            if os.path.getmtime(f) < week_ago:
                continue
            try:
                if '[SILENT]' in open(f, encoding='utf-8', errors='ignore').read(4000):
                    s += 1
                else:
                    t += 1
            except Exception:
                pass
        trig += t
        skip += s
        latest_age = (NOW - os.path.getmtime(files[0])) / 86400 if files else -1
        p(f'  {name}: last7d trigger={t} silent={s} | latest {latest_age:.1f}d ago')
    p(f'  WEEK TOTAL: LLM triggered={trig}, skipped={skip}')
except Exception as e:
    p(f'  !! {e}')

# ---------- 5. AGENT HEARTBEAT ----------
p('')
p('=== 5. AGENT HEARTBEAT (profile 目录最新文件 mtime 代理) ===')
try:
    for prof in sorted(glob.glob('/Users/hua/.hermes/profiles/*/')):
        name = prof.rstrip('/').split('/')[-1]
        newest = 0
        for root, dirs, files in os.walk(prof):
            dirs[:] = [x for x in dirs if x not in ('.git', 'node_modules')]
            for fn in files:
                try:
                    m = os.path.getmtime(os.path.join(root, fn))
                    newest = max(newest, m)
                except Exception:
                    pass
        newest_age = (NOW - newest) / 86400 if newest else -1
        flag = ' ← >7d 停摆风险' if newest_age > 7 else (' ← 高频活跃' if 0 <= newest_age < 1 else '')
        p(f'  {name}: newest_file={newest_age:.2f}d{flag}')
except Exception as e:
    p(f'  !! {e}')

# ---------- 6. DOC ARCHIVE / RKR ----------
p('')
p('=== 6. DOC ARCHIVE / RKR / FindEra ===')
try:
    rkr = '/Users/hua/rkr_staging/文档中转站'
    if os.path.isdir(rkr):
        rc, out = run(['du', '-sk', rkr])
        kb = int(out.split()[0]) if rc == 0 else 0
        n_files = sum(len(fs) for _, _, fs in os.walk(rkr))
        p(f'  RKR staging: {kb / 1024:.0f} MB, {n_files} files')
    else:
        p('  RKR staging MISSING')
    log = '/Users/hua/.hermes/logs/rkr_findera_schedule.log'
    if os.path.exists(log):
        p(f'  findera log: {(NOW - os.path.getmtime(log)) / 3600:.1f}h since write')
        try:
            tail = open(log, encoding='utf-8', errors='ignore').read()[-600:]
            for l in [x for x in tail.strip().split('\n') if x.strip()][-3:]:
                p(f'    | {l[:110]}')
        except Exception:
            pass
    rc, out = run(['docker', 'info', '--format', '{{.ServerVersion}}'], 30)
    p(f'  docker daemon: {"OK " + out.strip() if rc == 0 else "DOWN/headless (单次尝试不重试)"}')
except Exception as e:
    p(f'  !! {e}')

# ---------- 7. VERSIONS ----------
p('')
p('=== 7. VERSIONS ===')
for label, cmd in [('codex', '/Users/hua/.local/bin/codex --version'),
                   ('claude', '/Users/hua/.local/bin/claude --version')]:
    rc, out = run(cmd.split(), 30)
    p(f'  {label} local: {out.strip().splitlines()[0][:80] if out.strip() else "(no output)"}')
for label, pkg in [('claude-code', '@anthropic-ai/claude-code'), ('codex', '@openai/codex')]:
    rc, out = run(['npm', 'show', pkg, 'version'], 60)
    p(f'  {label} npm latest: {out.strip().splitlines()[0][:60] if rc == 0 else "(查询失败,网络超时属常态)"}')
rc, out = run(['git', '-C', '/Users/hua/hermes-agent', 'log', '-1', '--format=%h %cs %s'], 15)
p(f'  hermes-agent git HEAD: {out.strip()[:100] if rc == 0 else "(无法读取)"}')

# ---------- 8. DELIVERY ACCURACY ----------
p('')
p('=== 8. 投递准确率 (enabled job 的 last_delivery_error) ===')
n = 0
for j in ALL_JOBS:
    lde = j.get('last_delivery_error')
    if lde and j.get('enabled'):
        n += 1
        code = re.search(r'\[(\d+)\]', lde)
        p(f"  [{j['_profile']}] {j['id']} {j['name'][:30]} | code={code.group(1) if code else '?'} | {re.sub(r'[\\r\\n]+', ' ', lde)[:90]}")
if n == 0:
    p('  (无投递失败)')

print('\n'.join(OUT))
