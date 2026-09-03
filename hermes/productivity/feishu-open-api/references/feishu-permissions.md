# Feishu Bot Permission Checklist

**Always read the full error JSON on failure.** The "silent failure" mode is:
- Code returns `code: 99991672` or `code: 230xxx` with `msg: "Lack of necessary permissions, ext=need scope: xxx"`
- The operation does NOT raise an exception
- Your script keeps running, no message sent, no error visible

## Required permissions by operation

| Operation | API | Required scope | URL pattern |
|---|---|---|---|
| Read user/bot info | `bot/v3/info` | (default) | — |
| List chats bot is in | `im/v1/chats` GET | (default) | — |
| Create chat (bot-owned) | `im/v1/chats` POST | `im:chat` | `?q=im:chat` |
| Delete chat (only if bot is owner) | `im/v1/chats/{id}` DELETE | `im:chat`, `im:chat:delete` | `?q=im:chat,im:chat:delete` |
| **Read group messages** ← silent killer | `im/v1/messages` GET | **`im:message.group_msg`** | `?q=im:message.group_msg` |
| Send message to chat | `im/v1/messages` POST | `im:message:send_as_bot` | `?q=im:message:send_as_bot` |
| Add member (incl bot) to chat | `im/v1/chats/{id}/members` POST | `im:chat.members:write_only` | `?q=im:chat.members:write_only` |
| List chat members | `im/v1/chats/{id}/members` GET | (default) | — |

## Quick-grant URL template

```
https://open.feishu.cn/app/{APP_ID}/auth?q={SCOPE1},{SCOPE2}&op_from=openapi&token_type=tenant
```

For 4-bot ops split (销售/研发/生产/客服), apply to all 4 apps.

## Approval flow

- **Custom apps** (企业自建应用): grant → auto-approve, instant
- **Enterprise apps** (ISV / market apps): grant → needs admin approval, 5-30 min
- If user is not admin, they get "无权限申请" error and need to escalate

## Verify a permission is active

```python
# Try the read messages API. If "Lack of necessary permissions" → still missing.
r = requests.get(
    "https://open.feishu.cn/open-apis/im/v1/messages",
    headers={"Authorization": f"Bearer {token}"},
    params={"container_id_type": "chat", "container_id": chat_id, "page_size": 1}
)
d = r.json()
if d.get("code") == 99991672:
    print("STILL MISSING:", d["error"]["permission_violations"])
elif d.get("code") == 0:
    print("OK")
```

## Common false-positive cases

- `Bot/User can NOT be out of the chat` — bot isn't in this chat. NOT a permission issue.
  The bot must be **actually added** to the chat (user does this in UI or bot is owner
  from creating it). Check `GET /im/v1/chats` with bot token — if your chat doesn't
  appear, the bot is not really in it. UI often lies ("invited" ≠ "added").

