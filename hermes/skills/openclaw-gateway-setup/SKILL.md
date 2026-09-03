---
name: openclaw-gateway-setup
description: "Install, configure, verify, and recover the OpenClaw AI gateway on macOS (launchd-based background service). Covers first-time setup, launchd daemon configuration, file-descriptor limit workarounds, gateway crash recovery (launchctl exit -15, EMFILE, unreachable), switching the default LLM, registering a provider/model not in the built-in catalog, SecretRef-based API key injection from env files, and end-to-end inference verification."
version: 1.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [openclaw, gateway, setup, llm, launchd, macos, recovery, EMFILE, daemon]
    related_skills: [hermes-agent, hermes-gateway-profile-ops]
---

# OpenClaw Gateway Setup

OpenClaw is an AI agent runtime from Nous Research (peer to Hermes Agent, Claude Code, OpenClaw). It runs as a launchd background service on macOS, listens on `127.0.0.1:18789`, and exposes a Dashboard + WebSocket API for agent turns.

> **本 umbrella 吸收了两个姊妹 skill（已归档到 `references/`）**：
> - `references/openclaw-launchd-macos.md` — launchd 守护进程配置（文件描述符限制、PATH 问题）。
> - `references/openclaw-gateway-recovery.md` — Mac mini 上 gateway 崩溃后的诊断与恢复流程（exit -15、EMFILE、unreachable）。
>
> Setup → Recovery → Verification 三阶段俱全，先看本 skill 主体，需要深入时按需下沉。

This skill documents the **complete first-time setup workflow** — install the service, register a model provider, attach an API key via SecretRef, and verify with a real inference call.

---

## When to Use This

- New Mac, no OpenClaw yet → walk through all 5 steps
- Existing OpenClaw gateway won't accept connections → "Common blockers" section
- Switching default model or adding a provider that isn't in the built-in catalog → steps 2-4
- Key gotcha: model registered but SecretRef unresolved → env section below

---

## Step 1 — Verify the binary, then install as a service

```bash
which openclaw                           # expect ~/.local/bin/openclaw or similar
openclaw --version                       # e.g. "OpenClaw 2026.5.2 (8b2a6e5)"
openclaw gateway install                 # registers ~/Library/LaunchAgents/ai.openclaw.gateway.plist
openclaw daemon status                   # expect "Runtime: running" + "Listening: 127.0.0.1:18789"
lsof -nP -iTCP:18789 -sTCP:LISTEN        # confirm port bound
```

If `Runtime: running` but **"Gateway port 18789 is not listening"** — the install succeeded but startup was blocked. See "Common blockers" → **`gateway.mode` missing**.

---

## Step 2 — Decide your provider + model

OpenClaw ships with a model catalog (Amazon Bedrock, Anthropic, OpenAI, OpenRouter, …). Built-in `minimax` / `minimax-cn` providers also exist but are pinned to old versions (M2.7) — for **M3 or any newer model**, register a custom provider.

| Decision | What to pick |
|----------|--------------|
| Protocol | OpenAI-compatible → `api: openai-completions` |
| Anthropic-compatible | `api: anthropic-messages` |
| Bedrock / Vertex | `api: bedrock-converse-stream` |
| Auth style | API key → `auth: api-key` · bearer token → `auth: token` · OAuth → `auth: oauth` |
| Model id string | Whatever the provider's API expects (e.g. `MiniMax-M3`, `claude-sonnet-4-6`) |

---

## Step 3 — Write provider + model + default-model in one batch

OpenClaw config = JSON at `~/.openclaw/openclaw.json`. Schema is introspectable:

```bash
openclaw config schema | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin),indent=2))" > /tmp/openclaw-schema.json
openclaw config schema | python3 -c "
import json,sys
s=json.load(sys.stdin)
def walk(o, path=''):
    if isinstance(o,dict):
        for k,v in o.items():
            p=f'{path}.{k}' if path else k
            if isinstance(v,dict):
                t=v.get('title','')+v.get('description','')
                if any(x in t.lower() for x in ['provider','model','default','primary']):
                    print(f'{p}  {t[:80]}')
            walk(v,p)
walk(s)" | head -30
```

Then write a batch JSON file (one operation per item, **field names**: `path` + one of `value` / `ref` / `provider`):

```json
[
  { "path": "models.providers.<id>.baseUrl",  "value": "https://api.example.com/v1" },
  { "path": "models.providers.<id>.apiKey",
    "ref": { "provider": "default", "source": "env", "id": "EXAMPLE_API_KEY" } },
  { "path": "models.providers.<id>.auth",     "value": "api-key" },
  { "path": "models.providers.<id>.api",      "value": "openai-completions" },
  { "path": "models.providers.<id>.contextWindow", "value": 200000 },
  { "path": "models.providers.<id>.maxTokens",    "value": 16384 },
  { "path": "models.providers.<id>.models",
    "value": [ { "id": "<model-id>", "name": "<model-id>",
                 "api": "openai-completions",
                 "contextWindow": 200000, "maxTokens": 16384,
                 "input": ["text"] } ] },
  { "path": "agents.defaults.model", "value": "<id>/<model-id>" }
]
```

