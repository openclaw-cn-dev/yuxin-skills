# Feishu app_secret 轮换 / 重新配对排障

适用场景：用户说“重新配对飞书机器人”，但历史上其实已经配对过；当前症状是机器人不回消息、gateway 偶发断开、看起来像配对失效。

## 先判定是不是配对问题

先看两处：

1. `hermes pairing list`
- 如果还能看到已批准的 `feishu` 用户，通常不是 pairing 丢了。

2. `~/.hermes/logs/gateway.log`
- 若出现：`obtain self tenant access token failed, code: 10014, msg: app secret invalid`
- 结论：不是配对坏了，是 `FEISHU_APP_SECRET` 失效或已轮换。

## 标准修复

需要用户提供 4 个值：
- `app_id`
- `app_secret`
- `chat_id`
- `domain` (`feishu` / `lark`)

修复项：
- `.env`:
  - `FEISHU_APP_ID`
  - `FEISHU_APP_SECRET`
  - `FEISHU_DOMAIN`
  - `FEISHU_CONNECTION_MODE=websocket`
  - `FEISHU_ALLOWED_USERS=<chat_id>`
- `config.yaml`:
  - `platforms.feishu.home_channel.chat_id=<chat_id>`
  - `feishu.allowed_chats=<chat_id>`

注意：`config.yaml` 用 `hermes config set` 改；不要直接 patch Hermes 配置文件。

## 真验证，不要只看 connected

`gateway` 日志显示 `feishu connected` 还不够，必须再验一次 token：

POST `https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal`
body:
```json
{
  "app_id": "<app_id>",
  "app_secret": "<app_secret>"
}
```

成功标准：
- `code = 0`
- `msg = ok`
- 返回 `tenant_access_token`

只有这个通过，才说明新 secret 真生效。

## Windows / 手动 gateway 坑

如果 gateway 不是系统服务，而是手动 `hermes gateway run` 跑起来的：
- `hermes gateway restart` 会先停掉它
- 然后提示 `Gateway service is not installed`
- **不会自动重新拉起**

这时要手动再执行一次：
- `hermes gateway run`

所以完整顺序是：
1. 改 `.env`
2. `hermes config set ...`
3. `hermes gateway restart`
4. 如果提示 service 未安装，立刻补 `hermes gateway run`
5. 再验 token + `hermes gateway status`

## 本次有效信号

- 旧症状：`code: 10014, msg: app secret invalid`
- 新 secret 验证结果：`code=0`, `msg=ok`, `tenant_access_token_present=True`
- 新 chat：`oc_529aff7485ccc35de97a9e7233d665dd`
