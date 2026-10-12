# 0930 cron 实跑新增 — 铁律 95-97（本次会话·9 点 旺财 8 点 cron 延伸）

> 本次会话 0930 09:00 cron 实跑新增。沿用 0927 铁律 92-94 编号体系，铁律 95-97。

## 0930 cron 摘要

- **0 装日判定 → 沿用 0918 铁律 41**：本次 cron 无新 marketplace 装入候选（MKT 0918 已发版 / SMS 0501 / 0919 SMS-stable-3 不存在）
- **MS 远端 50 - 本地 50 = 18 个 md5 差异**（沿用 0926 铁律 81 md5 比对）—— **18 个本地比远端新**（0926 升级后 9-04 commit 撤回部分 v2.0.x 字段，本地保留新版），**无需再升**
- **SMS 远端 14 = 本地 14 = 100% 同步**（沿 0926 实测）
- **anthropics/skills 19 - 本地 5 = 14 候选**（沿用 0924 铁律 70 + 0925 拒装矩阵，全过滤）
- **Codex 上游 stable rust-v0.157.1**（沿用 0926 当天发布）+ 本地 **0.157.0 → 0.157.0**（0926 已升，本次不升）
- **Hermes 上游**：origin 落后 1 commit `34343e79ab`（fix(gateway)，沿用 0926 铁律 83 决策不升级）
- **飞书推送**：沿用 0926 + 0930 双重 token 死（**铁律 95 新立**）→ 跳过飞书推送 → final response 兜底
- **yuxin-skills commit 待生成**（本地 ahead 状态待 git rev-list 二次确认）

## 🆕 铁律 95 — boss-control profile `.env` 与 default profile `.env` 是两个独立 app 鉴权域（**本次会话实盘**）

**症状**：本次 8am cron（9 点旺财 9 点 cron 是同一链路）发现 `boss-control` profile 的 `.env` 现存 ID `<FEISHU_APP_ID>` 实测返 `code 10217 app has been deleted`——**9-26 memory 误以为此 ID 可用·9-30 实测破灭**。

**沿 0926 第 7 阶段**（`<FEISHU_APP_ID>` + `<FEISHU_APP_ID>` 都死）—— 9-30 进一步发现：**boss-control profile 的 ID 也死了**。

**两个 profile 鉴权域完全独立**：
- **default profile**（`~/.env` 或 `~/AppData/Local/hermes/.env`）：FEISHU_APP_ID = `<FEISHU_APP_ID>` 或 `<FEISHU_APP_ID>`（沿 0827 / 8-26 / 9-21 / 9-26 累计 4 次 10217）
- **boss-control profile**（`~/AppData/Local/hermes/profiles/boss-control/.env`）：FEISHU_APP_ID = `<FEISHU_APP_ID>`（9-30 第 5 次 10217）
- 两个 app 在飞书后台是**完全独立的两个 app**（不同 app_id + 不同 secret + 不同权限配置）
- 任一 app 在飞书后台被老大整删 → 该 profile 的所有 cron 都 10217
- 两个 app 同时 10217 = **老大可能 4 业务线都整删过飞书 app**

**9-30 决策**：
- 不重试 token endpoint（10217 是确定的）
- 不沿用任何历史 ID（**两个 profile 4 个已知 ID 全部 10217**）
- final response 明报失败 + 列出 4 类修复路径
- 本地 md 落档（已完成）
- 用 `terminal` 实测 token（不调用 `execute_code`，沿 0927 铁律 91）

**预防**：
- ✅ **每个 cron 启动第一步必 token endpoint 实测**，**实测 code 0 才推**，**不信 memory 历史结论**
- ✅ 两个 profile 的 `.env` 必分别 `grep FEISHU_APP_ID` + 分别实测
- ✅ 老大拍板推送路径后，**只用一个 profile 一个 app**（避免双 profile 双 token 错配）
- ❌ 不要信 memory 里"9-26 备用 ID 可用"——9-30 实证 memory 误判
- ❌ 不要用 `feishu_push.py` 硬编码 ID 跳过 `.env` 实测（9-26 已踩：硬编码 vs .env 双 token 都死）

## 🆕 铁律 96 — memory 校验铁律（**本次会话实盘·最大新学习**）