Apply:

```bash
openclaw config set --batch-file /tmp/openclaw-batch.json --dry-run   # validate first
openclaw config set --batch-file /tmp/openclaw-batch.json             # write (auto-backup → *.bak)
openclaw config validate                                             # confirm green
```

The original file is sha256-hashed and copied to `openclaw.json.bak` on every write. Reverting = `mv openclaw.json.bak openclaw.json`.

**Pitfall — `gateway.mode` missing.** A fresh install leaves `gateway.mode` unset → gateway runs but won't listen. Symptom in `daemon status`: "Gateway start blocked: existing config is missing gateway.mode". Fix:

```bash
openclaw config set gateway.mode local
openclaw daemon restart
```

---

## Step 4 — Inject API key (the part most people skip)

OpenClaw runs as a **separate launchd daemon** — it does NOT inherit keys from your interactive shell. Three options, pick by sensitivity:

### A. `env.vars` block — explicit, lives in openclaw.json

```json
{ "path": "env.vars.MY_API_KEY", "value": "sk-real-key-here" }
```

Pros: visible, no shell dependency. Cons: key is on disk (OpenClaw redacts the value when re-reading with `config get`, but the raw value is still in the file — protect with file permissions).

### B. `env.shellEnv.enabled = true` — load your shell profile at startup

```json
{ "path": "env.shellEnv.enabled",   "value": true },
{ "path": "env.shellEnv.timeoutMs", "value": 10000 }
```

Pros: keys live in `~/.zshrc` / `~/.bash_profile` / `~/.hermes/.env`. Cons: heavier startup, can fail in locked-down environments.

### C. SecretRef — pointer to an env var, resolved at call time

```json
{ "path": "models.providers.<id>.apiKey",
  "ref": { "provider": "default", "source": "env", "id": "MY_API_KEY" } }
```

Pros: no plaintext in config. Cons: requires the env var to be present in the daemon's process environment — combine with option A or B to actually populate it.

**渔芯 pattern (recommended)** — combine B + C:
1. Put the key in `~/.hermes/.env` (already where all other API keys live)
2. Enable `env.shellEnv` so OpenClaw's daemon imports it
3. Use SecretRef for the `models.providers.<id>.apiKey` so the key never lands in `openclaw.json`

**Verify a SecretRef resolves:**

```bash
# In your interactive shell (where .env is sourced):
openclaw config set --batch-file batch.json --dry-run
# If this fails with "SecretRefResolutionError: Environment variable ... is missing",
# the daemon will hit the same error. Fix the env injection before retrying.
```

---

## Step 5 — Verify with a real inference call

Don't trust "Runtime: running" alone — the gateway can be up while the model is unreachable. Run a one-shot:

```bash
openclaw capability model run \
  --model <provider-id>/<model-id> \
  --prompt "Reply in one sentence: what is your model name?"
# Expect: a coherent answer that names the model you configured.
```

Inspect the catalog your config produced:

```bash
openclaw capability model list 2>&1 | grep -i "<model-id>"
openclaw capability model providers | grep -i "<provider-id>"
```

If the model doesn't appear in the list, your batch write missed something — re-run `openclaw config validate` and look for which field is empty.

---

## Common blockers

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| `Runtime: running` but `Listening: ❌` | `gateway.mode` not set | `openclaw config set gateway.mode local && openclaw daemon restart` |
| `Service not installed. Run: openclaw gateway install` | First-time install never happened | `openclaw gateway install` |
| `SecretRefResolutionError: env X missing` | Daemon process doesn't see your shell env | Enable `env.shellEnv` and put the key in `~/.hermes/.env` or similar |
| `error: unknown command 'invoke'` | CLI verb is `run`, not `invoke` | `openclaw capability model run --model ... --prompt ...` |
| `--dry-run` fails with redacted ref | `--dry-run` runs in current shell, can't see daemon-only env vars | Skip `--dry-run`, do real write, then `config validate` |
| Inference returns 401 | API key wrong, or `auth: token` set when endpoint expects `api-key` header | Check provider docs; `auth: api-key` → `Authorization: Bearer …` for most OpenAI-compat endpoints |
| Inference returns 404 / unknown model | Wrong `models.providers.<id>.models[].id` — must match what the upstream API expects exactly | Look up the exact id in provider's `/v1/models` listing |

---

## Quick command reference

