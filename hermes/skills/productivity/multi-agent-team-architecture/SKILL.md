---
name: multi-agent-team-architecture
description: 渔芯 9 profile Hermes 多 Agent 架构设计/改造/故障响应方法论 + 本地协作框架 v2 + **4 大支柱协作机制 v1（8/3 实装：L0/L1/L2/L3 协作分层 + core/domain/on-demand skills 分类 + 任务 yaml 状态机 + 每日/每周复盘）**。覆盖 9 profile 共享 minimax key、volcengine-agent-plan 多模型套餐、cron 跨 profile 重复与去重、prompt caching、session 归档、launchd 守护、跨平台部署、GitHub yuxin-skills 仓库技能共享、本地协作框架、Agent 网络分类（能上网/禁网判断）、项目路径与任务库 canonical 真相 ~/.hermes/orchestration/。触发条件：9 profile 团队改造/本地协作框架/飞书只是汇报/3 网关保留/团队 token 优化/跨同事消息/minimax 401-402-429/订阅 key 同步/volcengine-agent-plan/gateway 拉起/session 归档/prompt cache/agent 档案/Dashboard/降本增效/5 同事心跳去重/跨平台 Agent/旺财/yuxin-skills/技能仓库共享/加新 agent/扩编/9→10/具体执行你决定/你是专家、整理 profile 散落元数据、profile.json 缺失/不规范、**华哥说"继续优化同事团队合作"/"团队协作机制升级"/"记忆管理"/"上下文管理"/"行为规划"/"复盘"**、**Profile $HOME 劫持（zhenglishi 565 文件案例）**、**批量加 core_skills**、**Claude Code 90s 超时 fallback**、**execute_code 被 cron 模式 BLOCKED**、**Dashboard 加 tab**、**任务状态目录读写**、**大规模文件搬迁/知识库物理重组/批量 mv（RKR 62 万文件级）**、**发现另一会话/agent 同时操作同一目录（并行执行/双会话撞车）**、**重新整理同事 agent 系统文件/集中目录树/团队管理视图/新增专家同事（原 yuxin-team-management 已并入）**。
version: 1.1.0
created: 2026-06-30
---

# 渔芯 9 Profile 多 Agent 团队架构

9 个独立 Hermes profile (default / maodou / laomo / xiaobao / heidou / afu / quant / zhenglishi / wangcai) 共享 1 把 minimax TokenPlanMax 订阅 key (sk-cp- 头)，通过 launchd 守护 + 飞书 WebSocket 与华哥交互。玉芬 (default) 是管理员，负责 5 同事调度与团队健康。旺财 (wangcai) 运行于 Windows，华哥直派，负责 CAD/SolidWorks 出图 + 自媒体自动化运营。