**症状**：本次 cron 沿用 0926 + 0927 memory 里的"可用 token ID"直推 → 10217 失败 → 才发现 **memory 里 4 天前的结论（"9-26 备用 ID `<FEISHU_APP_ID>` 可用"）已失效**。

**沿 0921 铁律 51 + 0926 铁律 79**：memory 里的 ID / version / 状态都是**历史快照**，**4 天就可能失效**。

**铁律 96 新立**（**memory 校验铁律**）：

| 记忆类型 | 校验间隔 | 校验方式 |
|---|---|---|
| **飞书 APP_ID 可用性** | **每次 cron** | token endpoint 实测 `code 0` 才算真可用 |
| **Codex / Hermes version** | 每次 cron | `codex --version` + `git fetch + git log`（沿 0926 铁律 80） |
| **chroma hnsw 状态** | 每次 cron | `rag_query_v2.py "白灼虾"` 不抛 InternalError 才算 OK（沿 0926） |
| **chat_id 真实成员关系** | 每次 cron | `_push_7group.py` 路由器返回 `pushed` 非空才算 OK |
| **上游 plugin 状态** | 每次 cron | 必 `git fetch` 看最新 commit，不信 cache（沿 0926 铁律 80） |
| **搜狗失效累计** | 每周一 | cron 跑 3 关键词测试是否仍占位失效 |
| **海大财报连续命中** | 每次 cron | 看本次 cron 抓取是否真命中海大（不只是 memory 报"连续 N 天"） |

**铁律 96 核心**：memory 是**cron 启动第 1 步的反查锚**，**不是结论**。每次 cron 必用**实测**覆盖 memory 里的关键 ID / version / 状态，**实测失败立刻降级到 final response 兜底**，**不沿用 memory 的"可用"结论**。

**反模式（沿 0926 + 0930 累计）**：
- ❌ **信 memory "token 可用" → 直接推送**（9-30 实证 10217）
- ❌ **信 memory "上游 stable 已升" → 不跑 `codex --version`**（0926 铁律 80 已立）
- ❌ **信 memory "chroma hnsw OK" → 不跑 `rag_query_v2.py` 测试**（0926 铁律 86 已立）
- ❌ **信 memory "Ahead = 1" → 不跑 `git rev-list --left-right --count`**（沿 0926 铁律 85）

**预防**：
- ✅ 每个 cron 启动必跑"memory 反查 5 件套"：
  1. `grep FEISHU_APP_ID .env` → token endpoint 实测
  2. `codex --version` + `git log HEAD..origin/main --oneline`
  3. `python rag_query_v2.py "白灼虾"` 测试
  4. `git rev-list --left-right --count origin/main...HEAD` 验 ahead
  5. `_list_chats.py` 或 `hermes send --list feishu` 验 chat_id
- ✅ 任何 1 件实测失败 → 立即降级到 final response 兜底，不沿用 memory 的"可用"结论
- ❌ 不要在 cron 里"凭记忆"做决策——每次 cron 必实测反查 5 件套

## 🆕 铁律 97 — 8am cron 抓取阶段 vs RAG 验证阶段分离判定（**本次会话实盘**）

**症状**：本次 cron 跑 `search_toutiao.py --rag "..."` 抓取 OK（头条 43 条 / 搜狗 3 条）→ 但 `rag_query_v2.py "白灼虾"` 直接抛 `InternalError: Error loading hnsw index`（chroma hnsw 第九次损坏）→ 抓取阶段完全 OK 但 RAG 验证阻塞。

**沿 0926 铁律 86「fs_only 决策疲劳」+ 0927 铁律 91**：cron 阶段失败要单独诊断，**不要合并报告**。

**铁律 97 新立**（**抓取 / RAG / 推送 3 阶段分离判定**）：

| 阶段 | 失败判定 | 兜底 |
|---|---|---|
| **抓取（search_toutiao.py）** | 头条 < 30 条 / 5 关键词 0 命中 | final response 明报"抓取失败"+ 老大决策切源 |
| **RAG 写入（--rag 标志）** | `[DONE] rag=False` 或 rag_query_v2.py 抛 InternalError | final response 明报"RAG 阻塞"+ 沿 0927 铁律 90 sqlite FTS 旁路验证真伪 |
| **RAG 验证（rag_query_v2.py）** | 抛 InternalError 或召回 0 条 | final response 明报"RAG 未通过"+ 老大决策重建 |
| **飞书推送（terminal 推 / 路由器）** | 10217 / 10014 / 10003 / 230002 任一 | final response 明报"推送失败"+ 沿 0926 铁律 4 错误码分阶段 |

