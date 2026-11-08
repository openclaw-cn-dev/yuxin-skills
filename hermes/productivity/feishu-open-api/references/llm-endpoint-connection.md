# Connecting a Third-Party LLM Endpoint

The full recipe for safely wiring a non-default LLM provider into Hermes
Agent. Captured 2026-06-07 after I fabricated a fake base_url, corrupted
`.env`, and spent 10 minutes rolling back.

## The rule (autonomy ≠ fabrication)

When the user says "直接接" / "你自己看着办" / "接进去跑跑看", the agent has
authority to choose the **approach**, but it does NOT have authority to
invent **infrastructure data** that the user has not provided. A
fabricated base_url (`api.gptapi.com`) silently fails DNS and corrupts
`.env` for 10 minutes. A wrong but **real** domain fails with a clean
401/403/404 — actionable in seconds.

**Hard requirement**: before editing `.env` or `config.yaml` for a
third-party LLM, the agent must have a **verified-reachable** `base_url`.
"Verified-reachable" means: the agent has either (a) received the URL
from the user, or (b) successfully run the connectivity probe below.

## Pre-flight: connectivity probe (1 second, saves 10 minutes)

Before touching `.env`, run this:

```python
import socket, urllib.request, ssl, sys

def probe(url, key='sk-test-probe'):
    parts = url.replace('https://', '').replace('http://', '').split('/')[0].split(':')
    host, port = parts[0], int(parts[1]) if len(parts) > 1 else 443
    try:
        ip = socket.gethostbyname(host)
        print(f'DNS OK: {host} -> {ip}')
    except socket.gaierror as e:
        print(f'DNS FAIL: {host} ({e})')
        return False
    try:
        req = urllib.request.Request(f'{url}/models',
            headers={'Authorization': f'Bearer {key}'})
        r = urllib.request.urlopen(req, timeout=5,
            context=ssl.create_default_context())
        print(f'HTTP OK: {r.status} (auth may still fail — that is expected)')
        return True
    except urllib.error.HTTPError as e:
        # 401/403/404 are GOOD — the domain resolves, the host is up
        print(f'HTTP REACHABLE: {e.code} (expected; will fix with real key)')
        return True
    except Exception as e:
        print(f'HTTP FAIL: {e}')
        return False

# Usage
probe('https://api.example.com/v1')
```

**Interpretation**:
- DNS FAIL (`getaddrinfo failed`) → domain doesn't exist. STOP, ask user for real URL.
- HTTP REACHABLE (any 4xx) → domain is up, real, you can use it. Continue.
- HTTP OK (200) → domain is up AND your key works. Go.

## Backup the .env FIRST

```bash
# Hermes rotates .env backups on certain config events
ls -la ~/AppData/Local/hermes/.env*
ls -la ~/AppData/Local/hermes/profiles/<name>/.env* 2>/dev/null
```

If a backup exists with the original values, use it for rollback.
If not, snapshot manually:

```bash
cp ~/AppData/Local/hermes/.env ~/AppData/Local/hermes/.env.manual-bak-$(date +%s)
```

## The four fields to change

| Field | File | Example | Notes |
|---|---|---|---|
| API key | `.env` (root) | `MINIMAX_CN_API_KEY=*** | Or per-profile `MINIMAX_CN_API_KEY` |
| Base URL | `.env` | `MINIMAX_BASE_URL=https://api.example.com/v1` | Use `/v1`, not bare domain |
| Provider | `config.yaml` | `model.provider` (built-ins: `minimax-cn`/`openrouter`/`anthropic`) | If your endpoint isn't a built-in, see "Custom provider" below |
| Base URL | `config.yaml` | `model.base_url` | Overrides provider default |

**Note**: `hermes config show` may display a different `base_url` than
`config.yaml` actually contains — the show command shows the **provider
default** when `config.yaml` has none. Always `grep base_url config.yaml`
to confirm what is live.

## Custom provider (when built-in doesn't fit)

Hermes has built-in providers (`minimax-cn`, `openrouter`, `anthropic`)
that ship with default base_urls. If your endpoint isn't OpenAI-compatible
with a known provider, you need a custom provider. Check
`hermes config set --help` and `hermes providers list` for the right syntax.
This path is heavier; prefer matching one of the built-ins first.

## Rollback (when something goes wrong)

Use `templates/dotenv-rollback.py`. The recipe:
1. Read the backup file (auto-discovered at `.env.bak.*` or the
   `.env.manual-bak-*` you made).
2. Use `python .replace()` (NOT regex) to swap the contaminated value
   back to the original. Regex collides with the `***` redaction filter
   (see `hermes-quirks.md` #1).
3. For URLs, use `sed -i "s|^FIELD=.*|FIELD=ORIG|"` — that handles
   special characters that would break `python .replace()` if escaped
   wrong.
4. Verify with `grep -E "FIELD" .env` — show the changed line plus 2
   lines of context.

See `templates/dotenv-rollback.py` for the full script.

## When to give up and ask

If the user provides a key but no base_url, the agent should:
1. State explicitly: "I need a verified-reachable base_url to proceed"
2. Offer 2-3 known-good defaults with a probe candidate (e.g. "want me
   to test api.openai.com / DeepSeek / 豆包 first?")
3. Wait for the user to pick or supply their own.

Do NOT proceed with a guessed base_url "to save the user a question".
The cost of asking is 1 turn; the cost of fabricating is 10 minutes of
rollback + 1 contaminated `.env` + loss of trust.
