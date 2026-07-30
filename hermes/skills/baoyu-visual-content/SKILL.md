---
name: baoyu-visual-content
description: "Create visual content with AI image generation: article illustrations, knowledge comics, and infographics. All baoyu tools use Hermes' image_generate tool (prompt-only, returns URL), share the same output conventions, reference handling, and prompt file discipline."
version: 1.0.0
author: 宝玉 (JimLiu)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [baoyu, article-illustration, knowledge-comic, infographic, creative, image-generation]
    homepage: https://github.com/JimLiu/baoyu-skills
---

# Baoyu Visual Content — Unified Skill

All three baoyu tools (article illustrator, knowledge comic, infographic) share:
- **Tool**: Hermes' `image_generate` (prompt-only, returns image URL, not local file)
- **Reference handling**: vision_analyze for reference images → extract traits as text
- **Output discipline**: every illustration needs a saved prompt file under `prompts/` before generation
- **Download step**: always `curl` the URL from `image_generate` result to local file
- **Security**: strip secrets/credentials from source content before writing any output file
- **Slug convention**: 2-4 words kebab-case; conflict → append `-YYYYMMDD-HHMMSS`

---

## Tool Integration (shared across all three)

```python
# image_generate returns a URL, NOT a local file
result = image_generate(prompt=..., aspect_ratio="landscape")
# result contains {"url": "https://..."} or similar

# Always download to local file
terminal(command='curl -fsSL -o "/abs/path/to/output.png" "' + result["url"] + '"')
```

Aspect ratio mapping: `16:9` → `landscape`, `9:16` → `portrait`, `1:1` → `square`

---

## Article Illustrator

Trigger: user asks to illustrate an article, add images, generate illustrations, or says "为文章配图" / "illustrate article".

**Three dimensions**: Type × Style × Palette

| Dimension | Values |
|-----------|--------|
| Type | infographic, scene, flowchart, comparison, framework, timeline |
| Style | notion, warm, minimal, blueprint, watercolor, elegant |
| Palette (optional) | macaron, warm, neon — overrides style's default colors |

**Output**: `{article-dir}/imgs/`, `outline.md`, `prompts/NN-{type}-{slug}.md`, `NN-{type}-{slug}.png`

**Workflow**: Analyze → Confirm settings → Generate outline → Generate prompts → Generate images → Finalize

For the full article illustrator skill, see `references/baoyu-article-illustrator.md`.

---

## Knowledge Comic

Trigger: user asks to create a knowledge/educational comic, biography comic, tutorial comic, or says "知识漫画" / "教育漫画" / "Logicomix-style".

**Options**: Art × Tone × Layout × Aspect

| Option | Values |
|--------|--------|
| Art | ligne-claire (default), manga, realistic, ink-brush, chalk, minimalist |
| Tone | neutral (default), warm, dramatic, romantic, energetic, vintage, action |
| Layout | standard (default), cinematic, dense, splash, mixed, webtoon, four-panel |
| Aspect | 3:4 (default, portrait), 4:3 (landscape), 16:9 (widescreen) |

**Output**: `comic/{topic-slug}/`, `analysis.md`, `storyboard.md`, `characters/`, `prompts/`, `*.png`

**Presets**: ohmsha (manga+neutral), wuxia (ink-brush+action), shoujo (manga+romantic), concept-story (manga+warm), four-panel (minimalist+neutral+four-panel)

For the full knowledge comic skill, see `references/baoyu-comic.md`.

---

## Infographic

Trigger: user asks to create an infographic, visual summary, information graphic, or says "信息图" / "可视化" / "高密度信息大图".

**Options**: Layout × Style

| Option | Values |
|--------|--------|
| Layout | 21 options (bento-grid default): linear-progression, binary-comparison, hierarchical-layers, hub-spoke, funnel, dashboard, periodic-table, venn-diagram, winding-roadmap, and more |
| Style | 21 options (craft-handmade default): claymation, kawaii, storybook-watercolor, chalkboard, cyberpunk-neon, corporate-memphis, technical-schematic, pixel-art, ikea-manual, and more |

**Output**: `infographic/{topic-slug}/`, `analysis.md`, `structured-content.md`, `prompts/infographic.md`, `infographic.png`

**Keyword shortcuts**: "高密度信息大图" → dense-modules layout; "信息图" → bento-grid layout

For the full infographic skill, see `references/baoyu-infographic.md`.

---

## Shared Reference Files

| File | Source | Content |
|------|--------|---------|
| `references/baoyu-article-illustrator.md` | baoyu-article-illustrator | Full article illustrator skill |
| `references/baoyu-comic.md` | baoyu-comic | Full knowledge comic skill |
| `references/baoyu-infographic.md` | baoyu-infographic | Full infographic skill |
| `references/styles-article.md` | baoyu-article-illustrator | Article style gallery + palettes |
| `references/styles-comic.md` | baoyu-comic | Art styles + tones + presets |
| `references/styles-infographic.md` | baoyu-infographic | Layout + style galleries |
| `references/prompt-construction.md` | baoyu-article-illustrator | Prompt construction methodology |
| `references/base-prompt.md` | baoyu-comic + baoyu-infographic | Base prompt template |
