#!/usr/bin/env python3
"""飞书推送简报到老板群 — 2026-06-08 实测通
用法：python feishu_push.py <md_path>
"""
import json, urllib.request, urllib.error, sys, os

APP_ID = "<FEISHU_APP_ID>"
APP_SECRET = "<FEISHU_APP_SECRET>"  # 老大自己填值（历史曾泄漏已红化）
CHAT_ID = "<FEISHU_CHAT_ID>"  # 老板总控群 chat_id（老大自己填值，历史曾泄漏已红化）

def push(md_path):
    if not os.path.exists(md_path):
        print("❌ no file:", md_path); return
    # token
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        token = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())["tenant_access_token"]
    except Exception as e:
        print(f"❌ token err: {e}"); return

    # 卡片（注意：字段是 content 不是 card，否 99992402）
    card = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": f"🌊 每日水产简报 | {os.path.basename(md_path)}"}, "template": "blue"},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": "**今早 9:00 自动生成**\n简报已存桌面。点按钮直接打开。"}},
            {"tag": "action", "actions": [
                {"tag": "button", "text": {"tag": "plain_text", "content": "📂 打开桌面知识库"}, "type": "primary",
                 "url": f"file:///{md_path.replace(chr(92), '/')}"},
                {"tag": "button", "text": {"tag": "plain_text", "content": "📄 看简报"}, "type": "default",
                 "url": f"file:///{md_path.replace(chr(92), '/')}"}
            ]},
            {"tag": "note", "elements": [{"tag": "plain_text", "content": "🤖 自动推送 · 每天 9:00"}]}
        ]
    }
    msg = {"receive_id": CHAT_ID, "msg_type": "interactive", "content": json.dumps(card)}
    url2 = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    req2 = urllib.request.Request(url2, data=json.dumps(msg).encode(),
                                  headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
    try:
        j = json.loads(urllib.request.urlopen(req2, timeout=10).read().decode())
        if j.get("code") == 0:
            print(f"✅ Pushed: message_id={j['data']['message_id']}")
        else:
            print(f"❌ {j.get('code')} {j.get('msg')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "230002" in body:
            print("❌ App 不在群里（230002），老大手动把 App 拉进群")
        elif "99992402" in body:
            print("❌ 卡片字段错（99992402），用 content 不是 card")
        else:
            print(f"❌ HTTP {e.code}: {body[:200]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        from datetime import date
        md = f"C:/Users/Administrator/Desktop/知识库/{date.today()}-水产简报.md"
    else:
        md = sys.argv[1]
    push(md)
