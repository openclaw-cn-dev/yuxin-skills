---
name: hermes-llm-endpoints
description: "Configure Hermes Agent to use a non-default LLM endpoint (custom proxy, mid-tier aggregator, OpenAI-compatible service). Covers the hardcoded provider base_url trap, the .env vs config.yaml distinction, probe-then-configure workflow, and the gateway restart requirement."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, llm, providers, configuration, custom-endpoint, openai-compatible, base-url]
---

# Hermes Custom LLM Endpoints

How to point Hermes Agent at an LLM endpoint other than the built-in providers' hardcoded URLs. Most relevant when the user has obtained an API key from a third-party proxy, aggregator, or self-hosted OpenAI-compatible service, and the built-in `minimax-cn` / `openai` / `anthropic` providers don't match.

## When to use this skill

Use this skill when ANY of the following:
- User has an `sk-...` style key from a non-standard provider
- User mentions a URL like `https://*.com/v1` that isn't in Hermes's built-in provider list
- `hermes chat -q "..."` returns 401/404/502 and the error message says the wrong endpoint or wrong key
- The user wants to switch from a paid official API to a cheaper proxy
- `hermes model` interactive picker has no option for the user's provider

Do NOT use this skill if:
- User is just changing models within the same provider — use `hermes model` or `hermes config set model.default <name>`
- User is using Nous Portal / OpenRouter / DeepSeek (these are built-in providers)
- User wants local Ollama — use the `ollama` provider, which is built-in

## The hardcoded provider base_url trap (CRITICAL)

Hermes's built-in providers (`minimax-cn`, `openai`, `anthropic`, etc.) have **hardcoded base URLs in the SDK code**. The `MINIMAX_BASE_URL` / `OPENAI_BASE_URL` / similar env vars do **NOT** override them at the agent loop level — Hermes reads the provider's hardcoded URL when constructing the request.

**Symptom:** `.env` says `MINIMAX_BASE_URL=https://my-proxy.com/v1` and `MINIMAX_CN_API_KEY=sk-xxx`, but requests still go to `https://api.minimaxi.com/v1` and return 401 ("login fail: API secret key invalid") because the proxy key is being sent to the wrong endpoint.

**Fix:** Switch to the generic OpenAI-compatible custom provider:

```bash
hermes config set model.provider custom
hermes config set model.base_url https://my-proxy.com/v1
hermes config set model.api_key sk-xxx-...
hermes config set model.default <model-id>
```

Then restart the gateway or start a fresh CLI session; `hermes config reload` is not a valid command, and running gateway/CLI processes read config at startup.


## Workflow: probe -> configure -> verify

**Never write credentials to .env based on a hunch.** Follow this sequence:

### 1. Probe the endpoint (1-3 second check, no side effects)

Run the bundled probe script:

```bash
python ~/.hermes/skills/devops/hermes-llm-endpoints/scripts/probe_endpoint.py \
  https://my-proxy.com/v1 sk-xxx-...
```

Status code meanings:
- exit 0, models listed -> real LLM proxy, key works
- exit 1, 401 -> endpoint up, key rejected (ask user for new key)
- exit 2, 404 -> wrong path, try `/api/v1/models` or other paths
- exit 3, `DNS_FAIL` -> **fake domain, abort immediately** (do not edit .env)
- exit 4, 5xx -> upstream unstable, retry 2-3 times before declaring dead

### 2. Verify the key with a minimal completion

Hit `/v1/chat/completions` with a tiny `ping` prompt to confirm the model id exists and the proxy can actually serve completions (not just list models).

### 3. Configure Hermes

Only after steps 1 and 2 pass, switch to the custom provider:

- `hermes config set model.provider custom`
- `hermes config set model.base_url https://my-proxy.com/v1`
- `hermes config set model.api_key sk-xxx-...`
- `hermes config set model.default <model-id>`

Do NOT also write the key to `.env` for this provider. The `model.api_key` in config.yaml is authoritative. Setting it in `.env` too creates two sources of truth and confuses the next agent that reads the file.

### 4. Verify end-to-end via CLI before restarting the gateway

```bash
hermes chat -q "answer with one digit: 1+1=?" -m <model-id>
```

If this returns the correct answer, the gateway will too — same config, same code path.

### 5. Restart gateway, then test via the messaging platform

If the gateway is installed as a service, restart it normally:

```bash
hermes gateway restart --profile <name>
```

If the gateway is **not** installed as a service and is being run manually, `hermes gateway restart` can stop the current process and then fail with "Gateway service is not installed". In that case, bring it back with a fresh manual run instead of assuming restart succeeded:

```bash
hermes gateway status
hermes gateway run
```

Then verify status/logs and send a real platform message:

```bash
hermes gateway status
tail -20 ~/.hermes/profiles/<name>/logs/gateway.log
```

