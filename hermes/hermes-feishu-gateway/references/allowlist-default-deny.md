# The Default-Deny Allowlist Trap

**This is the #1 reason a "successfully running" Feishu bot doesn't reply.**

Hermes 0.15.1 gateway default policy is `deny all unauthorized users` when no allowlist env var is set for any platform. The gateway prints a single WARNING to the log on startup:
```
WARNING gateway.run: No user allowlists configured. All unauthorized users will be denied.
Set GATEWAY_ALLOW_ALL_USERS=true in ~/.hermes/.env to allow open access,
or configure platform allowlists (e.g., TELEGRAM_ALLOWED_USERS=your_id).
```

This warning is **not an error** — the gateway continues to start, the wss connects, `hermes gateway list` shows `running`. But every inbound message is silently dropped at the auth gate, never reaches the agent, never generates a reply.

**The user reports:** "I sent a message in the Feishu group, the bot didn't reply." You check `hermes gateway list` — `running`. You check the log — wss connected. You check the SOUL.md and `.env` — correct. Conclusion: **allowlist**.

**Fix (for internal/company Feishu bots):** add to each profile's `~/.hermes/profiles/<name>/.env`:
```
FEISHU_ALLOW_ALL_USERS=true
FEISHU_GROUP_POLICY=open
```

- `FEISHU_ALLOW_ALL_USERS=true` — any Feishu user can DM the bot
- `FEISHU_GROUP_POLICY=open` — any user can trigger the bot in a group, not just an allowlist of user open_ids

Both are needed. The first is for 1:1 DM, the second is for group chats.

**For higher-security setups** (public-facing bots, customer-facing bots), use a positive allowlist instead:
```
FEISHU_ALLOWED_USERS=ou_aaa...,ou_bbb...,ou_ccc...   # comma-separated open_ids
```
But getting the open_ids requires `/contact/v3/users` lookups — out of scope for internal tools.

**Restart required:** env vars are read at gateway startup, not on every message. So after editing `.env`, you must:
```
hermes gateway stop -p <name>
hermes gateway run -p <name> 2>&1 | tee <log>
```

**Verification that the fix worked:** the WARNING in the log disappears, and the test message from any group member gets a reply.
