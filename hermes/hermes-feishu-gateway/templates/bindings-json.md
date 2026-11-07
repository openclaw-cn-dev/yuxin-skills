# feishu-bot-bindings.json 模板

存到 `~/feishu-bot-bindings.json`。每次 `list_feishu_chats.py` 跑完同步更新。

## 范例（2026-06-06 RAS 3-Agent）

```json
{
  "_comment": "3 个飞书 App 在 hermes 里的绑定关系。老大后续修改 SOUL.md 或换群绑这里查。",
  "agents": {
    "agent-sales": {
      "app_id": "cli_REDACTED_0001",
      "purpose": "飞书销售群自动接单/报价/跟进",
      "groups": [
        {"name": "RAS-销售部-测试",     "chat_id": "oc_REDACTED_grp1"},
        {"name": "RAS-老板总控",        "chat_id": "oc_REDACTED_grp2"},
        {"name": "抖音营销组",           "chat_id": "oc_REDACTED_grp3"},
        {"name": "总控群",              "chat_id": "oc_REDACTED_grp4"}
      ]
    },
    "agent-rd": {
      "app_id": "cli_REDACTED_0002",
      "purpose": "飞书研发群答技术问答/写方案",
      "groups": [
        {"name": "RAS-推广部-测试",     "chat_id": "oc_REDACTED_grp5"},
        {"name": "小红书营销组",         "chat_id": "oc_REDACTED_grp6"},
        {"name": "总控群",              "chat_id": "oc_REDACTED_grp4"}
      ]
    },
    "agent-prod": {
      "app_id": "cli_REDACTED_0003",
      "purpose": "飞书生产群排产/工单/调度",
      "groups": [
        {"name": "RAS-生产部-测试",     "chat_id": "oc_REDACTED_grp7"},
        {"name": "知识库",              "chat_id": "oc_REDACTED_grp8"},
        {"name": "总控群",              "chat_id": "oc_REDACTED_grp4"}
      ]
    }
  },
  "common": {
    "总控群": "oc_REDACTED_grp4"
  }
}
```

## 字段说明

- `_comment` — 维护提示，老大后续修改看
- `agents.<name>.app_id` — 飞书 AppID
- `agents.<name>.purpose` — 一句话用途
- `agents.<name>.groups[]` — 该 bot 已加的群
  - `name` — 群显示名（可改）
  - `chat_id` — 飞书群 ID（永久不变，rename 群不会改这个）
- `common.<群名>` — 多个 bot 都在的群（**总控群**就是这种，多 agent 协同用）

## 用法

- 改 SOUL.md 时查 `<agent-name>` 对应 `purpose` 确认职责
- 调试消息发送问题查 `chat_id`
- 加新群后跑 `list_feishu_chats.py` 重生
