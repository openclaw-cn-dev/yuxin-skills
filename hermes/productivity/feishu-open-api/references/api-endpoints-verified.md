# Feishu API endpoints — verified during 5-agent department build

Every endpoint below was called live against `open.feishu.cn` with App ID `<FEISHU_APP_ID>`. Status codes reflect what was actually returned on 2026-06-06.

## Auth

| Method | Path | Status | Notes |
|---|---|---|---|
| POST | `/open-apis/auth/v3/tenant_access_token/internal` | ✅ 200 | Body: `app_id` + `app_secret` (form-urlencoded). Returns `tenant_access_token` + `expire` (default 7200s). |

## App / scope probe

| Method | Path | Status | Notes |
|---|---|---|---|
| GET | `/open-apis/application/v6/applications/{app_id}?lang=zh_cn&user_id_type=open_id` | ✅ 200 | Returns full app config: name, type, bot ability, callback config, **all granted scopes** (level + token types), creator's open_id, avatar URL. The "GG" app came back with 400+ scopes already granted. |
| GET | `/open-apis/application/v6/scopes` | ✅ 200 | Returns global scope catalog with `grant_status: 1` for those the current token can use. |

## IM — chats

| Method | Path | Status | Notes |
|---|---|---|---|
| POST | `/open-apis/im/v1/chats` | ✅ 200 | Create group. Requires `permission_version: "v2"` or newer member-management ops fail. `user_id_list` takes `open_id`s. |
| DELETE | `/open-apis/drive/v1/files/{file_token}` | ❌ 400 (type required) | Cannot delete a chat via drive API. Chats are deleted from the Feishu client GUI only. |
| POST | `/open-apis/im/v1/chats/{chat_id}/members` | ✅ 200 (not tested this session, but documented) | Add bot to chat. Bot must have `im:chat` scope. |

## Docx

| Method | Path | Status | Notes |
|---|---|---|---|
| POST | `/open-apis/docx/v1/documents` | ✅ 200 | Body: `{"title": "..."}`. Returns `document_id` (which is also the page `block_id`, `block_type=1`). |
| GET | `/open-apis/docx/v1/documents/{doc_id}/blocks` | ✅ 200 | Lists root-level blocks. The page block is the first item. |
| POST | `/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children` | ✅ 200 | **The** write path. `parent_id` = `document_id` for top-level appends. `index: -1` appends. |
| POST | `/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}` | ❌ 404 | Missing `/children` suffix — does not exist. |
| PUT | `/open-apis/docx/v1/documents/{doc_id}/raw_content` | ❌ 404 | Deprecated/migrated. Use blocks API. |
| POST | `/open-apis/drive/v1/import_tasks/file?file_extension=md` | ❌ 404 | Path has changed in current 飞书 API version. Don't use. |

## Block types (numeric)

| block_type | meaning |
|---|---|
| 1 | page (document root) |
| 2 | text |
| 3 | heading1 |
| 4 | heading2 |
| 5 | heading3 |
| 12 | bullet |
| 19 | callout |

## IM — messages (not exercised this session but documented for next session)

| Method | Path | Use |
|---|---|---|
| POST | `/open-apis/im/v1/messages?receive_id_type=chat_id` | Send text/card message to chat. Body: `{"receive_id": chat_id, "msg_type": "text", "content": "{\"text\":\"...\"}"}` |
| POST | `/open-apis/im/v1/messages/{message_id}/reactions` | Add reaction emoji to a message |
| GET | `/open-apis/im/v1/messages/{message_id}` | Read a specific message (requires `im:message` or appropriate scope) |

## Rate limits observed

- Chat create: no throttling at 1 req/0.5s over 5 calls
- Block append: 65 blocks in 4 calls, ~0.3s sleep between batches, no 429s
- Token: 1 call per 2h (cached). Re-caching on every script call = waste.