```bash
# Service lifecycle
openclaw gateway install         # one-time setup
openclaw daemon start|stop|restart|status|uninstall

# Config introspection
openclaw config file             # prints active config path
openclaw config schema            # full JSON schema (huge — pipe through head/jq)
openclaw config get <dot.path>    # e.g. agents.defaults.model
openclaw config set <path> <val>  # single op, or --batch-file for many
openclaw config validate          # parse + schema check

# Inference verification
openclaw capability model list              # all catalog models
openclaw capability model providers         # per-provider status (configured/selected)
openclaw capability model inspect <model>   # one entry detail
openclaw capability model run --model <provider>/<model> --prompt "..."

# Diagnostics
openclaw doctor
openclaw status
tail -50 ~/.openclaw/logs/gateway.log
tail -50 ~/.openclaw/logs/gateway.err.log
```

---

## OpenClaw vs Hermes config — what transfers, what doesn't

If you've already configured Hermes for the same provider, you can **reuse**:
- The API key value (from `~/.hermes/.env`)
- The base URL
- The model id string

But you **must re-register** in OpenClaw — its `models.providers.*` catalog is independent of Hermes's `custom_providers.*`. They don't share.

The pattern that maps most cleanly between the two systems:

| Hermes | OpenClaw | Notes |
|--------|----------|-------|
| `custom_providers[0].models["M3"]` | `models.providers.<id>.models[].id` | Both: catalog entry |
| `custom_providers[0].base_url` | `models.providers.<id>.baseUrl` | |
| `custom_providers[0].api_key` (env ref) | `models.providers.<id>.apiKey` (SecretRef) | Same idea, different syntax |
| `model.default` | `agents.defaults.model` | Format: `"provider/model"` |
| `auxiliary.X.model` | `agents.defaults.X` (per-task sub-blocks) | |

---

## Configuration Core Patterns (核心模式) — merged from openclaw-config-setup

These are the deeper config-mechanism insights that don't fit neatly into the 5-step install workflow above but consistently trip people up once they're past the first install.

### Key file locations (where each setting actually lives)

| File | Purpose | Who manages it |
|------|---------|----------------|
| `~/.openclaw/openclaw.json` | Main config (model catalog, agent defaults, gateway behavior) | openclaw CLI |
| `~/.openclaw/agents/<agent>/agent/auth-profiles.json` | Credentials (profile+key+baseURL) | OpenClaw auto-managed |
| `~/.openclaw/agents/<agent>/agent/models.json` | Model catalog snapshot (may contain plaintext keys) | OpenClaw auto-generated |
| `~/.openclaw/service-env/<label>.env` | **OpenClaw's own independent env file** | openclaw CLI (created by `gateway install`) |
| `~/.openclaw/service-env/<label>-env-wrapper.sh` | Wrapper script that loads the env file | openclaw CLI auto-generated |
| `~/.openclaw/secrets/` | User-managed secrets dir (file provider target) | user-managed |

### Pitfall A — `gateway.mode` missing after install (also covered in Step 3)

`openclaw gateway install` only installs the launchd plist — **it doesn't listen on 18789 afterward** unless `gateway.mode=local` is set explicitly. The error log says:

```
Gateway start blocked: existing config is missing gateway.mode.
Treat this as suspicious or clobbered config. Re-run `openclaw onboard --mode local`
or `openclaw setup`, set gateway.mode=local manually, or pass --allow-unconfigured.
```

Always run `openclaw config set gateway.mode local && openclaw daemon restart` after a fresh install.

### Pitfall B — `auth-profiles.json` shadows `openclaw.json` SecretRefs

`openclaw secrets audit` may report `[REF_UNRESOLVED]` even while inference works fine. That's because **OpenClaw prefers `auth-profiles.json`**, ignoring the SecretRef in `openclaw.json`.

**Priority order:**
1. `auth-profiles.json` `profiles.<provider>` — highest, automatic
2. `openclaw.json` `models.providers.<id>.apiKey` SecretRef — second, often shadowed

For `openclaw.json`'s SecretRef to actually take effect, either delete the corresponding profile in `auth-profiles.json` or point both at the same key.

### Pitfall C — `models.json` plaintext keys auto-replaced with `'secretref-managed'`

When `openclaw.json` configures a SecretRef, OpenClaw **actively rewrites** `~/.openclaw/agents/<agent>/agent/models.json`:

```diff
- "apiKey": "sk-real-key..."
+ "apiKey": "secretref-managed"
```

This placeholder is a bare string — sending it to the API yields 401/1004 errors. If a file SecretRef reads from this file, **resolution returns the placeholder**, not the real key. So the `file` provider pointing at `models.json` is a dead end.

### Three SecretRef providers — which to pick

