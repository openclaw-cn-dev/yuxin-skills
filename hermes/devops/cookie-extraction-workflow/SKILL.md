---
name: cookie-extraction-workflow
description: 从任何需要登录的网站提取 Cookie，用于自动化脚本（Playwright/Selenium/requests/curl）。覆盖浏览器扩展推荐、F12 手动提取、Console JS 一键导出、各平台关键 cookie 字段（zhihu z_c0/SESSIONID、xhs web_session、douyin sessionid+ttwid、weibo SUB+SUBP、bilibili SESSDATA）、Cookie 转 curl header 格式、Cookie 有效性验证、过期检测与自动重提。Use when 老大说 "怎么提 Cookie"、"提取 Cookie"、"登录态"、"怎么用 Cookie 调 API"、"EditThisCookie"、"F12 找 Cookie"、"登录后再请求"，或任何"我要自动化操作已登录账号"场景。Triggers on "cookie 提取", "cookie 编辑器", "EditThisCookie", "复制 cookie", "F12 找 cookie", "登录态 怎么传", "z_c0 怎么找", "SESSIONID 在哪", "xhs 怎么登录", "douyin cookie 提取", "微博 cookie", "B 站 SESSDATA", "已登录 调用".
---

## 📁 支持文件

- `references/platform-cookie-keys.md` — **8 大平台 Cookie 关键字段速查表**（zhihu/xhs/douyin/weibo/bilibili/公众号/快手/拼多多），含 HttpOnly 标记、有效期、反爬严度
- `scripts/cookie_verify.py` — **Cookie 有效性一键验证**（支持 5 大平台，自动判断有效/过期/状态不明）

# Cookie 提取工作流（class-level skill）

从任何登录态网站提取 Cookie，喂给自动化脚本（curl/Playwright/requests），免登录、免验证码地调内部 API。

## 何时用这个 skill

✅ **用这个 skill 当**：
- 老大要给自动化脚本喂登录态（"我想自动发知乎"、"自动发小红书"、"自动抓微博"）
- 已有脚本但 Cookie 失效（"z_c0 过期了"）
- 不知道哪个 Cookie 字段重要
- 不知道 Chrome 哪个扩展能用

❌ **不要用这个 skill 当**：
- 老大要 OAuth/API key 接入（那走 API key 流程，不是 Cookie）
- 老大要 Playwright 自动登录（**那是从零登录**，不走 cookie 提取）
- 站点完全没登录态（公开 API 直接调）

## 核心 3 步流程

```
1. 浏览器登录目标站（带短信/扫码/2FA）
2. 提取关键 Cookie 字段（按平台各异）
3. 转成 curl/requests header 喂给脚本
```

---

## 1. 浏览器扩展选择（按推荐度）

| 扩展 | 评分 | 用户 | 优势 | 适用 |
|---|---|---|---|---|
| **EditThisCookie (fork)** | 4.4 ⭐ | 20K+ | Manifest V3、JSON/Netscape 导出、URL 解码、深色主题 | **首选 — 通用** |
| Get cookies.txt LOCALLY | 4.8 ⭐ | - | 一键 Netscape 格式（curl/wget 直接用） | 喂 curl 脚本 |
| Copy Cookies | 4.8 ⭐ | - | 点一下复制完整 cookie 到剪贴板 | 极简操作 |
| Cookie-Editor | 4.4 ⭐ | - | 现代 UI、过滤搜索 | 多账号管理 |

### 安装（Edge 浏览器）

```
1. 打开 edge://extensions/
2. 搜索 "EditThisCookie fork"
3. 认准：EditThisCookie (fork) by editthiscookiefork.com
4. 点 "获取" 安装
5. 浏览器右上角出现 🍪 图标
```

### 安装（Chrome 浏览器）

```
1. 打开 chrome://extensions/
2. 搜索 "EditThisCookie fork" 或访问 chromewebstore.google.com
3. 同上认准 fork 版（YoeriW 维护）
4. 点 "添加至 Chrome"
```

---

