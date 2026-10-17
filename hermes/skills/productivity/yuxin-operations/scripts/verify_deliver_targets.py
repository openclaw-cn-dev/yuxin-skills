#!/usr/bin/env python3
"""管理进化扫描 #1 补充:deliver 目标(chat_id)存活实测 — 走飞书 API,不用 channel_directory.json。

背景(2026-09-17 修正): channel_directory.json 只收录 ~2 个 base 飞书群(目录不全),
据此判定"群解散/投递失效"曾产生误报。唯一可信口径 = 飞书 API im/v1/chats/{id} 实测。

用法: python3 verify_deliver_targets.py
依赖: ~/.hermes/.env 中的 FEISHU_APP_ID / FEISHU_APP_SECRET
"""
import glob
import json
import os
import re
import urllib.request
from urllib.parse import quote

ENV = '/Users/hua/.hermes/.env'


def load_env(path):
    vals = {}
    for line in open(path):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            vals[k] = v
    return vals


def tenant_token(app_id, secret):
    req = urllib.request.Request(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        data=json.dumps({'app_id': app_id, 'app_secret': secret}).encode(),
        headers={'Content-Type': 'application/json'})
    r = json.loads(urllib.request.urlopen(req, timeout=15).read())
    return r.get('tenant_access_token')


def chat_alive(token, cid):
    req = urllib.request.Request(
        f'https://open.feishu.cn/open-apis/im/v1/chats/{quote(cid)}',
        headers={'Authorization': f'Bearer {token}'})
    r = json.loads(urllib.request.urlopen(req, timeout=15).read())
    if r.get('code') == 0:
        return True, r.get('data', {}).get('name', '?')
    return False, f"code={r.get('code')}"


def main():
    env = load_env(ENV)
    token = tenant_token(env['FEISHU_APP_ID'], env['FEISHU_APP_SECRET'])
    if not token:
        print("TOKEN FAIL — 检查 ~/.hermes/.env 凭据")
        return

    # 收集全部 job 引用的 oc_ chat_id
    targets = {}  # cid -> [job refs]
    paths = ['/Users/hua/.hermes/cron/jobs.json'] + glob.glob(
        '/Users/hua/.hermes/profiles/*/cron/jobs.json')
    for path in paths:
        pf = 'default' if '/profiles/' not in path else path.split('/profiles/')[1].split('/')[0]
        try:
            data = json.load(open(path))
        except Exception:
            continue
        for j in data.get('jobs', []):
            blob = json.dumps(j, ensure_ascii=False)
            for cid in set(re.findall(r'oc_[a-f0-9]{16,}', blob)):
                targets.setdefault(cid, []).append(f"{pf}:{j.get('name', '?')[:30]}")

    print(f"verifying {len(targets)} chat ids via Feishu API ...")
    dead = 0
    for cid, refs in sorted(targets.items()):
        try:
            ok, info = chat_alive(token, cid)
        except Exception as e:
            ok, info = False, f"ERR {str(e)[:60]}"
        tag = 'ALIVE' if ok else '*** DEAD ***'
        if not ok:
            dead += 1
        print(f"  {tag}  {cid}  {info}  <- {refs[0]}{' +%d more' % (len(refs)-1) if len(refs) > 1 else ''}")
    print(f"\nresult: {len(targets) - dead}/{len(targets)} alive, {dead} dead")


if __name__ == '__main__':
    main()
