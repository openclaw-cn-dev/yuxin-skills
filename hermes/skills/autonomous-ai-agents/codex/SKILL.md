---
name: codex
description: "Delegate coding to OpenAI Codex CLI (features, PRs)."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring, Volcano-Engine, Plugins, Computer-Use]
    related_skills: [claude-code, hermes-agent]
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## When to use

- Building features
- Refactoring
- PR reviews
- Batch issue fixing
- **Browser automation** — web scraping, 自媒体运营, form filling, data extraction from web apps (Codex's Playwright-based `browser`/`chrome` plugins are faster and more stable than Hermes' built-in browser stack)

Requires the codex CLI and a git repository.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- OpenAI auth configured: either `OPENAI_API_KEY` or Codex OAuth credentials
  from the Codex CLI login flow
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

For Hermes itself, `model.provider: openai-codex` uses Hermes-managed Codex
OAuth from `~/.hermes/auth.json` after `hermes auth add openai-codex`. For the
standalone Codex CLI, a valid CLI OAuth session may live under
`~/.codex/auth.json`; do not treat a missing `OPENAI_API_KEY` alone as proof
that Codex auth is missing.

### Recovering a broken npm install

If `codex --version` throws `Missing optional dependency @openai/codex-darwin-arm64`,
the npm install lost its platform-specific binary. Reinstall:

```bash
npm install -g @openai/codex@latest
```

This fixes the missing optional dependency without any additional flags.

### Cron/Sandboxed Upgrade Workflow (Permission Issues)

When upgrading Codex in a cron job or sandboxed environment:
1. **Global npm install may fail with EACCES** — `/usr/local/lib/node_modules` requires sudo
2. **sudo doesn't work in cron** — no terminal for password input
3. **华哥's codex lives at `~/.local`**, NOT the npm global default — always use this prefix

**Verified Workflow (2026-07-17) — direct local install without sudo:**
```bash
# Direct install to the exact prefix where codex is already installed
# This avoids any copying afterward
npm install -g @openai/codex --prefix /Users/hua/.local

# Verify
/Users/hua/.local/bin/codex --version
```

**Legacy fallback** (if prefix method times out or fails):
```bash
# Install to temp prefix then copy
npm install -g @openai/codex --prefix ~/.npm-global
cp -r ~/.npm-global/lib/node_modules/@openai/codex /Users/hua/.local/lib/node_modules/@openai/
```

**Path pitfalls to avoid**:
- Cron jobs run under Hermes profile home (`~/.hermes/profiles/<name>/home/`), but the real codex binary lives at `/Users/hua/.local/bin/codex`
- **Never use `~`** in paths during cron — it expands to the profile home, not the user home
- Always use absolute paths: `/Users/hua/.local/`, not `~/.local/`
- **npm can timeout** — if the install hangs after 60s, try again with a clean npm cache

## China Login Blocked (2026-07-11)

OpenAI blocks OAuth login from China IPs:
```
"error": {"code": "***SECRET***"}
```

**Workaround**: Codex **does not need OpenAI login** when using custom model providers (DeepSeek via LLM Gateway). All model calls go through `127.0.0.1:18888` → DeepSeek API. The blocked login only prevents:
- Using OpenAI's own models (GPT-4, etc.)
- OAuth-based MCP servers (Linear, Figma)
- Marketplace browsing directly

The 15 locally cached plugins work fine without login. OAuth-dependent ones (Linear, Figma) show auth errors but don't block Codex.

### API Key Login (Alternative)
Codex supports API key login: `codex login` with `sk-...` key. Project keys (`sk-proj-...`) need a project ID header. Regular API keys (`sk-...`) work directly. Free tier supports `gpt-4o-mini` and other models.

## Gateway Debugging — Lessons from 2026-07-11 DeepSeek Migration

When the Gateway returns 502 for Codex but direct HTTP tests pass, check:

### 1. Path matching: `/openai/v1/responses` vs `/openai/responses`
Codex may send either path depending on version. Gateway must match both:
```python
is_responses = request.path.startswith("/openai/responses") or request.path.startswith("/openai/v1/responses")
```

### 2. Volcengine URL correction must check backend URL, not route name
```python
# WRONG: "volc" in which — "which" is "primary"/"fallback", never contains "volc"
# RIGHT:
if is_responses and "volces.com" in backend["url"]:
    rest = "/chat/completions"  # volcengine doesn't use /v1/ prefix
```

### 3. Responses API `input` field translation
When `input` is a string (single-turn), wrap it in a proper messages list:
```python
if isinstance(input_val, str):
    body_json["messages"] = [{"role": "user", "content": input_val}]
```
Otherwise DeepSeek receives `"messages": "some string"` and returns 400.

### 4. DeepSeek model names are strict
DeepSeek API accepts ONLY `deepseek-v4-pro` or `deepseek-v4-flash` — no volcengine suffixes (`-260425`). Passing `***SECRET***` to DeepSeek returns 400.

### 5. Gateway process can hang silently
Symptoms: health endpoint returns 200, but no new requests logged. Process shows 0% CPU.
- Kill the process, unload launchd plist, start fresh with brew Python 3
- Launchd double-launch can cause state corruption
- `launchctl unload` the plist before manual restart to prevent auto-respawn

### 6. Python 3.14 + aiohttp 3.14.1 is the current runtime
Gateway run command:
```bash
/opt/homebrew/bin/python3 ~/.hermes/scripts/llm_gateway.py --port 18888
```
System Python 3.9 lacks aiohttp — always use brew Python.

## Current Setup (华哥's machine, as of 2026-08-08)

### LLM Gateway with Responses API SSE Translation (v0.144.1)

Codex v0.144.1 uses `wire_api = "responses"` which expects OpenAI Responses API format with SSE streaming. The LLM Gateway (`~/.hermes/scripts/llm_gateway.py`) provides full bidirectional SSE streaming translation:

**Request translation** (Responses → Chat Completions):
- `input` → `messages`, `max_output_tokens` → `max_tokens`
- Role: `developer` → `system`
- Content type: `input_text` → `text`
- Forces `stream: true` for SSE delivery

**SSE event translation** (DeepSeek SSE → Responses API events):
- `response.created` — session start with response ID
- `response.output_item.added` — before first text delta
- `response.output_text.delta` — per-token text streaming
- `response.completed` — final with output array and usage (prompt_tokens→input_tokens)

Gateway routes `/openai/responses` → `/v1/chat/completions` (DeepSeek) or `/chat/completions` (Volcengine).

### Breaking Changes in v0.142.5

1. **`wire_api` must be `"responses"`** — `"chat_completions"` causes config load failure: `unknown variant 'chat_completions', expected 'responses'`. Update all provider blocks.
2. **Plugin command changed** — `codex plugin install <name>` removed. Use `codex plugin add <name>@<marketplace>` instead.
3. **Some plugins removed** — `browser`, `chrome`, `computer-use` no longer available in `openai-api-curated` marketplace.

### Connection (as of 2026-07-11)

Codex CLI v0.144.1 connects through the **LLM Gateway** (port 18888) which now routes **DeepSeek as primary** (Volcengine Agent Plan quota exceeded 7/11, resets 7/13):