## 2. 手动 F12 提取（无需扩展）

适用场景：不想装扩展、临时一次、企业管控电脑。

### 步骤

```
1. 浏览器登录目标站
2. 按 F12 打开开发者工具
3. 切换到 Application 标签（不是 Elements！）
4. 左侧菜单：Storage → Cookies → https://<目标站>
5. 找关键字段（按平台表）
6. 双击 Value 复制
7. 发给小弟
```

### Console 一键导出（更快）

F12 → Console 标签 → 粘贴：

```javascript
// 导出所有 cookie 为 JSON
const cookies = document.cookie.split('; ');
const obj = {};
cookies.forEach(c => {
    const [k, v] = c.split('=');
    obj[k.trim()] = v;
});
console.log(JSON.stringify(obj, null, 2));

// 或单独拿关键字段
console.log('z_c0=' + (obj.z_c0 || 'NOT FOUND'));
console.log('SESSIONID=' + (obj.SESSIONID || 'NOT FOUND'));
```

**限制**：`document.cookie` **拿不到 HttpOnly 标记的 cookie**（如 z_c0 通常是 HttpOnly）。
要拿 HttpOnly 字段**必须用 F12 Application 标签**，或用扩展。

---

## 3. 各平台关键 Cookie 字段表

| 平台 | 关键字段 | 数量 | 备注 |
|---|---|---|---|
| **知乎 zhihu.com** | `z_c0` / `SESSIONID` / `__zse_ck` | 3 | z_c0 是 HttpOnly |
| **小红书 xhslink.com** | `web_session` / `webId` / `a1` | 3+ | web_session 是核心 |
| **抖音 douyin.com** | `sessionid` / `ttwid` / `msToken` | 3+ | ttwid 反爬关键 |
| **微博 weibo.com** | `SUB` / `SUBP` / `ALF` | 3 | SUB 是核心登录态 |
| **B 站 bilibili.com** | `SESSDATA` / `bili_jct` / `DedeUserID` | 3 | SESSDATA 是核心 |
| **微信公众号** | `wxtoken` / `pass_ticket` / `uin` | 5+ | 复杂，需公众号工具 |
| **快手 kuaishou.com** | `kuaishou.server.web_st` / `kpf` | 2 | web_st 是核心 |
| **微信公众号视频号** | 同公众号 | - | 需扫码 |

### 知乎 Cookie 三件套（详细）

```json
{
  "z_c0": "Mi4xQUFBQ...",
  "SESSIONID": "3a8b9c0d1e2f...",
  "__zse_ck": "001A1B2C3D-..."
}
```

- `z_c0` — **登录态凭证**（HttpOnly，最重要）。丢了 = 登出
- `SESSIONID` — 会话 ID。配合 z_c0 用
- `__zse_ck` — **反爬加密参数**。知乎 API 调用必带

**最小可用**：只提 z_c0 也行，API 调用失败再加另外两个。

### 小红书 Cookie 三件套

```json
{
  "web_session": "040721b3e0f...",
  "webId": "7f3a2b1c8d9e...",
  "a1": "1234567890abcdef..."
}
```

- `web_session` — 登录凭证（HttpOnly）
- `a1` — 设备指纹
- `webId` — 用户 ID

### 抖音 Cookie 三件套

```json
{
  "sessionid": "abc123def456...",
  "ttwid": "1%7C...",
  "msToken": "xyz789..."
}
```

- `sessionid` — 核心登录态
- `ttwid` — 反爬关键
- `msToken` — 设备 token

---

## 4. Cookie 转 HTTP Header

### 通用格式

```http
Cookie: name1=value1; name2=value2; name3=value3
```

### Python 构造（最稳）

```python
def cookies_to_header(cookies: dict) -> str:
    """把 {"z_c0": "...", "SESSIONID": "..."} 转成 Cookie header"""
    return "; ".join(f"{k}={v}" for k, v in cookies.items())

# 用法
header = cookies_to_header({
    "z_c0": "Mi4xQUFBQ...",
    "SESSIONID": "3a8b...",
})
# → "z_c0=Mi4xQUFBQ...; SESSIONID=3a8b..."

# requests 调用
import requests
r = requests.get("https://www.zhihu.com/api/v4/...", headers={"Cookie": header})

# curl 调用
import subprocess
subprocess.run(["curl", "-H", f"Cookie: {header}", "https://..."])
```

