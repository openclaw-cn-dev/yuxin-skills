# Multi-agent 飞书 department — architecture and onboarding

This is the design pattern for "spin up an N-agent AI company inside one 飞书 tenant". Verified during the 2026-06-06 build of a 5-agent RAS aquaculture company.

## Why N apps, not 1

飞书 has a hard rule: **one enterprise self-built app = one bot identity**. There is no API to create apps, and one app cannot impersonate multiple bots. So if you want N AI agents that each look like a distinct person in a 飞书 group, you need N apps.

Bonus: each agent can be granted a *minimal* scope set, so a sales agent can't accidentally call corehr or read other departments' docs.

## Topology

```
┌────────────────────────────────────────────────────────────┐
│  飞书 tenant                                              │
│                                                            │
│  ┌─────────────────┐    ┌──────────────────┐             │
│  │ RAS 销售 Agent  │    │ RAS 研发 Agent   │   ... N apps  │
│  │ App: cli_xxx1   │    │ App: cli_xxx2    │              │
│  │ Scopes: im,     │    │ Scopes: im,      │              │
│  │   contact       │    │   docs, cardkit  │              │
│  └────────┬────────┘    └────────┬─────────┘              │
│           │                     │                          │
│  ┌────────▼────────┐  ┌─────────▼────────┐  ┌───────────┐ │
│  │ 🎯 销售部群     │  │ 🛠 技术部群     │  │ 🧠 总控室 │ │
│  │ oc_...8f53      │  │ oc_...4e4e1     │  │ oc_...d65d│ │
│  │ (5 members)     │  │ (3 members)     │  │ (all)     │ │
│  └─────────────────┘  └──────────────────┘  └───────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────┐             │
│  │ 小弟 (Hermes)  on host:                  │             │
│  │   - token cache (N files)                │             │
│  │   - webhook router (or WS client)        │             │
│  │   - skill registry (per-agent)           │             │
│  │   - cron / event bus                     │             │
│  └──────────────────────────────────────────┘             │
└────────────────────────────────────────────────────────────┘
```

## 老大's 5-min checklist (per agent)

Repeat verbatim for each new agent:

1. **Open** https://open.feishu.cn/app — log in as 老大
2. **Click** 创建企业自建应用
3. **Fill**:
   - App 名称: `RAS {role} Agent` (e.g. `RAS 销售 Agent`)
   - App 描述: `AI Agent / 智能部门员工 / 接入 hermes-agent 路由`
   - 应用图标: skip (default)
4. **权限管理** — search and grant each scope from the role's permission list (see `feishu-permission-catalog.md`). For each scope, ensure both `user` and `tenant` token types are checked.
5. **应用能力 → 机器人 → 启用**
6. **事件订阅** — pick one:
   - 长连接接收 (recommended for 1-3 bots, no public URL needed)
   - Webhook (for >3 bots or when integrating with existing ingress)
7. **版本管理与发布** → 创建版本 v1.0.0 → 备注 `AI Agent 初始化版本` → 提交发布
8. **Send back** the 2 values: `App ID` + `App Secret` (one line each, e.g. `cli_xxx1\tSECRETxxx1`)

## 小弟's 7-step takeover (per agent, after receiving ID/Secret)

For each new app:
1. Cache the token via `scripts/feishu_token_cache.py`
2. Probe the app's actual granted scopes via `scripts/feishu_probe_app.py` (sanity check)
3. Add the bot to its designated business chat (call `POST /open-apis/im/v1/chats/{chat_id}/members` with the bot's open_id — requires that app's `im:chat` scope)
4. Register a handler for inbound messages (either via WS or webhook)
5. Wire the agent's skill set (each agent maps to a specific skill or set of skills)
6. Smoke-test with a 1-message round trip
7. Update the daily briefing (if marketing agent) cron schedule

Total per agent: ~4 minutes. For 5 agents: ~20 minutes.

## 老大's group layout (created programmatically)

| Group name | chat_id | Agent | Members |
|---|---|---|---|
| 🎯 RAS 销售部｜客户询盘分发 | oc_526cf104b447ef3195916edc07895fc4 | 销售 | 销售Agent, 老大, ... |
| 🛠️ RAS 技术部｜方案与图纸 | oc_6b343e07ab2584adfd16da8d8e54e4e1 | 研发 | 研发Agent, 老大, ... |
| 🏭 RAS 生产部｜订单与排产 | oc_118c24939fa3f375d0acbc5aa0763562 | 生产 | 生产Agent, 老大, ... |
| 📣 RAS 营销部｜内容生产 | oc_da277dd20ceb9d29ad74bcf245cae3b9 | 营销 | 营销Agent, 老大, ... |
| 🧠 RAS 总控室｜5 Agent 协同 | oc_e546349f3578683885c2edc4c6bf965d | 总控 | 全部Agent, 老大, GG |

## Cross-agent routing

When 销售Agent gets a customer inquiry:
1. Auto-reply with quote from the sales skill
2. If the customer asks for an equipment plan, 销售Agent posts to 技术部群 mentioning 研发Agent
3. 研发Agent picks it up, runs `ras-rd-agent` skill, posts back
4. 老大 gets a summary in 总控室

Implementation: a small router that reads `event.chat_id` and forwards to the agent's handler. No queue broker needed at this scale — synchronous in-process is fine.

## Token storage convention

```
D:\Users\Administrator\
  feishu_token.json              # "GG" / 总控 app
  feishu_token_sales.json       # sales agent app
  feishu_token_rd.json          # R&D agent app
  feishu_token_production.json  # production agent app
  feishu_token_marketing.json   # marketing agent app
```

Each file: `{"app_id", "tenant_access_token", "expire", "expire_at"}`. The cache script handles 10-min-pre-expiry refresh.
