---
name: yu-control-center
description: 渔芯控制中心(Control Center) — Streamlit 仪表盘,聚合 9 profile 状态、cron 任务、API key、铁律、产品/社区项目元数据,跑在 http://127.0.0.1:8765/。华哥 2026-08-03 启动,定位"公司运行状态控制面板"。修改必须经 Claude Code/Codex(继承 yuxin-code-iron-law)。已知架构陷阱:gateway_up 检查的是 launchd plist(不是 HTTP 端口)、profile.json skills_count 字段是历史虚高(实际数应从 ~/.hermes/profiles/{profile}/skills/ 目录数)、侧边栏只在有 pages/ 目录时出现(已禁用)。
version: 1.0
created: 2026-08-03
priority: high
---

# ⚡ 渔芯控制中心 YuXin Control Center

> **定位**:公司运行状态控制面板(Streamlit)。3 大模块 + 5 tab + 6 数据源 + 1 工具脚本。
> **访问**:http://127.0.0.1:8765/ (本地,headless mode)
> **华哥 2026-08-03 拍板**:扩展/修改必须经 Claude Code 或 Codex(继承 `yuxin-code-iron-law` v1.3)。

---

## 1. 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    YuXin Control Center                      │
├─────────────────────────────────────────────────────────────┤
│  Streamlit App (538 行,3 模块)                                │
│  ├─ 🤖 模块 1: 智能体团队 (5 tabs)                            │
│  │   ├─ 智能体清单 (中英表头 + 9 profile)                     │
│  │   ├─ Cron 任务清单 (53 个汇总)                             │
│  │   ├─ 大模型 API Key (6 providers + 路由表)                │
│  │   ├─ 工具仓库 (Claude Code + Codex 分开展示)              │
│  │   └─ 🛡️ 铁律 (5 条铁律完整版)                              │
│  ├─ 🐟 模块 2: 渔芯产品 (7 个产品全维度)                      │
│  └─ 🌐 模块 3: 渔芯社区 (11 个项目全维度)                    │
├─────────────────────────────────────────────────────────────┤
│  数据层 (6 个 JSON,全部在 ~/.hermes/state/)                   │
│  ├─ agent_status.json  (9 profile + 53 cron + 工具)         │
│  ├─ api_keys.json       (6 LLM providers + routing)         │
│  ├─ products.json      (7 渔芯产品)                          │
│  ├─ community.json     (11 社区项目)                         │
│  ├─ tool_logs.json      (Claude Code + Codex 详细)           │
│  └─ iron_law.json      (5 条铁律完整版)                      │
├─────────────────────────────────────────────────────────────┤
│  采集层 (1 个 Python 脚本)                                    │
│  └─ tool_repo_manager.py (533 行,Claude Code 重写版)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 文件清单(华哥 2026-08-03 已确认)

| 路径 | 行数 | 角色 | 修改门槛 |
|---|---|---|---|
| `/Users/hua/hermes/dashboard/app.py` | 538 | Streamlit 主入口,3 模块 | 🔴 必须 Claude Code/Codex |
| `/Users/hua/hermes/dashboard/assets/styles.css` | 61 | 科技未来风 CSS | 🔴 必须 Claude Code/Codex |
| `/Users/hua/hermes/dashboard/README.md` | 801B | 启动说明 | 🟢 可自写 |
| `/Users/hua/.hermes/state/*.json` | 6 个 | 数据源 | 🟢 玉芬可写(纯数据,铁律豁免) |
| `/Users/hua/.hermes/tool-repo/tool_repo_manager.py` | 533 | 工具版本采集 | 🔴 必须 Claude Code/Codex |
| `/Users/hua/.hermes/scripts/collect_status.py` | 110+ | 状态采集 cron | 🔴 必须 Claude Code/Codex |
| `/tmp/app_v1_yuxin_354lines.py` | 354 | 玉芬原版备份 | 🟢 可删 |

**启动命令**:
```bash
/Users/hua/Library/Python/3.9/bin/streamlit run /Users/hua/hermes/dashboard/app.py --server.port 8765 --server.headless true --server.address 127.0.0.1
```

---

## 3. 如何修改控制中心(华哥亲自用 Claude Code 优化的工作流)

### 3.1 选择工具(继承 yuxin-code-iron-law)