### 字符串格式（老大直接粘给小弟）

最简形式（带前缀）：

```
z_c0=Mi4xQUFBQ...; SESSIONID=3a8b...; __zse_ck=001A1B2C3D-...
```

或 JSON：

```json
{"z_c0":"Mi4xQUFBQ...","SESSIONID":"3a8b...","__zse_ck":"001A1B2C3D-..."}
```

**两种都收**，小弟按情况解析。

---

## 5. Cookie 有效性验证

提完 Cookie **先验证**再用，避免在失效 Cookie 上调 1 小时 API。

### 方法 A：curl 测登录态

```bash
# 知乎 — 访问"我的"页面看是不是已登录
curl -s -H "Cookie: z_c0=***" https://www.zhihu.com/api/v4/me
# 返 {"id":"xxx","name":"xxx",...} = 有效
# 返 {"error":{"code":100}} = 失效
```

### 方法 B：requests 测

```python
import requests
cookies = {"z_c0": "Mi4xQUFBQ...", "SESSIONID": "3a8b..."}
r = requests.get("https://www.zhihu.com/api/v4/me", cookies=cookies, timeout=10)
print(r.status_code, r.json().get('name', r.text[:200]))
```

### 方法 C：Playwright 加载 Cookie 测

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.context.add_cookies([
        {"name": "z_c0", "value": "Mi4xQUFBQ...", "domain": ".zhihu.com", "path": "/"},
        {"name": "SESSIONID", "value": "3a8b...", "domain": ".zhihu.com", "path": "/"},
    ])
    page.goto("https://www.zhihu.com")
    if page.locator(".Avatar").is_visible():
        print("✅ 登录态有效")
    else:
        print("❌ Cookie 失效")
    browser.close()
```

---

## 6. 过期检测与重提

### 典型过期信号

| 信号 | 平台 | 含义 |
|---|---|---|
| 返 `{"code": 100, "msg": "未登录"}` | 知乎 | 登录态失效 |
| 返 401/403 | 通用 | Cookie 被拒 |
| 跳转到 /login | 通用 | 需要重新登录 |
| API 返 `"登录已过期"` | 小红书/微博 | 重新提 |

### 自动重提策略

```python
def is_cookie_expired(resp_json: dict) -> bool:
    """各平台过期检测启发式"""
    code = resp_json.get('code') or resp_json.get('error', {}).get('code')
    msg = str(resp_json.get('msg') or resp_json.get('error', {}).get('message', ''))
    
    expired_signals = [
        '未登录', '请登录', '登录已过期', 'token expired',
        'unauthorized', 'invalid session', 'not login'
    ]
    if code in [100, 401, 403]:
        return True
    if any(sig in msg.lower() for sig in expired_signals):
        return True
    return False

# 用法
import requests
r = requests.get(API_URL, cookies=cookies)
if is_cookie_expired(r.json()):
    print("⚠️ Cookie 失效，请重新提取")
    # 触发老大重新提 Cookie
