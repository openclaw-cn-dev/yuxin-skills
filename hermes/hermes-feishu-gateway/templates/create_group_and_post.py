"""Create a Feishu group via the agent's bot, then post a welcome message.

The bot is the group creator, so it is automatically a member. This means
you do NOT need the `im:chat.members:write_only` scope for this flow —
you only need that scope to add other people to the group afterwards
(the user does that in the Feishu GUI or via a separate API call with
that scope enabled).

Usage:
    python create_group_and_post.py <group-name> <agent-name>

Example:
    python create_group_and_post.py "RAS-客服部-测试" agent-cs
"""
import json
import sys
import urllib.error
import urllib.request


SECRETS_PATH = r"C:\Users\Administrator\feishu-secrets.json"
WELCOME_TEMPLATE = (
    "👋 我是 [agent-purpose] bot「小弟-[agent-name]」。\n\n"
    "把 [what-they-should-send] 发我，[sla]。\n"
    "涉及 [escalation-trigger]，我立刻同步老大处理。"
)


def get_token(app_id, app_secret):
    body = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["tenant_access_token"]


def http_post(url, body, token):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.read().decode("utf-8")[:500]}


def http_get(url, token):
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    group_name = sys.argv[1]
    agent_name = sys.argv[2]

    with open(SECRETS_PATH, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    agent = secrets["agents"][agent_name]
    app_id = agent["app_id"]
    app_secret = agent["app_secret"]

    token = get_token(app_id, app_secret)
    print(f"Got token (…{token[-6:]})")

    # 1) Create the group. permission_version: "v2" is mandatory.
    create_body = {
        "name": group_name,
        "description": f"{agent['purpose']}（自动创建 by 小弟）",
        "permission_version": "v2",
    }
    resp = http_post("https://open.feishu.cn/open-apis/im/v1/chats", create_body, token)
    if resp.get("code") != 0:
        print(f"❌ 建群失败: {resp.get('msg')}")
        sys.exit(1)
    chat_id = resp["data"]["chat_id"]
    print(f"✅ 群已创建: {group_name} ({chat_id})")

    # 2) Post a welcome message. Bot is in the group as creator.
    welcome = WELCOME_TEMPLATE.replace("[agent-purpose]", agent["purpose"]).replace(
        "[agent-name]", agent_name
    )
    msg_body = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": welcome}, ensure_ascii=False),
    }
    msg_resp = http_post(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        msg_body,
        token,
    )
    if msg_resp.get("code") == 0:
        print(f"✅ 欢迎消息已发送")
    else:
        print(f"⚠️  消息发送失败（群已建好）: {msg_resp.get('msg')}")

    print(f"\n👉 下一步: 把老大拉进这个群 (chat_id={chat_id})")
    print(f"   用户可在飞书 GUI 群设置 → 群机器人 → 添加 自己")


if __name__ == "__main__":
    main()
