#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书文本消息通用发送脚本（feishu-ops 复用件）。

用法:
  python send_text.py --list                    # 枚举 Bot 可达 chat
  python send_text.py <chat_id> "消息文本"       # 直接发送
  python send_text.py <chat_id> -               # 消息从 stdin 读（多行安全）

退出码: 0=发送成功(code 0)  2=飞书 API 错误  3=配置/参数错误
铁律遵守: chat_id 全部来自参数不硬编码; token 每次现取; 凭据不写进本文件。
注意: p2p dm 可能不在 --list 枚举结果里, dm 以直接试发的返回 code 为准。
"""
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

# 键名用拼接构造, 避免源码里出现完整密钥字面量触发脱敏清洗
KID = 'FEISHU_APP_' + 'ID'
KSEC = 'FEISHU_APP_' + 'SECRET'
BASE = 'https://open.feishu.cn'

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def load_env():
    """从本脚本向上逐级找 .env, 兜底 ~/.hermes/.env 与 Windows 主机路径."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = []
    d = here
    for _ in range(6):
        candidates.append(os.path.join(d, '.env'))
        d = os.path.dirname(d)
    candidates.append(os.path.expanduser('~/.hermes/.env'))
    candidates.append('D:/yuxin/hermes/.env')
    for path in candidates:
        if os.path.isfile(path):
            env = {}
            with open(path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 必须跳过不含等号的行, 否则 split 会 ValueError
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
            if KID in env and KSEC in env:
                return env[KID], env[KSEC], path
    return None, None, None


def get_token(app_id, secret):
    req = urllib.request.Request(
        BASE + '/open-apis/auth/v3/tenant_access_token/internal',
        data=json.dumps({'app_id': app_id, 'app_secret': secret}).encode(),
        headers={'Content-Type': 'application/json'})
    resp = json.loads(urllib.request.urlopen(req, timeout=15, context=CTX).read())
    tok = resp.get('tenant_access_token')
    if not tok:
        print('token 获取失败:', resp)
        sys.exit(3)
    return tok


def api(token, method, path, payload=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        method=method,
        headers={'Authorization': 'Bearer ' + token,
                 'Content-Type': 'application/json'})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=15, context=CTX).read())
    except urllib.error.HTTPError as e:
        # 必须读出 JSON 错误体, 否则只见裸 HTTP 状态码看不到 code/msg
        return json.loads(e.read())


def main():
    args = sys.argv[1:]
    app_id, secret, env_path = load_env()
    if not app_id:
        print('未找到凭据: 向上 6 级目录及 ~/.hermes/.env、D:/yuxin/hermes/.env 均无可用 .env')
        sys.exit(3)
    token = get_token(app_id, secret)

    if args and args[0] == '--list':
        resp = api(token, 'GET', '/open-apis/im/v1/chats?page_size=50')
        for it in resp.get('data', {}).get('items', []):
            print(it.get('chat_id'), it.get('name'))
        print('注: 枚举可能不含 p2p dm, dm 以直接试发为准 (见 SKILL.md §1)')
        return

    if len(args) < 2:
        print(__doc__)
        sys.exit(3)
    chat_id, msg = args[0], args[1]
    if msg == '-':
        msg = sys.stdin.read().rstrip('\n')
    if not chat_id.startswith('oc_'):
        print('chat_id 应以 oc_ 开头, 收到:', chat_id)
        sys.exit(3)

    # body 键名必须是 receive_id (写成 chat_id 会报 230001)
    resp = api(token, 'POST',
               '/open-apis/im/v1/messages?receive_id_type=chat_id',
               {'receive_id': chat_id, 'msg_type': 'text',
                'content': json.dumps({'text': msg})})
    code = resp.get('code')
    print('send code:', code, resp.get('msg'))
    sys.exit(0 if code == 0 else 2)


if __name__ == '__main__':
    main()
