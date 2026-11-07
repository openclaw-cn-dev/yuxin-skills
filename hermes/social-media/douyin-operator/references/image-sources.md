# 小红书配图源战报（2026-06-09 设备篇实战更新 v3）

## 🆕 v3 新增：设备/养殖类主题（2026-06-09 验证）

### 核心发现
- ❌ **英文关键词基本 0 结果**：`indoor recirculating aquaculture` / `RAS facility` / `protein skimmer` / `shrimp farm pond` 全部无 murl 命中（Bing 中文环境优先）
- ✅ **中文关键词一抓一个准**（验证 5 个设备主题 100% 命中）：
  - `工厂化循环水养殖 车间` → 35 murl
  - `对虾养殖塘 增氧机` → 35 murl
  - `海鲈鱼 鲜活` / `罗非鱼 鲜活` → 35 murl
  - `蛋白分离器 鱼缸` → 35 murl
  - `水产养殖 水泵 设备` / `池塘增氧机 叶轮` → 35 murl
- 🔴 **国内 CDN 水印雷区**（必须 vision 验图）：
  - 09_蛋白分离器 img1：书法"禅"字装饰画（搜"鱼缸"被书法站污染）
  - 09_蛋白分离器 img2：5 格过滤腔体图有"渔帮手"商家水印（右下+多角）
  - 06_工厂化循环水：原版沙漠岩石+蓝球（"循环水"搜到地理纪录片）
  - 10_循环水设备价格：原版是汽修工人（"水泵 设备"搜到工业水泵）
- ✅ **修复方法**：英文产品名 + 中文应用场景 混搭，>80KB 才保留，跑完每张 vision 验图

### 设备类关键词模板（复制即用）
```python
EQUIP_QUERIES = {
    "工厂化循环水": [
        "工厂化循环水养殖 车间",
        "室内循环水养殖 鱼池",
        "循环水养殖设备 水泵",
        "工厂化养鱼车间",
    ],
    "蛋白分离器": [
        "protein skimmer",           # 英文产品名
        "reef aquarium sump",        # 英文应用场景
        "saltwater filtration system",
        "cone protein skimmer aquarium",
    ],
    # 通用：英文产品名 + 中文应用场景 混搭命中率最高
}
```

### 战果（2026-06-09 设备篇 5 篇 ×4 张 =20 张）
| 主题 | 图1 | 图2 | 图3 | 图4 | 备注 |
|---|---|---|---|---|---|
| 06_工厂化循环水 | ✅233KB 厂区 | ✅208KB 车间 | ✅169KB 设备 | ✅233KB 车间 | 全过 |
| 07_对虾养殖 | ✅94KB 塘口 | ✅126KB 活虾 | ✅94KB 工厂 | ✅94KB 投饵 | 全过 |
| 08_海鲈vs罗非 | ✅891KB 海鲈 | ✅31KB 罗非（白底）| ✅283KB 市场 | ✅328KB 冰鲜 | 全过 |
| 09_蛋白分离器 | ✅307KB 桶式（带商家水印） | ✅363KB 5 格过滤（多水印） | ✅86KB 系统 | ✅127KB 锥形 | 需去水印 |
| 10_循环水设备价格 | ✅177KB 水泵 | ✅172KB 增氧机 | ✅259KB 生物滤池 | ✅177KB 设备 | 全过 |

**水印解决方案**（待办，未做）：用 nano-pdf/imagemagick 去水印，或避开渔帮手/书法站 CDN。

---

# 小红书配图源战报（2026-06-08 实战更新 v2）

## 🎯 老大红线
老大说 **"你想办法 直到任务完成"** / **"自己弄"** / **"别再问我"** → 自循环死磕，不停顿问"怎么办"，**直到图落盘或被硬障碍堵死**才汇报。

## ✅ 唯一真活路径（2026-06-08 验证，必走）

### 🅰️ curl 直下已知 Pexels photo ID（**通杀**）
```bash
curl -L -A 'Mozilla/5.0' --max-time 12 -o 03.jpg \
  "https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?w=1200"
```

**为什么这能成**：
- Pexels CDN 不限 IP、不限 UA、不限频
- 不需要 API Key、不需要登录
- 一次能下 10-15 张
- 已知虾类好 ID：
  - **725992**（3 只橙红白灼虾铁盘，配 01 封面完美 ✅）
  - 2098085、3842911、1860208、1051143、9609836、1267320

**为什么之前 notes 写"Pexels 限流"是错的**：
- 那是 Bing→Pexels 搜索结果页 HTML 时被沙盒出网拦的，**不是 Pexels 本身限流**
- curl 直下 photo/{id} 这种 CDN 路径完全没事

