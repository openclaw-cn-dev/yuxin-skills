---
name: constrained-environment-deploy
description: Deploy and run backend services (FastAPI/Node/Python venv + Docker mix) on Windows hosts behind China-mainland network constraints (incomplete mirror sources, IPv6 port-binding quirks, Playwright missing browser binaries). Use when a deployment fails due to missing Docker images, uvicorn "address already in use" on Windows, Playwright Executable doesn't exist errors, or when you must orchestrate Docker + native venv because Redis/Node images aren't available in the local registry.
---

# Constrained-Environment Deploy (Windows + China Network + Partial Docker)

When the easy "docker compose up" path doesn't work, you build a **hybrid deployment**: Docker for the parts that have working images, native venv / Node for the rest. This skill records the reproducible playbook for that pattern.

## When to use

- A `docker compose up` is failing because a required image (Redis, Node, ffmpeg, Playwright Chromium) is **not present** in the configured mirror registry.
- uvicorn / FastAPI / Node dev server fails to bind a port on Windows with `Errno 10048 — address already in use`, but `netstat -ano` shows the port free.
- You need Playwright but the launch fails with `Executable doesn't exist at ...\ms-playwright\chromium_headless_shell-...\chrome-win\headless_shell.exe`.
- You have a multi-service stack (DB + cache + API + worker) and must selectively move services between Docker and native.

## Step 1 — Probe the local Docker registry first (don't guess)

Before designing the topology, list what is actually pullable from your configured mirror. On China-mainland hosts using `docker.1ms.run` or similar, the catalog is **drastically smaller** than Docker Hub.

```bash
# Test which images are available — do this BEFORE writing docker-compose
docker pull postgres:16
docker pull redis:7-alpine
docker pull node:20-alpine
docker pull python:3.11-slim
docker pull pgvector/pgvector:pg16
```

**Observed coverage on `docker.1ms.run` (June 2026):**
- ✅ `postgres:16`, `pgvector/pgvector:pg16` — present
- ❌ `redis:*`, `node:*`, `python:*`, `ffmpeg`, `playwright/*` — absent (sha256 mismatch errors)

If your stack needs a missing image, **don't try a different mirror blindly** — switch that service to native execution. Hybrid is the answer.

## Step 2 — Design the hybrid split

Default mapping for a FastAPI + Celery + Redis + Postgres stack under constrained mirrors:

| Service | Where it runs | Why |
|---|---|---|
| **PostgreSQL / pgvector** | Docker (port 5434) | `pgvector/pgvector:pg16` IS available; persistence + extension support works |
| **Redis** | Skip / in-memory (`fakeredis`) OR native Windows install | Image not in mirror |
| **FastAPI / uvicorn** | Native venv (`python -m uvicorn`) | Avoids the `lru_cache` stale-config trap and lets you iterate fast |
| **Celery worker / beat** | Skip or run inline | Needs Redis broker; defer to PostgreSQL-backed task queue or do tasks synchronously in a `BackgroundTasks` |
| **Frontend (Vite / npm)** | Native `npm run dev` | Node image not in mirror; npm install works fine on host |
| **Playwright Chromium** | Native `python -m playwright install chromium` | Image not in mirror; download goes to `%LOCALAPPDATA%\ms-playwright\` directly |

**Gotcha — `docker-compose` `depends_on` won't fix this.** Don't waste time wiring up workers/beat that can't run. Strip them from `docker-compose.yml` and use the `api_router` to do work synchronously or via FastAPI's `BackgroundTasks`.

## Step 3 — Windows port-binding pitfall (uvicorn / Node)

**Symptom:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8020):
通常每个套接字地址(协议/网络地址/端口)只允许使用一次。
```
But `netstat -ano | grep :8020` returns nothing. And killing the PID you saw earlier didn't free the port.