**`~/.codex/config.toml` (current, 2026-07-17 — via LLM Gateway, NO CC Switch):**
```toml
model_provider = "custom"
model = "deepseek-v4-pro"          # via LLM Gateway → DeepSeek API (primary)
model_reasoning_effort = "high"
disable_response_storage = true
wire_api = "responses"

[model_providers]
[model_providers.custom]
name = "hermes_gateway"
base_url = "http://127.0.0.1:18888/openai"       # NO /v1 suffix — Codex appends /v1/responses
wire_api = "responses"
requires_openai_auth = false
```

Gateway routes (in `~/.hermes/scripts/llm_gateway.py`): `/openai` primary→DeepSeek, fallback→Volcengine Agent Plan.

### Active Model
- **`deepseek-v4-pro`** — the ONLY model name that works with DeepSeek API directly. No `-260425` suffix (that's a volcengine-specific model ID). DeepSeek API accepts `deepseek-v4-pro` or `deepseek-v4-flash`.
- When volcengine quota resets (7/13), volcengine models become available again: `***SECRET***`, `deepseek-v4-pro-260425`, `glm-5.2`, etc.
- **Model capabilities**: See `references/volcengine-model-capabilities.md` for which models support vision input, image generation, and code. DeepSeek = text-only; doubao/GLM = vision; seedream = image gen.

### Installed Plugins (17, as of 2026-08-08)

v0.147.0 auto-discovers plugins from 4 marketplace cache directories:

**openai-api-curated (7):**
| Plugin | Purpose |
|--------|---------|
| `superpowers` | Extended capabilities |
| `github` | GitHub integration |
| `coderabbit` | Code review |
| `build-web-apps` | Web app development |
| `linear` | Project management (needs OAuth) |
| `sentry` | Error monitoring |
| `figma` | Design integration (needs OAuth) |

**openai-bundled (4):**
| Plugin | Purpose |
|--------|---------|
| `browser` | Browser automation |
| `chrome` | Chrome control |
| `computer-use` | Desktop automation |
| `visualize` | Data visualization |

**openai-primary-runtime (5):**
| Plugin | Purpose |
|--------|---------|
| `documents` | Document handling |
| `pdf` | PDF processing |
| `spreadsheets` | Spreadsheet operations |
| `presentations` | Presentation tools |
| `template-creator` | Template generation |

**sisyphuslabs (1):**
| Plugin | Purpose |
|--------|---------|
| `omo` | Model orchestration |

No manual `codex plugin install/add` needed — plugins auto-discovered from marketplace directories on each run.

**Unused (not in cache):** `latex`, `record-and-replay`, `remotion`, `game-studio`, `expo`, `render`, `nvidia`, `circleci`, etc. — available in marketplace but not cached locally.

### AGENTS.md (as of 2026-08-08)
Project-level instructions at `~/.codex/AGENTS.md`:
- Chinese primary language, English code comments
- Current model: `deepseek-v4-pro` via local Gateway `127.0.0.1:18888`
- 17 plugins across 4 marketplace cache directories (api-curated, bundled, primary-runtime, sisyphuslabs)
- Tools: GitHub CLI, Computer Use, Browser automation, LLM Gateway

### Maintenance (玉芬 managed)
Codex is under 玉芬's autonomous maintenance with 3 cron jobs:
- **Daily 9:00** — version check + auto-upgrade (see Cron/Sandboxed Upgrade Workflow)
- **Daily 10:00** — full status sync: version check, plugin audit (via `ls ~/.codex/plugins/cache/*/`), then GitHub sync via `~/.hermes/scripts/codex_github_sync.sh` (not the legacy `sync_codex_repo.sh`)
- **Weekly Mon 9:00** — full evolution scan: plugins, config, Gateway, AGENTS.md, new features

**Version check pattern for cron jobs (verified 2026-07-17):**
```bash
# 1. Get current version — use absolute path for cron safety
OLD=$(/Users/hua/.local/bin/codex --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')

# 2. Get latest npm version
NEW=$(npm view @openai/codex version 2>&1)

# 3. Compare and upgrade if needed
if [ "$OLD" != "$NEW" ] && [ -n "$OLD" ] && [ -n "$NEW" ]; then
  # Use direct local prefix install (verified method, no copying needed)
  npm install -g @openai/codex --prefix /Users/hua/.local
  
  # Verify and report upgrade
  VERIFIED=$(/Users/hua/.local/bin/codex --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
  echo "📦 Codex 已升级：$OLD → $VERIFIED。插件保持原样，如需更新插件请手动 codex plugin update。"
fi
```

**Daily Status Sync — TWO scripts, two purposes (2026-08-08 clarified):**

| Script | Purpose | GitHub Push | Cache Dir |
|--------|---------|:-----------:|-----------|
| `~/.hermes/scripts/codex_github_sync.sh` | **Real GitHub sync** (hourly cron) | ✅ `git@github.com:openclaw-cn-dev/yuxin-skills.git` | `/tmp/yuxin-skills-codex-sync/` |
| `~/6-产品研发/22-出图智能体训练/sync_codex_repo.sh` | Local backup only | ❌ local-only | `~/codex-workspace/yuxin-skills/` |

The hourly sync script calls `codex_self_evolution.py --sync-only`, which:
1. Version check → 2. Plugin validation (cache dirs) → 3. Copy AGENTS.md, config.toml (脱敏), skills/yuxin-*, plugins.json, STATUS.md → 4. Git commit + push

**Daily full cron** should run BOTH: version check + plugin audit first, then the hourly sync script for the GitHub push. The `sync_codex_repo.sh` in the 出图项目 is a legacy local-only script — it cannot push to GitHub because the `~/codex-workspace/` clone has no remote configured.

**PATH requirement for cron contexts (2026-08-08):**
- `codex` lives at `/Users/hua/.local/bin/codex` — NOT on default cron PATH
- Always prefix: `export PATH="$HOME/.local/bin:$PATH"` or use absolute path `/Users/hua/.local/bin/codex`
- The hourly sync script (`codex_github_sync.sh`) runs via Hermes venv Python, which handles PATH internally

**Plugin cache pitfall (2026-07-15, confirmed 2026-08-08):**
- Expected cache path `~/.codex/plugins/cache/openai-api-curated/` may be empty or not exist when not logged in
- `codex plugin list` without login = ALL plugins show "not installed" — this is the marketplace install state, NOT the cache reality
- AGENTS.md records 17 plugins across 4 cache dirs: openai-api-curated (7), openai-bundled (4), openai-primary-runtime (5), sisyphuslabs (1)
- **Real plugin status must be verified with `ls ~/.codex/plugins/cache/*/`**, not `codex plugin list`

**npm path mismatch (codex doctor finding):**
- Running codex: `/Users/hua/.local/lib/node_modules/@openai/codex`
- npm global root: `/usr/local/lib/node_modules/@openai/codex`
- This causes "npm install -g would update a different install" warning in `codex doctor`
- Workaround: Always use the local prefix install method (see Cron/Sandboxed Upgrade Workflow)

**GitHub sync fallback:**
- When GitHub SSH auth isn't configured, `sync_codex_repo.sh` initializes a local git repo at `~/codex-workspace/yuxin-skills/` without remote
- Status reports are saved locally even if remote push fails
- For actual GitHub push, use the hourly sync script which targets `/tmp/yuxin-skills-codex-sync/` with a pre-configured SSH remote

Update AGENTS.md after any model/provider/plugin change. Keep the `codex` skill in sync.

### MCP Servers (3)
Configured in `~/.codex/arkcli.config.toml`:
- **DataPro Search** — Volcengine data search
- **Echo Search** — General search engine
- **OpenViking Control Plane** — Cloud resource management

## Hermes ↔ Codex Collaboration

### 生产代码优化实战流程（2026-08-16 验证）

对正式项目（非临时 scratch）用 codex 做代码优化，稳定流程：

1. **任务描述写到文件**，避免 shell 转义（中文 + 引号 + 冒号等特殊字符）：`write_file /tmp/codex_task.txt`。内容必须自包含：背景 → 现状问题（编号列出）→ 具体任务（编号，含"只改哪些文件、不破坏哪些"）→ 要求（注释英文/日志中文/验证命令）→ 完成后报告什么。
2. **codex exec 读文件执行**（后台 + 完成通知）：
   ```bash
   terminal(command='cd <项目> && /Users/hua/.local/bin/codex exec --sandbox workspace-write "$(cat /tmp/codex_task.txt)"', background=true, notify_on_complete=true)
   ```
3. **实测验证 self-report**（codex 报告"已完成 + 测试全通过"不算数，必须亲自验）：
   - 读改动后的代码，确认逻辑真实落地（不是口头描述）
   - 实际启动/运行：`curl` health、调接口、看返回
   - 语法/import：`python3 -c "import ast; ast.parse(open('x.py').read())"` 和 `import` 模块验证

### 社交平台发布集成（codex_bridge 模式，2026-08-16）

华哥验证 Codex 浏览器插件做社交平台发布（登录/填表/发布）有优势。HG-运营中枢 用 `codex_bridge.py` 集成：FastAPI 服务接收发布任务 → `asyncio.subprocess` 调 `codex exec` 浏览器插件真实发布。任务提示词含平台名/创作者中心发布 URL/标题/正文/标签 + "登录→填表→发布→返回确认"，结果用 `PUBLISH_OK|平台|链接` / `PUBLISH_FAIL|原因` 格式约束。关键前提：**codex 必须切到 vision 模型**（doubao-seed-2-0-pro / glm-5.2-pro），text-only 的 deepseek 浏览器插件"看不见"页面无法真实操作。详见 `hg-ops-platform` 技能。

Use `delegate_task` to hand off coding tasks to Codex:

```python
# In Hermes, delegate a coding task to Codex
delegate_task(
    goal="Add dark mode toggle to settings page",
    context="Project at ~/project. Use codex exec with --sandbox workspace-write",
    toolsets=["terminal", "file"]
)
```

Or directly via terminal:
```bash
terminal(command="codex exec --sandbox workspace-write 'Add dark mode toggle'", workdir="~/project")
```

## Browser Automation via Codex

**When Hermes browser tools are too slow or unstable, delegate to Codex.** Codex's `browser` and `chrome` plugins (Playwright-based) are faster, handle dynamic pages better, and have built-in bot-detection evasion.

### Vision Model Requirement (critical)

Browser plugins need a model that can **see** screenshots. Text-only models can drive the browser but can't parse visual page state — effectively useless for real web automation.

| Model | Vision | Browser usable? |
|-------|:------:|:---------------:|
| `doubao-seed-2-0-pro` | ✅ | ✅ Best domestic option |
| `glm-5.2-pro` | ✅ | ✅ Long context + vision |
| OpenAI GPT-4o | ✅ | ✅ Native integration, needs proxy from China |
| `MiniMax-M2.7` | ❌ | ❌ Current model — browser plugins load but can't see |
| `deepseek-v4-pro/flash` | ❌ | ❌ Text-only |
| `doubao-seed-2-0-code-preview` | ❌ | ❌ Code-focused, no vision |

### Three paths to activate

| Path | Model | Setup | Status |
|------|-------|-------|:------:|
| A | OpenAI GPT-4o | API key (`sk-...`) + proxy via Gateway | 华哥说可以申请帐号 |
| B | Volcengine doubao-pro | Existing Agent Plan, switch model | 配额可能紧张 |
| C | GLM-5.2 | 智谱 API key | 需单独申请 |

### Usage pattern

```bash
# Delegate browser task to Codex (vision model required)
terminal(command="codex exec --sandbox workspace-write \
  'Go to https://creator.douyin.com, log in, and post this video draft'",
  workdir="~/codex-workspace", background=true, pty=true)
```

### Checking if Codex browser is ready

```bash
# 1. Confirm browser plugin exists
ls ~/.codex/plugins/cache/openai-bundled/browser/

# 2. Confirm model supports vision
grep '^model' ~/.codex/config.toml
# Must be doubao-seed-2-0-pro / glm-5.2-pro / or an OpenAI vision model
# MiniMax-M2.7 or deepseek = text-only = browser won't work visually

# 3. Quick smoke test with vision model
codex exec --skip-git-repo-check \
  "Navigate to https://example.com and tell me what the page title is" \
  2>&1 | tail -5
```

When the user says "I updated Codex", run these checks:

```bash
# 1. Check config loads without error
codex plugin list 2>&1 | head -3

# 2. If "unknown variant 'chat_completions'" → wire_api must be "responses"
grep -n 'chat_completions' ~/.codex/config.toml && \
  echo "⚠️  Change all 'chat_completions' to 'responses'"

# 3. Verify installed plugins
ls ~/.codex/plugins/cache/openai-api-curated/

# 4. LLM Gateway health
curl -s http://127.0.0.1:18888/health

# 5. Test a simple Codex call (using doubao, non-reasoning for speed)
echo "hello" | codex exec --skip-git-repo-check --sandbox workspace-write \
  -c model=***SECRET*** 2>&1 | tail -3
```

Common post-update fixes:
- `wire_api = "chat_completions"` → `"responses"` (most common breakage)
- Reinstall plugins: `codex plugin add <name>@openai-api-curated`
- `browser`/`computer-use` plugins unavailable → removed from marketplace
- Gateway using old code → `pkill -f llm_gateway && bootout launchd` + restart
- 404 on volcengine → check Gateway log for URL with extra `/v1/` prefix

Codex supports custom model providers via its `config.toml` and an optional companion `arkcli.config.toml` (for Volcengine/Ark CLI setups).

### Ark CLI (Volcengine Agent Plan)

Configure Codex to use a Volcengine Agent Plan (火山引擎智能体计划) model:

**`~/.codex/arkcli.config.toml`:**
```toml
model = "deepseek-v4-flash-260425"        # or deepseek-v4-pro-260425
model_catalog_json = "/Users/hua/.codex/arkcli.models.json"
model_context_window = 1048576            # 1M tokens
model_provider = "arkcli-agent-plan"

[model_providers]
  [model_providers.arkcli-agent-plan]
    base_url = "https://ark.cn-beijing.volces.com/api/plan/v3"
    experimental_bearer_token = "ark-xxxxx-xxxxx"
    name = "Volcano Engine (Agent Plan)"
    wire_api = "responses"
```

**`~/.codex/config.toml`** (primary config):
```toml
model_provider = "custom"
model = "deepseek-v4-flash-260425"
model_reasoning_effort = "high"
disable_response_storage = true
wire_api = "responses"

[model_providers]
[model_providers.custom]
name = "ark_agentplan"
base_url = "http://127.0.0.1:15721/v1"    # local proxy
wire_api = "responses"
requires_openai_auth = true
experimental_bearer_token = "PROXY_MANAGED"
```

**Model catalog** (`~/.codex/arkcli.models.json`) lists available models. Common ones:
- `deepseek-v4-flash-260425` — fast, 1M context
- `deepseek-v4-pro-260425` — stronger reasoning, 1M context
- `***SECRET***` — code-focused, 262K context

**Auth check:** `codex login status` shows whether you're logged in via API key or OAuth.

**Switching models:** Edit `model = "..."` in both `config.toml` and `arkcli.config.toml`, then restart Codex. The model must exist in the catalog JSON.

### Direct Connection (Bypass CC Switch) — Current

Codex connects directly to Volcengine Agent Plan (no CC Switch proxy).
When the user manually updates Codex, check `wire_api` values first — they're the most common breakage.

### LLM Gateway Management (port 18888)

The Gateway runs as a background process. Update code then restart:

```bash
# Kill and restart with brew Python (system Python 3.9 lacks aiohttp)
pkill -f llm_gateway.py
# IMPORTANT: Ensure launchd service is disabled first or it will auto-respawn
launchctl bootout gui/$(id -u)/com.yuxin.llm-gateway 2>/dev/null || true
/opt/homebrew/bin/python3 ~/.hermes/scripts/llm_gateway.py --port 18888 &

# Verify
curl -s http://127.0.0.1:18888/health
```

### Model Switching (DeepSeek ↔ Volcengine)

Use `~/.hermes/scripts/switch_model.py` to switch ALL components at once:

```bash
python3 ~/.hermes/scripts/switch_model.py deepseek     # 切 DeepSeek
python3 ~/.hermes/scripts/switch_model.py volcengine   # 切火山引擎
python3 ~/.hermes/scripts/switch_model.py status       # 看当前状态
```

This updates: Gateway routes + all 7 Hermes profiles + Codex config.toml + arkcli.models.json. Codex requires restart after switch.

The Gateway has an admin API for manual route control:
```bash
curl "http://127.0.0.1:18888/admin/switch?action=status"     # check
curl "http://127.0.0.1:18888/admin/switch?action=flip"       # swap primary↔fallback
curl "http://127.0.0.1:18888/admin/switch?action=to-primary" # force primary
```

**launchd pitfall**: A legacy launchd service (`com.yuxin.llm-gateway`) auto-respawns on system Python 3.9 (missing aiohttp). Always `bootout` before manual restart. The plist has been updated to use `/opt/homebrew/bin/python3` — reload with `launchctl bootstrap` when ready.

### CC Switch Proxy Troubleshooting (Fallback)

When Codex is routed through **CC Switch** (a local proxy that intercepts API calls), the proxy's SQLite database overrides whatever model you configure in Codex's `config.toml`. If CC Switch's stored model doesn't support the `/responses` endpoint, Codex fails with:

```
unexpected status 404 Not Found: CC Switch local proxy failed while handling Codex endpoint /responses.
Provider: 火山Agentplan; model: ark-code-latest;
upstream_status: HTTP 404;
cause: The requested model does not support the coding plan feature.
```

**Root cause:** CC Switch stores a `settings_config` JSON blob in its `providers` table with a hardcoded `model = "ark-code-latest"` that overrides the user's Codex config. The model `ark-code-latest` does not support the `/responses` API (coding plan feature).

**Quick fix** — update the model in CC Switch's SQLite database:

```bash
# 1. Find the Codex provider (dynamic — UUID changes on restart)
PROVIDER_ID=$(sqlite3 ~/.cc-switch/cc-switch.db \
  "SELECT id FROM providers WHERE app_type='codex';")
echo "Codex provider: $PROVIDER_ID"

# 2. Check what model CC Switch is currently using
sqlite3 ~/.cc-switch/cc-switch.db \
  "SELECT substr(settings_config, instr(settings_config, 'model ='), 50) \
   FROM providers WHERE id = '$PROVIDER_ID';"

# 3. Update the model (e.g. to deepseek-v4-flash-260425)
sqlite3 ~/.cc-switch/cc-switch.db \
  "UPDATE providers SET settings_config = \
   REPLACE(settings_config, 'model = \"ark-code-latest\"', \
   'model = \"deepseek-v4-flash-260425\"') \
   WHERE id = '$PROVIDER_ID';"

# 4. Verify the change
sqlite3 ~/.cc-switch/cc-switch.db \
  "SELECT substr(settings_config, instr(settings_config, 'model ='), 50) \
   FROM providers WHERE id = '$PROVIDER_ID';"
```

After updating, restart Codex. **Note:** CC Switch recreates the provider with a new UUID on restart, so always query by `app_type='codex'` rather than caching the UUID.

See `references/cc-switch-troubleshooting.md` for full details including schema inspection, common models that work with `/responses`, and how to recover if CC Switch reverts the change.

For Gateway SSE streaming debugging (Responess API translation, path matching, model name issues), see `references/gateway-sse-debugging.md`.

For batch image style analysis, standardization, and quality scoring (used in knowledge card projects), see `references/batch-image-style-analysis.md`.

### Post-Upgrade Recovery (v0.144+)

After `npm install -g @openai/codex@latest`, Codex auto-discovers plugins from marketplace directories. No manual reinstallation needed in v0.144+.

Quick post-upgrade checks:
```bash
codex --version
codex plugin list 2>&1 | head -5
grep -n 'chat_completions' ~/.codex/config.toml && echo "⚠️ wire_api must be 'responses'"
curl -s http://127.0.0.1:18888/health
```

Common issues:
- `wire_api = "chat_completions"` → `"responses"` (persistent pitfall across versions)
- Gateway using old code → `pkill -f llm_gateway && launchctl unload` + restart
- 404 on volcengine → check Gateway log for URL with extra `/v1/` prefix

### Desktop App

Codex has a native macOS desktop app. Run `codex app` to install and launch it:

```bash
codex app
```

On first run this:
1. Downloads a ~505MB DMG from `https://persistent.oaistatic.com/codex-app-prod/Codex.dmg`
2. Mounts the installer
3. Installs to `/Applications/Codex.app`
4. Launches the app

Subsequent runs open the existing app directly. The desktop app runs as a full
Electron-style process tree (main, renderer, GPU, network service).

After installation, the app can also be launched from Launchpad or
`/Applications/Codex.app`.

**Note:** `codex app` is a foreground process — use `background=true` in terminal
calls, or just tell the user to open it from /Applications.

### CLI ↔ Desktop App Shared State (verified 2026-08-13)

CLI 和桌面端 Codex **共用同一套 `~/.codex/` 状态存储**，不是各存各的。实测（华哥机器）确认：

| 共享存储 | 内容 |
|---------|------|
| `~/.codex/session_index.jsonl` | 会话索引（列表） |
| `~/.codex/sessions/YYYY/MM/` | 会话存档（按月） |
| `~/.codex/archived_sessions/rollout-*.jsonl` | 归档会话 |
| `~/.codex/state_5.sqlite` / `goals_1.sqlite` / `memories_1.sqlite` | 状态 / 目标 / **记忆** |
| `~/.codex/logs_2.sqlite` | 日志 |

- **CLI 跑完的任务**会落盘到 `session_index.jsonl` + `sessions/` 归档；桌面端（同一引擎、读同一 `~/.codex`）刷新/重启后能在会话列表和历史里看到。反向同理——桌面端产生的会话 CLI 也能读到。
- **`memories_1.sqlite` 记忆库共享** — CLI 任务里形成的"记忆"，桌面端后续会带上。
- **不是实时同步，是"落盘后可见"** — CLI 运行时桌面端不会实时看到中间过程；要等会话写完、桌面端刷新/重启后才出现。
- **桌面端自己的 `~/Library/Application Support/Codex/` 是独立 Electron/Chromium UI 缓存**（Cookie、Crashpad、SingletonSocket 等），不含对话内容；迁移 `~/.codex` 时不用管它。

### Doubao (豆包) Model Configuration — Direct via LLM Gateway

Codex can be configured to use Doubao (豆包) models from Volcengine Agent Plan directly, without CC Switch. This provides access to code-specialized models, vision capabilities, and faster reasoning models.

**`~/.codex/config.toml` (complete Doubao setup):**
```toml
# ========================================
#   Codex 豆包大模型配置
# 通过本地 LLM Gateway 访问火山引擎豆包
# ========================================

# Default model - Doubao code-specialized model (RECOMMENDED)
model = "doubao-seed-2-0-code-preview"

# Provider setup
[provider]
name = "custom"
base_url = "http://127.0.0.1:18888/openai/v1"  # API root — Codex adds /responses and /models
wire_api = "responses"

# Available models (via Gateway → Volcengine Agent Plan)
models = [
  # ===== 豆包系列 (推荐) =====
  "doubao-seed-2-0-code-preview",    # ✅ 代码专用（默认，最佳选择）
  "doubao-seed-2-0-pro",              # ✅ 通用Pro（思考强，推理好）
  "doubao-seed-2-0-lite",             # 🚀 轻量版（速度快）
  
  # ===== DeepSeek 系列 =====
  "deepseek-v4-pro",                  # 🧠 通用最强
  "deepseek-v4-flash",                # ⚡ 快速版
  
  # ===== GLM 系列 =====
  "glm-5.2-pro",                      # 📚 智谱清言
]

# Sandbox permissions
[sandbox]
permissions = [
  "disk-full-read-access",
  "network-full-access",
  "shell-full-access",
]

# Shell environment
[shell_environment_policy]
inherit = "all"

# Feature toggles
[features]
web_search = true
mcp = true
plugins = true
vision = true  # Enable vision for Doubao models

# ========================================
# Vision model config (for image analysis)
# ========================================
[vision]
model = "doubao-seed-2-0-pro"  # Vision-capable model
max_images = 10

# ========================================
# Model aliases (quick switching)
# ========================================
[model_aliases]
code = "doubao-seed-2-0-code-preview"  # Default, code-focused
pro = "doubao-seed-2-0-pro"            # Strong reasoning
lite = "doubao-seed-2-0-lite"          # Fast responses
ds = "deepseek-v4-pro"                  # DeepSeek general-purpose
flash = "deepseek-v4-flash"            # DeepSeek fast
glm = "glm-5.2-pro"                     # GLM long-context
```

**Quick switch examples:**
```bash
# Default (code model)
codex

# Pro reasoning mode
codex -m pro

# With images (vision analysis)
codex -i /path/to/screenshot.png

# Using aliases
codex -m code    # Code model
codex -m lite    # Fast mode
```

**Model capabilities:**
- `doubao-seed-2-0-code-preview` — 262K context, code-focused, text-only
- `doubao-seed-2-0-pro` — 1M context, strong reasoning, vision support
- `doubao-seed-2-0-lite` — 1M context, fast responses, cost-effective
- `deepseek-v4-pro/flash` — 1M context, pure text (no vision)
- `glm-5.2-pro` — 1M context, vision support, long document processing

### Codex Config Path Pitfalls — 2026-07-13 Findings

**Critical discoveries when configuring Doubao models:**

1. **Codex IGNORES $HOME variable** — It always reads config from `/Users/hua/.codex/config.toml` (hardcoded user home). When running under a different Hermes profile (e.g. `zhenglishi`), the profile's home `.codex/` is **completely ignored**. Update the real user home config only.

2. **`[features].plugins` must be boolean, NOT an array** — This is the #1 silent config parse failure:
   ```toml
   # ❌ WRONG — causes: "invalid type: string browser, expected a boolean"
   [plugins]
   enabled = ["browser", "github", "computer-use"]

   # ✅ CORRECT — plugins enabled is a single boolean flag
   [features]
   plugins = true
   ```
   Plugin auto-discovery works from marketplace cache directories — the `[plugins]` table with array is deprecated.

3. **Config cached in SQLite** — After config changes, clear state caches to ensure changes take effect:
   ```bash
   rm -f ~/.codex/state_5.sqlite*
   rm -f ~/.codex/goals_1.sqlite*
   rm -f ~/.codex/memories_1.sqlite*
   rm -f ~/.codex/logs_2.sqlite*
   ```
   Otherwise Codex may continue using cached provider settings.

4. **`base_url` must be the API root** — Codex automatically appends `/responses` and `/models` to it. The `/models` endpoint is called for reachability health check. So:
   ```toml
   # ❌ WRONG: base_url includes /responses — Codex will call /responses/responses
   base_url = "http://127.0.0.1:18888/openai/responses"

   # ✅ CORRECT: API root with /v1 suffix — Codex calls /v1/models and /v1/responses
   base_url = "http://127.0.0.1:18888/openai/v1"
   ```
   The LLM Gateway must handle both `/openai/v1/models` (for health check) and `/openai/v1/responses` (for actual calls).

5. **How to verify provider is actually used:**
   - Run `codex doctor` and check `model provider` / `openai API base URL` lines
   - If it still shows `https://api.openai.com/v1`, your provider config is being ignored
   - Check the LLM Gateway log — if no requests come in, Codex isn't using your base_url
   - Verify with `curl http://127.0.0.1:18888/openai/v1/models` directly first

### Desktop Chinese Locale (华哥's machine)

For a full Chinese interface, add to `~/.codex/config.toml`:

```toml
[desktop]
dock-icon-preference = "app-default"
localeOverride = "zh-CN"         # Chinese menus, settings, labels
followUpQueueMode = "queue"

[agent]
language = "zh-CN"
instructions = "用中文回复，代码注释用英文"
```

The `localeOverride = "zh-CN"` switches Desktop app UI to Chinese. The `[agent]` block ensures Codex's internal agent responds in Chinese. Combined with `~/.codex/AGENTS.md` ("中文为主"), this gives a fully Chinese experience — English CLI commands, Chinese agent responses and UI.

## One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Project Optimization Workflow (调研 → 任务 → 执行 → 验证)

"用 codex 优化项目"类任务的标准 4 步循环，每步验证通过后再走下一步：

1. **调研现状（自己做，不交给 codex）**：读关键源码、查运行端口（`lsof -nP -iTCP:PORT -sTCP:LISTEN`）、看 docker 状态、grep 假数据标记（`mock\|假数据\|占位\|placeholder`）。定位**具体**问题（例：OpenClaw Bridge `/cmd` 只入队不执行）。先搞清"哪里是假的/不可用"再派活。

2. **任务描述写文件，避免 shell 转义**：中文 + 引号/冒号/反引号直接塞 `codex exec "长串"` 必踩转义坑。用 write_file 写 `/tmp/codex_task.txt`，再 `codex exec --sandbox workspace-write "$(cat /tmp/codex_task.txt)"`。任务描述自包含（背景现状 + 具体改动点 + 明确要求 + 验证命令 + 报告格式），一次只给一个聚焦小任务，别一次派大活。

3. **长任务 background + notify**：codex exec 写代码约 1-3 分钟，用 `background=true, notify_on_complete=true`，再 `process(action="wait", timeout=240)` 阻塞收结果。

4. **验证 codex 产出（self-report 不可信）**：codex 报告"完成"≠真实完成。必须实测：读改动文件确认逻辑落地、`python3 -c "import ast; ast.parse(...)"` 语法、实际启动服务 + curl 健康检查。分步验证通过再派下一个任务。

Pitfall：codex 改正式项目时，工作区常有历史未提交改动，codex 会叠加其上。验证前先 `git status --short` 确认本次改动范围，别把历史遗留当成本次产出误判。

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## Multi-Step Optimization Tasks (多步优化任务)

When delegating a multi-step code-optimization task to Codex (e.g. "optimize this system, replace fake components, wire up a fallback"):

1. **调研现状 first** — read the architecture docs and the actual code yourself, identify what's fake/unusable/placeholder. Don't hand Codex a vague "improve this" — give it a precise list of concrete problems (e.g. "openclaw_bridge.py `/cmd` only appends to a list and returns 'queued', never executes").
2. **写任务描述到文件** — write the self-contained prompt via `write_file` to `/tmp/codex_task.txt`, then run `codex exec "$(cat /tmp/codex_task.txt)"`. This avoids shell-quoting hell with Chinese + special chars + newlines. Verified pattern (2026-08-16): 2 sequential optimization tasks completed cleanly this way.
3. **任务描述四段式** — (a) 背景 (b) 现状问题清单 (c) 具体任务+文件路径 (d) 要求/验证命令. Self-contained so Codex completes without follow-up questions.
4. **background=true + notify_on_complete=true** — a real code task takes 1-3 min; don't block. Poll with `process(action="wait", timeout=240)`.
5. **验证产出，别信 self-report** — Codex's final summary is a SELF-REPORT. After it finishes, independently verify: `stat` the files it claims to have created, `read_file` the key changed function to confirm the logic actually landed, actually start the service and `curl` its health/error endpoint. Same rule as subagent delegation.
6. **冒烟测试 first** — before a big task, run `codex exec --sandbox read-only --skip-git-repo-check "用一句话中文回答:..."` and check output shows `tokens used` > 0 — proves Codex reaches the LLM before you burn a full task on it.
7. **改动范围隔离** — tell Codex explicitly "只新增 X 文件 + 重命名 Y 为 .bak，不碰其他文件"; afterwards `git status --short` to confirm the diff is only what you asked for (working tree may already have unrelated uncommitted changes — don't attribute them to Codex).

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--sandbox workspace-write` | ✅ Current — sandboxed, auto-approves workspace writes |
| `--sandbox read-only` | Read-only sandbox (safe review) |
| `--sandbox danger-full-access` | No sandbox, full access (dangerous) |
| `--search` | Enable live web search (native Responses `web_search` tool) |
| `-m <model>` | Override model for this session |
| `-C <dir>` | Set working directory |
| `-p <profile>` | Layer a profile config on top |
| `--full-auto` | ⚠️ Deprecated, use `--sandbox workspace-write` instead |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

## Workspace Preparation (Batch Repos)

When the user asks Codex to explore, analyze, or work on **multiple repos at once**, prepare a workspace first. See `references/workspace-preparation.md` for the full pattern:

- Parallel background clones with `--depth 1`
- Handling 404 repos (wrong org/repo name)
- Verification and common pitfalls

```bash
# Quick reference: batch clone into a workspace
mkdir -p ~/codex-workspace
# Then clone each repo in parallel with background=true
```

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Pitfalls

1. **Daily maintenance: plugin list is empty when not logged in** — `codex plugin list` returns "No marketplace plugins found" without OpenAI login. This is normal behavior, NOT an error. The 16 plugins are cached and work fine, they just won't show up in the list until marketplace auth works.
2. **npm path mismatch warning in codex doctor** — Running codex is at `/Users/hua/.local/lib/node_modules/@openai/codex` but npm global root is `/usr/local/lib/node_modules/@openai/codex`. This causes "would update a different install" warning. Use the local prefix install method to upgrade safely.
3. **GitHub sync has TWO scripts** — `~/6-产品研发/22-出图智能体训练/sync_codex_repo.sh` is a local-only legacy script (no remote configured, saves to `~/codex-workspace/`). For actual GitHub push, use `~/.hermes/scripts/codex_github_sync.sh` which targets `/tmp/yuxin-skills-codex-sync/` with the pre-configured `git@github.com:openclaw-cn-dev/yuxin-skills.git` remote. The cron task should run the hourly sync script after version/plugin checks, not the legacy local script.
4. **Config path is hardcoded to user home** — Codex ignores `$HOME` and always reads from `/Users/hua/.codex/config.toml`. Profile-specific `.codex/` directories (e.g. under `~/.hermes/profiles/`) are completely ignored. **Note (2026-08-13): `~/.codex` is now a symlink → `/Users/hua/系统文件夹/Codex/`** (mirrors the Claude Code migration). The hardcoded path string is unchanged, so Codex still works through the symlink transparently — same pattern as `~/.claude`. Ops scripts (`codex_self_evolution.py`, `switch_model.py`) reference `/Users/hua/.codex/...` and are unaffected.
5. **`[plugins].enabled` must be boolean** — An array like `["browser", "github"]` causes silent parse failure: "invalid type: string browser, expected a boolean". Use `[features].plugins = true` instead.
6. **Always clear SQLite caches after config changes** — `rm -f ~/.codex/state_5.sqlite* ~/.codex/goals_1.sqlite* ~/.codex/memories_1.sqlite* ~/.codex/logs_2.sqlite*`. Otherwise old provider settings persist.
7. **ACP NOT supported (v0.144.1)** — The `--acp` flag does not exist. `delegate_task(acp_command="codex")` will fail with "unexpected argument '--acp'". Use `terminal(command="codex exec ...", pty=true)` instead for Hermes→Codex delegation.
8. **Skills context budget** — Codex caps skill descriptions at 2% of context. With 250+ skills in the Hermes ecosystem, all skill descriptions are dropped. For tasks requiring specific skills, reduce context by using `--ignore-rules` or running in a minimal profile.
9. **DeepSeek cannot process images (input or output)** — DeepSeek V4 Pro and Flash are text-only. No vision input (can't see images), no image generation. For visual tasks: switch to `doubao-seed-2-0-pro-260215` (vision input) or `glm-5.2` (vision + text). For image *generation*, only `seedream-4.0-250828` works on Volcengine but requires separate API setup. See `references/volcengine-model-capabilities.md` for the full capability matrix.
10. **`***SECRET***`** replaces deprecated `--full-auto` for fully automated runs. Combined with `-C <workdir>` sets the working directory.
11. **Always use `pty=true`** when running Codex via Hermes terminal — it's an interactive app and hangs without PTY.
12. **Gateway SSE `input_tokens` missing field** — When the Gateway's `build_sse_response_completed` receives an empty `usage` dict from Volcengine (common when the API doesn't include usage in the final SSE chunk), the `response.completed` event has `"usage": {}` which Codex fails to parse with `missing field 'input_tokens'`. **Fix**: Always initialize `normalized_usage` with defaults `{"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}`, and also accept `input_tokens`/`output_tokens` as alternative field names (Volcengine sometimes uses these instead of `prompt_tokens`/`completion_tokens`). See `references/gateway-input-tokens-fix.md`.
13. **Volcengine model name must include suffix** — When using `codex exec -m <model>`, the Volcengine Agent Plan model name must be the full name including the `-260425` suffix (e.g. `deepseek-v4-pro-260425`). The short name `deepseek-v4-pro` gets parsed as `4-pro` by Codex's model resolution and fails. The `-260425` suffix model name only works via Volcengine (not DeepSeek direct).
14. **base_url health check calls `/models`** — Codex verifies provider health by calling `GET <base_url>/models` before making any actual request. Your LLM Gateway must return a valid (non-404) response for this endpoint, otherwise `codex doctor` shows reachability failure and Codex may refuse to use your provider.
15. **npm install can timeout (observed 2026-07-17)** — The codex package is large and npm registry access from China can be slow. The `--prefix` install method sometimes hangs after 120s. **Fallback**: run `cd /Users/hua/.local && npm install @openai/codex --no-save` first (48s in our test), then retry the global-with-prefix command. The local install without `-g` is faster and doesn't modify symlinks.
16. **Codex overwrites config.toml on restart** (2026-07-17) — The ChatGPT desktop app regenerates `~/.codex/config.toml` on startup, reverting any manual model/base_url changes back to volcengine defaults. **Workaround**: (a) Kill all Codex/ChatGPT processes FIRST (`pkill -9 -f Codex; pkill -9 -f ChatGPT`), (b) Make config changes while Codex is dead, (c) Verify with `head -16 ~/.codex/config.toml | grep -E "model|base_url|name|requires"`, (d) Keep a backup at `~/.codex/config.toml.correct` for fast recovery. **Warning**: NEVER edit config.toml while Codex is running — it will be overwritten on next save/restart and your changes will be lost silently.
17. **CC Switch proxy overrides model silently** (2026-07-17) — When Codex routes through CC Switch (port 15721), the proxy's internal model mapping overrides whatever you set in config.toml. Even with `model = "deepseek-v4-pro"`, the actual API call uses the CC Switch's stored model (e.g., `deepseek-v4-flash-260425`). **Diagnostic**: the request ID prefix tells you where the request actually went — `02178...` = Volcengine, UUID format = DeepSeek. **Fix**: bypass CC Switch by setting `base_url` to the Hermes LLM Gateway (`http://127.0.0.1:18888/openai`) and killing CC Switch (`pkill -9 -f "CC Switch"`). Also remove `requires_openai_auth = true` and `experimental_bearer_token` — these are CC Switch artifacts.
18. **model_catalog_json overrides config.toml model** (2026-07-17) — The `model_catalog_json` setting points to `~/.codex/arkcli.models.json` (or `cc-switch-model-catalog.json`). Entries in this file have `slug` and `display_name` fields. **The `slug` value, NOT config.toml's `model`, is what Codex sends to the API.** If `slug` is `deepseek-v4-flash-260425` but config.toml says `deepseek-v4-pro`, the API receives the slug value. **Fix**: either (a) remove the `model_catalog_json` line from config.toml entirely, or (b) update the slugs in the catalog JSON to match valid model names. **Pitfall**: the catalog JSON persists across restarts and can cause "model name not supported" errors even when config.toml looks correct.
19. **`base_url` must NOT end with /v1 for Responses API** (2026-07-17) — When `wire_api = "responses"`, Codex automatically appends `/v1/responses` to the base_url. If base_url is `http://127.0.0.1:18888/openai/v1`, the final URL becomes `.../openai/v1/v1/responses` (double /v1). **Fix**: use `base_url = "http://127.0.0.1:18888/openai"` — Codex will call `.../openai/v1/responses` correctly. This differs from the chat_completions API where `/v1` in base_url is conventional.
20. **`codex plugin list` 显示 "not installed" 不代表插件缺失**（2026-08-04 实测）— cron 上下文无 OpenAI OAuth 凭据时，`plugin list` 返回的 status 是**相对于 marketplace 的 install state**（始终为 "not installed"），不是 cache 中的实际存在性。**真实插件状态必须用 `ls ~/.codex/plugins/cache/` 验证**：
    ```bash
    # 跨 4 个 cache 目录验证（共 17 个插件）
    for d in ~/.codex/plugins/cache/*/; do
      echo "$(basename $d): $(ls $d | wc -l) 个 — $(ls $d | tr '\n' ' ')"
    done
    # openai-api-curated: 7 个 — build-web-apps coderabbit figma github linear sentry superpowers
    # openai-bundled: 4 个 — browser chrome computer-use visualize
    # openai-primary-runtime: 5 个 — documents pdf presentations spreadsheets template-creator
    # sisyphuslabs: 1 个 — omo
    ```
    升级 Codex 后不要因为 `plugin list` 显示全部 "not installed" 就误报"插件丢失" — 只要 cache 目录还在就没问题（v0.144+ 自动发现机制）。
21. **Browser/chrome/computer-use plugins need a VISION-capable model** — The plugins load from cache and appear in the plugin list, but they are effectively useless with text-only models (MiniMax-M2.7, DeepSeek). The model must be able to process screenshots and page snapshots. Current options: `doubao-seed-2-0-pro` (volcengine, vision), `glm-5.2-pro` (vision), or OpenAI GPT-4o (needs proxy). **Diagnose**: if Codex browser tasks seem to run but produce nonsense results, check `grep '^model' ~/.codex/config.toml` — if it's MiniMax or DeepSeek, the model literally cannot see the page.

22. **CLI and Desktop app share the same `~/.codex` state store** (2026-08-13) — The Codex CLI and the Codex/ChatGPT desktop app are the *same engine* reading/writing one shared state directory, so CLI-run sessions DO appear in the desktop app (and vice-versa). Shared store: `session_index.jsonl` (session list), `sessions/` + `archived_sessions/rollout-*.jsonl` (transcripts), `state_5.sqlite` / `goals_1.sqlite` / `memories_1.sqlite` / `logs_2.sqlite`. Sync is **persist-then-visible, NOT real-time** — a CLI session only shows in the desktop app after it finishes, flushes to disk, and the app refreshes/restarts. `memories_1.sqlite` is shared too, so memories formed in a CLI task carry into the desktop app. The desktop app's own `~/Library/Application Support/Codex/` is just Electron/Chromium UI cache (Cookie, Crashpad, SingletonSocket) — no conversation content lives there.

23. **Desktop Computer Use PiP 崩溃循环（SkyComputerUseService 僵尸进程堆积）** — ChatGPT/Codex 桌面端（实测 26.810.41047）每 ~1.6s 启动一个 `SkyComputerUseService` 进程，连不上 OpenAI 云端（国内被墙）→ bootstrap 失败 → 无限 reconnect → 进程堆积到几百个 → V8Worker OOM（SIGABRT，栈顶 `node::OOMErrorHandler`）→ 桌面端崩溃重启循环。**诊断**：`log show --predicate 'processImagePath CONTAINS "ChatGPT"' | grep "CUAService bootstrap failed"`；崩溃日志 `.ips` 崩溃线程名 = `V8Worker`。**这是 OpenAI 已知 bug**（社区帖 1389210）。**Workaround**：`[desktop] ***SECRET*** = true`（26.730 有效，26.810 疑似回归未完全生效）。禁用插件 / 重命名 .app 均无效（桌面端从 bundled-marketplaces 缓存重建）。**解决**：用 Codex CLI 或降级桌面端到 26.803.41515。完整诊断手册见 `references/computer-use-pip-crash-loop.md`。

no conversation content lives there.

23. **Codex desktop 26.810 双故障：model_provider 被重写 + computer_use PiP 崩溃循环** (2026-08-14) — 两个独立问题叠加，症状分别是「不能新建项目」和「一直重启报错」：
  * ①「不能新建项目」= desktop 重写 `~/.codex/config.toml` 把 `model_provider` 改成 `"deepseek"`（新增 `[model_providers.deepseek]` 段指向 `https://api.deepseek.com/` + `wire_api="responses"`），但 **DeepSeek 官方 API 不支持 Responses 协议**（只有 `/chat/completions`）且那个 token 实测 401 → 新建项目时模型调用失败。修复：`model_provider` 改回 `"custom"`、`base_url` 改回 hermes_gateway(`http://127.0.0.1:18888/openai`)、`requires_openai_auth = false`。验证：`codex exec` 跑出 `tokens used > 0`（真调通，不是假阳性）。
  * ②「一直重启报错」= ChatGPT/Codex desktop 26.810.41047 on macOS 反复崩溃(SIGABRT, 崩溃线程 `V8Worker`, `node::OOMErrorHandler`)，根因是 Computer Use「画中画(PiP)」功能每 ~1.6s 启动一个 `SkyComputerUseService` 进程，连不上 OpenAI 云端(中国网络被墙) → `RemoteHostedPIPContent CUAService bootstrap failed` → 无限 reconnect → 进程堆积到 200~450 个 → 内存耗尽 → OOM 崩溃循环。**正确禁用方法是 feature flag，不是插件开关**：config.toml 的 `[features]` 段加 `computer_use = false`（snake_case）。三个无效/不足的做法：① `[plugins."computer-use@openai-bundled"] enabled = false` 无效(管插件，管不住 desktop 内置 PiP)；② 物理隔离 `~/.codex/computer-use/Codex Computer Use.app` 无效(desktop 会从 bundled 源重建)；③ 旧 workaround `[desktop] ***SECRET*** = true` 在 26.810 无效(社区帖 1389210 的 26.730 时代方案)。验证：`codex features list | grep computer_use` 应显示 false；重启 desktop 后 `ps aux | grep SkyComputerUseService` 数量稳定 0-1 个(PID 不变)而非每 15s 涨 50+。禁用 computer_use 不影响代码能力(CLI exec 照常)。排查崩溃日志：`ls -lt ~/Library/Logs/DiagnosticReports/ChatGPT*.ips`，用 python 读 `.ips`(首行 header + JSON body)看 `faultingThread` + `asi`(OOM 会显示 `node::OOMErrorHandler`)；系统日志线索：`log show --last 30m --predicate 'processImagePath CONTAINS "ChatGPT"' | grep "CUAService bootstrap failed"`。已知 bug 参考：OpenAI 社区 1389210、GitHub openai/codex#20683。**同一次会话还发现 desktop 重写 config.toml 会把 `model_provider` 从 `custom`(hermes_gateway) 改成 `deepseek`(官方 API `https://api.deepseek.com/`)，而 DeepSeek 官方不支持 `wire_api="responses"`(只有 chat/completions)，导致「不能新建项目」**。修复：改回 `model_provider = "custom"` + `[model_providers.custom] base_url = "http://127.0.0.1:18888/openai"` + `requires_openai_auth = false`。诊断佐证：`curl -X POST https://api.deepseek.com/chat/completions` 返回 401（token 失效）且该官方端点无 `/responses` 路由。

24. **前台 codex exec 超时会被 Hermes 守卫拦截，禁止原地重试**（2026-09-04 实测）— 大 prompt 的 `codex exec`（如长方案/文档生成）在前台跑满 600s 超时后，Hermes 把整条命令标记为 BLOCKED（"user has NOT consented… do NOT retry this command, do NOT rephrase it"），**原地重跑/换说法重跑都会被拒**。处置顺序：
    1. 先 `ls` 检查产物是否已落盘——超时 ≠ 没写出文件，别盲目重做
    2. 预期 >5 分钟的 codex 任务从第一步就用 `background=true, notify_on_complete=true`（见 Multi-Step #4），不要赌前台
    3. 交付物是文档/方案类（.md）时，被拦截后直接自己写完落盘——代码铁律只覆盖代码/脚本/工具（yuxin-code-iron-law 豁免条款），为"必须走 Codex"卡死整个任务没有意义；Codex 留给真正的代码阶段

25. **清理"孤儿"进程前必查 PPID**（2026-09-04 实测）— codex exec 超时后排查进程，会看到 `npm exec open-websearch / exa-mcp-server / @upstash/context7` 这类 MCP 进程，容易误判为 codex 的孤儿子进程去杀。实测它们的父进程是 `claude --settings /var/folders/.../claude_*.json` —— 即 **Hermes 当前会话自己的运行时**，杀了等于拆掉自己会话的 MCP 基础设施。规则：杀任何进程前先 `ps -o pid,ppid,etime,command -p <pid>` 看父进程链；PPID 指向 `claude --settings` / Hermes 运行时的一律不碰。

## Remote Reachability Check (run before recommending Codex)

华哥's setup (observed 2026-06-28): Codex CLI 0.135.0 was installed and authenticated, but `https://api.openai.com` returned `HTTP 000` (firewall block). Running `codex exec` from the shell just hangs with no error output. **Always check reachability first** — 30-second diagnostic saves a 5-minute "why is it hanging" round-trip:

```bash
# 30-second reachability + auth check
which codex && codex --version          # 1: is it installed?
codex login status                       # 2: is it authenticated?
curl -sS --max-time 5 -o /dev/null \
  -w "HTTP=%{http_code} time=%{time_total}s\n" \
  https://api.openai.com/v1/models       # 3: is the endpoint reachable?
# HTTP=000 → firewall block, Codex is unusable for cloud calls
# HTTP=401 → reachable, just no API key
# HTTP=200 → fully working
```

If remote is blocked, fall back to **`codex --oss --local-provider ollama exec '...'`** — assumes `qwen2.5-coder:7b` is pre-installed via `brew install ollama && ollama pull qwen2.5-coder:7b`. ~26s per call, but works fully offline. First launch with `--oss` may need `--skip-git-repo-check` and a trusted directory configured.
