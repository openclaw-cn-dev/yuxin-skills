---
name: feishu-ops
description: "飞书自动化运维类级技能（一个入口管全部飞书 API 面）— Bot 凭据与 token 获取、群/DM 通道实时发现（不硬编码 chat_id）、多维表格 Bitable 建表写数、云盘文件夹/上传/跨 Bot 共享限制、Wiki 知识库 Bot 权限限制与 OAuth 用户身份方案、任务收件箱巡检。触发：任何飞书机器人脚本/报告发送/云盘与知识库操作/多维表格监控/报错 230002、232009、1063002、99991663、1770001、1061044 时加载。核心铁律：chat_id 永远实时枚举不硬编码；token 每次重取不缓存；跨 Bot 分享用 ECS 共享目录不走云盘。"
license: MIT
metadata:
  author: 渔芯科技
  version: "1.0.0"
  created: "2026-09-17 curator consolidation"
  absorbed: [feishu-bitable, feishu-channel-discovery, feishu-wiki-operations, feishu-bot-cloud-drive]
---

# 飞书自动化运维（Feishu Ops）

> 按小节取用对应 API 面；完整流程与脚本照抄对应 reference。凭据统一在 `~/.hermes/.env`（FEISHU_APP_ID / FEISHU_APP_SECRET）。

## §0 通用铁律（所有 API 面共用）

1. **tenant_access_token 每次运行重新取**（约 2h 有效，不要缓存）：
   `POST /open-apis/auth/v3/tenant_access_token/internal`
2. **chat_id 永远不硬编码** — Bot 的群/DM 成员关系会随用户手动调整而变化，硬编码必然失效。发送前实时枚举 `/open-apis/im/v1/chats` 按 name 匹配。
3. 国内版域名 `https://open.feishu.cn`（国际版 `open.larksuite.com`）。

## §1 通道发现与消息发送

**报错路由**：230002（Bot 不在 chat）/ 232009（chat 已解散）/ 99991663（token 过期）→ 全部走实时枚举流程：每次重取 token → `GET /open-apis/im/v1/chats?page_size=50` → 按 name 匹配目标 → 发送。完整 Python 模板见 `references/feishu-channel-discovery.md`。channel 状态快照样例同文件。

## §2 多维表格 Bitable（把数据做成在线看板）

概念：app（app_token）→ table（table_id）→ field（列）→ record（行）。流程：取 token → `POST /open-apis/bitable/v1/apps` 建表 → fields 加列（type：1 文本/2 数字/3 单选/5 日期/11 人员/17 附件）→ `records/batch_create`（≤500 条/批）。可复用脚本 `~/.hermes/scripts/tokens_to_bitable.py`。完整流程见 `references/feishu-bitable.md`。

## §3 云盘与跨 Bot 协作

- 云盘（Drive）Bot 用 tenant token 可建文件夹/文档；**Wiki 空间创建必须 user_access_token**（99991663 = 拿 Bot token 干 Wiki 的事）。
- **飞书平台禁止 Bot 之间互相分享文件夹（code 1063002）**——平台级限制，与 App 权限无关；跨机器 Agent 协作用 **ECS 共享目录**，不走云盘分享。
- Docx block 类型权限：Bot token 只支持 text/heading/divider，bullet/ordered/code/quote 返回 1770001（整段合并为一个 text block 写入）。
- 巡检脚本 `scripts/cron_drive_check_v2.py`（2026-06-20 修复版：EditedTime 修正 + sanitizer-safe token 写入 + 动态 agent 查找）。注意 `/tmp` 拷贝运行时相对路径失效坑。详见 `references/feishu-bot-cloud-drive.md`。

## §4 Wiki 知识库

- 已知知识库 node_token 清单 + MCP 限制（wiki_search 只见 Bot 可见内容、无 wiki_node_create）见 `references/feishu-wiki-operations.md`。
- **OAuth 用户身份方案**：`npx @larksuiteoapi/lark-mcp login` 必须在用户本人 Mac 终端跑（Agent 终端 OAuth 交互会超时），绕开 Bot 权限。
- 认证/文件枚举/错误码速查：`references/feishu-wiki-api-base.md`（每次心跳任务先查）。
- **Agent 任务收件箱真相**：cron 提示的 `任务派发/{agent}/` 路径是错的，真实收件箱在 `{agent}/任务派发/{agent}/{实例}/`。见 `references/***SECRET***.md` + `scripts/check_study_helper_inbox.py`。

## §5 相关

- 发消息用 Hermes 原生 send_message（platform:oc_xxx）优先于手写 API；cron 报告走 origin auto-delivery，不手动 send（防 duplicate_target）。
- `productivity/feishu-api-notify` — 直发 REST 通知的完整凭据/签名细节（保留独立入口）。
- `productivity/feishu-drive-file-management` — 云盘文件管理 844 行主技能（保留独立入口）。