> 配套文档：`~/hermes/team/` (24 文件: README + team_overview + 7 agents/ + 3 communication/ + 4 infra/ + 3 runbooks + 2 backups + 3 memory/)
> 配套 L2 记忆：`~/hermes/memory_store/lessons/minimax_subscription_vs_payg.md` + `multi_profile_api_key_sync.md`
- `references/***SECRET***.md` (6/30 完整复活链路) + `references/***SECRET***.md` (minimax cache_control 端点实测) + `references/volcengine-agent-plan-models.md` (火山引擎智能体计划模型目录) + `references/no-agent-cron-heartbeat.md` (零 token 心跳脚本模式) + **`references/cron-python-environment.md` (cron 模式 Python 环境配置 + Pitfall #24 execute_code BLOCKED + 🆕 Pitfall #25 heredoc Python 子串被 tirith 拦的解法)** + **`references/local-orchestration-framework.md` (2026-07-31 上线本地协作框架 v2)** + **`references/2026-08-03-profile-8pieces.md` (8/3 实装 9 profile 标准 8 件套 + 9→10 扩编 SOP + 资源 L0/L1/L2/L3 vs 记忆 L1/L2/L3 反例 + 玉芬操作边界 v2)** + **`references/***SECRET***.md` (8/3 控制面板科技未来风 CSS 模板 + Streamlit 数据采集渲染分离模式 + 弃用 API 迁移清单 2025-12-31 + 多页应用约定 + 已知技术债清单)** + **`references/***SECRET***.md` (8/3 4 大支柱)**
- **`references/***SECRET***.md` (8/7 批量任务派发：tasks.db + inbox + 汇报 cron 三步法)**:L0/L1/L2/L3 协作分层 + core/domain/on-demand skills 分类 + 任务 yaml 状态机 + 每日/每周复盘 + 🔴 $HOME 劫持陷阱 + Claude Code 90s 超时 fallback + execute_code blocked 绕道 + TODO(tech-debt) 标记规范)`**
- **`references/***SECRET***.md` (8/28 黑豆实测：AGENTS.md `~/.hermes/profiles/<prof>/...` 相对路径在 cron 模式也会断，区别于 7/15 直接 `~` 陷阱；写盘必须用绝对路径 + 30 秒自检命令 + 跨同事推广)**
- **`references/***SECRET***.md` (8/20 毛豆实测 — 陷阱 AC.3 路径层归属误判：SKILL.md 可在 global 或 profile 层，凭印象扫描导致 3 份进化报告连续误判"缺失 9 个 references"。实测只缺 1 个，补建 v2.1.1-bug-fix-case.md 根治。含 find -type d 多路径定位 SOP + 陷阱 AC v1.1 三层诊断)**
+ **`references/full-team-launch-sop.md` (8/13 全面上线冲刺：启动所有网关+恢复所有心跳+连续调研主控 cron 的端到端 SOP + gateway_state.json 权威判断 + Python 批量重建 plist)**
+ **`references/***SECRET***.md` (8/30 派单+重拉实战配方：kanban.db assignee 中文业务名铁律 vs 英文 profile 名、inbox+kanban 双通道、enabled-但进程死→bootout+bootstrap 而非 load、派单前扫 paused cron、多 agent 分域研究扇出)**
+ **`references/boss-approval-landing-sop.md` (9/4 华哥批复落地 SOP：专家日报"按专业建议执行"类指令 → 权威文档+产品README+kanban(body带上下文)+cron prompt补第0步+心跳验证 五步桥接；批复只存在于玉芬会话，专家读不到)**
+ **`references/profile-code-cli-access.md` (9/6 宽博士实测：同事 profile 调不动 claude/codex 的双重根因 = wrapper PATH 漏 ~/.local/bin + 隔离 HOME 空凭据；修复 = wrapper v3 补 PATH + export CODEX_HOME/CLAUDE_CONFIG_DIR 指全局凭据；含模拟环境验证配方、最小影响重启纪律、delegate_task 批量超时降级路径)**
+ **`references/***SECRET***.md` (9/8 心博士 W6 Day1 实战：华哥逐项批复 → 玉芬跨 agent 文件级直接代执行 SOP——与 boss-approval-landing-sop 分工：后台无 bot agent + 小件明确交付时代拟而非 kanban 派回；含心博士资产路径地图（knowledge 正本/契约规范/同步清单/情商助手镜像）、代拟 provenance 标注（待红线审校转正）、同步清单 in-place append 防 vN 撞号、API/PRD/UAT/话术加项落点惯例、Day 计数多轨 pitfall)**
+ **`references/***SECRET***.md` (9/12 RKR 62万文件物理重组·双会话相撞实战：大规模搬迁/重组/批量 mv 前必查并行执行者（pgrep hermes-snap + lsof +D + ls -lt 三查）→ APFS `cp -Rc` 快照 31GB 仅 1m54s + 基线对账 → 冻结写库 cron → mv 绝对路径纪律；发现相撞后止损协议 = 停手/验明对方/还原误伤/给华哥选项，不抢文件树；含 RKR compose 容器相对路径不破结论 + 宿主侧 8 处硬编码清单)**
+ **`references/org-shrink-2026-09-27-10to2.md` (9/27 组织收缩令实战：10 profile 收缩为 2（只留玉芬+宽博士）——按智能体归组批量暂停 25 个 cron 的归属表法 + jobs.json 权威校验抓漏网 + 同日指令冲突以后到者为准 + 管理类任务随派单链路一并暂停的解释性判断纪律；恢复=job_id 级 resume)**

---

## 技能索引

- [profile-topology](#profile-topology) — 9 profile 物理布局 + 边界
- [l1-l2-l3-memory](#l1-l2-l3-memory) — 三层记忆架构（每 profile 独立 + 团队共享）
- [***SECRET***](#***SECRET***) — 火山引擎智能体计划多模型套餐
- [***SECRET***](#***SECRET***) — 订阅 vs 按量 2 套账户体系
- [prompt-caching-verified](#prompt-caching-verified) — minimax 端点实测支持 Anthropic cache_control（70% 节省）
- [***SECRET***](#***SECRET***) — 9 profile 视角下 cron 重复数学（108 个实际 job）
- [session-archive-math](#session-archive-math) — 24GB+ sessions 归档到 80MB 的策略
- [cross-platform-github-repo](#cross-platform-github-repo) — GitHub yuxin-skills 仓库跨机器技能共享
- [***SECRET***](#***SECRET***) — launchd 重启后用户私聊路由失效金标准（6/30 黑豆/阿福教训）
- [launchd-guardian-sop](#launchd-guardian-sop) — 拉起/诊断 5 同事 gateway 的标准动作
- [402-401-429-diagnosis](#402-401-429-diagnosis) — minimax 端点 3 种错误码根因 + 修复

---

## profile-topology

### 9 profile 物理布局

| Profile | 角色 | 平台 | config.yaml 路径 | .env 路径 | 调度边界 | Provider |
|---|---|---|---|---|---|---|
| **default** (玉芬) | 团队管理员 | macOS | `~/.hermes/config.yaml`（根目录，不在 profiles/） | `~/.hermes/.env` | 5 同事调度 + 监控 | **GLM-5.3-flash（智谱套餐，2026-08-28 起）** |
| maodou (毛豆) | 产品经理 + 3D 工程 | macOS | `~/.hermes/profiles/maodou/config.yaml` | `~/.hermes/profiles/maodou/.env` | 玉芬调度 | MiniMax-M3 (minimax-cn) |
| laomo (老莫) | 知识库 + 测试 | macOS | `~/.hermes/profiles/laomo/config.yaml` | `~/.hermes/profiles/laomo/.env` | 玉芬调度 | MiniMax-M3 (minimax-cn) |
| xiaobao (小宝) | 销售 + 自媒体 | macOS | `~/.hermes/profiles/xiaobao/config.yaml` | `~/.hermes/profiles/xiaobao/.env` | 玉芬调度 | MiniMax-M3 (minimax-cn) |
| heidou (黑豆) | 行政 + 财务 + 法务 | macOS | `~/.hermes/profiles/heidou/config.yaml` | `~/.hermes/profiles/heidou/.env` | 玉芬调度 | MiniMax-M3 (minimax-cn) |
| afu (阿福) | 客服 + 异议 | macOS | `~/.hermes/profiles/afu/config.yaml` | `~/.hermes/profiles/afu/.env` | 玉芬调度 | MiniMax-M3 (minimax-cn) |
| quant (宽博士) | 量化研究 | macOS | `~/.hermes/profiles/quant/config.yaml` | `~/.hermes/profiles/quant/.env` | **华哥直接管理（2026-08-29 完全独立，废玉芬调度）** | MiniMax-M3 (minimax-cn) |
| zhenglishi (学习助手) | 华哥个人学习 | macOS | `~/.hermes/profiles/zhenglishi/config.yaml` | `~/.hermes/profiles/zhenglishi/.env` | 玉芬调度（原华哥直派,2026-08-08 纳入）| MiniMax-M3 (minimax-cn) |
| **wangcai (旺财)** | **CAD + 自媒体专员** | **Windows** | `~/.hermes/profiles/wangcai/config.yaml` | `~/.hermes/profiles/wangcai/.env` | **华哥直派** | volcengine-agent-plan |
| **psychology (心博士)** | **心理学专家** | macOS | `~/.hermes/profiles/psychology/config.yaml` | `~/.hermes/profiles/psychology/.env`（待建） | **华哥直派（复刻宽博士独立模式，2026-09-04 立项）** | MiniMax-M3 (minimax-cn)，可切智谱套餐 |

> ⚠️ **2026-09-04 团队 9→10 扩编**：新增 psychology（心博士，心理学专家）。**当晚已上线**：launchd 网关 ai.hermes.gateway-psychology（KeepAlive）+ cron ×2（心跳 a45e94d998b4 no_agent / 自进化 b558afeac917）+ W1 Day 1 知识库 901 行 + 华哥拍板 3 件事（B+C 组合/关系记忆卖点/00 后画像）。仍缺：飞书 bot .env（心博士暂为后台专家，文件级共享）。立项实录见 `references/***SECRET***.md`；批复落地过程见 `references/boss-approval-landing-sop.md`；调研主文档 `/Users/hua/6-产品研发/渔芯独角兽/01-开发中/心理学专家底座/INDEX.md`。

> 🔴 **2026-09-27 组织收缩：10→2（最新状态以此为准）** — 华哥 16:00 下令只保留 **玉芬(default) + 宽博士(quant)**。其余 8 profile（maodou/laomo/xiaobao/heidou/afu/psychology/zhenglishi/wangcai）的全部 cron 已暂停（共 25 个，只停不删，profile/记忆/技能完整保留）。本节以下的 9/10 profile 拓扑表、5 同事心跳矩阵、派单 SOP 等均为**收缩前历史记录**，恢复扩编或排查"为什么同事没响应"时先读 `references/org-shrink-2026-09-27-10to2.md`（含全部 job_id 恢复清单）。

> ⚠️ **2026-08-28 现状修正**：上表 volcengine-agent-plan/minimax 列为历史设定。8/28 实测全景：玉芬=GLM-5.3-flash（智谱个人 pro 套餐），其余 8 profile 全部 MiniMax-M3 (minimax-cn)。同事模型切换需华哥明示——玉芬 8/28 曾误判"黑豆被改成 GLM"，实为 `profiles/heidou/home/.hermes/config.yaml` 是指向玉芬主配置的**软链接**（CC Switch 写入落在玉芬身上），黑豆真身配置从未变过。审计 profile 配置时先 `ls -la` 识别软链，真身 = `profiles/<名>/config.yaml`（profile 根目录）。

### 旺财（wangcai）简介

旺财是渔芯第 9 个 Agent，2026-07-08 创建，运行于 **Windows PC**（与 macOS 集群分离）。双核心职责：

1. **CAD/SolidWorks 出图** — 利用 Windows 原生 SolidWorks COM API (pywin32) + CadQuery + ezdxf 生成参数化 CAD 模型、DXF 图纸、STEP/STL 文件
2. **自媒体账号自动化运营** — 利用 Hermes browser 工具自动发布内容到抖音/小红书/视频号

**跨平台要点**：
- 旺财的 Hermes 版本走 `pip install hermes-agent`（与 macOS 一致）
- 飞书 WebSocket gateway 通过 config.yaml 配置（APP_ID/APP_SECRET 分离）
- 技能通过 GitHub `yuxin-skills` 仓库共享（详见 `cross-platform-github-repo` 节）
- **Codex CLI** 安装在 Windows 上作为编程引擎，与 Hermes Agent 协同工作（Codex 生成代码，Hermes 调度执行）
- 旺财的飞书 Bot 使用独立 APP_ID/APP_SECRET，不与 macOS 集群共享

### 关键陷阱（实战 6/30 验证）

- **default 不在 profiles/ 下** — 走根目录 `~/.hermes/config.yaml` + `~/.hermes/.env`
- **5 同事 .env 配置结构不对称** — 6 同事有完整 FEISHU_*，quant 和 zhenglishi 缺 `FEISHU_CONNECTION_MODE`（不影响但看 .env 会困惑）
- **5 同事历史 L1 都错把 Mac mini 当 Windows** — 6/26 之前是 Windows，6/30 之前已迁回 Mac，但 L1 没更新（已 6/30 重写修正）
- **旺财是 Windows 原生 Agent** — 路径使用反斜杠 `\\`（Python 中统一用正斜杠 `/` 或 raw string），SolidWorks COM 是 Windows 独有，macOS 同事无法直接操作 SolidWorks
- **新建同事走 SOP** — 新增同事时始终读 `playbooks/onboard-new-agent.md` 的 5 阶段流程（角色→模板→注册→部署→验证），不凭记忆跳步骤
- **Secret 泄露要 force push** — 如果不慎提交了飞书 Secret，立即 `git commit --amend` + `git push --force-with-lease` 修复。GitHub push protection 会拦截大部分，但不绝对

## 🚨 反模式（华哥 2026-07-31 14:55+ 明确）：飞书云盘不能做 Agent 协作基础设施

**核心规则**：
- **飞书 = 仅华哥（人）↔ 玉芬的汇报与沟通渠道**。大群 `***SECRET***` 和华哥 DM `***SECRET***` 是华哥↔玉芬通道。
- **agent 之间协作、玉芬对同事管理 = 必须在本机本地框架中完成**。飞书云盘 `任务派发/` 目录、飞书 inbox/outbox、飞书大群 @-mention = **不能**用作 agent 协调基础设施。
- 架构设计应**参考 GitHub 评分最高的 agent 协作方式**（MetaGPT SOP / CrewAI Task-Process / AutoGen 对话 / OpenAI Swarm handoff）。

**实战反例（2026-07-31 玉芬犯的错误）**：
- 把"工作目录变更"通知发到 11 个飞书云盘位置（每个 agent 根目录 + 任务派发子目录），并在大群广播
- 这是**错误的**协作方式：飞书云盘不是 agent 协作的可靠底层
- 正确做法：通知写到 `~/.hermes/orchestration/messages/<agent>/inbox/` 或 `shared_state/`，agent cron tick 读 inbox

**正确路径**：
- agent 协作 → `~/.hermes/orchestration/`（本地框架 v2，2026-07-31 上线，详见 `references/local-orchestration-framework.md`）
- 任务池 → `~/.hermes/kanban.db`（复用现有 SQLite）
- agent 消息 → `~/.hermes/orchestration/messages/<agent>/{inbox,outbox,sent}/`
- **飞书（2026-07-31 硬性新定位）**：仅作华哥↔玉芬的汇报与沟通渠道；9 个 profile 各自独立飞书 bot（不是单 bot 共享）
  - 玉芬 cli_a964873dd7b / 毛豆 cli_a96589aac2b / 老莫 cli_a9648293ffb / 小宝 cli_a9648259403 / 黑豆 cli_a96482d9857 / 阿福 cli_a96481f17df / 宽博士 cli_a97210406cb / 学习助手 cli_a972124317b / 旺财独立
  - 飞书云盘"任务派发/{agent}/"已废用（保留为历史归档，不再写入）
- 共享状态 → `~/.hermes/orchestration/shared_state/`
- 事件流 → `~/.hermes/orchestration/events/events.jsonl`（append-only）
- Agent 注册表 → `~/.hermes/orchestration/registry.yaml`（单一来源，替换各 .py 的 AGENTS = [] 分散列表）

**飞书云盘历史通知处理原则**：
- 之前误发的飞书云盘通知（v1/v2 工作目录变更通知）= **保留为历史归档，不删除**，加 deprecated 标记
- 不再使用飞书云盘做任何 agent 协作写入
- 飞书云盘目录（任务派发/任务单/产出）= 视为只读历史档案

---

## l1-l2-l3-memory

### 三层分工

| 层 | 容量 | 注入方式 | 存放位置 | 谁能看到 |
|---|---|---|---|---|
| **L1** | ~5KB 严格 | 自动注入每轮对话 | `~/.hermes/memories/MEMORY.md` (default) 或 `~/.hermes/profiles/<prof>/memories/MEMORY.md` (其他 7) | 自己 + 玉芬读文件 |
| **L2** | 无限 | grep / cat 按需 | `~/hermes/memory_store/` (共享) + `~/hermes/team/profile_<prof>/` (待建，专属) | 所有人 |
| **L3** | 永久 | session_search FTS5 | `~/.hermes/profiles/<prof>/sessions/` (active) + `sessions_archive/` (旧) | 自己 |

### L1 结构 (6/30 重整后模板)

每 profile L1 = 4 段：

```
# <名字> MEMORY (自动注入每轮对话)

§
## 身份层 (固定)
- 我是谁 / 我的 profile / 我的 PID / 我的核心职责 / 我的核心约束 (4-6 条)

§
## 任务层 (cron 自动更新)
- 当前状态 (gateway PID / WS 连接 / 心跳 schedule)

§
## 团队层 (共享 - 指向 l1_shared/)
- 8 同事一句话定位 / minimax 订阅架构 / 飞书私聊路由 / 华哥风格

§
## 知识沉淀
- L2 路径 / 我自己的 L2 专属 / session_search 检索
```

### 团队共享 L1 (l1_shared/team_overview_l1.md)

**关键设计**：3.3KB 单一文件，**所有 8 profile 的 L1 末尾都引用它**。但 L1 注入框架不识别"include"——**所以玉芬在 L1 末尾用一行指针** + 真值放 L2：

```markdown
## 团队层 (共享)
完整团队概览在 `~/hermes/team/memory/l1_shared/team_overview_l1.md`
详细团队档案在 `~/hermes/team/team_overview.md`
```

### 9 profile L1 字节数基准 (2026-07-08 实测)

| Profile | MEMORY.md | USER.md | 备注 |
|---|---|---|---|
| default | 1753B | (保留) | 管理员视角 |
| maodou | 1938B | (保留) | 产品设计 7 原则 |
| laomo | 1482B | (保留) | 本地优先 fallback |
| xiaobao | 1605B | (保留) | 蓝海 + 跨鸿沟 |
| heidou | 1479B | (保留) | 谈判 + 财务模型 |
| afu | 1472B | (保留) | 异议 + 心理学 |
| quant | 1538B | (保留) | 不经玉芬边界 |
| zhenglishi | 1740B | (保留) | 不经玉芬边界 |
| wangcai | 1531B | 1393B | Windows CAD + 自媒体 |

### 📁 华哥核心工作目录结构（2026-07-31 华哥明确）

**两个概念严格区分**：

| 概念 | 路径 | 用途 |
|---|---|---|
| **工作目录（CWD）** | `/Users/hua/rkr_staging/文档库/渔芯项目/` | 各同事 agent 默认 cwd，所有任务在此进行 |
| **项目文件存放处** | `/Users/hua/6-产品研发/` | 各项目物理存储：`00-FindEra寻元/` `01-RKR知识库/` `22-出图智能体训练/` `23-KnowHow知渔/` 等 |

**实战含义**：
- 同事 agent 接到任务时**默认 cwd = `/Users/hua/rkr_staging/文档库/渔芯项目/`**
- 需要访问具体项目时 `cd /Users/hua/6-产品研发/<编号>/<项目名>/`
- `rkr_staging/文档库/渔芯项目/` 已有大量内容（`8-量化研究/` `cad_samples/` `团队协作/` `tasks.db` 等），同事**无需新建**子目录

**错误教训**：玉芬 7/31 14:30 误把 cwd 解读为 `/Users/hua/6-产品研发/渔芯项目/`（自己新建的空目录），华哥 14:55 明确纠正：**《渔芯项目》在 rkr_staging 下**。下次涉及工作目录时**先 ls 验证路径**，不要凭推理。

### 9 profile 沟通通道矩阵 (2026-07-31 实测)

| 通道 | 玉芬↔其他 | 同事↔同事 | 备注 |
|---|---|---|---|
| 飞书大群 (`***SECRET***`) | ✅ | ✅ (read) | **唯一稳定跨同事通道** |
| 华哥 DM (`***SECRET***`) | ✅ | ❌ | 玉芬默认 home |
| 同事 home channel × 7 | ❌ (230002) | ❌ | 飞书 chat 私有，玉芬 bot 不在成员列表 |
| 飞书云盘 任务派发 | ✅ (异步) | ❌→✅ (改) | 5 同事任务派发子目录缺失（见 `feishu-drive-file-management`） |

**派单 SOP** = 大群 `@<agent>` + 任务派发目录**双通道**（华哥能看到同步消息；agent 心跳能读到任务文件）。

**派单闭环 5 步（2026-08-30 量化因子派单实战补充）**：

**🔴 第 0 步（2026-09-06 学习助手派单实测新增）：先读目标同事心跳 cron 的 prompt，确认它实际扫描哪个通道** — 架构规范说派单走本地 `orchestration/messages/<agent>/inbox/`，但学习助手（zhenglishi）的心跳 prompt 实际扫的是**飞书云盘 `任务派发/学习助手/`**（活跃目录 token `VsMRfTb3qlj4tJd3V7ncJTL6noe`，即含 产出/归档 子结构的那个；云盘有多个同名"学习助手"目录，见 feishu-drive-file-management 的 folder-token 地图）。按规范投到没人扫的通道 = 任务静默躺死。云盘上传一律用玉芬 bot 凭据（同事 bot 对根目录 403）。查法：`cronjob list` 找该同事心跳 job → 读其 prompt 里"检查 XX 目录/云盘"字样。
1. 写 inbox 派单文件 `~/.hermes/orchestration/messages/<agent>/inbox/task_*.md`（含任务说明 + `staging_save.py --source <lib>` 产出路径 + 写盘前 30 秒自检）
2. 写 kanban.db 任务（`assignee` 字段 = **中文名**，如「老莫」「阿福」，匹配 `heartbeat_check.py <中文名>` 传入的 agent_name）
3. **检查目标同事的 cron 是否被暂停** —— 老莫的心跳+自我进化两个 cron 曾在 8/16 被 pause，派单后不 `cronjob resume` 就永远读不到任务。派单前先 `cronjob list` 看目标同事 cron 的 `state`
4. 如需某主攻 agent 汇总，给它也写 inbox 协作通知（附分工表）
5. **核查进度**：`find /Users/hua/rkr_staging/文档中转站 -name "*.md" -newermt "时间"` 找新产出 + kanban `status` 字段 + `grep -c "$today" <prof>/logs/agent.log` 数今日活动

**执行时机差异（决定"同事多久开工"）**：心跳 cron（每小时，no_agent 脚本）只**检查**任务；真正**执行**任务的是「自我进化」cron（LLM 模式，通常每 4h）。派单后同事一般要等下一次自我进化 tick（16:00 这类整点）才开工——除非它像老莫那样心跳是每小时整点（14:00 立即触发，14:05 就交活）。华哥催进度时，先解释这个 tick 差，别误判成"同事没干活"。

## 华哥批复落地 SOP（专家日报「按专业建议执行」类指令，9/4 实战）

**触发**：同事专家日报/进化报告结尾「请示/待华哥拍板 X 件事」→ 华哥概括性批准（「按你这个专家的专业建议执行」「具体你拿主意」）。**专家自己的建议 = 已批准的决策**，玉芬负责把批准"翻译"成落地状态。

**关键认知**：日报 `deliver=origin` 发进玉芬聊天，华哥批复也只在玉芬会话里——**专家 agent 看不到批复**，必须由玉芬桥接，否则专家按原计划跑、拍板丢失。

**落地 5 步（详见 `references/boss-approval-landing-sop.md`）**：
1. 权威文档落决策（项目 INDEX.md 行动项：勾已完成 + 拍板记录引批复原话；一处写清不散写）
2. 下游产品 README 加决策表（让产品侧 agent 下一轮自进化可读到）
3. **kanban 派任务给专家**——body 写全拍板上下文（专家读不到聊天）；id 惯例 `task_<前缀>_<epoch>_<hex>`，assignee=中文业务名，created_by=yufen，workspace_kind=scratch
4. cron 提示词体检：新立 agent 的自进化 prompt 常缺「第 0 步 heartbeat_check.py 领任务」（7 老同事都有）→ `cronjob update` 补齐
5. `heartbeat_check.py <中文名>` 实测取到任务再汇报 + Mnemosyne 登记决策

**陷阱**：批复只写进专家 evolution 日志 ≠ 落地（专家下轮不保证回读自己的 evolution）；终端 `cat >> file << 'EOF'` 追加会被审批闸拦（BLOCKED），既有文件追加走 patch 工具，信息已由权威文档覆盖时主动放弃重复写入。

### L1 维护自动机制

- **cron `f392cbc559b4`** (玉芬-L1-compact-all-profiles, `0 */4 * * *`) — 遍历 8 profile，L1 > 2KB 自动备份 + 截断到 70%
- **脚本** `~/.hermes/scripts/l1_compact_one.sh` + `l1_compact_all.sh`
- **重写脚本** `~/hermes/team/memory/runbooks/refresh_all_l1.py` — 一次性 8 profile L1 全面重写

### L1 重写 SOP (refresh_all_l1.py 触发条件)

- 重大架构变更（如 6/30 订阅 key 修复）
- 过时认知累积（如"Windows Agent"消失）
- 新建 profile
- 团队成员加入/退出

**操作前**：
1. 备份当前 L1 (脚本自动 `.bak.YYYYMMDD_HHMMSS`)
2. 删除所有 `.lock` 和 `.bak.*` (default 之前 67 个文件 → 3 个)
3. 写新版 L1 (4 段结构)

---

## ***SECRET***

### 概述

火山引擎智能体计划（volcengine-agent-plan）是 ByteDance 火山引擎提供的**多模型订阅套餐**，与 minimax TokenPlanMax 并行作为团队的第二大 LLM Provider。毛豆（maodou）当前使用此套餐，其他 profile 可按需切换。

### 套餐定位

| 维度 | minimax TokenPlanMax | volcengine-agent-plan |
|---|---|---|
| 模型数量 | MiniMax 全系 (M3/M2.7/图像/语音/音乐) | **12 个模型**（多厂商） |
| 模型厂商 | 单一（MiniMax） | 多厂商（DeepSeek/Kimi/Doubao/GLM/MiniMax） |
| 并发上限 | 4-5 Agent | 取决于套餐，通常高于 minimax |
| 上下文 | 1M tokens | 各模型不同（262K~1M） |
| 当前使用者 | 7 profile（default + 5 同事 + quant + zhenglishi） | 毛豆（maodou） |
| API Key | `sk-cp-` 前缀（订阅 key） | `ark-` 前缀（火山引擎计划 key） |
| Endpoint | `https://api.minimaxi.com/anthropic` | `https://ark.cn-beijing.volces.com/api/plan/v3` |

