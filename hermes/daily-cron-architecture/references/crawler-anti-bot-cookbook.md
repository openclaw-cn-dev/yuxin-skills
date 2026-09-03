# 反爬绕过实战手册（2026-06-10 验证）

> **范围**：水产自媒体抓取（头条/搜狗/微博/知乎/百度/Bing/小红书/抖音等）
> **目的**：让"哪些站能抓 / 哪些站不能抓 / 怎么抓"沉淀成可复用知识
> **作者**：Hermes Agent @ 2026-06-10
> **完整版**：`C:\Users\Administrator\Desktop\知识库\反爬绕过实战手册.md`

---

## 🎯 抓取难度分级表（实战验证）

| 难度 | 来源 | 实测状态 | 备注 |
|---|---|---|---|
| 🟢 0 | **头条 so.toutiao.com** | ✅ 200 + 1.9MB | **最稳** —— 真 UA + curl |
| 🟢 0 | **搜狗 www.sogou.com** | ✅ 200 + 660KB | **次稳** —— 含知乎/百科/香哈 |
| 🟡 1 | **下厨房（搜索页）** | ⚠️ 200/403 飘忽 | 多次会 403 |
| 🟡 1 | **GitHub** | ⚠️ 国内慢 | 偶尔 timeout |
| 🟡 2 | **下厨房（详情页）** | ❌ 302→验证页 | 卡滑块 |
| 🟡 2 | **百度百科** | ❌ 302→验证页 | 卡滑块 |
| 🟡 2 | **百度搜索** | ❌ 1.5KB 验证页 | 强制安全验证 |
| 🟡 2 | **Bing 中文** | ⚠️ 进入但分词差 | 关键词被切碎 |
| 🔴 3 | **微博 s.weibo.com** | ❌ 9KB 验证页 | "Sina Visitor System" |
| 🔴 3 | **知乎 www.zhihu.com** | ❌ 650B zse-ck 验证页 | 需 zse-ck cookie |
| 🔴 3 | **小红书** | ❌ 全反爬 | X-Sign + X-LF-Token |
| 🔴 3 | **抖音搜索** | ❌ 需 X-Bogus 签名 | 加密参数 |
| 🔴 3 | **微信公众号** | ❌ 搜狗入口也卡 |  |
| 🔴 3 | **淘宝/京东** | ❌ 强反爬 |  |
| 🔴 4 | **DuckDuckGo/Yandex/Ecosia** | ❌ 国内 timeout | 网络慢 |
| 🔴 4 | **维基百科 en** | ❌ 国内 timeout | 网络慢 |

---

## 🛠️ 5 大反爬绕过技法

### 技法 1: 真 UA + 真实 Referer

```python
# ✅ 推荐
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
Referer = "https://www.google.com/"  # 或源站首页

# ❌ 不行
UA = "curl/7.68.0"  # 被识别为爬虫
```

**调用方式**：curl 直接带 `-A "$UA"` flag

### 技法 2: Scrapling StealthyFetcher (stealth 模式)

```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch(
    url,
    headless=True,
    disable_resources=True,  # 不加载图片/CSS，加速
    network_idle=True,
)
```

**反爬等级**：
- ✅ 可过：基本 JS 检测
- ⚠️ 弱：滑块验证
- ❌ 强：阿里云盾/腾讯防水墙

### 技法 3: hermes browser 工具（playwright）

```python
browser_navigate(url)  # 真浏览器 + 真渲染
browser_console(expression)  # JS 执行
browser_click(ref)
browser_type(ref, text)
```

**优势**：可处理 JS 渲染 + 点击 + 滚动
**劣势**：慢（每次 1-3 秒），需人工选 selector

### 技法 4: 反检测浏览器（playwright-extra + stealth）

```python
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    stealth_sync(page)  # 关键！
    page.goto(url)
```

### 技法 5: Cookie + 登录态

- **微博**：需 SUB/SUBP cookie（登录后浏览器 devtools 抓）
- **知乎**：需 zse-ck（更复杂，JS 加密）
- **抖音**：需 sessionid + msToken
- **小红书**：X-Sign + X-LF-Token（**目前无解**）

---

## 📚 5 大踩坑案例（实战记录）

### 坑 1: 下厨房搜索页反复 403
**现象**：第一次抓返回 200 + 10 条数据，第二次 403
**原因**：高频访问触发 IP 限流
**解决**：`time.sleep(2)` 每次抓取间隔，或换 IP 代理池

### 坑 2: Bing 中文搜索分词差
**现象**：搜 "白灼虾 做法 步骤" 返回 10 条「白」字相关
**原因**：Bing 中文分词把 "白灼虾" 切成 "白 + 灼 + 虾"
**解决**：用全名 + 引号 `"白灼虾"`（部分有效）

