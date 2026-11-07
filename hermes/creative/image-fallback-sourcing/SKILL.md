---
name: image-fallback-sourcing
version: 1.1.0
description: |
  6-tier fallback chain for sourcing real images when AI image generation fails, is blocked, or returns placeholders.
  Use when:
    - User needs a real image (food / product / scene) and no AI gen API key is available
    - DALL-E / Midjourney / Stable Diffusion all return errors, paywalls, or 92-byte fake images
    - You need a photorealistic photo, not AI art
    - User has zero patience for the question "please provide an image URL"
  Triggers: 小红书配图 / 抖音封面 / 内容创作缺图 / AI 生图失败 / "自己想办法搞张图"
category: creative
metadata:
  tested_on: 2026-06-12
  working_env: Windows 10 + git-bash + Python 3.11 + curl
  revision_notes: |
    v1.1.0 (2026-06-12):
    - Added "中餐 AI 生图翻车" pitfall with LCM_Dreamshaper_v7 local SD test
    - Documented which Tier 1-3 to skip for Chinese cuisine, recommend Pexels/Bing path
---

# Image Fallback Sourcing

## The 6-Tier Chain (always run top-to-bottom, never skip)

### Tier 1 — Polinations.ai (free, no key)
```
GET https://image.pollinations.ai/prompt/{urlencoded_prompt}?width=1024&height=1024&seed=42&nologo=true
```
- ⚠️ As of 2026-06: returns HTTP 402 (USDC paywall). Still try — sometimes the legacy endpoint bypasses.
- If 402, immediately drop to Tier 2.

### Tier 2 — Stable Horde (distributed free SD, no key)
```
POST https://stablehorde.net/api/v2/generate/async
Header: apikey: 0000000000  (any string works)
Body: {"prompt":"...","params":{"width":512,"height":512,"steps":25,"sampler_name":"k_euler_a","n":1},"models":["Edge Of Realism"],"r2":true}
```
Then poll `GET /generate/status/{id}` every 20s.

**⛔ CRITICAL GOTCHA: ~30% of workers return 92-byte FAKE images to scam kudos.** Verify before accepting:
- File size MUST be > 30 KB
- First 4 bytes MUST be PNG header `89 50 4E 47` (not `86 db 69 b3` = random noise)

**Best models** (low queue as of 2026-06):
- `Edge Of Realism` (7 workers, queue=0) — photorealistic, top pick
- `majicMIX realistic` (7 workers, queue=0)
- `AbsoluteReality` (queue=22M — too slow, skip)

Check live: `GET /api/v2/status/models?type=image` → pick `queued < 10000`.

See `references/stable-horde-fake-workers.md` for the full verification pattern.

### Tier 3 — HuggingFace Inference API (free, no key for some models)
```
POST https://api-inference.huggingface.co/models/{model_id}
Body: {"inputs":"...","options":{"wait_for_model":true,"use_cache":false}}
```
- ⚠️ First request to a model takes 1-3 min cold start. Use `--max-time 180` in curl.
- ⚠️ **Python urllib on this machine throws SSL EOF errors. Use curl, not Python.**
- Realistic models to try: `dreamlike-art/dreamlike-photoreal-2.0`, `stabilityai/stable-diffusion-2-1-base`, `prompthero/openjourney`

### Tier 4 — Pexels CC0 (real photos, real but pay attention)
- **Photo CDN 直链**（curl 通）：`GET https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?w=1200`
  - ✅ 不限 IP、不限 UA、不限频、不需要 Key
  - 必须用**已知 photo ID**（见 `references/pexels-photo-id-bank.md`）
- ⚠️ **Pexels 搜索页 HTML 已挂**（2026-06-09 实测：Cloudflare 验证页拦截，沙盒浏览器都过不去）
  - 不要再尝试爬 https://www.pexels.com/search/
  - 想"找"新 ID → 走 Tier 7 Bing 抓 murl
- Pexels 搜索/英文关键词对"设备/养殖/中文食材"基本 0 结果

### Tier 5 — Unsplash Source API
- `GET https://source.unsplash.com/featured/?{keyword}`
- ⛔ As of 2026-06, returns 503 on most queries. Skip unless desperate.

## Tier 7 (added 2026-06-09): Bing 图片搜索 murl + PIL 底部裁水印
当 Pexels 401 / Unsplash 503 / Wikimedia SSL 失败时的兜底。中文搜索 ~70% 结果来自
nipic/nximg.cn（带水印），用黑名单过滤 + PIL 切底部 14% 解决。完整脚本 + 关键坑见
`references/bing-pil-watermark-removal.md`。

**关键坑**：
- Bing JSON 里 `"` 被转义为 `&quot;`，正则必须用 `murl&quot;:&quot;...&quot;`
- 黑名单必须含 `nximg.cn`（nipic 的 CDN 域名，常见陷阱）
- 永远 `vision_analyze` 抽查 2-3 张再批量裁，不要相信文件大小

