# moosecloud.cc — LLM Proxy Notes

**Verified 2026-06-07** via real `/v1/models` listing and `/v1/chat/completions` round-trip.

## Endpoint

- Base URL: `https://moosecloud.cc/v1`
- Auth: `Authorization: Bearer <key>` (OpenAI-compatible)
- Auth header variants the server also accepts: `x-api-key`, `x-goog-api-key` (suggests upstream Google Gemini routing for some models)

## Available models (15 total as of 2026-06-07)

```
codex-auto-review
gpt-4o-audio-preview
gpt-4o-realtime-preview
gpt-5.2
gpt-5.2-2025-12-11
gpt-5.2-chat-latest
gpt-5.2-pro
gpt-5.2-pro-2025-12-11
gpt-5.3-codex
gpt-5.3-codex-spark
gpt-5.4
gpt-5.4-2026-03-05
gpt-5.4-mini
gpt-5.5
gpt-image-2
```

## Stability notes (the load-bearing fact)

- **`gpt-5.4` and `gpt-5.4-mini` are stable** — single-digit-second responses, no 5xx in repeated tests.
- **`gpt-5.5` is unreliable** — repeated `502 Upstream stream ended without a terminal response event` errors. Likely the upstream 5.5 endpoint is misconfigured or rate-limited on the proxy side.
- **Default to `gpt-5.4`** when configuring for production use. Switch to `gpt-5.4-mini` if cost/speed matters more than quality.
- Re-test `gpt-5.5` periodically — proxies fix upstream issues without notice.

## Probe recipe (no credentials needed, just paste your key)

```bash
python ~/.hermes/skills/devops/hermes-llm-endpoints/scripts/probe_endpoint.py \
  https://moosecloud.cc/v1 sk-...
```

## Hermes config

```bash
hermes config set model.provider custom
hermes config set model.base_url https://moosecloud.cc/v1
hermes config set model.api_key sk-...
hermes config set model.default gpt-5.4
hermes gateway restart --profile boss-control
```

## Cost / token shape (observed)

- `gpt-5.4-mini` completion with 5 output tokens: `usage: {prompt: 24, completion: 5, total: 29}`
- `gpt-5.5` with simple prompt: `usage: {prompt: 24, completion: 27, reasoning_tokens: 20}` — the model uses chain-of-thought, so a "ping" call actually burns 20 reasoning tokens. Watch the budget if the user is on a tight plan.

## What this server is NOT

- Not the official OpenAI API
- Not a Nous Portal / OpenRouter endpoint
- Not a Google AI Studio endpoint
- Likely a third-party aggregation layer that buys capacity from upstream providers (OpenAI, Google) and resells. **Treat as semi-trusted** — assume the proxy operator can see request/response content. Do not pass secrets or PII through it.