| 改动类型 | 首选工具 | 命令模板 |
|---|---|---|
| Streamlit 业务代码 | **Claude Code** | `claude -p --allowedTools "Read,Edit,Write,Glob,Grep" -- "..."` |
| CSS 样式 | **Claude Code** | 同上 |
| 大型 JSON 数据整合 | **Codex CLI** | `cat /tmp/p.txt \| codex exec --skip-git-repo-check -s danger-full-access` |
| 元数据 JSON 修改 | **玉芬自写**(铁律豁免) | 直接 `write_file` |
| README | **玉芬自写** | 直接 `write_file` |

**完整工作模式** 见 `yuxin-code-iron-law` v1.3 + `references/claude-p-allowedTools-working-pattern.md`(5/5 任务成功 reproduction)

### 3.2 标准工作流(玉芬/华哥都可执行)

```
1. 拆分任务(每个 prompt 改 1 个文件,不要 1 个大 prompt 改 5+)
2. 写聚焦 prompt(明确 Read 哪个、Edit/Write 哪个、严格限制)
3. 跑 claude -p --allowedTools
4. 独立验证(md5sum / wc -l / python3 ast / grep -c)
5. 失败就重发 prompt(改 1 个字段)
```

### 3.3 5 个 prompt 模板参考

具体 5 个改写任务的完整 prompt + 验证命令,见 `references/claude-p-allowedTools-working-pattern.md`(已写在那里,5/5 成功 reproduction)。

---

## 4. 已知架构陷阱(2026-08-03 测试发现)

### 陷阱 1:`gateway_up` 字段含义 ≠ Gateway 端口可达

**坑**:`collect_status.py` 第 26-31 行检查的是 **launchd 守护进程** `ai.hermes.gateway-{profile}.plist` 是否在 `launchctl list` 列表中,**不是 HTTP 端口 18888/15721 是否通**。

**症状**:Dashboard 显示 7 个 profile `gateway_down`,但 `curl 127.0.0.1:15721` / `curl 127.0.0.1:18888` 都 200。

**原因**:只有 2 个 profile(quant + zhenglishi)有独立 launchd plist,其他 7 个共享主 Gateway `ai.hermes.gateway.plist`(PID 878)。

**修复选项**:
- A. 接受现状(共享主 Gateway,Dashboard 显示只是 plist 状态)
- B. 为每个 profile 单独建 plist(`hermes gateway run --profile X --replace`)
- C. 改 `collect_status.py` 第 26-31 行,改用 HTTP 端口探测(用 requests / urllib)
- D. 在 Dashboard "工具仓库" tab 显示实际 HTTP 端口状态,而不是 plist 状态

### 陷阱 2:`profile.json` 的 `skills_count` 字段虚高

**坑**:profile.json 里的 `skills_count` 是 2026-08-03 玉芬**手填的估算值**,与实际 `~/.hermes/profiles/{profile}/skills/*.md` 文件数不匹配。

**实测偏差**(8/3 21:00):

| profile | 实际 skills 数 | profile.json skills_count | 偏差 |
|---|---|---|---|
| maodou | 2 | 45 | -43 ⚠️ |
| afu | 1 | 66 | -65 ⚠️ |
| xiaobao | 1 | 42 | -41 ⚠️ |
| heidou | 1 | 34 | -33 ⚠️ |
| laomo | 1 | 32 | -31 ⚠️ |
| zhenglishi | 1 | 3 | -2 |
| default | 0 | 2 | -2 |
| quant | 0 | 2 | -2 |
| community | 0 | 0 | 0 ✅ |

**根因**:profile 自身的 skills/ 目录是私有 skill,大部分 skill 在 `~/.hermes/skills/` 公共池里。Dashboard 显示的是 profile 私有数,但元数据填的是"估算总技能数"。

**修复**:
- A. 元数据改填"实际私有数"(`ls profiles/{p}/skills/*.md | wc -l`)
- B. Dashboard 读取 `~/.hermes/skills/` 公共池(更准确,需遍历所有 skill 的 frontmatter 看属于哪个 profile)
- C. 加新字段 `public_skills_count`(只显示公共池数)

### 陷阱 3:Streamlit 多页应用 = 侧边栏

**坑**:Streamlit 一旦有 `pages/` 目录,**自动启用左侧导航栏**显示所有 .py 文件作为子页面。华哥 8/3 明确:"左侧导航条有一个app,一个铁律。取消左侧导航栏"。