| Provider | When to use | How |
|----------|-------------|-----|
| `env` (source=env) | Key already in launchd/service env (Hermes mode) | `{"source":"env","provider":"default","id":"MINIMAX_CN_API_KEY"}` |
| `file` (source=file) | Key drops into OpenClaw's secrets dir | `{"source":"file","provider":"myprov","id":"value"}` + `secrets.providers.myprov.{source:file,path:~/.openclaw/secrets/key.txt,mode:singleValue}` |
| `exec` (source=exec) | Read from 1Password/Bitwarden/Vault | Configure `secrets.providers.<name>.command` + `args` |

**Recommended for independent operation:** `file` provider with `mode=singleValue` + `id=value`, dropping the key into `~/.openclaw/secrets/<name>.txt` with mode 600. **Gotcha:** the Hermes security sandbox refuses to read `~/.hermes/.env`, so the terminal returns the key as `***` placeholder — you can't script the copy. You'll need to manually paste the key into OpenClaw's secrets file once.

**Easiest path:** just give OpenClaw its **own independent key in `auth-profiles.json`** (with a profile name you choose). It takes effect at OpenClaw startup without touching `openclaw.json`'s SecretRef at all.

### End-to-end verification — must go through the daemon path

```bash
openclaw capability model run --gateway --model <provider_id>/ModelName --prompt "一句话自我介绍"
```

Without `--gateway`, the local CLI path reads `auth-profiles.json` directly and reports "No API key found" even when the daemon would work fine. The `--gateway` flag forces it to read `openclaw.json`'s SecretRef via the daemon.

### launchd plist ↔ `openclaw.json` env injection relationship

`openclaw gateway install` generates a plist that looks like:

```xml
<key>ProgramArguments</key>
<array>
  <string>/Users/hua/.openclaw/service-env/<label>-env-wrapper.sh</string>
  <string>/Users/hua/.openclaw/service-env/<label>.env</string>
  <string>/usr/local/bin/node</string>
  <string>/Users/hua/.local/lib/node_modules/openclaw/dist/index.js</string>
  <string>gateway</string>
  <string>--port</string>
  <string>18789</string>
</array>
```

The plist doesn't inject env directly — it runs `env-wrapper.sh` first, then sources `ai.openclaw.gateway.env`. That `.env` declares `OPENCLAW_SERVICE_MANAGED_ENV_KEYS=<list>` so OpenClaw knows which keys it owns.

**User-exported env** (like `export XXX=***` in `~/.zshrc`) gets picked up implicitly when `env.shellEnv.enabled=true` triggers the login shell at startup — this is an **implicit source** that audits often miss. To sever the implicit dependency: set `env.shellEnv.enabled=false` in `openclaw.json`, or move the key entirely into OpenClaw's own `service-env/<label>.env`.

### Config diagnostic quick-reference

| Symptom | Root cause | Fix |
|---------|------------|-----|
| gateway install → port not listening | `gateway.mode` missing | `openclaw config set gateway.mode local` |
| inference 1004 / 401 | SecretRef resolves to `'secretref-managed'` placeholder | Check if auth-profiles.json shadows it, or read from an independent secrets file |
| `openclaw capability model run` → "No API key found" | CLI path doesn't read openclaw.json | Add `--gateway` to force daemon path |
| `secrets audit` shows plaintext but inference works | auth-profiles.json shadows openclaw.json SecretRef | This is by design, not a bug — go fully independent via auth-profiles.json |
| `daemon restart` hangs 60s without responding | file SecretRef resolution failing without fail-fast | kill the process + fix the file path/content + restart |
| `daemon status` → gateway.mode missing | install only registered the plist, didn't fill mode | `openclaw config set gateway.mode local` |

### Config-introspection commands worth memorizing

```bash
openclaw config file              # absolute config path
openclaw config schema            # full JSON schema (authoritative for field names)
openclaw config get <path>        # dot-path read (e.g. gateway.mode)
openclaw config set <path> <val>  # single-field set (supports --ref-provider)
openclaw config set --batch-file <json>  # batch write (preferred)
openclaw secrets audit            # plaintext / unresolved / priority issues
openclaw capability model list | grep <keyword>  # see builtin/registered models
openclaw daemon status            # gateway health + port listening
```

## Related skills

- `openclaw-launchd-macos` — launchd plist's PATH/EMFILE/KeepAlive details (runtime issues)
- `openclaw-gateway-recovery` — recovery workflow after a gateway crash

## Support files

- `templates/minimax-m3-batch.json` — drop-in batch JSON for `openclaw config set --batch-file`, ready to copy/paste. Includes the SecretRef + env.vars pairing + gateway.mode.
- `references/fishing-yu-workflow.md` — 渔芯 2026-06-22 实战记录：完整操作流水 + 6 个踩坑点 + 可复制验证清单 (gateway install + verify path).
- `references/openclaw-config-session-2026-06-22.md` — 渔芯 2026-06-22 config-mode session record (merged from `openclaw-config-setup`): 3 core pitfalls + 3 SecretRef providers + diagnostic table.