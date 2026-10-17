#!/usr/bin/env python3
"""
宽博士任务文件夹扫描脚本 — 渔芯量化研究 cron 专用
自动检查飞书云盘任务派发目录下的所有宽博士子文件夹

使用方法:
  python3 kuanboshi_task_scanner.py

输出:
  - 发现 N 个任务文件 → 列出文件名
  - ✅ 宽博士 当前无待处理任务 → 无任务
"""
import urllib.request, json, os

BASE = 'https://open.feishu.cn/open-apis'
BP = 'Bearer '

# 宽博士入口文件夹 token (在 任务派发/ 下)
ENTRY_FOLDER_TOKEN='EsEAfQL0vl34bBdQYP4c2Llbn5y'

# 从 .env 读取凭据（绝对路径，兼容 cron 环境）
creds = {}
with open('/Users/hua/.hermes/.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('FEISHU_APP_') and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            creds[k] = v

APP_ID = creds.get('FEISHU_APP_ID', '')
APP_SECRET=*** 获取 Token
body = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode('utf-8')
req = urllib.request.Request(
    BASE + '/auth/v3/tenant_access_token/internal',
    data=body, method='POST'
)
req.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        resp = json.loads(r.read())
        if resp.get('code') != 0:
            print(f"❌ Token获取失败: {resp}")
            exit(1)
        token = resp['tenant_access_token']
except Exception as e:
    print(f"❌ Token获取异常: {e}")
    exit(1)

auth_header = BP + token

# 第一步：列出入口文件夹，找到所有 "宽博士" 子文件夹
url = BASE + f"/drive/v1/files?folder_token={ENTRY_FOLDER_TOKEN}&page_size=50"
req2 = urllib.request.Request(url, headers={"Authorization": auth_header})
try:
    with urllib.request.urlopen(req2, timeout=10) as r:
        resp2 = json.loads(r.read().decode())
except Exception as e:
    print(f"❌ 列表入口失败: {e}")
    exit(1)

if resp2.get('code') != 0:
    print(f"❌ API返回错误: {resp2}")
    exit(1)

all_files = resp2.get('data', {}).get('files', []) or []
kuanboshi_folders = [f for f in all_files if f.get('name') == '宽博士' and f.get('type') == 'folder']

# 第二步：检查每个宽博士文件夹
task_files = []
for folder in kuanboshi_folders:
    ftok = folder.get('token')
    url2 = BASE + f"/drive/v1/files?folder_token={ftok}&page_size=50"
    req3 = urllib.request.Request(url2, headers={"Authorization": auth_header})
    try:
        with urllib.request.urlopen(req3, timeout=10) as r:
            resp3 = json.loads(r.read().decode())
    except Exception:
        continue
    
    if resp3.get('code') != 0:
        continue
    
    files_in_folder = resp3.get('data', {}).get('files', []) or []
    for f in files_in_folder:
        task_files.append({
            'folder_token': ftok,
            'file_token': f.get('token'),
            'file_name': f.get('name'),
            'file_type': f.get('type')
        })

# 输出结果
if len(task_files) == 0:
    print("✅ 宽博士 当前无待处理任务")
else:
    print(f"发现 {len(task_files)} 个待处理任务:")
    for tf in task_files:
        print(f"  - {tf['file_name']}")