**修复**:删除 `pages/` 目录即可关闭多页应用 + 侧边栏。

**注**:本项目已删 pages/(8/3 21:50),现在只有"App"主入口,所有内容在 `app.py` 主程序内。

### 陷阱 4:Streamlit 1.x → 2.x deprecation

**坑**:`use_container_width=True` 在 Streamlit 2.x 弃用,2025-12-31 后会硬性失败。

**修复**:`width='stretch'`(8/3 Claude Code 任务 1 已修完 4 处)

**其他弃用**:`general.email` config(早期 Streamlit 1.x 移除),启动时打 warning 但不影响运行。

### 陷阱 5:`@st.cache_data(ttl=300)` 5 分钟缓存

**坑**:数据加载函数默认 5 分钟缓存,改 JSON 后 dashboard 不会立即刷新。

**修复**:
- 等 5 分钟自动刷新
- 或重启 streamlit 进程
- 或改 `ttl` 为更短(临时调试用)

---

## 5. 升级路线图(华哥已拍板,2026-08-03)

| 优先级 | 改动 | 推荐工具 | 备注 |
|---|---|---|---|
| P1 | gateway_up 改 HTTP 端口探测 | Claude Code | 改 collect_status.py 第 26-31 行 |
| P1 | profile.json skills_count 自动采集 | Claude Code | 加 scripts/collect_profile_skills.py |
| P1 | community profile 加默认任务 | 玉芬 | 配 1-2 个 cron(品牌/CRM 监控) |
| P2 | 3 个 paused cron 长期未恢复(6-26/7-3/7-5) | 玉芬 | 审计:是有意暂停还是事故? |
| P2 | Streamlit 弃用 config 清理 | Claude Code | 改 streamlit config.toml,删 general.email |
| P3 | 加新模块 4:Token 用量分析 | Claude Code | 拉 tokens_report.py 输出 |
| P3 | 加新模块 5:Skills 健康度 | Claude Code | 扫 421 skills 找孤立/重复 |

---

## 6. 4 个飞书 channel(沟通矩阵)

| Channel ID | 名称 | 谁投到这里 |
|---|---|---|
| `oc_2db3b5373825567c3681d1ca580e0143` | 华哥 home | 22 个 cron(含玉芬 default) |
| `oc_568a685a2083722cc7fe507ace752545` | 大群 | 2 个 cron |
| `oc_23bd798272a60cbfc15c82b954823730` | 寻元 | 1 个 cron |
| `feishu` (无 ID) | 通用 | 3 个 cron |

**Dashboard 状态** ≠ 飞书连通性。飞书 API 走 `https://open.feishu.cn/open-apis/`,与 streamlit/Gateway 解耦。

---

## 7. 相关文件指引

- **代码铁律与执行模式**:`yuxin-code-iron-law` v1.3(含 references/)
- **玉芬编码工作流**:`yuxin-coding-workflow`
- **多 Agent 架构**:`multi-agent-team-architecture` / `yuxin-team-management`
- **Dashboard 采集脚本**:`~/.hermes/scripts/collect_status.py`(110+ 行)
- **Dashboard 数据采集背景**:`~/.hermes/state/agent_status.json`(8/3 由玉芬自写 + tech_debt 标注 + 已由 Claude Code 评估保留)
- **🆕 数据源 Schema 总览**:`references/data-schemas.md` — 6 个 JSON 文件的字段定义、添加/修改流程、字段约定

---

## 8. 监控 checklist(华哥/玉芬日常)

```
□ Dashboard HTTP 200 (curl http://127.0.0.1:8765/_stcore/health)
□ 9 profile.json 存在 + skills/memory/cron 字段非空
□ 53 cron 至少 44 enabled
□ 4 个飞书 channel 至少 home (oc_2db3b5373825567c3681d1ca580e0143) 有心跳
□ 工具版本:Claude Code + Codex + Hermes 都有数据
□ iron_law.json 含 5 条铁律(完整版)
```

---

## 9. 版本历史

| 版本 | 日期 | 改动 |
|---|---|---|
| v1.0 | 2026-08-03 | 初版 — 整合 8/3 测试发现的 5 大架构陷阱 + 升级路线图 |
