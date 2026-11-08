#!/bin/bash
# 知识库备份脚本 - 飞书云盘
# 运行一次，完整上传

cd /Users/hua/.hermes

source venv/bin/activate 2>/dev/null || source ~/hermes-agent/venv/bin/activate

python3 -c "
import subprocess, json, os, hashlib, time

with open('/Users/hua/.hermes/profiles/default/.env') as f:
    env = dict(line.strip().split('=', 1) for line in f if '=' in line)
r = subprocess.run(['curl', '-s', '-X', 'POST',
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps({'app_id': env['FEISHU_APP_ID'], 'app_secret': env['FEISHU_APP_SECRET']})],
    capture_output=True, text=True)
TOKEN = json.loads(r.stdout)['tenant_access_token']
print(f'Token OK')

KB_ROOT = '/Users/hua/Desktop/渔芯科技/2-知识库'
FOLDER_MAP = {
    'RAS系统': 'MSMWfBbGklAlPvd6NQfcNprenZe',
    '水产养殖': 'RgQOfWEy1lHN5AdJO83ctTfPn5f',
    '水产养殖深库': 'O1BFfXg14llXZodIe8zcsVfZnTf',
    '市场行情': 'OpmGfBeqFlWioLdkOppcNb2Gnrg',
    '设备知识库': 'TV7sfYjDcltCWfd7H22cyhSlnIh',
    '研究': 'Ra5ofYuQDlqc4zdI0tbckoegnib',
    '鱼乐宝RAS数字孪生平台': 'SQEEftip7lHcnZdbh2OcZqlon0b',
    '鱼晓一号': 'XFdhfs8qAlm00udgRykceducnSb',
    '用户服务': 'GlxJfoQc5l7LgndY9ElcQU1UnJd',
    '建筑AI': 'Zs1DftzRMlHF75dDIC4cKf8bnPh',
    '其它': 'Qt0zfRHXalRJxBdET6rcTI7JnId',
}
SKIP = {'_archive', '设备3d建模库', '设备资料', '养殖案例'}

ok, fail = 0, 0
for folder_name, ftoken in FOLDER_MAP.items():
    fpath = os.path.join(KB_ROOT, folder_name)
    if not os.path.exists(fpath): continue
    for root, dirs, files in os.walk(fpath):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for fname in files:
            fp = os.path.join(root, fname)
            size = os.path.getsize(fp)
            if size > 20*1024*1024: continue
            md5_hash = hashlib.md5(open(fp, 'rb').read()).hexdigest()
            proc = subprocess.run(
                ['curl', '-s', '-X', 'POST',
                 'https://open.feishu.cn/open-apis/drive/v1/files/upload_all',
                 '-H', f'Authorization: Bearer {TOKEN}',
                 '-F', f'file_name={fname}',
                 '-F', 'parent_type=explorer',
                 '-F', f'parent_node={ftoken}',
                 '-F', f'size={size}',
                 '-F', f'md5={md5_hash}',
                 '-F', f'file=@{fp}'],
                capture_output=True, text=True, timeout=30
            )
            try:
                r2 = json.loads(proc.stdout)
                if r2.get('code') == 0:
                    ok += 1
                else:
                    fail += 1
            except:
                fail += 1
            if (ok+fail) % 20 == 0:
                print(f'{ok+fail}: {ok}ok {fail}fail')

print(f'FINAL: {ok}ok {fail}fail')
"