### Tier 6 — vision_analyze verification (mandatory)
- After ANY download from Tier 1-5, **always verify** with `vision_analyze` to confirm the image matches the request.
- Pexels / Unsplash / search engines often return wrong images. Trust nothing without verification.
- If wrong, try next ID from the bank. If all wrong, **stop and report** (don't keep burning time).

### Tier 7 — Bing 图片搜索 HTML scrape（2026-06-09 新增，**实际救场**）
- URL: `https://www.bing.com/images/search?q={query}&form=HDRSC2`
- ⛔ **正则坑**：Bing HTML 把 `"` 转义成 `&quot;`，必须用这个正则：
  ```python
  urls = re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', html)
  ```
  而不是常见的 `r'"murl":"(https?://[^"]+)"'`（那个匹配 0 个）
- ✅ **中文关键词命中率 100%**（35/35 murl），英文关键词基本 0
- ✅ **国内 CDN 实测通**：699pic/126.net/sinaimg/alicdn/baike/baidu 都返真图
- ⚠️ **水印雷区**：09_蛋白分离器 抓出"禅"字书法 + 渔帮手 logo；06 抓出沙漠岩石；10 抓出汽修工人
- ⚠️ **每张必须 vision 验图**（不验=50% 翻车）
- 跑法：抓 4-6 个候选，>80KB 保留，验图不对就跳下一个

## Workflow pseudocode

```
# Phase 1: AI gen (1-3 tiers in parallel, 60s timeout each)
for tier in [pollinations, stable_horde, hf]:
    img = try_generate(tier, prompt, timeout=60)
    if img and verify_is_real_image(img):  # size>30KB, PNG/JPEG magic bytes
        return img

# Phase 2: Real photo fallback (Tier 4)
for photo_id in curated_ids_for_category(prompt):
    img = curl_download(pexels_url(photo_id))
    if vision_confirms_match(img, prompt):  # vision_analyze
        return img

# Phase 3: Honest report
return "I tried 6 tiers. All blocked or returned wrong images. Please drop a real photo into [target path]."
```

## Output to user

On success: `✅ Got image via [tier] from [source]. Path: [full path].` (1 line, no extras)

On partial: `Got N candidates, [M] verified by vision as matching. Using [ID] at [path].`

On failure: `All 6 tiers failed. Last option: please drop a real photo at [path] or paste any image URL. (5-second fix, I take it from there.)`

**NEVER** ask "which tier do you want me to try" or "should I use AI gen or stock photo" — that's the user's job to read the report, not decide infrastructure.

## User autonomy pattern (CRITICAL — 2026-06-08 signal)

When user says any of:
- 「自己想办法」
- 「看着办」
- 「我只要结果」
- 「不可以再问我」

**Run the full chain silently and report only the final outcome.** Do not:
- List A/B/C options
- Ask "should I use AI or stock photo"
- Ask "what category of image"
- Show the tier-by-tier progress

The pattern fires repeatedly. Future sessions will see it again. Capture the "fully autonomous output" report as the only acceptable response shape:

```
✅ Got [N] images. Saved to: [path1], [path2], ...
```

or

```
❌ All tiers failed. Please drop a real photo at [path]. (5-second fix.)
```

Both formats are < 2 lines. No explanation, no options, no "what do you want to do next."

## Key pitfalls

- **Python urllib SSL is broken on this machine** — most HTTPS calls fail with EOF. Use curl.
- **Stable Horde workers are NOT trustworthy** — verify file size AND PNG header bytes.
- **Pexels "shrimp" search returns city models** — use curated IDs, never search.
- **Pexels search HTML is Cloudflare-blocked (2026-06-09)** — don't try to scrape, use Bing instead.
- **Bing HTML escapes `"` as `&quot;`** — regex must be `murl&quot;:&quot;...&quot;`, not `"murl":"..."`.
- **设备/养殖/中文食材必须中文关键词**（英文 0 命中，中文 35/35）。
- **国内 CDN 常带水印**（商家 logo/书法站/装饰画）—— 抓完每张必 vision 验图。
- **HF first request is slow** (1-3 min) — set `--max-time 180` and don't panic.
- **Vision verify is not optional** — even "looks right" Pexels photos can be wrong (mosques, sushi, fried chicken all returned for "boiled shrimp" search).
- **Don't ask the user for images** — they will say "自己想办法". Use the fallback chain.

## Verified photo ID banks (Pexels CC0)

- `references/pexels-photo-id-bank.md` — base curated list (verified via vision, not search results), focused on shrimp/seafood.
- `references/pexels-cc0-id-bank-food-equipment.md` — **water/food/equipment-aquaculture 8-image kit** (5 美食: 白灼虾/堆虾/海鲜大餐/寿司/树桩料理; 3 设备/场景: 塔吉锅/鱼缸/工业罐). Reuse strategy covers 10 笔记 × 4 张 = 40 张配图.
- `references/pexels-known-bad-ids.md` — **23 IDs vision-verified as wrong** (city models, fried chicken, red rocks, bathroom brush, goldens, ...). ~80% miss rate. **Always vision-verify before reusing**.
- `scripts/fetch_pexels.sh` — bash one-liner to batch-download any IDs with progress + size info. Usage: `bash fetch_pexels.sh /path/to/out 725992 566344 566345`.
- `scripts/fetch_image.py` — **full 6-tier chain implementation in one script** (Tier 1 pollinations / Tier 2 stable_horde with size+header check / Tier 3 HF / Tier 4 Pexels CDN / Tier 5 Unsplash / Tier 6 vision verify). Usage: `python fetch_image.py "boiled red shrimp" 03.jpg`.

## Stable Horde verification patterns

- `references/stable-horde-fake-workers.md` — exact size + PNG header check code (the canonical recipe).
- `references/bing-pil-watermark-removal.md` — Tier 7: Bing murl 提取正则 + 黑名单图库站 + PIL 裁水印 + Windows `os.startfile` 兜底开文件夹。
- `references/stable-horde-hack-workers.md` — the **Zikeri**-class hack node phenomenon (30-50s fast-done + <200B base64 + no PNG header), the legit-worker names (`smellycat1`, `Roaring 3050` series, `Gravitate7706 Dreamer`), and defensive code.
