import json, shutil, os, sys

# 1. 把启动器复制进各自 profile 的 scripts/（新调度规则：no_agent 脚本必须落在 profile scripts 目录内）
os.makedirs('D:/yuxin/hermes/profiles/quant/scripts', exist_ok=True)
os.makedirs('D:/yuxin/hermes/profiles/zhenglishi/scripts', exist_ok=True)
shutil.copy2('D:/yuxin/hermes/scripts/quant_watchdog.py',
             'D:/yuxin/hermes/profiles/quant/scripts/quant_watchdog.py')
shutil.copy2('D:/yuxin/company/03-库/01-知识库/算力监控台/hourly_patrol.py',
             'D:/yuxin/hermes/profiles/zhenglishi/scripts/hourly_patrol.py')

# 2. 改 jobs.json 的 script 字段为相对名（在 profile scripts 范围内，合规且可解析）
for prof, jid, newval in [
    ('quant', '3786acbe0226', 'quant_watchdog.py'),
    ('zhenglishi', '30eeef1e58c5', 'hourly_patrol.py'),
]:
    p = f'D:/yuxin/hermes/profiles/{prof}/cron/jobs.json'
    bak = p + '.bak-20261111-scriptrange-fix'
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
    d = json.load(open(p, encoding='utf-8'))
    hit = False
    for j in d.get('jobs', []):
        if j.get('id') == jid:
            j['script'] = newval
            hit = True
            print(prof, jid, '->', newval)
    if not hit:
        print(prof, jid, 'NOT FOUND!')
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 3. 语法验证
for prof in ('quant', 'zhenglishi'):
    p = f'D:/yuxin/hermes/profiles/{prof}/cron/jobs.json'
    json.load(open(p, encoding='utf-8'))
print('verify ok')