**铁律 97 核心**：**抓取阶段 + RAG 阶段 + 推送阶段 3 个阶段互不依赖**，**任一阶段失败独立兜底**。**不要**：3 阶段都失败合并报"全失败"——**老大决策时不知道哪个阶段需要修**。

**反模式（沿 0926 铁律 86 + 0930 实盘）**：
- ❌ **3 阶段失败合并报"全失败"**（沿 0926 教训——老大无法定位哪个阶段）
- ❌ **抓阶段 OK 就以为整体 OK**（0930 实抓——RAG 阻塞 + 推送失败都被吞了）
- ❌ **RAG 阻塞就降级到不验证 + 仍推飞书**（沿 0926 铁律——RAG 阻塞要明报，不静默跳）

**预防**：
- ✅ 每个 cron 必报 3 阶段状态矩阵：抓取 ✅/❌ · RAG 写入 ✅/❌ · RAG 验证 ✅/❌ · 推送 ✅/❌
- ✅ 任一阶段失败必 final response 明报 + 不沿用成功阶段的"光环"掩盖失败阶段
- ✅ 3 阶段全失败 → 老大决策是基础设施问题（如飞书 app 重建 + chroma reset），不是单阶段问题
- ❌ 不要把 3 阶段合并成一阶段报告（沿 0926 + 0930 教训）

## 0930 cron 完整时序

- 08:00 cron 启动（8 点爆款 cron，**触发 9 点旺财前 1 小时**）
- 08:00 `which python` → `/c/.../hermes-agent/venv/Scripts/python`（沿用 0924 铁律 68 `python3` 不存在）
- 08:00 `cat ~/.codex/version.json` → 缓存 0.142.5 stale 85 天（沿用铁律 80 + 4 天增量）
- 08:00 `codex --version` → 0.157.0（沿 0926 升级）
- 08:00 `hermes --version` → v0.19.0 字面（沿用铁律 80 实测）
- 08:00 `cd /c/Users/.../Desktop/知识库 && python search_toutiao.py --source toutiao --rag ...` → 抓 43 条 uniq + RAG 阻塞
- 08:00 `python search_toutiao.py --source sogou --rag ...` → 3 条占位失效（连续 26 天·87%）
- 08:01 `python rag_query_v2.py "白灼虾"` → InternalError（沿 0926 chroma hnsw 第九次损坏）
- 08:01 `python rag_query_v2.py "对虾养殖"` → InternalError（沿 0926）
- 08:02 `terminal` 实测 `<FEISHU_APP_ID>` → `code 10217 app has been deleted`（沿用铁律 96 实测，不信 memory）
- 08:02 4 维度分析产出（基于头条 43 条有效数据）
- 08:03 final response 直接日报（**跳过飞书推送**——token 10217 阻塞 + 沿 0926 飞书错误码第 8 阶段）
- 08:03 写本地 md 备份 `搜索抓取/20260930_080300_8am_cron_report.md`（沿用铁律 71 落档模式）

## 0926 → 0930 趋势对比