### 模型目录（12 个可用模型）

| Model ID | 上下文 | 类型 | 推荐用途 |
|---|---|---|---|
| `deepseek-v4-pro-260425` | **1M** | 通用旗舰 | **最强推理**，产品设计决策、3D 工程分析、复杂编码 |
| `deepseek-v4-flash-260425` | **1M** | 通用快速 | 日常对话、简单任务、快速迭代 |
| `kimi-k2.7-code` | ? | 代码专用 | 纯编码任务（LookForge 后端、Rust/Python） |
| `kimi-k2.6` | ? | 通用 | Kimi 前代，备选 |
| `glm-5.2` | **1M** | 通用 | GLM 最新，长上下文场景备选 |
| `minimax-m3` | ? | 通用 | MiniMax 旗舰，与 minimax 订阅同模型 |
| `minimax-m2.7` | ? | 通用 | MiniMax 前代，备选 |
| `doubao-seed-2-0-pro-260215` | 262K | 通用 | Doubao Pro |
| `doubao-seed-2-0-lite-260215` | 262K | 通用轻量 | Doubao Lite，快速简单任务 |
| `doubao-seed-2-0-mini-260215` | 262K | 通用迷你 | Doubao Mini，最低成本 |
| `***SECRET***` | 262K | 代码预览 | Doubao 代码模型 |
| `ark-code-latest` | ? | 代码 | 火山引擎最新代码模型 |

### 模型选择方法论（按 Agent 角色）

当需要为某个 Agent 配置模型时，按以下步骤：

**Step 1 — 了解套餐全貌**
先读 `~/.hermes/config.yaml` 中 `providers.volcengine-agent-plan.models` 列表，确认可用模型。

**Step 2 — 分析 Agent 角色需求**

| Agent 角色 | 核心需求 | 推荐模型 | 理由 |
|---|---|---|---|---|
| 产品经理 + 3D 工程（毛豆） | 强推理 + 编码 + 长上下文 | `deepseek-v4-pro-260425` | 1M 上下文，推理和编码都顶级 |
| 知识库/测试（老莫） | 文档处理 + 搜索 | `deepseek-v4-flash-260425` | 快速，1M 上下文 |
| 销售/自媒体（小宝） | 创意写作 + 营销 | `kimi-k2.7-code` 或 `deepseek-v4-pro` | 创意 + 代码 |
| 行政/法务（黑豆） | 文档审核 + 合规 | `deepseek-v4-flash-260425` | 快速够用 |
| 客服（阿福） | 对话 + 异议处理 | `deepseek-v4-flash-260425` | 快速响应 |
| 量化研究（quant） | 数据分析 + 策略 | `deepseek-v4-pro-260425` | 强推理 |
| 学习助手（zhenglishi） | 知识整理 | `deepseek-v4-flash-260425` | 快速够用 |
| **CAD + 自媒体（旺财）** | **代码生成 + 浏览器操作** | `deepseek-v4-flash-260425` | 1M 上下文，Codex CLI 生成 CAD 代码，Hermes 执行浏览器自动化 |

**Step 3 — 切换模型**
```bash
# 修改 profile 的 config.yaml
# model.default 改为目标模型 ID
# model.provider 保持 volcengine-agent-plan

# 重启 gateway 生效
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-<prof>.plist
sleep 2
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway-<prof>.plist
```

**Step 4 — 验证**
```bash
grep -A2 "^model:" ~/.hermes/profiles/<prof>/config.yaml
ps aux | grep "hermes.*gateway.*<prof>" | grep -v grep
```

### 关键陷阱

