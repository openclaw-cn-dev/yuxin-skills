---
name: hermes-agent
description: "Configure, extend, or contribute to Hermes Agent."
version: 2.0.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

## Session learning: profile-specific skill visibility

When a cron task reports a skill as missing, distinguish the registry result from filesystem reality. A same-named `SKILL.md` may exist in the target profile while the active skill registry exposes a different profile or no entry. Record this as a registry/index gap; do not duplicate the skill or silently substitute another role's workflow. For policy research, classify evidence as full official text verified, official page located but text unavailable, or search signal pending verification; only the first category supports definitive compliance conclusions.

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively** — setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Integration: World2Agent Sensor Bridge

`@world2agent/hermes-sensor-bridge` connects World2Agent sensors (感知层/事件触发) to Hermes Agent, giving Hermes "ears" for external events (Hacker News, GitHub, X, market data, etc.).

```bash
npm install -g @world2agent/hermes-sensor-bridge
hermes skills install machinepulse-ai/world2agent-plugins/hermes-sensor-bridge/skills/world2agent-manage
```

Then in chat: `/world2agent-manage add @world2agent/sensor-hackernews`

See `references/world2agent-hermes-bridge.md` for full architecture, delivery modes, and troubleshooting.

## Smithery MCP Market Integration

[Smithery.ai](https://smithery.ai) 是MCP服务器市场，提供715+认证服务器。Hermes可直连Smithery MCP服务器：

```bash
# 安装Smithery CLI
npm install -g @smithery/cli

# 搜索MCP服务器
smithery search gmail

# 查看已安装服务器
smithery list
```

### 热门Smithery MCP服务器（按安装量排序）

| 服务器 | 安装量 | 分类 | 用途 |
|--------|--------|------|------|
| Google Sheets | 42.6k | 办公 | 表格数据处理 |
| Gmail | 29.9k | 办公 | 邮件管理 |
| Exa Search | 29.2k | 搜索 | 网络深度搜索 |
| Sentry | 20.2k | 开发 | 错误追踪 |
| Slack | 18.4k | 办公 | 团队消息 |
| GitHub | 15.8k | 开发 | PR/Issue管理 |
| Supabase | 12.3k | 开发 | 数据库操作 |
| Memory | 7.9k | 工具 | 持久记忆 |

### 在Hermes中配置Smithery服务器

```yaml
# ~/.hermes/config.yaml
mcp_servers:
  gmail:
    command: "npx"
    args: ["-y", "@smithery/protocol-server-gmail"]
  github:
    command: "npx"
    args: ["-y", "@smithery/protocol-server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxxx"
```

## agency-agents 专家角色库（97.7k ⭐）

[agency-agents](https://github.com/msitarzewski/agency-agents) 是211个可复用AI专家角色库，每个都有完整的人设、专业流程和交付物。

### 安装

```bash
cd ~/skills/agency-agents-zh

# 自动检测并一键安装
./scripts/install.sh

# 指定工具安装
./scripts/install.sh --tool hermes    # Hermes专用
./scripts/install.sh --tool openclaw
./scripts/install.sh --tool claude-code
```

### 支持的AI编程工具

✅ Claude Code / ✅ OpenClaw ⭐ / Cursor / GitHub Copilot / Windsurf / **Kiro / Trae / OpenCode / Aider / Gemini CLI / Qwen Code / Codex CLI / DeerFlow (字节) / WorkBuddy (腾讯) / Antigravity / Hermes Agent**

### 覆盖部门（18个）

- 🛠️ 工程部 — 前端/后端/AI/DevOps/安全/嵌入式/FPGA/飞书集成等 30+
- 🎨 设计部 — UI/UX/品牌/图像提示词
- 📢 营销部 — 小红书/抖音/微信/B站/快手/知乎/公众号
- 💰 付费媒体部 — 广告审计/PPC/程序化购买
- 💼 销售部 — 大客户/赢单策略/Discovery/售前
- 🏦 金融部 — 财务预测/发票管理/风控
- 👔 人力资源部 — 招聘/绩效管理
- ⚖️ 法务部 — 合同审查/合规制度
- 🚚 供应链部 — 库存预测/供应商评估
- 📦 产品部 / 项目管理 / 游戏开发 / 学术 / 测试 / 战略 / 支持

### 中国市场原创（46个）

平台运营：小红书、抖音、微信视频号、B站、快手、微博、知乎、公众号  
电商：淘宝/拼多多/京东、直播电商、跨境电商  
集成：飞书、钉钉、微信小程序  
垂直：政务ToG、医疗合规、供应链  
金融：金税发票、支付风控

## AI Coding Skills 生态

### andrej-karpathy-skills（128k ⭐）

源自Karpathy的AI编程三大原则：
1. **Think Before Coding** — 错误假设、隐藏困惑时显式陈述
2. **Simplicity First** — 最小代码，200行能解决就不用1000行
3. **Surgical Changes** — 只改必要代码，不"顺便"改进
4. **Goal-Driven Execution** — 先写测试定义成功标准

```bash
# Claude Code插件市场
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin install andrej-karpathy-skills@karpathy-skills
```

### addyosmani/agent-skills（40.8k ⭐）

Google工程师推出的生产级工程技能系统，完整开发生命周期覆盖：

```
DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP
 /spec    /plan    /build     /test    /review   /ship
```

```bash
# Claude Code插件市场
/plugin marketplace add addyosmani/agent-skills
```

### 两者互补

| 维度 | Karpathy Skills | addyosmani/agent-skills |
|------|----------------|------------------------|
| 核心理念 | 行为准则（如何思考） | 工程流程（如何执行） |
| 粒度 | 全局准则（4条） | 细粒度技能模块 |
| 覆盖范围 | 编码行为 | 完整开发生命周期 |

**渔芯实践**：叠加使用——Karpathy准则作为底层行为约束，agent-skills作为上层执行框架。

## ARIS 自动研究框架（8.3k ⭐）

[***SECRET***](https://github.com/wanshuiyin/***SECRET***) — 对抗性双模型研究工作流。

### 核心概念：跨模型对抗性评审

- **Executor**：Claude Code 快速执行
- **Reviewer**：Codex (GPT-5.4 xhigh) 慢速但严谨批判

这解决了单模型自审的**局部最小值问题**——同一模型评审自己的输出会产生盲点。

### 五大工作流

| 工作流 | 命令 | 说明 |
|--------|------|------|
| Pipeline | `/research-pipeline "<方向>"` | 一句话启动完整研究流程 |
| 靶向研究 | `/research-pipeline "改进X"` | 读论文→找弱点→克隆→生成→运行→写论文 |
| 反驳 | `/rebuttal "论文+评审"` | 自动生成rebuttal |
| 论文写作 | `/paper-writing` | 从想法到论文 |
| 会议演讲 | `/paper-slides` / `/paper-poster` | 生成PPT/Poster |

### 自我优化机制

ARIS的`Meta-Optimize`功能可分析日志→提出SKILL.md改进，实现ARIS自我优化。

### 四大审计层

```
experiment-audit → result-to-claim → paper-claim-audit → citation-audit
```

## RKR 知识库平台安全加固（v3.2）

RKR（调研与知识库平台）与 Hermes Agent 深度集成，以下安全修复需要了解：

### 1. 文件类型白名单
- 外部上传必须验证文件类型，防止恶意文件
- 白名单：`.pdf`, `.docx`, `.md`, `.csv`, `.xlsx`, `.jpg`, `.png` 等
- 无效类型返回 415 错误

### 2. 项目权限验证
- 外部上传必须验证 `ProjectMember` 记录
- 返回 403 错误如果用户不是项目成员

### 3. Hermes Agent 工具权限隔离
- 所有搜索工具必须传递 `allowed_project_ids` 参数
- `search_knowledge_base`: 必需参数，验证项目访问权限
- `cross_project_search`: 过滤无权限项目
- `list_categories`: 验证项目权限

### 4. SQL 参数化查询
- `search_across_projects` 使用参数化查询
- `search_keywords` 添加 `allowed_project_ids` 参数
- 防止 SQL 注入攻击

### 5. 加密配置
- `ENCRYPTION_SALT` 从 config 读取，不硬编码
- PBKDF2 盐值可自定义

## 渔芯团队运营参考

- `references/multi-agent-team-setup.md` — **创建多Agent隔离团队的标准流程**（5个Profile + SOUL.md + MEMORY.md + 飞书配置 + 关键限制说明，含 2026-06-30 launchd bootstrap 坑 + 私聊路由激活坑 + 8-profile L1 架构）
- `references/***SECRET***.md` — **launchd load/bootstrap 5:I/O error 排查** + 飞书私聊路由激活 + awk $3 精确匹配 PID
- `references/cron-api-error-decoder.md` — **minimax 401/402/429 三种错误的精确区分**（含 sk-cp- 订阅 vs sk-api- 按量）+ 8 profile .env 批量同步 Python 模板
- `references/active-profile-mechanism.md` — terminal `hermes` 怎么用错 profile + 何时 LaunchAgents 也会跟着错
- `references/terminal-chinese-paths.md` — **terminal workdir 中文字符路径阻塞处理方案** + 端口冲突 fallback 策略
- `references/world2agent-hermes-bridge.md` — World2Agent 传感器接入 Hermes（事件驱动）

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill (ID can be a hub identifier OR a direct https://…/SKILL.md URL; pass --name to override when frontmatter has no name)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks. Open WebUI connects via the API Server adapter.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### Cron Jobs

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/resume [name]       Resume a named session
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/cron                Manage cron jobs (CLI)
/reload-mcp          Reload MCP servers
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/status              Session info (gateway)
/profile             Active profile info
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

### Updating Models / API Keys Across All Profiles

When a provider upgrades or replaces a model (e.g. `MiniMax-M2.7` → `MiniMax-M3`) or when an API key rotates / migrates (国内→国际版), **the model name + provider + base_url live in 4 separate places, AND the API key lives in `.env`** — a `hermes config set model X` loop alone will leave the others pointing at the old version, and they'll silently fire on the next context-compression / cron tick. Worse: if `.env` is missing the key, cron errors will be misleading (`Connection error` instead of "key not found"). Scan and patch all FIVE:

#### 1. Profile-level top `model:` (the obvious one)

```bash
for prof in afu heidou laomo maodou quant xiaobao zhenglishi; do
  hermes config set model MiniMax-M3 --profile $prof
done
hermes config set model MiniMax-M3   # root config
```

#### 2. Root `auxiliary.*` sub-task models (easy to miss)

The root `~/.hermes/config.yaml` has an `auxiliary:` block with **11 sub-tasks** (vision, web_extract, compression, skills_hub, approval, mcp, title_generation, triage_specifier, kanban_decomposer, profile_describer, curator, flush_memories). Each can carry its own `model:` field — when set explicitly (not `auto`), it overrides the top-level model. **Background compression especially** uses this — a stale M2.7 here means every long conversation silently compresses via the old model.

```bash
# Find which auxiliary sub-tasks still reference the old model
grep -nE "model:" ~/.hermes/config.yaml | head -40

# Patch the bad one(s) individually — `hermes config set` does one dot path at a time
hermes config set auxiliary.compression.model MiniMax-M3
```

Pitfall: `auxiliary.X.model` may use **lowercase provider-style names** like `minimax-2.7` instead of the canonical `MiniMax-M2.7`. Don't assume the format — read the line first, then write.

#### 3. Cron job `~/.hermes/cron/jobs.json` (most hidden)

Each cron job carries an optional `model` field that **overrides the profile default**. High-frequency tasks (every 30 min) can rack up thousands of calls against the old model before anyone notices. `hermes cron` has no model-edit subcommand — patch the JSON directly:

```bash
# Find hardcoded old model names in cron jobs
grep -nE '"model":\s*"[^"]*M2\.7|M2\.7-highspeed' ~/.hermes/cron/jobs.json

# Bulk patch (jq):
jq '(.jobs[]? // .[]) | select(.model? | test("M2\\.7")) | .model |= "MiniMax-M3"' \
   ~/.hermes/cron/jobs.json

# Or single-target with `patch` tool against the unique line
# Validate JSON after edit
python3 -c "import json; json.load(open('/Users/hua/.hermes/cron/jobs.json'))" && echo OK
```

Note: jobs.json root structure may be a bare array OR wrapped in `{"jobs": [...]}`. Adjust the jq path accordingly.

#### 4. LaunchAgent plists (rarely hardcode model, but worth a one-line check)

Plists normally pass `--profile <name>` only — the model comes from that profile's `config.yaml`. But if any plist has a `--model` flag in its `ProgramArguments`, patch it.

```bash
for f in ~/Library/LaunchAgents/*hermes* ~/Library/LaunchAgents/*Hermes*; do
  grep -l -- '--model\|MiniMax' "$f" 2>/dev/null
done
```

#### 5. `.env` API keys per profile (most often missed — causes silent cron failures)

Each profile has its OWN `~/.hermes/profiles/<name>/.env`. `config.yaml` only references provider/model/base_url — **the actual API key is loaded from this profile-scoped `.env`**. If a profile was created without cloning `.env`, cron jobs will fail with the misleading error `RuntimeError: Connection error.` even though the model + provider + base_url in `config.yaml` are perfectly correct.

Quick check across profiles:

```bash
for prof in afu heidou laomo maodou quant xiaobao zhenglishi; do
  echo "=== $prof ==="
  cat ~/.hermes/profiles/$prof/.env 2>/dev/null | grep -E "MINIMAX_CN_API_KEY|MINIMAX_API_KEY|OPENAI|ANTHROPIC|API_KEY" | sed 's/=.*/=<set>/'
done
```

Mirror from default when a profile is missing the key:

```bash
# Read from default (profile that works)
grep '^MINIMAX_CN_API_KEY=*** ~/.hermes/.env >> ~/.hermes/profiles/zhenglishi/.env
# If the line already exists, replace it instead of appending — sed -i.bak is cleaner:
grep -v '^MINIMAX_CN_API_KEY=*** ~/.hermes/profiles/zhenglishi/.env > /tmp/zhen.env
echo "MINIMAX_CN_API_KEY=*** >> /tmp/zhen.env
mv /tmp/zhen.env ~/.hermes/profiles/zhenglishi/.env
```

Pitfalls:
- `MINIMAX_CN_API_KEY` (国内) vs `MINIMAX_API_KEY` (国际) — different env var names, different endpoints, different quota pools. Migrating a profile between them requires BOTH renaming the var AND updating `provider:` + `providers.<name>.base_url`.
- A `.env` line containing only `=sk-xxx` with a leading `*** suffix (no space, no comment) — hermes dotenv parser strips inline `# comment` but NOT a `#` in the key value itself.
- API key rotation: when the user reports "额度恢复了 / 配额恢复", check whether the key value itself changed before assuming anything else.

#### Final verification — search for any remaining old name

```bash
# Catches MiniMax-M2.7, MiniMax-M2.7-highspeed, lowercase minimax-2.7, etc.
grep -rnE "MiniMax-M2\.7|minimax-2\.7|M2\.7-highspeed" \
     ~/.hermes/config.yaml \
     ~/.hermes/profiles/*/config.yaml \
     ~/.hermes/cron/jobs.json 2>/dev/null
# Should print nothing.
```

### One-Click Multi-Provider Switching (DeepSeek ↔ Volcengine)

For bulk model switching across ALL Hermes profiles + Codex + Gateway, use:

```bash
python3 ~/.hermes/scripts/switch_model.py deepseek     # 切 DeepSeek
python3 ~/.hermes/scripts/switch_model.py volcengine   # 切火山引擎
python3 ~/.hermes/scripts/switch_model.py status       # 查看状态
```

This is faster than the manual 5-layer checklist below and also updates Codex config + arkcli.models.json.

#### Final verification — scan for staleness

# Sanity-check YAML + JSON still parse
python3 -c "import yaml; yaml.safe_load(open('$HOME/.hermes/config.yaml')); print('YAML OK')"
python3 -c "import json; json.load(open('$HOME/.hermes/cron/jobs.json')); print('JSON OK')"
```

#### What `hermes config set` CAN do / CANNOT do

- ✅ Top-level scalar: `hermes config set model MiniMax-M3`
- ✅ Nested scalar (one dot path): `hermes config set auxiliary.vision.model MiniMax-M3`
- ✅ Array element by index: `hermes config set custom_providers.0.model MiniMax-M3`
- ❌ Nested keys with the full path in one shot — level by level only
- ❌ Delete keys — only set to empty/`null`/space (残留条目 stays in YAML)
- ❌ Accept `--provider` flag (that's for `hermes chat`, not `hermes config`)
- ❌ Edit cron job models — must patch `jobs.json` directly
- ⚠️ **Without `--profile`, writes to `active_profile`, NOT `default`** — `hermes config set model X` goes to whatever `~/.hermes/active_profile` points to. When bulk-switching models across profiles, ALWAYS include `--profile <name>`.
- ⚠️ **`HERMES_HOME` env-var drift is WORSE than `active_profile`** — when a shell/cron context has `HERMES_HOME=/Users/hua/.hermes/profiles/<other>` exported (e.g. a gateway subprocess for profile `zhenglishi`), then `hermes config set` (even without `--profile`) resolves to THAT profile's `config.yaml`, NOT `default`. Symptom: you edit `model` intending 玉芬(default) but it silently lands in another profile. 渔芯实案 (2026-08-17): `switch_work_model.py` used bare `hermes config set model X` and spent days writing 玉芬's model into `zhenglishi/config.yaml` while 玉芬's real config never changed. **Fix: always pass `--profile default` (or the exact profile name) explicitly, and verify with `grep -n '^model:' /Users/hua/.hermes/config.yaml` after.**

- ⚠️ **Core-agent `model:`/`provider:` is sacred — never auto-switch it** — the default profile (the dispatcher/orchestrator the user depends on, e.g. 玉芬 in 渔芯) is the single point of failure. If a usage-switching script (peak/valley scheduler, CC Switch, anything time-based, ANY cron) writes to default's `model:` or `provider:` field with a wrong endpoint/key, the agent silently dies — Feishu messages queue, cron tasks fail, the user doesn't know why until manually inspecting config. 渔芯 verified pitfall (2026-08-17): `switch_work_model.py` had a `switch_yufen()` that toggled 玉芬 between `minimax` and `deepseek` per time-of-day; one bad write set `provider: minimax-vision` (quant's sk-cp key + OpenAI v1 endpoint) instead of `minimax-cn` (玉芬's `MINIMAX_API_KEY` + anthropic endpoint), 玉芬 stopped responding. The user said verbatim: *"你把自己改死了，你要直接配置minimax，不要走cc switch。下次不要出错了，我可是离不开你了。"* **Rule: write the default profile's `model:` and `provider:` directly to `~/.hermes/config.yaml` and freeze it. Auto-switching scripts must explicitly skip the default profile, or only touch non-core agents (e.g. Codex, sub-agents).** If the user ever says "我可是离不开你" or "把自己改死了", treat default's model/provider as untouchable.

- ⚠️ **`minimax-vision` ≠ `minimax-cn`** — a single `config.yaml`'s `providers` block can contain multiple providers with similar names that point to totally different endpoints and keys. 渔芯 case: `minimax-cn` (玉芬's own `MINIMAX_API_KEY` + `https://api.minimaxi.com/anthropic`) vs `minimax-vision` (quant's `sk-cp-...` key + `https://api.minimaxi.com/v1`). Running `hermes config set provider minimax-vision --profile default` on 玉芬 = 玉芬 uses quant's key = 死. **Before any `hermes config set provider <name>`, read `providers.<name>.api_key[_env]` and `base_url` and confirm they belong to the agent you're configuring.** Don't trust provider names alone — verify keys and endpoints. When multiple providers share similar names, prefer the one whose `api_key_env` matches the agent's own `.env` (e.g. 玉芬's `.env` has `MINIMAX_API_KEY` → use `minimax-cn`, not `minimax-vision`).

- ⚠️ **Verify the fix actually worked after `hermes config set`** — `hermes config set` returns `✓ Set X in /path/to/config.yaml` even when the operation is conceptually wrong (wrong profile, wrong provider, failed write). Treat the success line as a syntactic ack, not a semantic one. Always follow up with: (1) `grep -nE '^(model|provider):' <expected-config.yaml>` to confirm the write landed in the right file with the right value, (2) test the new model/provider with a 1-token API call before declaring done (curl the provider's `base_url` with the matching key), (3) update memory + cron job notes if the change is permanent. 渔芯 2026-08-17: I saw `✓ Set provider = minimax-cn` but the config's `provider:` line ended up as `minimax-vision` (likely due to YAML ordering quirks + a previous edit on the same key); only the grep step surfaced it.

**Clean residual YAML entries** (old model names under `custom_providers[0].models`) when CLI can't delete:
```python
import yaml
path = "/Users/hua/.hermes/config.yaml"
with open(path) as f:
    cfg = yaml.safe_load(f)
for p in cfg.get("custom_providers", []):
    for key in list(p.get("models", {}).keys()):
        if key.startswith("MiniMax-M2"):  # adjust pattern as needed
            del p["models"][key]
with open(path, "w") as f:
    yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
```

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `search` | Web search only (subset of `web`) |
| `todo` | In-session task planning and tracking |
| `rl` | Reinforcement learning tools (off by default) |
| `moa` | Mixture of Agents (off by default) |
| `homeassistant` | Smart home control (off by default) |

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Security & Privacy Toggles

Common "why is Hermes doing X to my output / tool calls / commands?" toggles — and the exact commands to change them. Most of these need a fresh session (`/reset` in chat, or start a new `hermes` invocation) because they're read once at startup.

### Secret redaction in tool output

Secret redaction is **off by default** — tool output (terminal stdout, `read_file`, web content, subagent summaries, etc.) passes through unmodified. If the user wants Hermes to auto-mask strings that look like API keys, tokens, and secrets before they enter the conversation context and logs:

```bash
hermes config set security.redact_secrets true       # enable globally
```

**Restart required.** `security.redact_secrets` is snapshotted at import time — toggling it mid-session (e.g. via `export HERMES_REDACT_SECRETS=true` from a tool call) will NOT take effect for the running process. Tell the user to run `hermes config set security.redact_secrets true` in a terminal, then start a new session. This is deliberate — it prevents an LLM from flipping the toggle on itself mid-task.

Disable again with:
```bash
hermes config set security.redact_secrets false
```

### PII redaction in gateway messages

Separate from secret redaction. When enabled, the gateway hashes user IDs and strips phone numbers from the session context before it reaches the model:

```bash
hermes config set privacy.redact_pii true    # enable
hermes config set privacy.redact_pii false   # disable (default)
```

### Command approval prompts

By default (`approvals.mode: manual`), Hermes prompts the user before running shell commands flagged as destructive (`rm -rf`, `git reset --hard`, etc.). The modes are:

- `manual` — always prompt (default)
- `smart` — use an auxiliary LLM to auto-approve low-risk commands, prompt on high-risk
- `off` — skip all approval prompts (equivalent to `--yolo`)

```bash
hermes config set approvals.mode smart       # recommended middle ground
hermes config set approvals.mode off         # bypass everything (not recommended)
```

Per-invocation bypass without changing config:
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

Note: YOLO / `approvals.mode: off` does NOT turn off secret redaction. They are independent.

### Shell hooks allowlist

Some shell-hook integrations require explicit allowlisting before they fire. Managed via `~/.hermes/shell-hooks-allowlist.json` — prompted interactively the first time a hook wants to run.

### Disabling the web/browser/image-gen tools

To keep the model away from network or media tools entirely, open `hermes tools` and toggle per-platform. Takes effect on next session (`/reset`). See the Tools & Skills section above.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`
- **Can't restart from inside gateway**: `hermes gateway restart` and `hermes gateway stop` refuse to run when the calling process is inside the gateway itself (safety guard against restart loops). **Workaround**: use launchd directly — `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway` for the default profile, or `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway-<profile>` for a named profile. This talks to launchd, not the gateway process, so it bypasses the guard. Verify with `launchctl list | awk '$3 ~ /ai\\.hermes\\.gateway$/ {print $1, $2}'`.

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.
- **macOS terminal `workdir` path blocked on Chinese folders**: The terminal tool's `workdir` parameter rejects non-ASCII characters like `渔芯科技`. **Workaround: always use `cd "/path/with/chinese" && command` pattern instead of `workdir`.** See `references/terminal-chinese-paths.md` for the full recipe.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

### The `active_profile` Mechanism (Critical for Terminal Users)

### `active_profile` — Why Terminal `hermes` Sometimes Runs the Wrong Identity

**Mechanism**: `hermes profile use <name>` writes the profile name to `~/.hermes/active_profile`. When you run `hermes` in the terminal without `--profile`, Hermes reads this file and uses that profile. If the file is empty or missing, it falls back to `default`.

**The confusion pattern**: After `hermes profile use maodou`, ALL terminal sessions run as maodou. If you later run `hermes profile use default`, the file is deleted and terminal `hermes` reverts to bare `default` (which has no SOUL.md = generic identity). This makes the terminal feel like it's "becoming a different agent."

**LaunchAgents are NOT affected**: Every plist hardcodes `--profile <name>` in `ProgramArguments`. They read `active_profile` only when the profile name is missing from arguments — which is never the case for properly configured plists. Gateway processes always run the correct profile.

Verification:
```bash
cat ~/.hermes/active_profile          # check current terminal default
```

If the terminal is running the wrong identity, either:
- `hermes profile use maodou` to set it back
- Or use explicit `--profile`: `hermes -p maodou chat`

> See also: `references/active-profile-mechanism.md` for the full decision table and the confusion scenario explained.

## Common Pitfalls

1. **API Key NOT inherited from main .env** — Each profile's `.env` is fully isolated. Even if the main `~/.hermes/.env` has `MINIMAX_CN_API_KEY`, sub-profiles do NOT inherit it. Every sub-profile must have its own `MINIMAX_CN_API_KEY` explicitly set. Without it, the bot can receive Feishu messages but will fail with HTTP 401 when calling the LLM.

2. **`launchctl bootstrap gui/<uid>` fails on Hermes plists with `Bootstrap failed: 5: Input/output error`** (2026-06-30 验证) — On macOS 13+, the modern `bootstrap` command is supposed to be preferred over legacy `load`, but **on these specific Hermes gateway plists, bootstrap returns I/O error 5 and never loads**. The user-facing symptom: `launchctl list | grep ai.hermes.gateway-<name>` shows nothing. **Workaround: use legacy `launchctl load ~/Library/LaunchAgents/ai.hermes.gateway-<name>.plist`** — works 100% of the time on these plists. After loading, verify with `launchctl list | awk -v lbl="ai.hermes.gateway-<name>" '$3==lbl {print $1}'` (use `$3` exact match, not `grep` — `grep "ai.hermes.gateway"` will falsely match `ai.hermes.gateway-maodou` when looking for `ai.hermes.gateway`).

3. **Feishu private chat routing requires user-initiated touch after long bot downtime** (2026-06-30 黑豆/阿福 验证) — The gateway's WebSocket can be fully connected (logs show "✓ feishu connected"), cron ticker running, but **private DMs from the user still get silently dropped at the Feishu server side**. Root cause: Feishu enterprise apps require the user to have sent the bot at least one message in the chat history before the "im.message.receive_v1" webhook fires. After >1 day of bot downtime, this routing can be discarded server-side even when the gateway is healthy. **Symptom**: bot can send to group chats, but user private messages don't reach the bot's gateway.log. **Fix**: user opens Feishu, searches for the bot name, opens the chat, sends any one message ("在吗" works). Feishu may show a "开始对话" / "Start chat" prompt — click it. After that one interaction, private routing is permanently re-established. **Doesn't apply to group chats** — group routing is purely on bot membership. **This is independent of the launchd process being up** — restarting the gateway does NOT re-establish the routing.

4. **Each profile's L1 (`~/.hermes/profiles/<name>/memories/MEMORY.md`) drifts independently** (2026-06-30 验证) — When 5+ profiles have been running independently for months, their L1 memories will contain **stale platform assumptions** (e.g. 5 profiles each had L1 saying "I'm a Windows Agent running on a different machine and must use Feishu cloud drive to talk to 玉芬" — all wrong since they were migrated to the same Mac mini). The drift isn't caught by any standard mechanism: cron is fine, gateway is fine, model is fine, but the agent's L1 description of itself is wrong. **Detection**: grep for "Windows" / "云盘中转" / "与玉芬不在同一台" across `~/.hermes/profiles/*/memories/MEMORY.md` and audit for current platform reality. **Fix**: refresh_all_l1.py pattern — rewrite each profile's L1 with current platform facts (PID, gateway state, last reactivation), then bulk-gzip sessions older than 30 days to reclaim space.

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

Auto-discovery: any `tools/*.py` file with a top-level `registry.register()` call is imported automatically — no manual list needed.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs — never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Key Rules

- **Never break prompt caching** — don't change context, tools, or system prompt mid-conversation
- **Message role alternation** — never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met

## Absorbed: webhook subscriptions (2026-09-02 curator merge)

Former standalone `webhook-subscriptions` skill → `references/webhook-subscriptions.md`: event-driven agent runs via webhook subscriptions — configuration, payload shape, and gateway wiring. Read it when wiring external systems to trigger Hermes runs without a cron poller.