```

---

## 7. 关键 pitfall

### 7.1 HttpOnly cookie 拿不到

**症状**：F12 → Console 跑 `document.cookie` → 看不到 `z_c0` / `web_session` / `sessionid`。

**根因**：HttpOnly 标记的 cookie **不暴露给 JS**，只能在 Network/Application 标签看到。

**解决**：
- 装 EditThisCookie (fork) — 它**能读 HttpOnly**
- 或 F12 → Application → Cookies（手动找）
- 永远不要让老大"在 Console 跑 JS 拿 cookie" — 拿不全

### 7.2 Cookie 域名不对

**症状**：Cookie 提了但 API 返 401。

**根因**：cookie 有 `domain` 字段（`.zhihu.com` / `www.zhihu.com`）。`www.` 前缀或 `.` 前缀不一致时，浏览器不发送。

**解决**：
- domain 填 `.zhihu.com`（带点）— 匹配所有子域
- 不要填 `zhihu.com`（不带点）— 只匹配根域

### 7.3 Cookie 顺序敏感

**症状**：3 个 cookie 都提了，单放某个返 401，组合 OK。

**根因**：某些站点 API 后端按 cookie 顺序校验（虽然标准不要求）。

**解决**：
- 保持提 cookie 时的**原顺序**
- Python 字典保持插入顺序（Py3.7+）
- 存 cookie 时按 F12 看到的顺序写

### 7.4 HTTPS Only

**症状**：本地测试 HTTP 服务 OK，放生产 HTTPS 服务返 401。

**根因**：cookie 设了 `Secure` 标志，**只在 HTTPS 传**。

**解决**：
- 生产必须 HTTPS
- 测试用 `Secure=False` 的 cookie（`web_session` 默认有 Secure 标志）

### 7.5 Cookie 过期时间 ≠ Session 过期时间

**症状**：浏览器显示 cookie 还有 7 天，但 API 返"登录失效"。

**根因**：cookie 本身的 Expires/Max-Age 是 cookie 浏览器存续时间，**登录态可能提前失效**（异地登录、密码改、安全事件）。

**解决**：
- 每次跑自动化前**先验证 cookie**（5 秒）
- 准备**备用账号 cookie**（1 主 + 1 备）

---

## 8. 工作流速查

### 老大第一次提 Cookie

```
1. 浏览器登录（带短信/扫码）
2. 装 EditThisCookie (fork) 扩展
3. 点 🍪 图标
4. 点导出按钮（向下箭头）
5. 选 JSON 格式
6. 复制字符串发给小弟
```

### 小弟拿到 Cookie 后

```python
import json, subprocess

# 1. 解析
cookies_str = '老大发的字符串'
cookies = {}
if cookies_str.startswith('{'):
    cookies = json.loads(cookies_str)
else:
    # "k1=v1; k2=v2" 格式
    for kv in cookies_str.split('; '):
        k, v = kv.split('=', 1)
        cookies[k] = v

# 2. 验证（必须先验证！）
hdr = "; ".join(f"{k}={v}" for k, v in cookies.items())
r = subprocess.run(['curl','-s','-H',f'Cookie: {hdr}','https://www.zhihu.com/api/v4/me'],
                   capture_output=True, text=True, timeout=10)
print("验证响应:", r.stdout[:200])
# ✅ 返 {"id":"..."} = 有效
# ❌ 返 {"code":100} = 失效，让老大重提

# 3. 转成 requests/Playwright 用的格式
import requests
session = requests.Session()
session.cookies.update(cookies)
# 或 Playwright 见上面
```

---

## 9. 关联

- `hermes-secret-handling` — Cookie 也算"凭证"，不走泄露
- `code-project-analysis` — 分析项目里 Cookie 是怎么用的
- `hermes-llm-endpoints` — LLM key 走 OAuth/API key 流程（不靠 Cookie）
- `browser-automation` — Playwright/Selenium 操作浏览器（自动登录 vs Cookie 提取）

## 10. 速查：失败诊断树

```
Cookie 提取后 API 失败
├─ 返 401 / 未登录
│  ├─ z_c0 没拿全（HttpOnly 漏掉）→ 装 EditThisCookie (fork) 重提
│  ├─ Cookie 顺序错 → 按 F12 看到的顺序重排
│  ├─ domain 不对 → 改成 .zhihu.com（带点）
│  └─ 过期了 → 重新登录 + 重提
├─ 返 403 / Forbidden
│  └─ 缺反爬参数（__zse_ck / msToken / ttwid）→ 提全
├─ 返 404
│  └─ API 路径错 → 查目标站 API 文档
└─ 返 200 但内容空
   └─ 反爬 → 加 User-Agent / Referer / 加频率限制
```