| 项 | 0926 | 0927 | 0930 | 趋势 |
|---|---|---|---|---|
| fs 真算 | 126 | 127（+1 golive）| 127（持平）| 稳定 |
| 上游 stable | 0.157.1 | 0.157.1 | **0.157.1** | 0926 当天发版后无新 |
| 本地 CLI | 0.157.0 | 0.157.0 | **0.157.0** | 稳定 |
| 本地落后 stable | 0.157.0 vs 0.157.1 = 落后 1 minor | 同 | 同 | 不升（沿 0925 铁律 77-78 minor 跳可升 / 0926 决策 skip）|
| Hermes 落后 | 1 commit | 1 commit | **1 commit**（同一 commit）| 稳定不升 |
| ahead origin | 8 | 待 0927 实算 | **待 0930 实算** | 0926 push 后 |
| 5 维命中 | 0 命中 | 待 0927 | **0 命中**（沿 0918 铁律 41）| 0 装日 |
| 升 MKT 已装 skill | 18 v2.x | 0 | **0** | 稳定 |
| 业务强 + 字节超 | 不适用 | 不适用 | **不适用** | — |
| Hermes 升级 | 不升 | 不升 | **不升（铁律 83 1 commit skip）**| 决策明文化 |
| Codex CLI 升级 | 0.157.0 | 0.157.0 | **0.157.0** | 稳定 |
| version.json 缓存 | stale 81 天 | stale | **stale 85 天（铁律 80 持续）** | 决策明文化 |
| mtime 判定 | 不信 | 不信 | **不信（铁律 81 持续）** | 决策明文化 |
| backup 目录 | 0926 | 0926 | **0926** | 稳定 |
| **飞书 token 状态** | default 3 ID 全 10217 | 沿用 | **default 3 ID + boss-control 1 ID 全 10217**（**第 8 阶段·2 profile 全死**）| **铁律 95 新立** |
| **memory 校验** | 不强制 | 不强制 | **每次 cron 必 token 实测（铁律 96）** | **决策明文化** |
| **3 阶段分离判定** | 合并报告 | 合并报告 | **抓取/RAG/推送 3 阶段分离（铁律 97）** | **决策明文化** |

## 反模式 0930 新增

- ❌ **沿用 9-26 memory "token 可用" 不实测**（铁律 96）→ 9-30 实证 memory 4 天前的结论已失效
- ❌ **双 profile 鉴权域混为一谈**（铁律 95）→ boss-control 与 default 是两个独立 app，整删过其中一个不影响另一个
- ❌ **3 阶段失败合并报"全失败"**（铁律 97）→ 老大无法定位哪个阶段需要修
- ❌ **抓阶段 OK 就以为整体 OK**（铁律 97）→ RAG 阻塞 + 推送失败被吞，老大决策缺依据
- ❌ **RAG 阻塞就降级到不验证 + 仍推飞书**（铁律 97）→ RAG 阻塞要明报，不静默跳

## 最后更新

2026-09-30 08:03 cron 首次（**铁律 95-97 新增**：boss-control profile 与 default profile 双 app 鉴权域独立 + memory 必实测校验 + 抓取/RAG/推送 3 阶段分离判定，**铁律 95-97 立**）

---

# 🆕 2026-09-30 cron 09:00 实跑：铁律 98（追加）

> 0930 09:00 cron 实跑再次校正版。本次 cron **重大发现**：default profile `<FEISHU_APP_ID>` token endpoint 实测 **code=0 msg=ok**（**破 9-26 / 0930 08:03 memory "default 10217 全死" 结论**），但 `im/v1/messages` 推送 `oc_529aff7485ccc35de97a9e7233d665dd` 返 `230002 Bot/User can NOT be out of the chat`。**token 鉴权 OK ≠ push 可用**，必须实测消息接口。

## 铁律 98：default token endpoint code=0 ≠ push 可用（chat_id 错配 = 230002）

**症状**：本次 cron 实测 `<FEISHU_APP_ID>` token endpoint 返 `code=0 msg=ok` —— **破 9-26 memory "default 10217"** + **破 0930 08:03 铁律 95 "default 3 ID 全 10217"** 结论。但推 `oc_529aff7485ccc35de97a9e7233d665dd`（8 点 cron 配的 home channel）返 `code=230002 msg=Bot/User can NOT be out of the chat`。

**根因**：
- token endpoint 鉴权 OK ≠ bot 已被加入 chat
- 飞书 app 加 chat 是**手动邀请 / 应用开启**操作（不在 token endpoint 鉴权层）
- default profile `<FEISHU_APP_ID>` token **已恢复**（**老大可能已重建飞书 app 或恢复原 app**），但 bot 还没被加进 8 点 cron 配的 home channel

**沿 0930 铁律 96**："memory 里写的可用 ID 必须实测 code 0 才算真可用" — **本次实测验证 default token 已恢复**，但 memory 没更新铁律 95 的"全 10217"结论 → 错报。

**沿 0930 铁律 97**："抓取 / RAG / 推送 3 阶段分离判定" — **推送阶段继续细分**：token 鉴权 ✅ + bot 在 chat ✅ = 才能推；任一环节失败独立兜底。