- `Bad Request` from `POST messages` with `json=...` kwarg — likely the `json`
  kwarg got mangled by the string filter (see `hermes-quirks.md` #1). Use
  `data=json.dumps(...).encode()` with `Content-Type: application/json; charset=utf-8` header.

## The "用户说加了机器人, list_chats 看不到" diagnostic (高发场景, 2026-06-06 三连踩)

**症状** (出现概率: **每次部署都中**):

```
老大: "我已经把你拉进去了"
你调 GET /im/v1/chats 用 bot token
→ 列表里没有老大建的新群
→ 群里发消息: 30 秒 / 1 分钟 / 永远没回复
```

**根因** (3 种, **按概率排序**):

1. **加的是"别的 App"** (最常见) — 老大在飞书 App GUI 加的机器人 ≠ 小弟有 Secret 的那个
   - 比如老大建了个"总控机器人"App, 加进了群
   - 但小弟 4 套 Secret 是 agent-sales/rd/prod/cs, **没有总控机器人**
   - 老大以为"加的就是机器人", **其实加的是另一个 App**
   - **解法**: 让老大在群里 → 群设置 → 群机器人 → 看机器人列表里的**真实名字**; 老大**截图**小弟**立刻知道**

2. **加对了 App, 但还没"激活"** (次常见)
   - 飞书有个**冷启动**问题: 机器人加进群后, 必须**收到至少 1 条群消息**才会出现在 `list_chats` 里
   - 老大在群里发了消息, 但**机器人还没收到** (异步同步, 1-2 分钟)
   - **解法**: **等 2 分钟** + **重跑 list_chats**; 或者让老大在群里**@ 一下机器人**触发

3. **App 没发布版本** (少见但致命)
   - 即使机器人被加进群, **App 没发版** = 飞书认为这个 App "不在线" = **永远响应不了**
   - **解法**: 飞书开放平台 → App → 版本管理 → 创建版本 → 申请发布

**诊断 SOP** (30 秒内定因):

```python
TP = os.path.expanduser("~/feishu-tokens.json")
T = json.load(open(TP))
url = "https://open.feishu.cn/open-apis/im/v1/chats"
r = requests.get(url, headers={"Authorization": "Bearer " + T["agent-sales"]}, params={"page_size": 50}, timeout=10)
chats = r.json().get("data", {}).get("items", [])

NEW_CHAT = "oc_老大给的id"
found = any(c["chat_id"] == NEW_CHAT for c in chats)
if not found:
    print("销售小成不在这个群")
    print("老大在群里 -> 群设置 -> 群机器人")
    print("如果列表里有机器人, 截图给我看名字")
    print("如果列表里没机器人, 老大需要: 添加 -> 销售小成")
else:
    print("销售小成在群里, 问题在别处")
```

**关键启示** (给小弟的): **永远用 list_chats 验证, 不要相信老大的"已经加了"**。**老大没说谎**, 飞书 GUI 和 API 之间有 3-5 分钟的同步延迟, 加上"加错 App"的人为错误, 至少 50% 的"机器人不回消息"案例根因在这里。

## Wipe-and-rebuild cycle (2026-06-06 高频模式)

**模式** (一次会话内**完整经历一次**):

```
阶段 1: 部署 5 bot + 6 群 + 14 skill + 5 profile
阶段 2: 老大说"全部删掉 不要用原来那套方案"
阶段 3: 删 5 profile + 删 14 skill + 删 6 群 (老大手动)
阶段 4: 老大建新群, 改业务线, 重新拉机器人
阶段 5: 老大说"按我的指令执行, 处理好群组消息不回的问题"
```

**这个 cycle 的 3 个硬约束**:

1. **删 secrets.json = 永久丢失**: 之前小弟加密存了 4 套 Secret 在 `~/feishu-secrets.json`, 删了之后**必须老大重发**才能继续用飞书 API
2. **删 profile = 删 chat history + 群关系**: hermes 内部的 profile 删了, 飞书那边的**群还在** (群里还有机器人, 但 token 拿不到)
3. **重启 session 后 memory 清空**: 用户说"删除之前关于这方面的记忆", 实际是把所有 ras-/feishu- 相关文件 + 老 skill 全部 `rm -rf`

**给小弟的 SOP** (用户说"全部删掉"时):

```bash
# A. 删 profile (不能批量, 一个一个来)
for p in ras-sales ras-rd ras-production ras-marketing ras-boss; do
  hermes profile delete $p -y
done

# B. 删 skill (两棵树)
rm -rf ~/.hermes/skills/domain/ras-*
rm -rf ~/.hermes/skills/social-media/ras-*
for p in ~/.hermes/profiles/*/skills/; do
  rm -rf $p/domain/ras-*
  rm -rf $p/social-media/ras-*
done

# C. 删临时文件 (小弟之前写的)
rm -f ~/feishu-*  ~/new_group_chat_ids.json  ~/feishu_seen_message_ids.json

# D. 删 output 文档
rm -f ~/AppData/Local/hermes/output/ras-*

# E. 飞书群: 小弟**没有 im:chat:delete 权限**, 让老大手动解散
```

**关键** (用户说"现在只群了一个群"后): **不要问"之前那些群要不要删"**, 用户已经说了"全部删掉"; **直接问"新群 ID 是啥"**, 把 100% 注意力放到新方向上。**这是 concise-output 的 anti-pattern 5 的具体场景**。
