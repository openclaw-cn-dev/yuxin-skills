#!/usr/bin/env python3
"""
飞书云盘任务文件夹扫描模板（cron 专用）
特点：
- 从 .env 动态读取凭据（不怕平台端轮换）
- 用绝对路径（不怕 profile 切换）
- urllib 原生（不怕 curl subprocess 问题）
- 已验证可用（2026-06-26 宽博士 cron）

使用方法：
1. 修改 FOLDER_TOKEN 为目标文件夹
2. 修改业务逻辑部分
3. python3 cron_task_scanner.py
"""

import urllib.request, json, os

BASE = 'https://open.feishu.cn/open-apis'
ENV_PATH = '/Users/hua/.hermes/.env'
BP = 'Bearer '

# ========== 配置 ==========
FOLDER_TOKEN = 'EsEAfQL0vl34bBdQYP4c2Llbn5y'  # 宽博士任务根目录
# =========================

def main():
    # 1. 读取凭据
    creds = {}
    with open(ENV_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('FEISHU_APP_') and '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                creds[k] = v

    A = creds.get('FEISHU_APP_ID', '')
    S = creds.get('FEISHU_APP_SECRET', '')

    # 2. 获取 Token
    body = json.dumps({"app_id": A, "app_secret": S}).encode('utf-8')
    req = urllib.request.Request(
        BASE + '/auth/v3/tenant_access_token/internal',
        data=body, method='POST'
    )
    req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=10) as r:
        resp = json.loads(r.read().decode())
        if resp.get('code') != 0:
            print(f"TOKEN ERROR: code={resp.get('code')}, msg={resp.get('msg')}")
            return 1
        token = resp['tenant_access_token']

    auth = BP + token

    # 3. 列出文件
    url = f'{BASE}/drive/v1/files?folder_token={FOLDER_TOKEN}&page_size=50'
    req2 = urllib.request.Request(url, headers={'Authorization': auth})
    with urllib.request.urlopen(req2, timeout=10) as r:
        data = json.loads(r.read().decode())

    if data.get('code') != 0:
        print(f"LIST ERROR: code={data.get('code')}, msg={data.get('msg')}")
        return 1

    files = data.get('data', {}).get('files', [])

    # ========== 业务逻辑开始 ==========
    # 示例：打印所有文件/文件夹
    print(f"Found {len(files)} items:")
    for f in files:
        print(f"  [{f.get('type')}] {f.get('name')} (token: {f.get('token')[:8]}...)")

    # 你的业务逻辑：
    # - 过滤出文件（非 folder）
    # - 下载新任务文件
    # - 处理任务
    # - 上传结果
    # - 发飞书消息汇报

    return 0

if __name__ == '__main__':
    exit(main())
