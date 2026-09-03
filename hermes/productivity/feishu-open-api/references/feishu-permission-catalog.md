# 飞书 permission scope catalog — by use case

When creating a new agent app, these are the scopes to grant per role. Each scope is added under 权限管理 in the 飞书开发者后台. For each scope, ensure both `user` and `tenant` token types are checked.

## Universal (every bot needs these)

| Scope | Why |
|---|---|
| `im:message` | Send messages (text + cards) |
| `im:message.send_as_user` | Send messages that look like they're from a user (for forwarded alerts) |
| `im:message.group_at_msg:readonly` | Read @-bot messages in groups |
| `im:message.p2p_msg:get_as_user` | Read direct messages to the bot |
| `im:message.group_msg:get_as_user` | Read group messages the bot is mentioned in |
| `im:chat` | Read/write group metadata |
| `im:chat:read` | List chats the bot is in |
| `im:chat.moderation:write_only` | Update chat config (e.g. add a member, set announcement) |
| `im:chat.announcement:write_only` | Post group announcements |
| `im:resource` | Upload/download media in messages |
| `contact:user.employee:readonly` | Look up employees by open_id / email / mobile |
| `contact:contact.base:readonly` | Read contact directory |
| `cardkit:card:write` | Send interactive card messages (the recommended UX for bot replies) |

## Per-role add-ons

### 销售 Agent
- `im:message.send_as_user` (already in universal — keep)
- `contact:user.id:readonly` — resolve open_id ↔ user_id
- `drive:file` — attach PDF quotes
- `docs:document.media:download` — pull customer-shared docs

### 研发 Agent
- `docs:doc:readonly` — read technical docs in the tenant
- `docx:document:readonly` — read docx files
- `sheets:spreadsheet:readonly` — read spec sheets
- `drive:file` — attach generated CAD/工艺图 PDFs
- `application:bot.basic_info:read` — read sibling bot info for cross-agent handoff

### 生产 Agent
- `approval:definition` — define approval flows for 工单
- `approval:instance:read` — check approval status
- `task:task:write` — create tasks (排产工单)
- `task:tasklist:write` — create task lists
- `task:comment` — comment on tasks
- `calendar:calendar.event:create` — schedule production milestones

### 营销 Agent
- `im:datasync.feed_card.time_sensitive:write` — push time-sensitive feed cards (the daily briefing)
- `im:message.urgent.status:write` — mark a message as urgent
- `im:chat.top_notice:write_only` — pin a brief to the top of a chat
- `wiki:space:read` — pull from wiki-based brand playbooks
- `drive:file` — attach generated images / cover art

### 总控 Agent (the "GG" supervisor)
- Everything from all 4 roles (it's the supervisor — needs full visibility)
- `corehr:corehr:readonly` — read org chart (optional, for routing)
- `directory:employee.base.base:read` — directory lookups
- `report:report` — read BI dashboards

## How to probe what an existing app already has

```python
# scripts/feishu_probe_app.py
import urllib.request, json, ssl, sys

APP_ID = "<FEISHU_APP_ID>"
with open(r"D:\Users\Administrator\feishu_token.json") as f:
    token = json.load(f)["tenant_access_token"]

ctx = ssl.create_default_context()
def get(path):
    req = urllib.request.Request(
        f"https://open.feishu.cn{path}",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        return json.loads(r.read().decode())

app = get(f"/open-apis/application/v6/applications/{APP_ID}?lang=zh_cn&user_id_type=open_id")
print("App name:", app["data"]["app"]["app_name"])
print("Bot ability (mobile):", app["data"]["app"]["mobile_default_ability"])
print("Callback type:", app["data"]["app"]["callback_info"]["callback_type"])
print("Subscribed callbacks:", app["data"]["app"]["callback_info"]["subscribed_callbacks"])
print("Granted scopes (count):", len(app["data"]["app"]["scopes"]))
print("Sample scope names:")
for s in app["data"]["app"]["scopes"][:5]:
    print(" ", s["scope"], "—", s["description"], "(level", s["level"], ")")
```

Output for the "GG" app in this tenant: 400+ scopes, including all 4 agent role scopes. Lesson: **don't assume you need to grant everything — probe first.**
