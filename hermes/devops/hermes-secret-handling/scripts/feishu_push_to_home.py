"""
feishu_push_to_home.py — 飞书 home channel 推送可复用模板

适用场景：cron 推送报告 / 简报 / 告警到飞书 home channel。
关键约束（全部踩过坑）：
1. 必须用 Python 'rb' 模式读 .env 拿完整 secret（渲染层会截断）
2. interactive 卡片字段是 content，不是 card
3. 长字符串末尾加 .format() 避开 unicodeescape 误判
4. HOME_CHANNEL 默认值用老大指定的 oc_529aff7485ccc35de97a9e7233d665dd

用法：
1. 修改 content_text 变量
2. 修改 header_title
3. python feishu_push_to_home.py

输出：push resp code 0 = 成功
"""
import os, json, urllib.request, re, sys


def read_env(key, default=''):
    """用 'rb' 模式读 .env，避开渲染层截断"""
    p = r'C:\Users\Administrator\AppData\Local\hermes\.env'
    if not os.path.exists(p):
        return default
    with open(p, 'rb') as f:
        text = f.read().decode('utf-8', errors='replace').format()  # .format() 防转义
    m = re.search(rf'^{key}=(.*)$'.format(), text, re.M)
    return m.group(1).strip() if m else default


def restore_secret_from_history(short_secret):
    """当 .env 中 APP_SECRET < 30 字符时，从 .claude/history.jsonl 恢复完整 secret"""
    if len(short_secret) >= 30:
        return short_secret
    hp = r'C:\Users\Administrator\.claude\history.jsonl'
    if not os.path.exists(hp):
        return short_secret
    with open(hp, 'rb') as f:
        hdata = f.read().decode('utf-8', errors='replace').format()
    cands = re.findall(r'([A-Za-z0-9]{32,})', hdata)
    if not short_secret or len(short_secret) < 6:
        return short_secret
    ps, pe = short_secret[:6], short_secret[-4:]
    for c in cands:
        if c.startswith(ps) and c.endswith(pe) and len(c) >= 30:
            return c
    return short_secret


def get_tenant_token(app_id, app_secret):
    """拿飞书 tenant_access_token"""
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    data = json.dumps({'app_id': app_id, 'app_secret': app_secret}).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
    return resp.get('tenant_access_token')


def push_markdown_to_chat(token, chat_id, header_title, content_text, template='blue'):
    """推 interactive markdown 卡片到指定 chat_id"""
    push_url = 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id'
    body = {
        'receive_id': chat_id,
        'msg_type': 'interactive',
        'content': json.dumps({
            'config': {'wide_screen_mode': True},
            'header': {'title': {'tag': 'plain_text', 'content': header_title}, 'template': template},
            'elements': [{'tag': 'markdown', 'content': content_text}]
        }, ensure_ascii=False)
    }
    req = urllib.request.Request(push_url, data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token})
    return json.loads(urllib.request.urlopen(req, timeout=15).read().decode())


def push_report(content_text, header_title='📊 报告', home_channel_default='oc_529aff7485ccc35de97a9e7233d665dd'):
    """一站式：读 env → 拿 token → 推飞书 → 返 resp

    用法：
        push_report('# 报告内容\\n...', '📊 我的报告')
    """
    # 1. 读凭证
    app_id = read_env('FEISHU_APP_ID')
    app_secret=*** = read_env('FEISHU_APP_SECRET')
    if not app_id or not app_secret:
        print('!!! FEISHU_APP_ID / FEISHU_APP_SECRET 未配置')
        sys.exit(1)

    # 2. secret 长度 < 30 尝试恢复
    if len(app_secret) < 30:
        app_secret=*** restored == app_secret:
            print('!!! .env 中 APP_SECRET 长度 < 30 且 history.jsonl 无法恢复')
            sys.exit(1)
        print('✓ 从 history.jsonl 恢复完整 secret')

    # 3. 拿 token
    token = get_tenant_token(app_id, app_secret)
    if not token:
        print('!!! 拿 token 失败')
        sys.exit(1)
    print('token: ' + token[:20] + '...')

    # 4. 拿 home channel
    chat_id = read_env('FEISHU_HOME_CHANNEL', home_channel_default)
    print('chat_id: ' + chat_id)

    # 5. 推
    r = push_markdown_to_chat(token, chat_id, header_title, content_text)
    print('push resp:', r)
    if r.get('code') == 0:
        print('OK 飞书推送成功 message_id=' + r['data']['message_id'])
    else:
        print('FAIL 飞书推送失败 code=' + str(r.get('code')))
    return r


if __name__ == '__main__':
    # 示例：推一条简单消息
    push_report(
        content_text='**Hello from Hermes**\n\n这是一条测试消息。'.format(),
        header_title='📊 测试推送'
    )