- **套餐模型不共享 minimax 订阅额度** — volcengine-agent-plan 有独立额度，不会和 minimax 争 4-5 Agent 并发上限
- **模型 ID 必须精确匹配** — 如 `deepseek-v4-pro-260425` 不是 `deepseek-v4-pro`（少了日期后缀）
- **volcengine-agent-plan 不是 volc-ark** — 两者 endpoint 不同（`/api/plan/v3` vs `/api/v3`），API key 也不同
- **重启 gateway 后飞书私聊路由可能失效** — 需要华哥私聊激活（见 ***SECRET***）

### 参考文件

- `references/volcengine-agent-plan-models.md` — 完整模型目录 + 实测参数

---

## ***SECRET***

### 2 套账户体系（必看 — 6/30 根因）

| Key 前缀 | 账户类型 | 额度机制 | 标识 | 当前状态 |
|---|---|---|---|---|
| `sk-cp-` | **包月订阅** (TokenPlanMax) | 折扣包月 + 月度 ~18 亿 token + 并发上限 4-5 Agent | plan 页订阅 key | ✅ 7 profile 共用 |
| `sk-api-` / `sk-api-v2-` | **按量付费** | token 计费，余额扣完即停 | 通用 API key | ❌ 6 同事之前用，6/30 已耗尽 402 |

### 套餐规格 (TokenPlanMax)

- 支持模型：MiniMax 全系 (M3 / M2.7 / 图像 / 语音 / 音乐)
- 并发 Agent：**4-5 个** (上限) — 8 profile 共享会撞
- 上下文：1M tokens
- 多模态：M3 原生（图像/视频输入）
- 月度 M3 额度：**~18 亿 token**
- 计费方式：折扣包月

### 7 profile 现状 (6/30)

- 全部用 `sk-cp-` 订阅 key
- sha256 = `***SECRET***`
- 长度 125 字符
- endpoint: `https://api.minimaxi.com/anthropic`
- model: `MiniMax-M3`
- 实际上 default 和 zhenglishi 是同一把 key（不是真独立账户）

### 强制同步字段

`MINIMAX_CN_API_KEY` 必须 8 profile 一致（除非刻意拆分到独立账户）。

### 不应同步的私有字段

- `FEISHU_APP_ID` / `FEISHU_APP_SECRET` (bot 身份)
- `FEISHU_HOME_CHANNEL` (bot 自己的 home)
- `.hermes-internal` token (框架私有)
- `FEISHU_HOME_CHANNEL_THREAD_ID` (部分 profile 有)

### Key 同步 SOP (Python 不要 sed)

```python
# 关键：必须 Python 写入，sed 会吃 * 等 regex 字符
for prof in ['afu', 'heidou', 'laomo', 'maodou', 'quant', 'xiaobao']:
    env_file = f'/Users/hua/.hermes/profiles/{prof}/.env'
    new_key = open('/tmp/sub_key').read().strip()
    with open(env_file) as f:
        lines = f.readlines()
    with open(env_file, 'w') as f:
        for line in lines:
            if line.startswith('MINIMAX_CN_API_KEY=*** '):
                f.write(f'MINIMAX_CN_API_KEY=*** + new_key + '\n')
            else:
                f.write(line)
```

### 验证 (sha256 优先于肉眼)

```bash
# 1. 静态检查
for prof in default afu heidou laomo maodou quant xiaobao zhenglishi; do
  src = [ "$prof" = "default" ] && ~/.hermes/.env || ~/.hermes/profiles/$prof/.env
  sha = $(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' "$src" | shasum -a 256 | awk '{print substr($1,1,16)}')
  echo "$prof: $sha..."
done

# 2. 动态单测
KEY=$(awk -F= '/^MINIMAX_CN_API_KEY/ {print $2}' ~/.hermes/profiles/maodou/.env)
curl -sS -w "HTTP=%{http_code}\n" -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
  -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01" -H "content-type: application/json" \
  -d '{"model":"MiniMax-M3","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}'
```

### 风险与瓶颈

- **并发 4-5 Agent** — 8 profile 共享常撞（待办：再开 1 把订阅 key 轮询）
- **月度 ~18 亿 token** — 估算 2-3 周烧完（待办：写额度监控 cron）
- **key 字符残缺 (401)** — 飞书/终端传输截断（用 sha256 验证，不靠肉眼）

---

## prompt-caching-verified

**🎯 6/30 验证结论：minimax 端点完全支持 Anthropic `cache_control` 头**，响应有 `cache_creation_input_tokens` / `cache_read_input_tokens` 字段。

### 实测响应

```json
{
  "usage": {
    "input_tokens": 186,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 114,  ← 114 token 从缓存读！
    "service_tier": "standard"
  }
}
```

### zhe 6/1 调研的 5 大模式 (立即可用)

1. **系统 Prompt 缓存优先** — 稳定 L1/team_overview_l1 注入，每次都缓存
2. **工具定义分离缓存** — 工具描述加 `cache_control`
3. **对话历史缓存** — 3 轮后开始省
4. **1 小时 TTL** — 夜间批量任务用
5. **缓存断点顺序优化** — 易变内容放最后，前缀稳定才能命中

### 关键规则

- 缓存块 ≥ 1024 tokens 才生效
- 稳定内容放前缀（role/rules/examples）
- 易变内容放后缀（用户查询/日期）
- 缓存读取成本约 1/10 输入价格
- 读取路径：`"system": [{"type":"text","text":"...","cache_control":{"type":"ephemeral"}}]`

### 预期节省

- zhe 调研引用：作者 3800 次/天 × 3800 token 系统 Prompt → **节省 70% 账单**
- 我们场景：8 profile 共享 1 key + 高频 cron 汇报 → **预估节省 50-70% input token**

### 待办 (代码层)

- 改 hermes agent 调用方式，让 L1/team_overview/system 自动加 `cache_control`
- 实测对比（有 vs 无 cache_control）的 token 差异
- cron 重写为 no-agent 模式时考虑 prompt cache

**zhe 调研位置**：`~/Desktop/渔芯科技/9-学习笔记/***SECRET***降低账单.md`

---

## ***SECRET***

### ⚠️ jobs.json ≠ cronjob 全局系统（2026-07-31 实测）

**两个完全独立的存储**：
- `~/.hermes/profiles/<prof>/cron/jobs.json` = profile 本地副本（每个 profile 一份）
- `cronjob` MCP 全局系统 = 实际跑的 cron 任务的 source of truth（**全局唯一**）

**实测差异**：
- cronjob 全局 52 个任务
- 8 profile jobs.json 汇总：default 52 / quant 4 / zhenglishi 9 / 同事 1-3 个
- **大量 jobs.json 任务在全局系统里不存在**（如 quant 4 个 cron：宽博士持续深度调研 / 周一开盘前提醒 / 宽博士每日量化策略日报 / 华哥组合持仓监控）—— jobs.json 是过期本地副本
- 反之，全局 52 个里有部分是 no_agent=true 脚本模式（jobs.json 没记录）

**实战含义**：
- **pause/resume cron** 必须用 `cronjob` MCP 工具 + 全局 id，**不要用 `hermes cron pause <id>` CLI** + jobs.json id（CLI 会全部 not found）
- 想清掉 jobs.json 里的"幽灵 cron"（实际未触发）→ 直接编辑 jobs.json，不影响全局 cron 跑
- 想新增/修改实际跑的 cron → 用 `cronjob(action='create'/'update')`

### 6/30 发现的数学

**每个 profile 视角下看到的 cron** = 全集（含自己 + 其他 7 profile 的副本）。

实际 cron db 是共享的，但 `hermes cron list` 在不同 `HERMES_PROFILE` 下显示**各自视角**看到的副本。

例：5 同事心跳 cron = `262419748f9b` (阿福) / `066886014d67` (小宝) / `260b7b982ab7` (老莫) / `9071b1bae756` (黑豆) / `ac9bae2949bd` (毛豆) — 5 个 cron id
但在 8 profile 视角下，**每个 profile 都看到 5 个** = 5 × 8 = 40 次/小时触发尝试

### 双 cron 重复陷阱 (6/30 实战)

每个 5 同事**有 2 个心跳 cron**：
- 老心跳 (no-skill 模式) — `262419748f9b` 阿福-客服心跳 等
- 双 cron (用 skill 模式) — `老莫-每小时心跳汇报` / `小宝心跳-每小时汇报` / `毛豆-每小时汇报` / `黑豆心跳汇报` / `阿福心跳汇报`
- **双 cron 的 skill 全部 `not found`** (`laomo-knowledge` / `xiaobao-heartbeat` / `maodu-task-status-reporter` / `heidou-workflow` 都不存在)
- **每 5 同事的双 cron 每小时 402** = 每天 5 × 24 = 120 次失败 LLM 调用

### 数学汇总 (9 profile 视角)

- 实际唯一 cron id 数：~12
- 9 profile 视角下重复：~12 × 9 = 108 个 job
- 每小时 LLM 调用尝试：~96 (实际很多 no-agent 不调 LLM，但失败的会试)
- 失败 cron 每小时浪费：~5 个 (120 次/天)
- 玉芬额外：主动巡视 6/天 + 自进化 12/天 + 早间简报 1/天 + Tokens 多维日报 1/天 = 20 次/天

### 去重方案（已实施）

**选项 A — no-agent 化** ✅ 已实施（2026-07-04）
- 毛豆心跳 → `~/.hermes/scripts/maodou_heartbeat.sh` (no_agent=true)
- 玉芬巡视 → `~/.hermes/scripts/yufen_patrol.sh` (no_agent=true)
- 零 token 消耗，有任务才出声，无任务静默
- 详见 `references/no-agent-cron-heartbeat.md`

**选项 B — 单视角心跳**（待定）
- 只保留 1 个 profile 跑心跳，其他 7 profile 删

**选项 C — 删除失败双 cron** ✅ 已实施（2026-07-04）
- 删除了 2 个 `agent-skills-scan` 坏 cron（Broken pipe）

---

### 🔴 陷阱：heartbeat_check.py 三数据库盲区 — `~/.hermes/tasks.db` 被遗漏（2026-08-09 创业项目 P0 断层）

**症状**：AI 创业项目 9 条 P0 任务全部在 `~/.hermes/tasks.db`，但所有同事 Agent 心跳都报告"无待处理任务"，任务进度汇报 cron 显示 11% 完成率（仅小宝 1/9）。

**根因**：`heartbeat_check.py` 只扫描两个数据源：
- `~/.hermes/kanban.db`（真源）✅
- `~/Desktop/渔芯科技/团队协作/tasks.db`（桌面,历史遗留）✅
- **`~/.hermes/tasks.db`**（hermes 内置,创业项目 P0 全部在这里）**❌ 不查！**

**结果**：任务存在但 Agent 根本看不见 → 心跳返回空 → 进入自我进化模式 → P0 任务零进展。

**修复（2026-08-09 已实施）**：
1. 迁移 P0 任务到 kanban.db（真源）
2. 在 `heartbeat_check.py` 新增 `query_hermes_tasks()` 函数，查询 `~/.hermes/tasks.db` 作为第三后备源
3. 详见 `references/***SECRET***.md`

**关键教训**：发现同事"不干活"时，先验证他们能不能**看到**任务 — 跑 `python3 ~/.hermes/scripts/heartbeat_check.py <agent>` 确认心跳返回值。

### 🔴 陷阱：cron 中 `~` 波浪号解析到 profile 家目录（2026-07-15 小宝心跳复现）

