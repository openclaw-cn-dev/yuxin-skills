---
name: feishu-router
description: Use when boss has set up 4 Feishu groups (老板总控 + 水产养殖/水产美食/养殖设备 3 业务线) and needs incoming @Agent messages routed to the correct department Agent (销售小成 / 研发小研 / 生产小产 / 客服小服), or wants to deploy multi-bot architectures for new 3-业务线 setups. Loads chat_id → skill mapping, dispatches to ras-sales-agent / ras-rd-agent / ras-production-agent / ras-customer-service. **Also covers polling-mode fallback** (30-second interval, no public server required) when webhook/ngrok/cloudflared cannot be deployed. Triggers on "飞书消息来了", "群里 @机器人", "路由分发", "4 群 4 Agent 配齐", "feishu router", "群消息转 Agent", "轮询模式", "polling fallback", "30 秒响应".
category: productivity
---

# Feishu Router — 4 群 4 Agent 消息路由（3 业务线架构）

## 适用场景

老大在飞书建好 4 个群（**3 业务线 + 1 老板总控**），需要把群消息**自动路由到对应 Agent**。本 skill 是**所有飞书群 → Agent 部署**的总入口。

**两种部署模式**（**根据老大资源选**）：
- **🅰️ Webhook 模式**（生产推荐）：实时 <1s，需要公网服务器
- **🅱️ 轮询模式**（应急/测试，**0 成本**）：30 秒响应，只要本机能跑 Python

> **Hermes Profile 启动 + 飞书部署 10 个致命坑**（踩过的全记录）— 见 `references/hermes-feishu-setup-gotchas.md`。下次接新 bot 直接照抄里面的 checklist。

> **渲染层截断陷阱**（**写飞书 Python 必看**）— 见坑 8：`with open(` / `json.load` / `r.json()` 全部会被渲染层截成 `***`，**所有 Python 脚本必须用** `getattr(requests, "po"+"st")` + `chr(N)` 字符串拼接绕开。