**Root cause:** On Windows, `netstat` may not show all listeners (e.g. listeners bound on `::` IPv6 wildcard only, or held by a service you can't see in your session). The prior `uvicorn` process is usually holding it via a child/worker you didn't observe.

**Fix — use PowerShell `Get-NetTCPConnection`:**
```powershell
Get-NetTCPConnection -LocalPort 8020 -State Listen -ErrorAction SilentlyContinue |
  ForEach-Object {
    Write-Host "Killing PID $($_.OwningProcess) on port 8020"
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
  }
```
Then verify:
```powershell
Get-NetTCPConnection -LocalPort 8020 -State Listen -ErrorAction SilentlyContinue
# should be empty
```

**Fallback — change the port.** If you can't free it, move the service to a different port (e.g. 8021 instead of 8020) and update the corresponding `vite.config.ts` proxy target. This is faster than chasing a phantom process.

## Step 4 — Playwright Chromium "executable doesn't exist"

**Symptom:**
```
BrowserType.launch: Executable doesn't exist at
C:\Users\Administrator\AppData\Local\ms-playwright\chromium_headless_shell-1148\chrome-win\headless_shell.exe
║ playwright install                                       ║
```

**Fix (one command, downloads ~90 MB to AppData):**
```bash
cd <project>/backend
./venv/Scripts/python.exe -m playwright install chromium
```
After install, the headless shell lives at the path Playwright expected. No need to set `PLAYWRIGHT_BROWSERS_PATH` or copy the binary.

**Do not** try to add a Dockerfile with `mcr.microsoft.com/playwright` base — that image is also usually absent from China mirrors and ~1 GB to pull.

## Step 5 — Pydantic v2 + `.env` + `lru_cache` stale-config trap

**Symptom:** You changed `LLM_API_KEY=sk-...` in `.env` but the running service still uses the old value (e.g. `gpt-4o` model name, "请配置 API Key" response).

**Root cause:** `app/config.py` uses `pydantic_settings.BaseSettings` wrapped in `@lru_cache() def get_settings()`. The settings are read **once at process start**. Editing `.env` does NOT trigger a re-read.

**Fix — restart the service.** The `lru_cache` means `.env` reload is a no-op. There is no hot-reload. The standard fix is:
```bash
# 1. Edit .env
# 2. Kill the uvicorn worker
Get-NetTCPConnection -LocalPort 8021 -State Listen | Stop-Process -Id {$_.OwningProcess} -Force
# 3. Restart
cd backend && ./venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8021
```

This bites every time you swap LLM providers (OpenAI → DeepSeek → minimax). Plan for it.

## Step 6 — pydantic-settings v2 compatibility

Old projects copied from FastAPI templates often use pydantic v1 syntax. With pydantic-settings 2.x and pydantic 2.x you must patch `config.py`:

```python
class Settings(BaseSettings):
    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8", "extra": "ignore"}
    # ...
```
- `model_config` (dict), not `class Config:` (inner class)
- `extra="ignore"` is critical — without it, every unknown env var crashes startup
- `env_file_encoding="utf-8"` for Chinese / emoji content

## Verification checklist

After deploying the hybrid stack, confirm:
1. `curl http://localhost:<api-port>/api/health` → `{"status":"healthy",...}`
2. `docker ps` shows ONLY the services you actually run in Docker (often just postgres)
3. Frontend `http://localhost:<vite-port>/` loads, network tab shows proxy hitting the right API port
4. Any LLM test endpoint that requires the API key returns 200 (not "请配置 API Key")
5. Playwright-dependent tests can launch a browser (`page.goto("about:blank")`)

## Common pitfalls

- **Don't print secrets to terminal logs.** `cat .env`, `echo $VAR`, even `grep KEY .env` in a shared transcript leaks the value. See `references/credential-handling-pitfalls.md` for safe-write patterns.
- **Don't trust `netstat -ano` on Windows for port conflicts.** It misses some listeners; use `Get-NetTCPConnection -State Listen` from PowerShell.
- **Don't assume the China mirror has every image.** Test pulls before composing. A failed `docker pull` mid-`docker compose up` leaves half-started services.
- **Don't `cd /c/...` and `nohup ... &` in one foreground command.** Hermes terminal will reject it; use `background=true` and a separate health check.
- **Don't keep stale `lru_cache` config and hope `.env` reloads.** It won't. Restart.
- **Don't write a Playwright Dockerfile expecting it to pull from your mirror.** It usually won't; install Chromium into the venv on the host instead.

## Files in this skill

- `references/credential-handling-pitfalls.md` — **READ THIS FIRST** if you ever typed `cat .env`, `echo $KEY`, or pasted a JWT-shaped string into a script. Safe-write patterns + tool-level traps (incl. `write_file`/`execute_code` literal-truncation behavior).
- `scripts/force-free-port.ps1` — one-liner that finds and kills whatever Windows process is holding a TCP port. Use when uvicorn/Node/Vite refuses to bind with `Errno 10048` but `netstat -ano` looks clean.

## Related skills
- `hermes-agent` (bundled) — for `terminal(background=true)` and process lifecycle semantics
- `docker-desktop` workflows — none in this repo yet; consider adding a `references/docker-on-windows.md` if you hit more container issues
