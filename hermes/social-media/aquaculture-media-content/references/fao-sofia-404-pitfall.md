# FAO SOFIA 404 错误页误识别为正文 — 复现与修复

**触发**：`merge.py` 抓 `https://www.fao.org/fishery/en/sofia`（蓝色转型旗舰报告页）
**首次发现**：2026-06-10 简报（每日 cron 跑出）

## 现象

curl 返回 200 + HTML，但 HTML 里**没有正文**，而是 FAO 站点的404 错误页：

```
English Français Español 中文 Русский العربية
网页未找到
您正在寻找的网页或者被移除或者不再存在。请使用搜索框获取您正在寻找的信息。

Page not found
The page you are looking for has either been moved or no longer exists.
...
```

`merge.py` 第 96 行的 `strip_html` 只剥 `<script>/<style>/<[^>]+>`，不知道这是错误页，会把上面这串当正文：

```python
paras = [p.strip() for p in re.split(r"\.\s", text) if len(p.strip()) > 80]
intro_en = ". ".join(paras[:6]) + "."  # ← 错误页内容直接进 intro_en
```

结果：今日简报「FAO 蓝色转型」section 的「摘要」字段被污染成多语言 404 文本。

## 复现

```bash
curl -L -s -A 'Mozilla/5.0' --max-time 12 \
  "https://www.fao.org/fishery/en/sofia" | grep -E "Page not found|网页未找到"
# 命中 → 当前页面不可用
```

## 临时绕过（merge.py 改法）

在 `merge.py` 第 97 行加 guard：

```python
blue = {}
bt = os.path.join(TMP, "blue_transformation.html")
if os.path.exists(bt):
    html = safe_read(bt)
    if not any(s in html for s in [
        "Page not found", "网页未找到",
        "Page non trouvée", "Página no encontrada",
    ]):
        text = strip_html(html)
        paras = [p.strip() for p in re.split(r"\.\s", text) if len(p.strip()) > 80]
        blue = {
            "title": "Towards Blue Transformation",
            "url": "https://www.fao.org/fishery/en/sofia",
            "intro_en": ". ".join(paras[:6]) + ".",
            "key": "全球渔业和水产养殖产量 2.14 亿吨 (历史新高)，预计 2030 年再增 15%",
        }
```

## 备选方案

1. **缓存上一次成功抓取的蓝色转型摘要** — `merge.py` 优先读 `~/.cache/aqua/blue_transformation_cache.txt`
2. **换 endpoint** — FAO 实际报告在 `https://openknowledge.fao.org/items/...` PDF，绕过 HTML 路径
3. **降级到 GLOB FISH overview 页**：`https://www.fao.org/in-action/globefish/` 也是稳定的统计入口

## 验证

```bash
python merge.py /tmp/foo /tmp/test.md
grep "网页未找到" /tmp/test.md && echo "❌ 仍污染" || echo "✅ 干净"
```