### 坑 3: 知乎返回 zse-ck 验证页
**现象**：HTML 只有 650 bytes，meta id="zh-zse-ck" 加密
**原因**：知乎 zse-ck 反爬，要求 JS 计算 zse-ck 后提交
**解决**：需登录 cookie + 模拟 JS 加密（**目前无解**）

### 坑 4: 微博 Sina Visitor System
**现象**：HTML 9KB，title="Sina Visitor System"
**原因**：微博强制访客系统
**解决**：必须先访问 weibo.com 拿 SUB cookie，再带 cookie 访问 s.weibo.com

### 坑 5: 头条中文 unicode 转义
**现象**：标题里残留 `\\u003cem\\u003e白灼虾\\u003c/em\\u003e`
**原因**：头条 SSR 注入 em 标签做高亮
**解决**：
```python
for em in ["\\u003cem\\u003e", "\\u003c/em\\u003e", "<em>", "</em>"]:
    title = title.replace(em, "")
```

### 坑 6: regex `\u003c` 在 shell heredoc 中被吞
**现象**：用 `cat << EOF` 写 python 文件时，`\u003c` 被 shell 当作转义
**解决**：用 execute_code 工具直接写文件，或用 `\\\\u003c` 双重转义

---

## 🔥 实战公式：什么网站用什么方法

### 水产美食/爆款（最稳）
```bash
# 头条 + 搜狗 + 抓取入库 RAG
python search_toutiao.py --source toutiao --rag "白灼虾" "对虾养殖" "循环水设备"
python search_toutiao.py --source sogou --rag "白灼虾" "对虾养殖"
```

### 设备/技术原理
- 1688 商品页 → ❌ 强反爬
- 设备厂家官网 → ✅ 多数可抓
- 行业报告 → ❌ 多数需下载

### 公司财报
- 巨潮资讯网 → ⚠️ 偶尔 200
- 东方财富 → ⚠️ 偶尔 200
- 上市公司公告 → ❌ 强反爬

### 政府/行业数据
- 农业农村部 → ⚠️ 偶有 200
- FAO 联合国粮农组织 → ✅ **很稳**（国际站，国内直连）

---

## 🧰 工具栈

| 工具 | 用途 | 安装 |
|---|---|---|
| **curl** | HTTP 抓取（**主力**） | 系统自带 |
| **Scrapling** | stealth 抓取 | `uv pip install scrapling` |
| **Playwright** | 真浏览器 | `playwright install chromium` |
| **playwright-stealth** | 反检测 | `uv pip install playwright-stealth` |
| **hermes browser 工具** | 远程浏览器 | 内置（browser_navigate 等）|
| **hermes web 工具** | 远程搜索/抓 | 内置（web_extract 等）|

---

## 🎯 30 天反爬升级路线图

### 第 1-7 天（已有，2026-06-10 完成）
- ✅ curl + 真 UA 抓头条
- ✅ 搜狗搜索 vr-title 解析
- ✅ 增量入库 RAG

### 第 8-14 天（待办）
- ⬜ Scrapling StealthyFetcher 抓下厨房详情页
- ⬜ 装 playwright + chromium + stealth
- ⬜ 抓 1688 商品页（设备选型）

### 第 15-21 天（待办）
- ⬜ 抓小红书/抖音（**需 cookie + X-Bogus**）
- ⬜ 抓微博（**需 SUB cookie**）
- ⬜ 抓知乎（**需 zse-ck**）

### 第 22-30 天（待办）
- ⬜ 抓详情页正文（不只标题）
- ⬜ 抓评论/点赞数（爆款打分）
- ⬜ 抓 30 天趋势数据（行业分析）

---

## 💡 6 条铁律（实战提炼）

1. **真 UA + 真实 Referer** → `Mozilla/5.0 ... Chrome/120 ...` + `Referer: https://www.google.com/`
2. **小站优先**：头条/搜狗 > 百度/微博/知乎
3. **小测再批量**：新站先 1-3 页看是否稳定
4. **入库 RAG 优先**：抓详情页难，**标题+摘要就够 RAG 检索**
5. **反爬强站不死磕**：投入产出比低，跳过
6. **30 天沉淀 > 实时抓取**：跑一个月攒够爆款库再做行业分析

---

## 🆘 老大实战建议

1. **优先抓头条+搜狗** —— 90% 水产爆款都在这
2. **反爬强站别死磕** —— 投入产出比低
3. **每个新网站先小测** —— 一次抓 1-3 页看是否稳定
4. **入库 RAG 优先** —— 抓详情页很难，但标题+摘要足够 RAG 检索
5. **数据沉淀 > 实时抓取** —— 跑 30 天攒够爆款库

---

*最后更新：2026-06-10*
*维护人：Hermes Agent*
*踩坑记录：实时更新*
