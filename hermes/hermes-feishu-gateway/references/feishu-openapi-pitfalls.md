# 飞书 OpenAPI 实战硬核坑

2026-06-06 RAS 3-Agent 接入 + 之前 5-Agent 验证累积。所有 path 都在 https://open.feishu.cn/document/ 有文档，但**实际行为跟文档有出入**，下面记的都是验证过的「唯一可行」路径。

## 1. 写 docx 唯一路径

```
POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
```

- `document_id` **就是** page 的 block_id（不是另一个 ID）
- `block_id` 不带 `/children` 写不进
- 试过的 404 路径：
  - `POST /open-apis/docx/v1/documents/{id}/raw_content` ❌
  - `POST /open-apis/docx/v1/documents/{id}` ❌
  - `POST /open-apis/docx/v1/documents/{id}/blocks/{id}` ❌（少了 `/children`）

## 2. send_message 发 topic 必拒

```json
{"receive_id_type": "chat_id", "msg_type": "text", ...}
```

- 带 `topic_id` 字段 → 返 `[99992402] field validation failed`
- DM 走 `feishu:{chat_id}` 不带 topic
- 群消息走 `chat_id` 模式

## 3. 一个 App = 一个 bot

- 飞书严格 1:1，多 Agent 必须多 App
- App 只能在 https://open.feishu.cn/app 后台由**人**创建（小弟做不了）
- App 创建后需要「发布上线」走企业管理员审批

## 4. 建群必带 permission_version

```json
{
  "name": "群名",
  "permission_version": "v2"
}
```

- 不带 `v2` → 后续加成员/改权限操作全挂
- `v1` 是旧版，已弃用

## 5. tenant_access_token 端点

```
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Body: {"app_id": "...", "app_secret": "..."}
```

- 返 `{"code": 0, "tenant_access_token": "t-xxx", "expire": 7200}`
- token 2 小时有效，每次调用前重新拿
- 返 `99991663/99991664` = App 没发布/没权限

## 6. im/v1/chats 拉群列表

```
GET https://open.feishu.cn/open-apis/im/v1/chats?page_size=50
Header: Authorization: Bearer t-xxx
```

- **只列机器人已被加进的群**
- 机器人没进任何群 → `data.items` 空数组
- 群分页：`page_token` 字段循环

## 7. 事件订阅（Webhook 模式用）

如果选 webhook 模式（不用 websocket），需配：
- Encrypt Key（消息加密用）
- Verification Token（首次握手验签用）
- 这俩 hermes feishu adapter 读 `FEISHU_ENCRYPT_KEY` / `FEISHU_VERIFICATION_TOKEN` 环境变量

## 8. lark-oapi 库

`pip install lark-oapi` 后可 Python 直接调，但 hermes 0.15.1 venv 已自带。**本机沙箱拦 pip install**——别试，要装走 GUI 手动或换路径。

## 9. 消息内容类型

- `text` — 纯文本
- `post` — 富文本（用 `zh_cn.content` 数组）
- `image` / `file` / `audio` / `media` — 需先 upload 拿 file_key
- `interactive` — 卡片消息（最复杂但最帅）
- `share_chat` / `share_user` — 分享
