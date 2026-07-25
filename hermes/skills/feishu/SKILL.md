---
name: feishu
description: 飞书 (Feishu / Lark) platform skills — cloud drive operations, wiki knowledge base management, and Bot-to-Bot file sharing patterns. Load when you need to interact with the 飞书 open API (tenant token), manage docs/folders in 飞书云盘, operate 飞书知识库 (Wiki) spaces, or coordinate multiple 飞书 Bot agents on shared work.
version: 1.0.0
metadata:
  hermes:
    tags: [feishu, lark, 飞书, cloud-drive, wiki, bot, open-api, tenant-token]
---

# 飞书 (Feishu) Platform Skills

Class-level umbrella for working with the 飞书 (Feishu / Lark) open API from Hermes. Each child covers a distinct surface area (cloud drive, wiki, bot-specific patterns).

## When to load this skill

You're about to call the 飞书 open API, manage 飞书云盘 (Drive) files, create or fill a 飞书知识库 (Wiki) space, or coordinate cross-Bot file sharing.

## Children (pick one)

- `feishu-bot-cloud-drive/` — Bot 飞书云盘 operations and cross-Bot file-sharing patterns. Covers the critical platform limit: **Bot 之间无法通过 API 互相分享文件夹** (code `1063002 Permission denied`) — use ECS shared directories instead.
- `feishu-drive-file-management/` — 飞书云盘 file management: create folders, upload, download, share. Tenant access token via `POST /auth/v3/tenant_access_token/internal`.
- `feishu-wiki-operations/` — 飞书知识库 (Wiki) space operations, permission management, and content sync patterns. **Wiki 空间创建必须用 user_access_token** — Bot cannot create Wiki spaces (`code 99991663`).

## Key 飞书 Platform Limits (load this section first)

These are the platform-level constraints that trip up most first-time users — covered in detail in the relevant child skill:

1. **Bot cannot create Wiki 空间** — must use user_access_token. Error `99991663` = "Invalid access token for authorization".
2. **Bot cannot share folders with another Bot** — code `1063002 Permission denied`. This is a platform limit, not a permissions issue. Use ECS shared directory or send file content directly via message attachments.
3. **Token truncation in shell** — Hermes truncates `...` in Bearer tokens → `99991663`. Always write token to `/tmp/token.json` and read back full value.

## How to choose

- **Cross-Bot file sharing or Bot cloud-drive ops** → `feishu-bot-cloud-drive/`
- **Generic cloud drive file CRUD** → `feishu-drive-file-management/`
- **Wiki knowledge base (read / write / sync)** → `feishu-wiki-operations/`

## Related (not in this umbrella)

- `apple/imessage/` — Apple iMessage / SMS — different platform.
- `email/himalaya/` — Email via terminal — different protocol.
- `yuanbao/` — 元宝 group @mention / DM (different Chinese chat platform).
- `productivity/lookforge-mcp-hermes/` — LookForge MCP server with 飞书 wiki integration (project-specific recipe).

## Session-specific recipes (references/)

- `references/laomo-feishu-group-sync.md` — 老莫's working 飞书大群 (oc_23bd798272a60cbfc15c82b954823730) message-push recipe: the `sync_to_group.main()` API quirk, direct text-message script with hardcoded `APP_ID`/`APP_SECRET`, and the canonical error-code table (`10014`, `99991663`, `230001`).