Then send a real test message from the platform (Feishu DM, Telegram, etc.).

## Pitfalls

1. **Hardcoded provider base_urls** — see "The hardcoded provider base_url trap" above. This is the #1 reason custom endpoint configuration silently fails.
2. **Config changes don't propagate to running gateway** — the gateway process reads config at startup. After any `hermes config set` change, restart the gateway if it is installed as a service, or manually relaunch it if it is being run in foreground mode. A `hermes chat` test passing does not mean the gateway already updated.
3. **`hermes gateway restart` is service-oriented** — on machines where the gateway is running manually and has never been installed as a service, `hermes gateway restart` can successfully stop the current gateway and then fail with "Gateway service is not installed". Always follow with `hermes gateway status`; if it is not running, recover with `hermes gateway run`.
4. **The redaction-mask character in tool output** — when the agent reads a file or tool output that contains a redacted API key, the redacted form may use `***` characters. The `***` glob breaks bash heredocs, python `re` literals, and `write_file` content. Workaround: display the key as a fingerprint (`sk-71dd...a605`) and rebuild it in code via string concatenation (`'sk' + '-' + 'rest'`) instead of pasting the raw value. See `hermes-secret-handling` for the redaction layer.
5. **Fake-sounding model names** — names like "GPT-5.5" / "GPT-5.4" sound like fake models (they don't exist in OpenAI's official lineup as of 2026-01), but some real proxies do host them. Don't dismiss based on the name; verify by hitting `/v1/models`. Dismiss based on the **endpoint behavior** (DNS fail, 404, etc.).
6. **Boss-control / named profile `.env` vs root `.env`** — the root `~/.hermes/.env` is what the `custom` provider's `model.api_key` is read from (or directly from config.yaml). Named profile `.env` files are loaded for the gateway runtime env, not for the model config. If the agent edits the wrong file, the gateway will appear to start fine but the model will still use the old key.
7. **`hermes config set` is the only safe way to edit config.yaml** — direct `patch` / `sed` / `write_file` against `config.yaml` is rejected with "Refusing to write to Hermes config file: security-sensitive configuration." Use `hermes config set KEY VALUE` for all model config changes.
8. **Provider-specific model name conventions** — proxies often rename models. `gpt-4` on one proxy may be a different model entirely on another. Always cross-check by listing `/v1/models` and matching the id exactly (case-sensitive).
9. **First-call latency / cold upstream** — many proxies return 502 on the first request while the upstream connection warms up. If the first chat call 502s but `/v1/models` works, retry 1-2 times before declaring the provider broken.

## Backup and rollback

Always back up `.env` before changing credentials:

```bash
cp ~/.hermes/.env ~/.hermes/.env.bak.$(date +%Y%m%d_%H%M%S)
```

Rollback recipe: read the most recent backup with `read_file` (or `cat`), then write the original key value back via a python script using `.replace()` (not `re.sub()` — the mask character in some keys breaks regex). Always verify the restored key length matches the original.

## Verification checklist

After configuring a new endpoint, do these in order:

- [ ] `python probe_endpoint.py <url> <key>` returns exit 0
- [ ] `hermes chat -q "ping" -m <model>` returns 200 with content
- [ ] `hermes config show` shows `model.provider: custom` and the expected `base_url`
- [ ] `hermes gateway restart --profile <name>` succeeds
- [ ] `hermes gateway list` shows the profile running
- [ ] Tail the gateway log — should see the platform connection line ("feishu connected" / "telegram connected" / etc.)
- [ ] Send a test message from the messaging platform and confirm the response is on-topic (not an error / fallback)

## Files in this skill

- `references/moosecloud-cc.md` — specifics for moosecloud.cc (15 models, gpt-5.4 stable, gpt-5.5 upstream 502)
- `references/third-party-fastapi-llm-config.md` — **给 FastAPI 后端项目（不是 Hermes 自身）配 LLM key 的完整流程**（HG-小红书 → ZH-知乎 实战）：9 步 + minimax/DeepSeek/硅基流动/OpenRouter 配置模板 + @lru_cache() 陷阱 + Windows 端口占用 + DEBUG 开关 + 注册测试账号 + 流式响应验证
- `references/clone-and-rename-fastapi-project.md` — **克隆 + 改名 + 跑通整个 FastAPI 项目**（HG-小红书 → ZH-知乎 实战）：10 步流程（复制目录 → 批量改名 → 改 .env → Docker 镜像源 → PostgreSQL → venv → npm → 端口冲突 → DEBUG → 端到端验证），混合部署避开 docker.1ms.run 镜像残缺
- `scripts/probe_endpoint.py` — re-runnable endpoint probe (no credentials baked in, takes URL+key as args, returns typed exit codes)