**问题（2026-07-15 实战复现）**：
当 cron job 在某个 profile 上下文中运行时（如 quant profile 运行小宝心跳），`~/.hermes/scripts/heartbeat_check.py` 中的 `~` 波浪号 **不是解析到 `/Users/hua/`**，而是解析到 **该 profile 的 home 目录**：
```
~/.hermes/scripts/heartbeat_check.py
→ 实际解析为：/Users/hua/.hermes/profiles/quant/home/.hermes/scripts/heartbeat_check.py
```
该路径通常不存在，导致 cron 执行直接报错：
```
[Errno 2] No such file or directory: '/Users/hua/.hermes/profiles/quant/home/.hermes/scripts/heartbeat_check.py'
```

**并行问题：profile 下的 tasks.db 是空占位符（2026-07-15 发现）**：
```
~/.hermes/profiles/xiaobao/tasks.db  # 0 字节，空文件
~/.hermes/tasks.db                   # 真实 Global Tasks DB（12KB+，有 schema）
```
`heartbeat_check.py` 写的是 **根目录** 的 `~/.hermes/tasks.db`，不是 profile 下的。如果 cron 路径解析错了，脚本会尝试在 profile home 下创建新的空 DB。

**紧急兜底（遇到报错立即执行）**：
如果 cron 已经报错，不要等修复配置 — 直接查 tasks.db 真源：
```python
import sqlite3
conn = sqlite3.connect('/Users/hua/.hermes/tasks.db')
cur = conn.cursor()
cur.execute("SELECT id, title, status, priority FROM tasks WHERE assigned_to='小宝' AND status='pending' ORDER BY CASE priority WHEN 'P0' THEN 1 WHEN 'P1' THEN 2 ELSE 3 END, created_at ASC LIMIT 1")
task = cur.fetchone()
conn.close()
if not task:
    print("✅ 小宝 无待处理任务")
else:
    print(task)  # 继续处理
```

**根本解决方案（二选一）**：

**方案1（推荐 ✅）：cron 用绝对路径调用**
修改 cron prompt 中的命令，直接用全局绝对路径：
```bash
python3 /Users/hua/.hermes/scripts/heartbeat_check.py 小宝
```

**方案2：在每个 profile 下复制脚本**
```bash
# 列出所有 profiles：ls /Users/hua/.hermes/profiles/
# 对每个需要心跳的 profile（quant, xiaobao, maodou, laomo, heidou, afu, zhenglishi...）
mkdir -p /Users/hua/.hermes/profiles/quant/home/.hermes/scripts
cp /Users/hua/.hermes/scripts/heartbeat_check.py /Users/hua/.hermes/profiles/quant/home/.hermes/scripts/
```

**🆕 2026-08-28 黑豆实测补充 — AGENTS.md 自身路径也会断**：本节覆盖"cron 命令里直接 `~/.hermes/...`"，但 AGENTS.md / SKILL.md **规范本身**用的也是 `~/.hermes/profiles/<prof>/...` 相对路径（如 `~/.hermes/profiles/heidou/memory/`），在 cron 模式下同样解析到 `profiles/<prof>/home/.hermes/profiles/heidou/memory/`（不存在）。**解决方案**：cron 模式下所有写盘/读盘命令必须用绝对路径 `/Users/hua/.hermes/profiles/<prof>/...`，不仅是 `~/.hermes/scripts/...`。详见 `references/***SECRET***.md`。

**快速排障清单（报错时按顺序检查）**：
```bash
# 1. 检查全局脚本是否存在
ls -la /Users/hua/.hermes/scripts/heartbeat_check.py

# 2. 检查当前 profile 的家目录
ls -la /Users/hua/.hermes/profiles/quant/home/.hermes/scripts/ 2>/dev/null || echo "Profile scripts dir does not exist"

# 3. 检查全局 tasks.db 是否存在 + 有 schema
ls -la /Users/hua/.hermes/tasks.db
sqlite3 /Users/hua/.hermes/tasks.db ".schema tasks"  # 应该看到 CREATE TABLE ...

# 4. 检查指定同事的待处理任务（正确列名）
sqlite3 /Users/hua/.hermes/tasks.db "SELECT id, title, status, priority FROM tasks WHERE assigned_to='小宝' AND status='pending' ORDER BY CASE priority WHEN 'P0' THEN 1 WHEN 'P1' THEN 2 ELSE 3 END, created_at ASC LIMIT 1"
```

**关键事实**：
- cron 运行时的工作目录 = profile 的 home 目录，**不是** `/Users/hua/`
- `~` 波浪号解析由 shell/OS 决定，cron 在 profile 上下文中会解析到 profile 家目录
- `/Users/hua/.hermes/scripts/heartbeat_check.py`（全局）是真实存在的，只是 cron 找不到
- **所有 9 个 profiles** 都会遇到这个问题（不仅是 workflow agents）
- 2026-07-13 已创建全局脚本 + 全局 tasks.db（初始化空表）
- **Global Tasks DB 列名差异**：`assigned_to` 列（不是 `assignee`，也不是 `agent`），优先级字符串 `'P0'`/'P1'/'P2'（不是数字 0/1/2）
- **Profile tasks.db 是空占位符**：每个 profile 下的 `~/.hermes/profiles/<prof>/tasks.db` 是 0 字节空文件，**不是**真实任务数据库
- **真实任务 DB 位置**：`/Users/hua/.hermes/tasks.db`（根目录，约 12KB+，有完整 schema）
- **tasks 表 schema**：`id INTEGER PRIMARY KEY`, `title TEXT`, `description TEXT`, `assigned_to TEXT`, `priority TEXT DEFAULT 'P2'`, `status TEXT DEFAULT 'pending'`, `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`, `updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`

**判断何时触发**：
- cron 执行报 `No such file or directory` 且路径含 `profiles/*/home/` → 就是这个问题
- 每个 Agent 的心跳 cron 第一次执行时大概率会遇到

---

## session-archive-math

### 6/30 实战结果

| Profile | 原始 sessions | active (7d) | archive (30-90d) | old (>90d) | 节省空间 |
|---|---|---|---|---|---|---|
| default | 12758 | 329 | 12429 | 0 | 1.8GB → 34MB |
| afu | 733 | 55 | 678 | 0 | 87MB → 4.9MB |
| heidou | 1433 | 54 | 1379 | 0 | 170MB → 4.1MB |
| laomo | 810 | 64 | 746 | 0 | 120MB → 6.9MB |
| maodou | 900 | 55 | 845 | 0 | 130MB → 4.7MB |
| quant | 3308 | 52 | 3256 | 0 | 676MB → 4.2MB |
| xiaobao | 1077 | 108 | 969 | 0 | 138MB → 8.3MB |
| zhenglishi | 3058 | 165 | 2893 | 0 | 333MB → 13MB |
| **wangcai** | **0** (新) | **0** | **0** | **0** | 新 profile，无历史 session |
| **总计** | **24550** | **882** | **23195** | **0** | **~3.7GB → ~80MB (96% 节省)** |

### 归档策略

- **7 天内**: active (高频检索)
- **7-30 天**: gzip 压缩 (session 仍可查)
- **30-90 天**: 移到 `sessions_archive/`
- **90 天+**: 移到 `sessions_old/` (可手动清理)

### 文件名格式 (3 种, 6/30 适配)

- `20260425_233232_326e2470.jsonl` (default + zhe) — `YYYYMMDD_HHMMSS_<hex>.<ext>`
- `session_20260426_002321_xxx.json` (部分)
- `request_dump_cron_<id>***SECRET***.json[.gz]` (maodou/xiaobao)

**提取日期正则**：`grep -oE "20[0-9]{6}" | head -1` — 第一个 8 位数字串

### 自动 cron

- `e330c9cdaa05` (session-archive-all-profiles, `0 3 * * 0` 周日 3AM)
- 脚本: `~/.hermes/scripts/session_archive_one.sh` + `session_archive_all.sh`
- 权限: 700

### 触发时机

- 任意 profile sessions 数 > 1000 → 立刻跑一次
- 每周日 3AM 自动跑
- 磁盘占用 > 5GB → 立刻跑

---

### cross-platform-github-repo

### 概述

渔芯技能/配置通过 GitHub 仓库 `github.com/openclaw-cn-dev/yuxin-skills` 跨机器共享。这是解决 Windows（旺财）与 macOS（其他 8 profile）之间技能同步的核心机制。

### 仓库结构 (v2.0 — 2026-07-08)

```
yuxin-skills/
├── agents/                          # 所有智能体定义
│   ├── index.json                   # Master 注册表（12+ agents）
│   ├── hermes/                      # Hermes Agent profiles
│   │   ├── template/                # 新建 Hermes 同事模板
│   │   └── wangcai/                 # 旺财（MEMORY/USER/config.yaml）
│   ├── codex/                       # Codex CLI 配置
│   │   ├── template/                # 新建 Codex CLI 模板
│   │   └── wangcai/                 # 旺财的 Codex AGENTS.md
│   ├── claude-code/                 # Claude Code 模板
│   └── openclaw/                    # OpenClaw 网关模板
├── skills/                          # 共享技能
│   ├── wangcai-cad/                 # CAD/SolidWorks 出图
│   └── wangcai-social-media/        # 自媒体自动化运营
├── playbooks/                       # 📖 标准操作流程
│   ├── onboard-new-agent.md         # 新建智能体 SOP（5 阶段：角色→模板→注册→部署→验证）
│   ├── sync-skills-from-mac.md      # 技能同步指南
│   └── health-check-all-agents.md   # 全智能体健康检查
└── templates/                       # 部署模板
    ├── hermes-agent/                # Hermes 部署包
    │   ├── setup_wangcai.ps1       # Windows 一键部署
    │   └── INSTALL.md               # Windows 部署说明书
    └── codex-cli/                   # Codex CLI 配置
        └── AGENTS.md                # Codex 角色配置
```

### 跨机器共享流程

```bash
# macOS — 推送更新
cd ~/.hermes/skills-repo && git pull && git add -A && git commit -m "..." && git push

# Windows — 拉取更新
cd %USERPROFILE%\.hermes\skills-repo && git pull
```

### Secret 安全管理

**🚨 必须：不要将飞书 Secret 等敏感信息提交到 Git 仓库。**

GitHub 默认开启 push protection，检测到 config.yaml 等文件中的密钥会阻止推送。

**正确做法**：
1. 在配置文件中使用占位符 `***SECRET***`
2. 本地部署时手动替换为真实 Secret
3. 提交前检查 `git diff --cached` 确认无密钥泄露

```yaml
# config.yaml — 占位符模式（安全推送）
feishu:
  app_id: cli_xxx
  app_secret: "***SECRET***"  # ⚠️ 部署时替换
```

**如需修复已提交的密钥**：
```bash
# 1. 替换密钥为占位符
# 2. amend 提交
git commit --amend
git push --force-with-lease
```

### 在 Windows 上部署新 Agent

参考 `playbooks/onboard-new-agent.md` 中的完整 5 阶段流程。快速版：

1. 克隆仓库：`git clone git@github.com:openclaw-cn-dev/yuxin-skills.git %USERPROFILE%\\.hermes\\skills-repo`
2. 安装 Hermes Agent：`pip install hermes-agent`
3. 选择模板：`copy %USERPROFILE%\\.hermes\\skills-repo\\agents\\hermes\\template\\* <新同事名>\\`
4. 填写 MEMORY.md / USER.md / config.yaml（替换 Secret 占位符）
5. 注册到 `agents/index.json`
6. 启动 gateway：`hermes gateway run --profile <新同事名>`
7. 飞书私聊激活（见 `***SECRET***`）