### 工作流（5 步，2 分钟搞定 1 张图）
1. **找候选 ID**：用 Pexels 站内搜索拿 10-15 个 ID（老大浏览器复制，或用 web search 拿公开 IDs）
2. **批量 curl**：
   ```bash
   for id in 725992 2098085 3842911 1860208 1051143 9609836 1267320; do
     curl -L -A 'Mozilla/5.0' --max-time 12 -o "03_cand_${id}.jpg" \
       "https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?w=1200"
   done
   ```
3. **vision 验图**（每张必问）：
   ```python
   vision_analyze(image_url="...\\03_cand_725992.jpg",
                  question="是熟白灼虾（橙红色）吗？什么做法？")
   ```
4. **挑最匹配的** → `cp 03_cand_725992.jpg 03_done.jpg`
5. **清理候选**：`rm 03_cand_*.jpg`

## ❌ 已废路径（2026-06-08 二次确认，2026-06-09 三次确认，别再试）

| 源 | 死因 |
|---|---|
| **Python urllib + ssl** | **SSL 全部超时**（同台机器 curl 通，Python SSL 挂） |
| Pexels 搜索页 HTML | 403 Forbidden / Cloudflare 验证页 |
| Unsplash `source.unsplash.com` | 2024-05 下线，503 |
| Pixabay HTML 搜索 | 403 |
| Wikimedia Commons API | SSL 超时 |
| LoremFlickr / Picsum / Civitai / Imgur | 0 字节 / 沙盒出网拦 |
| 699pic / 千图 / 阿里 CDN | 403 / 反爬 / 防盗链 |
| 百度图片 / bkimg | 0 字节 / 反爬 |
| 小红书 / 下厨房 / 美食站 | 403 / 要登录 / 防盗链 |
| Pollinations CloudFront | 排队满 / API Key 限流 / 402 paywall |
| 搜狗图片 / 谷歌 lh3 | 反爬 |
| **Bing murl 正则 1**（`"murl":"..."`） | 匹配 0 — Bing HTML 把 `"` 转义成 `&quot;` |
| **Bing murl 正则 2**（`murl:"..."`） | 匹配 0 — 同上 |
| ✅ **Bing murl 正则 3**（`murl&quot;:&quot;...&quot;`） | **匹配 35** — 唯一正确 |

**关键教训**：**别再花 30 分钟试"免费 API 自动抓"了**。要么用 🅰️（Pexels+curl），要么让老大自己存图。

## 🔁 备选方案（按老大耐心降序）

### 🅱️ 老大浏览器手动存图
- 路径：`C:\Users\Administrator\AppData\Local\hermes\xhs_<topic>\0{1,2,3,4}_<用途>.jpg`
- 5 分钟搞定，零折腾（最后才考虑）

### 🅲️ AI 生图（需要 Key）
- ComfyUI 本机（NVIDIA 6GB+ 显存）
- OpenAI DALL-E（需 OPENAI_API_KEY）
- Pollinations 付费（$5/月）

## 🔴 抓图 5 大坑（必看）

1. **关键词必须带品类大词**：`{品类} {大词} 高清`（如"基围虾 海鲜 高清"），别只用动词（"白灼""下锅"）
2. **设备/养殖类必须中文关键词**（"蛋白分离器"），英文 "protein skimmer" 0 命中
3. **每张图必须 vision 验图**（用 `vision_analyze` 问"是虾吗"/"是设备吗"），699pic 返的可能是鸡蛋/馄饨/篮球/书法"禅"字
4. **沙盒路径用 Windows 原生**（`C:\Users\...\`）或 `os.environ['TEMP']`，**别用 `/c/...`**
5. **Bing murl 解析正则**：用 `murl&quot;:&quot;` 不用 `"murl":"`（HTML 实体编码差异）

## 📂 配图目录规范（**2026-06-08 老大定**）

**存盘位置**：`C:\Users\Administrator\Desktop\小红书\<主题>\`

```
C:\Users\Administrator\Desktop\小红书\<主题>\
├── 笔记正文.md      # 标题 + 正文 + 标签（可直粘小红书）
├── 01_cover.jpg     # 封面
├── 02_<步骤>.jpg    # 步骤
├── 03_<步骤>.jpg    # 步骤
└── 04_<成品>.jpg    # 成品/蘸料
```

**历史路径（已废）**：`C:\Users\Administrator\AppData\Local\hermes\xhs_<topic>\` — 别再用。

## 🧪 验图 prompt 模板
```python
vision_analyze(
    image_url=path,
    question="是{品类}吗？什么做法？描述画面"
)
```
返"不是"就跳过，返"是的"就保留。