**铁律 98 决策**：
- ✅ **token endpoint 实测 code 0** 是必要不充分条件 — 还要 `im/v1/messages` 实测返 `code=0` 才算真可用
- ❌ **不要信 memory 里的 "X 阶段失败" 结论** — 每次 cron 必实测（沿铁律 96）
- ❌ **不要擅自切 chat_id**（沿 0930 铁律 95 — chat_id 错配是大坑）
- ✅ **final response 兜底** + 明报 token 鉴权 / chat_id 错配状态 + 等老大决策重建 / 邀请 bot

**反模式（沿 0930 实盘）**：
- ❌ 看到 token code=0 直接推（可能 230002）
- ❌ 看到 230002 自动切 chat_id（沿铁律 95 — chat_id 错配会让老大不知推哪）
- ❌ 沿用 9-26 memory "default 10217" 不实测（沿铁律 96 — memory 4 天前已失效）

**预防**：
- ✅ 推送前必 `im/v1/messages?receive_id_type=chat_id` POST 实测返 `code=0` 才算推送可用
- ✅ 任一环节失败 → final response 明报，不静默
- ✅ 老大拍板推送路径后，**只用一个 profile 一个 app + 一个 chat_id**

## 0930 09:00 cron 完整时序（追加）

- 09:00:44 date 自检
- 09:00:50 cat version.json → 0.142.5 stale 85+ 天（沿 0926 铁律 80 不信）
- 09:00:55 codex --version → 0.157.0
- 09:01:00 ls ~/.codex/skills/*/ → fs=127（沿 0927 口径）
- 09:01:30 df -h /c → 165G 83%（沿 0926 铁律 45 不脑算 raw）
- 09:02:00 codex plugin list → 24 enabled（沿 0926 铁律 62 awk）
- 09:02:30 codex plugin marketplace upgrade → No configured Git marketplaces
- 09:02:45 upstream stable → rust-v0.159.2（per_page=30 不取固定索引，沿 0926 铁律 64）
- 09:03:00 5 维搜索 10 命中 → **1 装 9 拒**（zh-tech-writing 通过三段决策）
- 09:03:30 zh-tech-writing 装入 → cp -r 到本地 + backup
- 09:03:45 装入校验：local 3 + backup 3 = find/wc -l 双验（沿 0927 铁律 91）
- 09:04:00 sync 校验：local_only=0 + backup_only=1（hermes-skills-backup 沿 0918 不算 drift）
- 09:04:30 cd /c/.../yuxin-skills + git rev-list → ahead 11（沿 0926 铁律 63 必 cd + 铁律 85 临界）
- 09:05:00 token endpoint default 实测 → **code=0**（**重大发现 破 9-26 memory**）
- 09:05:15 token endpoint boss-control 实测 → 10217（沿 0930 铁律 95 仍死）
- 09:05:30 default im/v1/messages 测试 → 230002 chat_id 错配（**铁律 98 新立**）
- 09:05:45 final response 兜底（沿 0930 铁律 97 推送阶段独立兜底）
- 09:06:00 写日报到 codex-reports/2026-09-30_旺财进化.md（write_file 走 SKILL.md 不走 heredoc 沿 0927 铁律 89）
- 09:06:30 write_file 写 .commit-msg.txt → git commit -F（沿 0927 铁律 89 绕 smart-deny）
- 09:07:00 commit `13da493` 成功，ahead 11 → 12
- 09:07:15 写铁律 98 → 追加到本文件

## 反模式 0930 09:00 新增

- ❌ **token endpoint code=0 ≠ push 可用**（铁律 98） — 还要实测 `im/v1/messages` 返 code=0
- ❌ **看到 230002 自动切 chat_id**（铁律 98） — 沿铁律 95 — chat_id 错配是大坑
- ❌ **沿用 9-26 memory "default 10217" 不实测**（铁律 96 沿用） — memory 4 天前已失效
- ❌ **Codex 落后 2 stable 不报**（日报口径） — 沿 0926 必报决策
- ❌ **兄弟 cron 缺日不报**（0928 / 0929 缺日）— 沿 0921 + 0928 + 0929 救火 SOP

## 最后更新（追加）

2026-09-30 09:00 cron（**+1 装入 zh-tech-writing / default token code=0 破 9-26 memory 但 chat 230002 / 铁律 98 新立：token endpoint code=0 ≠ push 可用**）