或者使用一键脚本（Windows PowerShell 管理员）：
```powershell
# 旺财专用
.\\templates\\hermes-agent\\setup_wangcai.ps1
```

### 关键陷阱

- **Secret 泄露风险** — GitHub push protection 会在提交时拦截，但最好 commit 前检查
- **Windows 路径反斜杠** — 仓库中统一用正斜杠 `/`，部署脚本自动处理
- **PowerShell 执行策略** — 首次运行需 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
- **Codex CLI** — 旺财在 Windows 上使用 Codex CLI 作为编程引擎（生成 CadQuery/SolidWorks 代码），Hermes 负责调度执行

## ***SECRET***

### 6/30 教训（黑豆/阿福）

**根因**：飞书企业应用"接收消息"事件，需要**用户↔bot 至少 1 次主动交互**才会触发 webhook 推送。

6/29 资源政策关停 5 同事 launchd → 6/30 15:54 重启 → 飞书侧路由失效 → 华哥私聊黑豆/阿福**没回复**（消息被飞书侧拒收）。

### 🔴 陷阱：`hermes gateway run --replace` 不在 launchctl list 中（2026-07-03 实测）\n\n当用 `hermes gateway run --profile maodou --replace` 手动拉起 gateway 时，进程在 `ps aux` 可见但 **`launchctl list | grep ai.hermes.gateway-maodou` 找不到**。\n\n**原因**：manual `--replace` 不走 plist/launchd。`launchctl list` 只显示通过 `launchctl load/bootstrap` 加载的 plist 服务。\n\n**Patrol 金标准**：\n```bash\n# 查所有 gateway 进程（包含 manual 拉起）\nps aux | grep \"hermes.*gateway\" | grep -v grep | awk '{print $2, $11, $12, $13, $14}'\n# 查 launchd 管理的（只包含 plist 服务）\nlaunchctl list | grep \"ai.hermes\"\n# 两者对照，manual 启动的只出现在 ps 中\n```\n\n**量化/学习助手 launchd plist 缺失问题**：quant 和 zhenglishi 的 plist 文件 `~/Library/LaunchAgents/ai.hermes.gateway-{quant,zhenglishi}.plist` **存在**（7 个 plist），但进程消失后 `launchctl print` 显示 \"Could not find service\" = plist 未被 load。重启后手动拉起的进程会自动消失，因为没有 plist 自动恢复机制。\n\n**修复**（如果目标是要开机自启）：\n```bash\nlaunchctl load ~/Library/LaunchAgents/ai.hermes.gateway-{prof}.plist\n# 验证\nlaunchctl print gui/$UID/ai.hermes.gateway-{prof}  # 必须返回服务详情，不是 \"Could not find\"\n```\n\n### 🚨 PITFALL (2026-07-01 实测): 玉芬 Bot 不在同事群/同事 DM，唯一稳定跨同事通道是大群 `@`-mention

**症状**：`feishu send failed: [230002] Bot/User can NOT be out of the chat.`

**同事频道可达性矩阵 (2026-07-01 实测，default profile App ID `cli_a964873dd7b8dbda`)**：

| 目标频道 | Chat ID | 玉芬可达 | 备注 |
|---|---|---|---|
| 渔芯科技 (大群) | `***SECRET***` | ✅ | **唯一稳定的跨同事通道** |
| 华哥↔玉芬 (DM) | `***SECRET***` | ✅ | 默认 home channel |
| 产品部-毛豆 (群) | `***SECRET***` | ❌ | 230002 |
| 毛豆 DM | `***SECRET***` | ❌ | 230002 |
| 技术部-老莫 (群) | `***SECRET***` | ❌ | 230002 |
| 销售部-小宝 (群) | `***SECRET***` | ❌ | 230002 |
| 行政财务-黑豆 (群) | `***SECRET***` | ❌ | 230002 |
| 客服部-阿福 (群) | `***SECRET***` | ❌ | 230002 |

**SOP (直接执行，不再试错)**：

1. 派单 → 写 `~/Desktop/渔芯科技/4-部门空间/<同事>-<职责>/workspace/<task>.md`
2. 派单 → 写 `tasks.db` (assignee=同事, status=in_progress)
3. 派单 → `send_message` 到 **大群 `@<同事名字>`** (不要先试群/DM)
4. 等 60s → 同事 cron ticker 自动从 workspace + tasks.db 拉取任务

**为什么大群 = 唯一通道**：飞书企业应用加 bot 进群需要华哥审批；单纯 REST 发送，玉芬 bot 必须在该 chat 的成员列表里 = 不在同事群/同事 DM = 230002

**边界情况**：
- 大群 `@` 不显示 → 用纯文本 `@毛豆 ` (飞书 mention 自动解析)
- 同事 bot 不在线 → 大群消息到了但读不到 → 先 `launchctl load` 同事 gateway (见 `launchd-guardian-sop`)
- 消息确认 → 检查 `send_message` 响应里的 `message_id`，存到派单文件作为回执

### 玉芬主动发到大群 ≠ 激活私聊

- 玉芬用 bot 主动发消息到大群：成功（"走主动发送 API"，不受影响）
- 华哥私聊 bot：失败（飞书侧路由未激活）

### 激活方法（华哥手动，30 秒）

1. 飞书搜索 bot 名字
2. 点开对话
3. 发任意一句话（"在吗"）
4. 如有"开始对话"提示 → 点击

### 预防

- **拉起 launchd 后** — 玉芬主动告诉华哥"X 同事需要您私聊激活"
- **避免长时间停机** — 长期不活跃 bot 路由会失效
- **飞书后台** — 定期检查"接收消息 v2.0"事件订阅是否启用

### 检测命令（玉芬自助）

```bash
# bot 能否列出用户对话
curl -sS "https://open.feishu.cn/open-apis/im/v1/chats?page_size=20" \
  -H "Authorization: Bearer <tenant_access_token>"
# 正常 = 至少 2 个 (HOME channel + 大群)
# 异常 = 0 个 (bot 被踢/未激活)
```

---

## launchd-guardian-sop

### 当前 8 gateway 状态 (6/30 16:00+)

| Profile | PID | 启动方式 |
|---|---|---|
| default | 3876 | 老进程 (8:01AM) |
| maodou | 46493 | launchctl load (15:54) |
| laomo | 46496 | launchctl load (15:54) |
| xiaobao | 46499 | launchctl load (15:54) |
| heidou | 46502 | launchctl load (15:54) |
| afu | 46505 | launchctl load (15:54) |
| quant | 42358 | 老进程 (6/29) |
| zhenglishi | 42361 | 老进程 (6/29) |

### 诊断命令（先查 disabled 状态）

```bash
# 检查所有 gateway 服务是否被 disabled（macOS 26 常见）
launchctl print-disabled gui/$(id -u) | grep "ai.hermes.gateway"
# 输出示例： "ai.hermes.gateway-laomo" => disabled
```

### 拉起命令（三步法）

```bash
# 第1步：如果服务被 disabled，先 enable
# ⚠️ UID 是 bash 只读变量，不能 UID=$(id -u)，必须用 myuid 或其他变量名
myuid=$(id -u)
launchctl enable gui/$myuid/ai.hermes.gateway-<prof>

# 第2步：legacy load（不要用 bootstrap）
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway-<prof>.plist

# 第3步：验证
launchctl list | grep ai.hermes.gateway-<prof>
# 期望输出：PID	0	ai.hermes.gateway-<prof>
```

### 🔴 陷阱：services 被 disabled 时 legacy load 报 I/O error

**症状**：`launchctl load` 报 `Load failed: 5: Input/output error`，但 plist 语法检查通过。

**根因**：macOS 26 下 launchd 服务可能处于 **disabled** 状态（`launchctl print-disabled` 可见）。直接 `load` 会报 I/O error，必须先 `enable`。

**完整修复流程**（2026-07-04 实战验证）：
```bash
# ⚠️ UID 是 bash 只读变量，必须用 myuid 等替代
myuid=$(id -u)

# 1. 检查 disabled 状态
launchctl print-disabled gui/$myuid | grep "ai.hermes.gateway-<prof>"
# 如果显示 disabled：

# 2. enable
launchctl enable gui/$myuid/ai.hermes.gateway-<prof>

# 3. load（现在应该成功）
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway-<prof>.plist

# 4. 验证
launchctl list | grep ai.hermes.gateway-<prof>
```

### 🔴 陷阱：bootstrap 报 I/O error（plist 已注册但进程僵死）

**症状**：`launchctl bootstrap` 报 `Bootstrap failed: 5: Input/output error`，但 `enable` 已执行过。

**根因**：plist 已在 launchd 服务表注册（残留状态），bootstrap 无法覆盖已有注册。即使进程已死，launchd 仍认为该 label 被占用。

**修复：先 bootout 再 bootstrap**（2026-08-10 实战验证）：
```bash
myuid=$(id -u)
# 1. 清理残留注册
launchctl bootout gui/$myuid/ai.hermes.gateway-<prof> 2>/dev/null
sleep 1

# 2. 重新注册
launchctl bootstrap gui/$myuid ~/Library/LaunchAgents/ai.hermes.gateway-<prof>.plist

# 3. 验证
launchctl list | grep ai.hermes.gateway-<prof>
```

**注意**：优先使用 `launchctl load`（legacy），bootstrap 仅在 `load` 不支持的场景使用。**实测区分（2026-08-30）**：`disabled` 服务用 `enable` + legacy `load` 即可；但 `enabled` 且进程已死（`launchctl list` 显示 `Exit=-9` 或 PID 缺失）的服务，`bootout` 后 legacy `load` 仍报 `Load failed: 5: Input/output error`，**必须 `bootout` 再 `bootstrap`**（不是 load）。

### 停止

```bash
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-<prof>.plist
```

### 重启

```bash
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway-<prof>.plist
sleep 2
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway-<prof>.plist
```

### 验证

```bash
launchctl list 2>/dev/null | awk -v lbl="ai.hermes.gateway-<prof>" '$3==lbl {print $1; exit}'
# 期望：非空 PID
```

### 关键陷阱

- **label 匹配必须精确** (`$3==lbl` 不是 grep) — 因为 `ai.hermes.gateway` 前缀会匹配 `ai.hermes.gateway-<prof>` 用 grep
- **legacy load 优先** — bootstrap 在 6 同事 plist 报 I/O error
- **services 可能被 disabled** — 先 `launchctl print-disabled` 检查，`enable` 后再 `load`（见上方诊断命令）
- **拉起后等 3-5 秒** — gateway 启动 + 飞书 WS 连接需要时间
- **plist 不要嵌入 API key** — 不要写 `MINIMAX_CN_API_KEY` 到 plist 的 EnvironmentVariables。正确做法：plist 只设 `HERMES_HOME=/Users/hua/.hermes` + `--profile <name>`，API key 放在 profile 的 `.env` 中。嵌入 key 的 plist 在 macOS 26 下可能导致 `launchctl load` 行为异常
- **日志文件名用 `gateway-launchd.log`** — 不要用 `gateway.log`，避免与手动 `hermes gateway run` 进程的日志冲突
- **🔴 飞书 app_id 冲突** — 如果 profile 缺独立 `.env`（无 `FEISHU_APP_ID`），会继承全局值，与 default 的飞书 websocket 锁冲突 → gateway 启动即退出（日志：`non-retryable startup conflict: feishu`）。**每个 profile 必须有独立 `.env`**，要么设专属 Feishu bot，要么显式置空 `FEISHU_APP_ID=` 禁用飞书。详见 `references/feishu-appid-conflict.md`

