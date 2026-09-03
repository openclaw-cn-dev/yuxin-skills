# 平台 Cookie 关键字段速查

按平台列出从 F12 / EditThisCookie 提取时**必须拿**的字段，及常见陷阱。

## 知乎 zhihu.com

```json
{
  "z_c0": "Mi4xQUFBQ...",
  "SESSIONID": "3a8b9c0d1e2f...",
  "__zse_ck": "001A1B2C3D-..."
}
```

- `z_c0` — 核心登录态（**HttpOnly**，必须用 F12/扩展）
- `SESSIONID` — 会话 ID
- `__zse_ck` — 反爬加密，**API 调用必带**
- 域: `.zhihu.com`

**最小可用**：只提 z_c0 + __zse_ck（多数 API 够用）
**完整三件套**：上述 3 个 + `d_c0`（设备 ID）

## 小红书 xhslink.com / xiaohongshu.com

```json
{
  "web_session": "040721b3e0f...",
  "webId": "7f3a2b1c8d9e...",
  "a1": "1234567890abcdef..."
}
```

- `web_session` — 核心登录态（**HttpOnly**）
- `a1` — 设备指纹（**关键** — 缺这个直接限流）
- `webId` — 用户标识
- 域: `.xiaohongshu.com`

**坑**：小红书风控严，Cookie 有效期**通常 7-30 天**，过期前 1-2 天会有"频繁操作"提示

## 抖音 douyin.com

```json
{
  "sessionid": "abc123def456...",
  "ttwid": "1%7C...",
  "msToken": "xyz789..."
}
```

- `sessionid` — 核心登录态
- `ttwid` — **反爬关键**（URL encoded）
- `msToken` — 设备 token
- 域: `.douyin.com`

**坑**：抖音 **CDN 反爬**——`__live_version__` 和 `MANIFEST` 头也要带

## 微博 weibo.com

```json
{
  "SUB": "abc123...",
  "SUBP": "xxx...",
  "ALF": "yyy..."
}
```

- `SUB` — 核心登录态
- `SUBP` — 加密参数
- `ALF` — 时间戳
- 域: `.weibo.com`

## B 站 bilibili.com

```json
{
  "SESSDATA": "xxx,yyy...",
  "bili_jct": "csrf_token...",
  "DedeUserID": "12345"
}
```

- `SESSDATA` — 核心登录态
- `bili_jct` — **CSRF token**（发评论/弹幕必带）
- `DedeUserID` — UID
- 域: `.bilibili.com`

## 微信公众号 / 视频号 mp.weixin.qq.com

```
{wxtoken, pass_ticket, uin, devicetype, accticket, version, lang, ...}
```

**复杂**——需要：
1. 微信 PC 客户端 + 公众号工具（**方糖** / **壹伴** / **新媒体管家**）
2. 或用 `wechaty` 库 hook
3. 域: `.qq.com` + `.weixin.qq.com`

**通常建议用第三方 SaaS**（如 [Wechaty](https://wechaty.bot) / [wxy.tudouyao.com](https://wxy.tudouyao.com)），别自己抓

## 快手 kuaishou.com

```json
{
  "kuaishou.server.web_st": "...",
  "kpf": "...",
  "userId": "..."
}
```

- `web_st` — H5 web session
- `kpf` — 设备指纹
- 域: `.kuaishou.com`

## 小红书国际版 RED

```json
{
  "red_session": "...",
  "userId": "..."
}
```

## 拼多多 pinduoduo.com

```json
{
  "PDDAccessToken": "...",
  "pdd_user_id": "..."
}
```

---

## 通用注意事项

1. **域名前缀** — 必须带 `.`（如 `.zhihu.com`）以匹配所有子域
2. **HttpOnly 标记** — 必须在 F12 Application 标签或 EditThisCookie 扩展里看，**JS `document.cookie` 拿不到**
3. **顺序** — Python 3.7+ 字典保持插入顺序，保存时按 F12 看到的顺序
4. **HTTPS Only** — `Secure` 标志的 cookie 在 HTTP 服务上不会发，生产必须 HTTPS
5. **过期时间** — 浏览器存的 Expires ≠ 登录态有效时间，异地登录/安全事件会提前失效

## 速查表

| 平台 | 核心字段 | HttpOnly | 常见有效期 | 反爬严度 |
|---|---|---|---|---|
| 知乎 | z_c0 | ✓ | 30天 | 中 |
| 小红书 | web_session + a1 | ✓ | 7-30天 | **高** |
| 抖音 | sessionid + ttwid | 部分 | 14-30天 | **高** |
| 微博 | SUB | ✓ | 30天 | 中 |
| B站 | SESSDATA + bili_jct | ✓ | 30天 | 中 |
| 公众号 | wxtoken + pass_ticket | ✓ | 2小时 | **极高** |
| 快手 | web_st | ✓ | 7-30天 | 高 |
