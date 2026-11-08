# Profile Teardown Safety — "全部删掉" / "不用原来那套方案" Pitfall

**Date verified:** 2026-06-06, Windows + Hermes 0.15.1.

## The trap

When 老大 pivots business line (e.g. RAS → 水产养殖/美食/设备) and says "全部删掉" or "不用原来那套方案", the LLM-default reaction is to `hermes profile delete <name>` for every profile. **Don't.** The profile list is usually mixed:

| State in `hermes profile list` | Meaning | Deleting it is... |
|---|---|---|
| `agent-sales   MiniMax-M3  running` | **Alive** — has API key in `~/.hermes/profiles/agent-sales/profile.yaml`, gateway is wired up | **Destructive** — wipes the API key, breaks the next gateway run, may force 老大 to re-enter the key |
| `ras-boss  —  stopped` | **Empty ghost** — created via `hermes profile create` but never bootstrapped (no `.env`, no `config.yaml`, no API key) | **Safe** — nothing to lose |

The trigger: a previous session bootstrapped N profiles the proper way (with API key + .env + gateway start), then a later session **re-created** N more profiles with the same names but never bootstrapped them. Now the list has 2N profiles, half alive, half ghosts. The user just sees "9 profiles, delete them all" — the LLM obliges, the alive half dies, the user re-pastes API keys next session.

## How to detect alive vs ghost

```bash
hermes profile list
# Look at the "Model" + "Gateway" columns:
#   Model filled + Gateway "running"  → ALIVE (has key)
#   Model "—"      + Gateway "stopped" → GHOST (empty)
```

For borderline cases (model filled but gateway stopped), also check:

```bash
cat ~/.hermes/profiles/<name>/profile.yaml
# If api_key: is empty or absent → GHOST
# If api_key: sk-... → ALIVE
```

## The safe teardown recipe

```bash
# 1. List
hermes profile list

# 2. Partition
ALIVE=$(hermes profile list | awk '/MiniMax-M3/ && /running/ {print $1}')
GHOSTS=$(hermes profile list | awk '/—/ && /stopped/ {print $1}')

# 3. Show 老大 the partition + ask
echo "ALIVE (have API key, deleting wipes the key):"
echo "$ALIVE"
echo ""
echo "GHOSTS (empty, safe to delete):"
echo "$GHOSTS"
# 老大 says OK → then run
```

**Always ask 老大 before touching the ALIVE set.** A one-line confirmation ("保活 N 个有 API key 的，删 N 个没 key 的，对吗？") saves a re-bootstrap.

## When the user is in a hurry

If 老大 says "我急" / "别问直接干" / "默认就按你建议":

1. Default: **delete the GHOSTS, KEEP the ALIVE** (rename them via `hermes profile create <newname>` only if 老大 wants to repurpose; don't `delete` the alive ones).
2. If 老大 explicitly says "全删包括活的" → stop gateway first (`hermes gateway stop --all`), then `hermes profile delete <name>` for each, **warn 老大 that they'll need to re-paste API keys** before starting any new gateway.

## Why this matters for 飞书 agent rebuilds

The 4 App IDs + 4 Secrets are 飞书 resources owned by 老大 (they don't change). The 4 hermes profiles are *config wrappers* around those resources. If the wrapper profiles die, you don't lose the 飞书 Apps, but you DO lose:

- The per-profile `.env` (FEISHU_APP_ID / SECRET / ALLOW_ALL_USERS)
- The gateway PID/log paths (`~/hermes-gateway-logs/<name>.log`)
- The cached tokens (`feishu-tokens.json` keys)

So worst case is rebuild, not data loss. But it's a 10-15 min rebuild vs a 30-sec confirmation. Always confirm.

## Verified on 2026-06-06

In a real session, 老大 pivoted from RAS to 水产养殖/美食/设备 and said "全部删掉 不要用原来那套方案". The profile list had 9 entries:

- 4 `agent-*` profiles (alive, MiniMax-M3 / running, API keys present) — kept
- 5 `ras-*` profiles (ghosts, — / stopped, never bootstrapped) — safe to delete

Catching the split saved 老大 from re-pasting 4 API keys. Total pivot time: 5 min instead of 30 min.