### 一键验证脚本

`~/hermes/team/runbooks/verify_team_health.sh` — 跑一次看 8 profile 完整健康状态 (gateway + LLM + WS + .env 备份)。

---

## 402-401-429-diagnosis

### 错误码速查 (6/30 实战)

| HTTP | 错误 | minimax 响应 | 根因 |
|---|---|---|---|
| 401 | authentication_error | "Please carry the API secret key" | **key 字符残缺** (飞书/终端脱敏截断) |
| 402 | insufficient_balance_error | "insufficient balance (1008)" | **订阅/月度 token 用完** |
| 429 | rate_limit_error | (未实测) | **5h 限额 / 并发 4-5 上限** |

### 401 诊断 (key 字符 / 前缀问题)

- 错误信息："login fail: Please carry the API secret key in the 'X-Api-Key' field"
- **空 key 和错 key 报同样错** (端点收不到有效 key)
- 根因 1：key 字符串字符数不对 (订阅 key 必须 125 字符)
- 根因 2（2026-08-17 玉芬反复报 401 的真相）：`.env` 的 `MINIMAX_CN_API_KEY` 被误填成**火山 ark key（46位）**。hermes 内置 minimax-cn 走国内 key `MINIMAX_CN_API_KEY`，拿火山 key 调 MiniMax 官方 API → 401。**诊断：`grep '^MINIMAX_CN_API_KEY=' ~/.hermes/.env`，前缀 `ark`（46位）=错，须 `sk-cp`（125位）**。
- 修复：让华哥重新贴 key → sha256 验证 → 铺同事 .env；若玉芬 .env 国内 key 是 ark，直接从任一同事 .env（如 afu）复制正确的 sk-cp key 覆盖

### 402 诊断 (额度耗尽)

- 错误信息："insufficient balance (1008)"
- 多个同事**同时**报 402 (共用一个池)
- 修复：等下月自动重置 / 充值按量 fallback / 暂停不忙的 cron

### 429 诊断 (频率限制)

- 7 profile 共享 1 key, **并发撞上限 4-5 Agent**
- 修复：暂停部分 cron / 等 5h 自动恢复 / 再开 1 把订阅 key 轮询

### 完整诊断流程图

```
华哥: "X 同事挂了"
  │
  ├─→ 1. 跑健康检查 ~/.hermes/scripts/minimax_health_check.sh
  │     │
  │     ├─ 空输出 = 端点 OK → 跳到 (2)
  │     └─ 有输出 → 看 HTTP 码 → 401/402/429 分支
  │
  ├─→ 2. 查 launchd + 飞书
  │     launchctl list | grep ai.hermes.gateway-X
  │     tail -50 ~/.hermes/profiles/X/logs/gateway.log
  │     │
  │     ├─ 进程在 + 日志正常 → 私聊路由问题 (走 飞书私聊路由激活)
  │     └─ 进程没了 → 拉起 launchd
  │
  └─→ 3. 私聊路由激活
        华哥飞书搜索 → 发一句话 → 激活
```

---

## 🟢 团队健康全量巡检（5 分钟 SOP）

当华哥问"同事正常吗"时，按以下顺序跑一遍（首选绝对路径 `python3 /Users/hua/...`，防止 profile HOME 劫持）。

### 1. Gateway 进程状态
```bash
launchctl list | grep "ai.hermes.gateway" | awk '{printf "%-32s PID=%-8s Exit=%-4s\n", $3, $1, $2}'
# 期望：9 个都在。Exit 非 0 不一定是故障（kickstart -k 会留 Exit:-9）
```

### 2. 飞书连接 + LLM 活跃度
```bash
for prof in maodou laomo xiaobao heidou afu quant zhenglishi community; do
  last=$(grep "feishu.*Connected\|Disconnected" /Users/hua/.hermes/profiles/$prof/logs/gateway.log 2>/dev/null | tail -1)
  calls=$(grep "$(date +%Y-%m-%d)" /Users/hua/.hermes/profiles/$prof/logs/agent.log 2>/dev/null | grep -c "tool_call\|response")
  printf "%-12s 飞书: %s  今日调用: %s\n" "$prof:" "${last: -30:-3}" "${calls:-0}"
done
```

### 3. LLM 连接错误
```bash
for prof in maodou laomo xiaobao heidou afu quant zhenglishi; do
  errors=$(grep "$(date +%Y-%m-%d)" /Users/hua/.hermes/profiles/$prof/logs/gateway-launchd.error.log 2>/dev/null | grep -ci "ERROR\|401\|402\|403\|429\|timeout")
  printf "%-12s 错误: %s\n" "$prof:" "${errors:-0}"
done
```

### 4. Cron 任务实际执行情况
```bash
for prof in maodou laomo xiaobao heidou afu quant zhenglishi; do
  echo "--- $prof ---"
  grep "$(date +%Y-%m-%d)" /Users/hua/.hermes/profiles/$prof/logs/agent.log 2>/dev/null | grep -i "job.*fail\|job.*complete\|delivered" | tail -5
done
```

关键判据：
- 飞书 `Connected` 但今日调用 0 = 可能在 idle（没收到任务）
- 飞书 `Disconnected` = 需重启
- LLM 错误 > 0 = 查具体错误码
- 无 cron 记录 ≠ cron 没跑（可能 no_agent 脚本模式，不写 agent.log）

---

## 🔴 陷阱：审批按钮 "Unauthorized approval click" — session 过期导致审批无效

### 症状
华哥在飞书收到 agent 弹出的审批按钮，点击后日志显示 `WARNING: Unauthorized approval click by <user_id>`，按钮反复点都过不了。用户配对正常（`hermes pairing list` 显示已批准）。

### 根因
Hermes 飞书审批按钮绑定到**生成按钮时的活跃 session**。一旦 agent 收到新消息进入新的处理轮次，旧 session 的审批卡片就失效。高频率 cron agent（如学习助手）经常在上一轮 cron 还没跑完时收到华哥新消息 → session 重建 → 旧按钮全部 Unauthorized。

### 修复（永久）
```bash
# 改为 smart 模式：低风险命令自动批准，高风险仍提示
hermes -p <profile> config set approvals.mode smart
# 重启 gateway
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway-<profile>
```

### 适用场景
所有高频率 cron agent（学习助手、宽博士、毛豆等），避免审批弹窗打断任务流水线。

---

## 🔴 陷阱：Cron job provider 漂移 — 换 provider/model 后 job 仍指旧值

### 症状
切换了 profile 的 provider/model（如 minmax-cn → deepseek-cn），gateway 重启后 cron job 报 `Unknown provider 'deepseek-direct'` 或类似错误。

### 根因
Hermes cron job 在 `jobs.json` 中**独立存储** `provider` 和 `model` 字段。修改 `config.yaml` 不会自动同步到已有的 cron job。job 创建时会把当时的 provider/model 快照进去。

### 检测
```bash
python3 -c "
import json
with open('/Users/hua/.hermes/profiles/<prof>/cron/jobs.json') as f:
    data = json.load(f)
jobs = data if isinstance(data, list) else data.get('jobs', [])
for j in jobs:
    p = j.get('provider', 'N/A')
    if p and p not in ['None', None]:  # 显式设置了 provider
        print(f\"  {j.get('name','?')}  provider={p}  model={j.get('model','?')}\")
"
```

### 修复（批量）
```python
import json
path = '/Users/hua/.hermes/profiles/<prof>/cron/jobs.json'
with open(path) as f:
    data = json.load(f)
jobs = data if isinstance(data, list) else data.get('jobs', [])
for j in jobs:
    if j.get('provider') == '<旧 provider>':
        j['provider'] = '<新 provider>'
        j['model'] = '<新 model>'
is_list = isinstance(data, list)
with open(path, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2 if is_list else None)
# 验证 JSON
python3 -c "import json; json.load(open(path)); print('OK')"
```

### 预防
每次 `hermes config set model X --profile <prof>` 后，必须检查 `jobs.json` 是否有硬编码旧 provider/model 的 job。

---

## 🔄 批量 Provider 切换脚本模式

午夜 00:05 自动切换 6 个 agent 从 DeepSeek 到 MiniMax 的脚本模板：
`~/.hermes/scripts/switch_to_minimax.py`

**模式**：
1. 先 curl 测目标 provider 额度（防止无额度盲切）
2. 更新 root `config.yaml` 的 provider 配置
3. 逐个 patch profile `config.yaml` 的 model + provider
4. `launchctl kickstart -k` 逐个重启 gateway

**关键点**：
- 用 `no_agent=true` cron job + 脚本（零 LLM token）
- 测额度失败 → `sys.exit(1)` 不执行切换
- 用 Python 读写 YAML/JSON（不用 sed，profile HOME 劫持风险）

---

## 🔴 大规模搬迁/重组必查并行执行者（2026-09-12 RKR 62万文件重组实战）

共享资产树（RKR 文档库、~/6-产品研发）是全团队共享盘——**动手前先确认没有另一个会话在跑同一方案**。P62 教训防"同日换技术路线"（版本维度），本教训防"双会话同时 mv"（执行维度）。

**动手前 30 秒三查**：
```bash
pgrep -fl 'hermes-snap'                  # hermes 派生的活跃 bash 任务（特征临时文件名）
lsof +D /目标目录 2>/dev/null | head     # 谁的句柄在树里
ls -lt /目标目录 | head                  # 顶层最近修改（有无"正在进行"痕迹）
```
发现活跃执行者 → 从其 eval 脚本内容看进度（`ps -p <pid> -o command | tr '\\' '\n' | sed -n '/eval/,/__hermes_ec/p'`）→ **停手走止损协议**：①自己一切写操作停止，不"修复"对方半成品 ②还原自己误伤部分（mv 回原位 + `find <误建目录> -depth -type d -empty -delete`）③汇报华哥给选项（让对方跑完转验收 vs 叫停接管），不抢文件树。

**搬迁四步纪律**：① APFS 快照（`cp -Rc`，31GB 实测 1m54s，零额外占用）+ `find -type f | wc -l` 对账基线（62 万级 du/find 放后台跑）② 冻结所有写目标树的 cron（staging_save.py 写中转站不在此列；迁完 resume）③ mv 用绝对路径、禁长 cd 链、每条 `&& echo OK-标签`，报 No such file 立即停 ④ 源路径逐条 `ls -d` 验证——清单布局可能与实际差一层壳。完整复盘见 `references/***SECRET***.md`。

## 配套文件

- `references/***SECRET***.md` — **Hermes 计费与 Token 统计**（state.db sessions 表是权威数据源、usage_pricing.py 硬编码定价字典、华哥 provider 组合的费用全 0 根因与修复、订阅模型标 included）
- `~/hermes/team/README.md` — 团队总档入口
- `~/hermes/team/team_overview.md` — 8 profile 速查
- `~/hermes/team/agents/<prof>.md` — 7 同事详细档案
- `~/hermes/team/communication/message_routing.md` — 飞书私聊路由详细
- `~/hermes/team/infra/minimax_subscription.md` — 订阅架构详细
- `~/hermes/team/infra/gateway_launchd.md` — launchd 详细
- `~/hermes/team/infra/health_checks.md` — 健康检查详细
- `~/hermes/team/infra/cron_inventory.md` — 25 个 cron 清单
- `~/hermes/team/memory/architecture.md` — 三层记忆架构详细
- `~/hermes/team/runbooks/verify_team_health.sh` — 一键验证
- `~/hermes/team/runbooks/restart_gateway.sh` — 重启 gateway
- `~/hermes/team/runbooks/401_402_429_diagnosis.md` — 错误诊断
- `~/hermes/memory_store/lessons/minimax_subscription_vs_payg.md` — 6/30 完整复盘
- `~/hermes/memory_store/lessons/multi_profile_api_key_sync.md` — key 同步规范

