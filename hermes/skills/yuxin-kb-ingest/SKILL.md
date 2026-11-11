---
name: yuxin-kb-ingest
description: 渔芯知识库(lookforge.net/kb)读写统一入口。华哥/玉芬说「上传到知识库」「存进知识库」「入库」「沉淀」时调 kb_ingest 写；说「从知识库查找」「查知识库」「知识库里有没有」时调 kb_search 检索。四域 aqua/eng/ai/life 必须显式。所有智能体共享——调研结论/笔记/方案统一沉淀到此库。MCP 工具已全局接好，直接调用，无需配 token。
triggers:
  - 上传到知识库
  - 存进知识库
  - 从知识库查找
  - 查知识库
  - 知识库
  - 入库
  - 沉淀
  - kb_ingest
  - kb_search
version: "1.1"
created: 2026-11-06
updated: 2026-11-06
priority: high
---

# 渔芯知识库 · 读写统一入口（上传 + 检索）

> 2026-11-06 华哥定调：**所有智能体的调研数据统一沉淀到渔芯知识库**（生产库 lookforge.net/kb）。
> 读用 `kb_search`，写用 `kb_ingest`。MCP 工具 `yuxin-kb` 已全局接好（读写同一生产库），
> 本 skill 是共享正本，所有 agent 共用，直接调工具即可，无需配 token。

## 一、写（上传到知识库）：`kb_ingest`

华哥说「上传到知识库 / 存进知识库 / 入库 / 沉淀一下」时执行。

| 参数 | 必填 | 规则 |
|---|---|---|
| `title` | 是 | ≤300 字，具体到主题/对象（如「YJ-150 增氧机现场调试参数」） |
| `content` | 是 | Markdown 正文，≤200 万字符 |
| `domain` | 是 | `aqua` 养殖 / `eng` 工程 / `ai` 智能 / `life` 生活 |
| `source_url` | 否 | 原始链接（调研来源） |

正文结构：**结论先行 → 关键事实/数据 → 来源链接 → 日期**。
相同正文重复写入返回 `duplicate` + 原 `doc_id`（内容哈希去重，重传无害）。

## 一·补、MCP 工具未加载时的直连 HTTP 兜底

某些 session（cron 模式、`execute_code` 被 BLOCKED、未挂 `yuxin-kb` MCP）里没有 `kb_ingest` 工具。此时直接用 HTTP API 写库，打同一生产库，无需 MCP：

- 端点：`POST https://lookforge.net/v1/admin/ingest`
- 鉴权：`Authorization: Bearer <KB_ADMIN_TOKEN>`，token 在 `/Users/hua/.hermes/.env` 的 `KB_ADMIN_TOKEN=` 行
- body：`{"title","content","domain"}`（可选 `source_url`），JSON UTF-8
- 成功返回：`{"ok":true,"doc_id":"d_...","duplicate":false,"chunks":N,"embedded":true}`

端点/payload 与 `~/.hermes/scripts/kb_auto_sync.py` 的 `ingest()` 一致。终端里跑 `python3` 或 `curl` 均可；现成脚本见 `scripts/kb_ingest_direct.py`（读 .env token，不再硬编码）。

## 二、读（从知识库查找）：`kb_search`

华哥说「从知识库查找 X / 查知识库 / 知识库里有没有 X」时执行。

| 参数 | 规则 |
|---|---|
| `query` | 必填，问题或关键词 |
| `domain` | **强烈建议填**（aqua/eng/ai/life/all）；不填走全库，容易 504 超时 |
| `mode` | `keyword` 关键词（省 token，默认）/ `hybrid` 关键词+向量（语义） |
| `limit` | 返回条数，默认 5 |

返回片段带**标题 + 路径 + 相似度**，引用时标注来源标题。命中后可用 `kb_doc` 展开读全文。

## 三、域判定（判不准问华哥，不要猜）

- 养殖设备 / 工艺 / 病害 / 水质 / 品种 → `aqua`
- 图纸 / 结算 / 合同 / 报价 / 工程规范 → `eng`
- 论文 / 代码 / 提示词 / 评测 / AI 工具 → `ai`
- 笔记 / 灵感 / 生活 / 财务 / 健康 → `life`

## 四、验证

1. `kb_ingest` 返回 `doc_id` / 块数 / 向量化状态；
2. `kb_search`（带 domain）查标题关键词，确认命中；
3. MCP 已指向生产 `https://lookforge.net`（读写一致，不写本地开发库）。

## 五、失败处理

- `401/403`：token 失效（`KB_ADMIN_TOKEN` 在 `/Users/hua/.hermes/.env`），不要反复重试；
- `429`：写入口限流（30 次/分钟/客户端），稍后重试；
- `503`/超时：API 不可用，记录后稍后重试，不要烧 token 空转。

## 六、自同步兜底

玉芬已挂**自同步 cron**（`kb_auto_sync.py`，定时扫描 `rkr_staging/文档库/` 新笔记 → 批量 kb_ingest 增量上传，幂等）。
agent **主动上传仍是第一优先级**（结论即时进库）；自同步只兜底漏传的落盘笔记。

> 维护/改造自同步脚本时看 `references/kb-auto-sync-script.md`：时间窗口增量、永久失败 vs 可重试、PDF 垃圾检测、domain 路径先验、写限流、禁区清单。

## 七、铁律

- **四域必须显式**，禁止留空（空域 = 待复审脏数据）；
- 不把密码/密钥/手机号等敏感信息写进正文；
- 一次调研产出一篇，不要把多篇拼成一个文档；
- 写库前若正文含外部原文大段复制，先摘要改写，避免版权与噪声；
- **检索务必指定 domain**，全库 keyword 扫 54 万块会 504 超时。
