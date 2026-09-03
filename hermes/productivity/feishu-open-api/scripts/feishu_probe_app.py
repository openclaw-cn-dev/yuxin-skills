# -*- coding: utf-8 -*-
"""feishu_probe_app.py — dump an app's identity and granted scopes.

Use this BEFORE building anything: you may find the app already has all
the scopes you need. (The "GG" app in this tenant had 400+ scopes granted.)

Usage:
    python feishu_probe_app.py <app_id> [token_cache.json]
"""
import urllib.request, json, ssl, sys


def _get(token, path):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        f"https://open.feishu.cn{path}",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def probe(app_id, token):
    res = _get(token, f"/open-apis/application/v6/applications/{app_id}"
                       f"?lang=zh_cn&user_id_type=open_id")
    if res.get("code") != 0:
        print(f"FAIL: {res}")
        return
    app = res["data"]["app"]
    print(f"=== {app.get('app_name')} ({app_id}) ===")
    print(f"描述:        {app.get('description')}")
    print(f"创建源:      {app.get('create_source')}")
    print(f"创建者:      {app.get('creator_id')}")
    print(f"Bot (PC):    {app.get('pc_default_ability')}")
    print(f"Bot (移动):  {app.get('mobile_default_ability')}")
    cb = app.get("callback_info", {})
    print(f"回调类型:    {cb.get('callback_type')}")
    print(f"订阅事件:    {cb.get('subscribed_callbacks')}")
    print(f"owner type:  {app.get('owner', {}).get('type')}")
    scopes = app.get("scopes", [])
    print(f"已开通 scopes 数: {len(scopes)}")
    # Bucket scopes by category for the report
    by_cat = {}
    for s in scopes:
        cat = s["scope"].split(":")[0]
        by_cat.setdefault(cat, []).append(s["scope"])
    print("\n按一级分类分布:")
    for cat in sorted(by_cat):
        print(f"  {cat:25s}  {len(by_cat[cat]):3d} 个")
    # Highlight the most relevant ones for IM/bot work
    must_have = [
        "im:chat", "im:message", "im:message.send_as_user",
        "im:message.p2p_msg:get_as_user", "im:message.group_msg:get_as_user",
        "im:chat.moderation:write_only", "contact:user.employee:readonly",
        "cardkit:card:write", "docs:doc:readonly", "docx:document:readonly",
    ]
    granted = {s["scope"] for s in scopes}
    print("\n通用 IM 权限核对:")
    for m in must_have:
        print(f"  {'✓' if m in granted else '✗'}  {m}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python feishu_probe_app.py <app_id> [token_cache.json]")
        sys.exit(1)
    app_id = sys.argv[1]
    cache = sys.argv[2] if len(sys.argv) > 2 else r"D:\Users\Administrator\feishu_token.json"
    with open(cache, "r", encoding="utf-8") as f:
        token = json.load(f)["tenant_access_token"]
    probe(app_id, token)