## Token 支出统计

华哥会要求「汇总公司 token 支出明细」（成本监控）→ 见 `references/token-usage-reporting.md`：数据源 = 各 profile state.db 的 sessions 表；费用字段未启用（全 0）需按公开单价估算；缓存 token 占比 ~93% 是 prompt caching 别误读为新消耗；`tokens_report.py` 手动跑报「未找到数据」要直接查 state.db。

## 🔴 陷阱：陷阱诊断沿用上份结论导致连续误判（2026-08-20 毛豆 08-20_16 实测）

**症状**: 8-20_04 / 08 / 12 三份毛豆进化报告都报"SKILL.md 缺失 9 个 references,W3 启动门槛第 5 项阻塞"，但实测只有 1 个缺失。

**根因**: 后份报告**沿用前份的扫描路径结果**,没重新实测 → 错判被 3 份报告层层"加固",直到 16:00 改用 `find -type d` 多路径定位才打破。

**修复**: 任何陷阱诊断报告必须含以下**自洽校验段**:
```markdown
## 自洽校验段（强制）
- [ ] 本期使用的扫描路径: <绝对路径>
- [ ] 路径是否 `ls -la` 验证存在: ✅ / ❌
- [ ] 是否多路径扫描定位: ✅ (`find ... -type d`) / ❌ (单一假设路径)
- [ ] 是否独立于上份报告的结论: ✅ / ❌
- [ ] 如 ❌,说明沿用依据: <理由>
```

**预防 SOP**:
1. 进化报告首节固定写「路径自检 + 多路径扫描结果」
2. 如果本期引用上份的诊断,必须显式说明「沿用」+ 标注「未经新实测」
3. 每周一次「进化报告自洽审计」cron,随机抽 3 份报告实测验证

**关联**: `references/***SECRET***.md` — 路径层归属误判的具体案例

---

## 关键脚本

- `~/.hermes/scripts/minimax_health_check.sh` — 端点 5 分钟 ping
- `~/.hermes/scripts/l1_compact_one.sh` + `l1_compact_all.sh` — L1 压缩
- `~/.hermes/scripts/session_archive_one.sh` + `session_archive_all.sh` — session 归档
- `~/hermes/team/memory/runbooks/refresh_all_l1.py` — 8 profile L1 重写

## 6/30 关键事件时间线

| 时间 | 事件 |
|---|---|
| 15:38 | 诊断 402 根因 (按量账户耗尽) |
| 15:41 | 备份 7 个 .env (`.env.bak.20260630_154158`) |
| 15:48 | 同步 default 订阅 key 到 6 同事 |
| 15:48 | 6 同事 LLM 端点 200 OK |
| 15:50 | 注册 health-check cron `3d1cf3a9627c` |
| 15:54 | 拉起 5 同事 launchd (legacy load) |
| 16:00+ | 黑豆/阿福飞书私聊路由失效 (教训) |
| 16:10 | 华哥私聊激活黑豆/阿福 |
| 16:15-16:30 | 团队总档 24 文件重整 |
| 16:20 | 8 profile L1 全面重写 (refresh_all_l1.py) |
| 16:20 | 注册 L1-compact cron `f392cbc559b4` |
| 16:24 | 24550 sessions 归档 (96% 空间节省) |
| 16:25 | 注册 session-archive cron `e330c9cdaa05` |
| 16:30+ | 降本增效: zhe 调研复盘 + prompt caching 端点实测 + cron dedup 数学 |

## 玉芬操作边界（华哥 2026-08-08 更新：全权管理）

**华哥 2026-08-08 明确**：「公司所有同事的任务都归你安排。我只向你布置任务，你对任务负责。有进展可随时向我汇报。」

**核心变更**：
- **quant (宽博士) 和 zhenglishi (学习助手) 不再"华哥直派"** — 全部 7 同事（毛豆/老莫/小宝/黑豆/阿福/宽博士/学习助手）统归玉芬管理
- 华哥只向玉芬布置任务，不直接派发给其他同事
- 玉芬对所有同事的任务进度和产出负责
- 原`玉芬操作边界`§红线外中的「quant/zhe 是华哥直派」和「给华哥转派 zhe/quant 的任务」等条目**已废止**

**⚠️ 2026-08-29 更新：宽博士退出玉芬管辖** — 华哥定调宽博士(quant)**完全独立**：唯一直属华哥、不请示玉芬、不参与公司其它任务，定位=量化专家/华哥的专属量化智能助手。玉芬不再给宽博士派单/审批/调度；quant AGENTS.md 已升 v7（备份 `AGENTS.md.bak-20260829_115526`），共享 Mnemosyne 已登记此边界（全公司 agent 可查，勿再给宽博士派非量化任务）。zhenglishi 及其余 6 同事仍归玉芬管理。

**红线内（自主决策，无需请示）**：
- 全部 7 同事的任务分配/调度/跟踪 + cron 心跳与自我进化管理
- （8/29 起为 6 同事：毛豆/老莫/小宝/黑豆/阿福/学习助手，宽博士除外）
- 8 profile .env key 同步 / launchd 拉起重启 / cron 增删改 / L1 重写 / session 归档
- 渔芯社区工作流管理（硬件开发 + 新360行行业工作流 + 07软件项目开发）
- 渔芯社区 cron `3328b7053970`（每2h软硬件工作流进化）

**红线外（请示华哥）**：改 minimax 订阅 key 池 / 删重要数据 / 改 hermes-agent 源码

**陷阱**：华哥说"你做决定"→ 直接做决策+立刻执行，不要甩 A/B/C 选项。例外：红线外或不可逆操作仍需请示。

---

## 学习助手双重保障机制（2026-08-17 华哥新增）

学习助手（zhenglishi，原"整理师"，业务名已统一为「学习助手」）是玉芬(default)的**双重保障/备份修复人**：玉芬自身故障（模型 401/402、provider 配错、gateway 崩溃、cron 失效）且无法自修时，学习助手有权检查/诊断/修复玉芬的 config.yaml、.env、gateway、cron。

- 修玉芬必须遵守 `hermes-config-safe-edit` 技能五条铁律（先备份→单字段→改完实测→查守护进程）
- 边界：只修玉芬(default)，**绝不动其他同事**
- 每天 9:00 cron `bc085cd0f1e0`（profile=zhenglishi）发玉芬状态巡检到华哥飞书
- profile 技术名 zhenglishi 不变，改的是业务称呼（默认总表里已用「学习助手」）

## model_rotation_daemon 已停用（2026-08-17）

`~/Library/LaunchAgents/com.yuxin.model-rotation.plist`（跑 `model_rotation_daemon.sh`，每 5 分钟健康检查 + 自动 switch provider + kill/重启 default gateway）是**玉芬模型反复"被改死"的真凶**——检测到 provider"不健康"就自动改玉芬 config.yaml 并重启 gateway，与"玉芬固定 minimax"冲突。

- **已停用**（launchctl unload + bootout），**勿重启**
- 玉芬的 model/provider 现在只能手动改，不再有自动守护进程覆盖
- 改玉芬配置前必查此守护进程是否被重新拉起（见 `hermes-config-safe-edit` 技能）

### 🔴 回归：停用后仍会自动复活（2026-08-25 实测）

「已停用」不是永久状态——plist 文件仍在 `~/Library/LaunchAgents/com.yuxin.model-rotation.plist`，**开机/登录会重新 load**。08-25 玉芬每日扫描发现该 daemon 已复活（PID 运行 2 天+），每 5 分钟轮询并正把 default provider 定在 `deepseek-direct/deepseek-v4-pro`。

**每次扫描 / 改玉芬配置前必查（3 步）**：
```bash
launchctl list | grep model-rotation            # 有 PID = 又活了
tail -5 ~/.hermes/logs/model_rotation_out.log    # "📊 当前: provider=... model=..." 每 5 分钟一条 = 主动轮询中
grep -A2 "^model:" ~/.hermes/config.yaml | head -3   # 看它把玉芬定在哪个 provider（对比"应固定 minimax"）
```
判定：daemon 复活 + 把玉芬 provider 改离 minimax → 属异常（除非华哥已明确改 provider），列入扫描报告「关键异常/需华哥决策」，**不要擅自 unload**（可能是华哥有意重启）。

## 已吸收：Agent 网络分类 + 项目路径/任务库真相（2026-09-02 curator 合并）
- **agent-network-classification** → `references/agent-network-classification.md` — 渔芯两类 Agent 的网络环境判断（同事 Agent 能上网 vs 嵌入新系统 Agent 禁网）；决定该 agent 能否调外网 API，避免凭印象下结论。
- **maodou-product-paths-fix** → `references/project-paths-taskdb-truth/` — 渔芯项目路径与任务库的 canonical 事实（LookForge 路径、tasks.db / kanban.db、git diff 监测基线）；任何 cron 心跳引用项目路径前先核对此文件。
触发：判断某 agent 能否上网、心跳检查引用项目路径、查询任务库/看板状态。


## 公司资产 5 维盘点（原 company-asset-audit,2026-10-01 收纳）

华哥说「全面盘点」/「重新梳理资产」/「整体架构优化」/「看公司全景」时的标准化 5 维扫描（大模型 API key / agent 团队 / RKR 知识库 / 公司运营 / 产品研发）+ 输出模板 + 巡检/dashboard 脚本:`references/asset-audit/company-asset-audit.md`(scripts/templates 同目录)。控制中心 Dashboard（原 yuxin-control-center）架构、启动/停止命令、已知问题与维护清单:`references/asset-audit/control-center-dashboard.md`(Streamlit 3 模块 / 5 JSON 数据源;改动必须走 Claude Code / Codex,见 yuxin-code-iron-law)。

## 上下文与记忆管理（原 context-memory-management,2026-10-01 收纳）

L1/L2/L3/Mnemosyne 分层架构、>55% 触发自动压缩（不审批只报告）、压缩 cron 运维、L1→Mnemosyne 迁移、多 profile 批量迁移与跨机器 Sync(旺财):`references/context-memory-management.md`(分册 `references/***SECRET***.md`、`references/***SECRET***.md`)。

## 10-agent 集中管理方法论（原 yuxin-team-management,2026-10-09 curator 收纳）

> 📂 整档位置：`references/yuxin-team-management/`（SKILL.md + references/）。

渔芯 10-agent 集中管理方法论（2026-08-01 整理，2026-09-04 心博士入职扩至 10 人）。适用：华哥需要「重新整理同事 agent 系统文件」「建集中目录树管理所有同事」「新增一位专家型同事」或类似「multi-agent 系统的 profiles 散落管理问题」。触发词：重新整理 / 集中管理 / 统一视图 / 同事 agent 整理 / 团队管理视图 / 新增同事 / 复刻宽博士模式建专家；华哥发批量批复指令（"需拍板项目全选'是'"等）。与本 skill 主线的关系：主线讲「架构设计 + 协作机制」（怎么搭），本子库讲「集中目录树 + 新增同事的落地操作」（怎么整理/怎么扩编）——同一个 class 的两个操作层。
