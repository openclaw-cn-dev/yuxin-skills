---
name: ***SECRET***
description: 渔芯 Dashboard v2.0 架构与代码铁律 v1 自动驱动模式 — 华哥 8/3 拍板。物理位置、结构、3 模块/5 tab 顺序、代码铁律 v1、Claude Code/Codex 自动驱动模式、Gemini 工具调用禁忌、Gateway 架构现状、Skills 元数据虚高问题。
version: 1.0
created: 2026-08-03
---

# 渔芯 Dashboard v2.0 + 代码铁律 v1 · 知识手册

> **触发场景**: 任何涉及 Dashboard 修改、代码开发、Claude Code/Codex 调用的工作
> **优先级**: high (Dashboard 是华哥自己优化的高频入口,代码铁律是公司级铁律)

---

## 1. Dashboard v2.0 物理位置(2026-08-03 华哥拍板)

| 文件 | 路径 | 行数 | 备注 |
|---|---|---|---|
| 主入口 | `/Users/hua/hermes/dashboard/app.py` | 538 | Streamlit 3 模块主程序 |
| CSS | `/Users/hua/hermes/dashboard/assets/styles.css` | 61 | 科技未来风(深色 + 网格 + 霓虹) |
| 数据源 | `/Users/hua/.hermes/state/*.json` | 6 个 | agent_status / api_keys / products / community / tool_logs / iron_law |
| 工具脚本 | `/Users/hua/.hermes/tool-repo/tool_repo_manager.py` | 533 | Claude Code/Codex 版本采集 |
| 玉芬原版备份 | `/tmp/app_v1_yuxin_354lines.py` | 354 | 不需要可删 |

**启动命令**:`/Users/hua/Library/Python/3.9/bin/streamlit run /Users/hua/hermes/dashboard/app.py --server.port 8765 --server.headless true --server.address 127.0.0.1`

**华哥要自己调 Claude Code 优化 Dashboard** — 玉芬只负责测试。

---

## 2. Dashboard 3 模块 / 5 tab 顺序(华哥拍板)

**模块 1 · 智能体团队**(5 tab,顺序固定):
1. 📋 智能体清单 Agent Roster(9 个 agent + 中文名 + 中英表头)
2. ⏰ Cron 任务清单 Cron Jobs
3. 🧠 大模型 API Key(6 个 provider + 路由策略 + 预算)
4. 🔧 工具仓库 Tool Repo(Claude Code + Codex 各自 Skills/Plugins/版本/日志)
5. 🛡️ 铁律(放第 5 位,工具仓库后面)

**模块 2 · 渔芯产品**(7 个产品,多维表格)
**模块 3 · 渔芯社区**(11 个项目,多维表格)

---

## 3. 关键约束

- ❌ **无 pages 目录** — 华哥 8/3 明确"取消左侧导航栏",Streamlit 多页路由被禁
- ✅ 铁律 v2.0 数据在 `iron_law.json`(243 行,5 条铁律),模块 1 第 5 tab 渲染
- ✅ 启动方式 streamlit 单页,不是 multi-page app
- ✅ 数据 30 分钟自动 refresh(`collect_status.py`)

---

## 4. 代码铁律 v1(2026-08-03 华哥铁律,优先级最高)

### 适用范围
任何代码/脚本/工具开发:Python / JS / TS / Shell / CAD macro / Streamlit / Vue / React / .py .js .ts .sh

### 默认调用链(强制)
1️⃣ **Claude Code**:`claude -p --allowedTools "Read,Edit,Write,Glob,Grep" "<prompt>"`
2️⃣ **Codex CLI**:`codex exec --skip-git-repo-check -s danger-full-access "<prompt>"`
3️⃣ **自写 + 标注**:仅当 Claude Code + Codex 都明确失败,**文件首行加 `# TODO(tech-debt): 改由 Claude Code/Codex 重写`** + 飞书通知华哥登记技术债

### 不适用场景(可自写,不算违规)
✅ 文档/Markdown/方案/报告
✅ AGENTS.md / 记忆 / skill 文本内容
✅ 纯配置文件(JSON/YAML/TOML,只写不调逻辑)
✅ 一行命令 / 临时修复 / 调试 print
✅ 数据迁移 / 纯 shell 批处理
✅ 写元数据 JSON(Dashboard 数据源,纯数据)
✅ Streamlit 纯布局/渲染代码(无业务逻辑)

### 违反处置
- 1 次:立即停手 + 改由 Claude Code/Codex 重写 + 飞书报告
- 2 次:写复盘 + 标注技术债 + 玉芬停手等待华哥审批
- 3 次:对应 profile 自动降级(暂停 self-evolution 24h),等华哥手动重启

---

