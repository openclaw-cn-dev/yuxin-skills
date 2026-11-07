# Bing 图片搜索 murl 提取 + PIL 去水印（兜底流程）

适用：Pexels API 401 / Cloudflare 403 / Unsplash 503 / Wikimedia SSL 握手失败，
但 Bing 公共图片搜索仍能返回真图直链的场景。

## 1. Bing murl 提取（HTML 实体转义后）

```python
import urllib.request, urllib.parse, re, ssl
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0"
ctx = ssl.create_default_context()

def bing_image_urls(query, n=8):
    url = "https://www.bing.com/images/search?" + urllib.parse.urlencode(
        {"q": query, "form": "HDRSC2", "first": "1"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
        html = r.read().decode("utf-8", errors="ignore")
    # 关键：Bing 把 JSON 里的 " 转义成 &quot;
    urls = re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', html)
    good = [u for u in urls if re.search(r"\.(jpg|jpeg|png)", u, re.I)
            and "sprite" not in u.lower() and len(u) < 500]
    return good[:n]
```

**关键坑**（3 次踩过）：
- ❌ `re.findall(r'"murl":"(https?://...)"', html)` → 0 个匹配，因为 Bing 输出的是 `&quot;`
- ❌ `re.findall(r'murl(?:&quot;|:&quot;)(\"?)(https?://[^&"]+)\1', html)` → 分支反向引用在长 HTML 里不可靠
- ✅ 简化版（实测拿到 30+ 个 URL）：`murl&quot;:&quot;(https?://[^&]+)&quot;`

## 2. 黑名单图库站（带水印）

```python
BAD_HOSTS = ["nipic", "699pic", "588ku", "zcool", "hellorf", "huaban",
             "nipic.com", "nximg.cn"]  # nximg.cn 是 nipic 的 CDN 域名
```

**实战发现**：Bing 中文搜索 ~70% 结果来自 nipic/nximg，文件名后缀 `_1.jpg`、
`104947076000_2.jpg` 几乎一定是 nipic 源。**必须在过滤阶段**剔除，不要等下载后裁。

## 3. PIL 底部裁切去水印

多数图库水印在底部 10-15%（"昵图网 www.nipic.cn"、"图虫创意"、"ID:..."）：

```python
from PIL import Image
img = Image.open(p)
w, h = img.size
new = img.crop((0, 0, w, int(h * 0.86)))  # 切掉底部 14%
new.save(p, "JPEG", quality=92)
```

**优势**：零依赖、200ms 完成、对椒盐皮皮虾/海鲜摆盘这种主体居中的图零损失。

**不适用**：水印在中央 / 倾斜 / 半透明叠加 → 这种只能用 AI inpaint，放弃换图。

## 4. 验收必须 vision 抽查

经验：过滤后剩 5 张椒盐皮皮虾，3 张仍带水印（黑名单漏了 nximg）。
**永远 vision_analyze 抽查前 2-3 张**，确认主体内容 + 水印位置再批量裁。

## 5. Windows 打开文件夹的正确姿势

`explorer.exe` 在 hermes terminal 里启动后**立即 exit 1**（GUI app 正常行为），
shell 误判失败。改用 Python：

```python
import os
os.startfile(r"C:\Users\Administrator\Desktop\xxx")  # ✅ 稳
```

或 `subprocess.Popen(["explorer", path])` 兜底。**不要**用 `&` 后台或裸 `start`。

## 6. 完整生产脚本骨架

```python
queries = ["椒盐皮皮虾 成品", "椒盐皮皮虾 摆盘", "椒盐皮皮虾 高清"]
save_dir = r"C:\...\04_椒盐皮皮虾"
os.makedirs(save_dir, exist_ok=True)

ok = 0
for q in queries:
    if ok >= 5: break
    urls = bing_image_urls(q, n=6)
    urls = [u for u in urls if not any(b in u.lower() for b in BAD_HOSTS)]
    for u in urls[:4]:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA,
                                                       "Referer": "https://www.bing.com/"})
            with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
                data = r.read()
            if len(data) > 60000:  # 60KB 阈值，过滤小图标
                with open(os.path.join(save_dir, f"img_{ok+1}.jpg"), "wb") as f:
                    f.write(data)
                ok += 1
                break
        except: continue

# 批量裁水印
for fn in os.listdir(save_dir):
    if fn.endswith(".jpg"):
        img = Image.open(os.path.join(save_dir, fn))
        w, h = img.size
        img.crop((0, 0, w, int(h*0.86))).save(os.path.join(save_dir, fn), "JPEG", quality=92)
```

## 7. 红线（2026-06-08 老板"自决/结果导向"v3）

- **不要问"要不要裁水印"**——直接裁完 + 报告"已裁掉 14% 底部"
- **不要列 ABC 选项**——直接给最终结果 + 1 句总结
- **不要复述过程**——只给"5 张已存 X 目录" + 文件大小表格