## 5. Claude Code/Codex 自动驱动模式(玉芬核心工作流)

### Claude Code(3-5 分钟,可写文件)
```bash
claude -p --allowedTools "Read,Edit,Write,Glob,Grep" "<prompt>"
```
- **`--allowedTools` 白名单让 Edit/Write 自动执行**,不需要人工批准
- 只用 `-p` 时 Edit 工具需要"写入权限批准"被卡
- 第一次 `claude -p "..."` 启动对话,后续 `claude -p -c` 继续

### Codex CLI(2-3 分钟,可写文件)
```bash
codex exec --skip-git-repo-check -s danger-full-access "<prompt>"
```
- **`-s danger-full-access` 必须** — 无 -s 时 read-only sandbox 自动检测会失败,任务跑 4-5 分钟后报错"沙箱完全阻止写入"
- **`--skip-git-repo-check` 必须** — 否则报"Not inside a trusted directory"
- 不支持 `--allowedTools` 参数

### Prompt 写文件禁忌
- ❌ 避免用反引号或特殊字符(被 bash 当命令执行,timeout 300s)
- ✅ 长 prompt 写到 `/tmp/prompt.txt`,再 `cat /tmp/prompt.txt | codex exec ...`
- ✅ 多行 prompt 用 heredoc(`cat > /tmp/prompt.txt << 'EOF' ... EOF`)

---

## 6. Gateway 架构现状(2026-08-03 测试发现)

只有 2 个同事有独立 launchd plist:
- `ai.hermes.gateway.plist` (PID 878) — 主 Gateway
- `com.yuxin.llm-gateway.plist` (PID 865) — yuxin LLM Gateway
- `ai.hermes.gateway-quant.plist` (PID 46479) ✅
- `ai.hermes.gateway-zhenglishi.plist` (PID 46398) ✅

**7 个 profile 没独立 plist**(default/maodou/xiaobao/afu/heidou/laomo/community),共享主 gateway。Dashboard `gateway_up` 字段是检查 plist,所以 7 个显示 down。

**架构选择**:
- A. 接受现状(共享主 gateway)
- B. 为每个同事建独立 plist(`hermes gateway run --profile X --replace`)

---

## 7. Skills 元数据虚高问题

`profile.json` 的 `skills_count` 是 8/3 玉芬自报,不是真实采集。实际 `~/.hermes/profiles/<x>/skills/` 私有只有 0-2 个,公共池在 `~/.hermes/skills/`。

| profile | 实际 | 元数据 | 偏差 |
|---|---|---|---|
| maodou | 2 | 45 | -43 ⚠️ |
| afu | 1 | 66 | -65 ⚠️ |
| xiaobao | 1 | 42 | -41 ⚠️ |
| heidou | 1 | 34 | -33 ⚠️ |
| laomo | 1 | 32 | -31 ⚠️ |

**修复方法**:用 `tool_repo_manager.py` 同样模式采集 `~/.hermes/profiles/<x>/skills/` 真实数量,写回 `profile.json`。

---

## 8. 同事心跳 cron 状态(2026-08-03 19:00 测试)

- 8 同事 4h 自我进化 cron:7 ok + 1 error(黑豆 8/3 16:35 HTTP 529 过载,下次自动重试 ok)
- 6 同事 1h 心跳 cron:全部 ok
- 玉芬 default 8 个 cron:7 ok + 1 error(玉芬-自我提升模式 8/2 22:00)
- 全局:53 个 cron,46 ok / 6 err / 9 paused

**4 个飞书 channel**:
- `***SECRET***` — 华哥 home(22 个 cron 投这里)
- `***SECRET***` — 大群
- `***SECRET***` — 寻元

---

## 9. 完整铁律 v2.0(`iron_law.json` 243 行)

5 条铁律整合:

| ID | 类别 | 来源 | 优先级 |
|---|---|---|---|
| KNOWLEDGE-001 | 🧠 项目知识库 | Claude Code 全局(7-23) | high |
| SECURITY-001 | 🔒 数据安全 | Claude Code 全局(7-21) | high |
| EXEC-001 | 🛡️ Codex 命令黑名单(9 大类 A-I) | Codex AGENTS.md | high |
| CODE-001 | 💻 渔芯代码开发铁律 v1 | 华哥(8-3) | **highest** |
| FORBIDDEN-001 | 🚫 8 条严禁 | 华哥 v1 | high |

数据源:`~/.claude/CLAUDE.md` + `~/.codex/AGENTS.md` + 9 份 profile/AGENTS.md 铁律章节。

---

## 版本历史

| 版本 | 日期 | 改动 |
|---|---|---|
| v1.0 | 2026-08-03 | 初版 — Dashboard v2.0 + 代码铁律 v1 + 同事管理现状 |
