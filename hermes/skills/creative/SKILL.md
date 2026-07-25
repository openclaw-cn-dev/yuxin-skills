---
name: creative
description: Creative content generation — diagrams, illustrations, infographics, animations, ASCII art, music, and design mockups. Each child skill is a distinct output format or tool. Load when you need to create visual / audio / interactive content and want to pick the right format.
version: 1.0.0
metadata:
  hermes:
    tags: [creative, design, art, illustrations, infographics, video, animation, music]
---

# Creative Content Generation

Class-level umbrella for producing creative content. Pick the child that matches your output format.

## When to load this skill

You need to produce something creative and want to discover what formats are available.

## Children (by output type)

### Static visuals
- `architecture-diagram/` — Dark-themed SVG architecture / cloud / infra diagrams.
- `excalidraw/` — Hand-drawn Excalidraw JSON diagrams (arch, flow, sequence).
- `sketch/` — Throwaway HTML mockups: 2-3 design variants to compare.
- `claude-design/` — One-off HTML artifacts (landing page, deck, prototype).
- `popular-web-designs/` — 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS.

### Illustrations & infographics
- `baoyu-article-illustrator/` — Article illustrations: type × style × palette consistency.
- `baoyu-comic/` — Knowledge comics (知识漫画): educational, biography, tutorial.
- `baoyu-infographic/` — Infographics: 21 layouts × 21 styles.

### AI-generated images / video / audio
- `comfyui/` — ComfyUI workflows: generate images, video, audio.
- `comfyui-skill-openclaw/` — Run ComfyUI workflows from any AI agent via `comfyui-skill` CLI.
- `comfyui-hermes-setup/` — Install ComfyUI + comfyui-skill-cli on macOS (Hermes Agent integration).
- `manim-video/` — Manim CE animations (3Blue1Brown-style math/algo videos).
- `manim-setup-hermes/` — Install Manim CE on macOS for Hermes Agent.
- `touchdesigner-mcp/` — Control a running TouchDesigner instance via MCP.
- `songwriting-and-ai-music/` — Songwriting craft and Suno AI music prompts.
- `pixel-art/` — Pixel art with era palettes (NES, Game Boy, PICO-8).

### Code-driven visual art
- `p5js/` — p5.js sketches: gen art, shaders, interactive, 3D.
- `pretext/` — Browser demos with `@chenglou/pretext` (DOM-free text layout).
- `ascii-art/` — ASCII art: pyfiglet, cowsay, boxes, image-to-ASCII.
- `ascii-video/` — ASCII video: convert video/audio to colored ASCII MP4/GIF.
- `algorithmic-art/` — Algorithmic art with p5.js + seeded randomness. (Parent of `algorithmic-art/`)

### Design specs & style
- `design-md/` — Author / validate / export Google's DESIGN.md token spec files.
- `theme-factory/` — Toolkit for styling artifacts with a theme. (Sibling — see top-level `theme-factory/`)

### Text content
- `humanizer/` — Humanize text: strip AI-isms and add real voice.
- `creative-ideation/` — Generate project ideas via creative constraints.

## How to choose

- **One-off mockup for review** → `sketch/`
- **Production landing page / deck** → `claude-design/`
- **Architecture diagram for a doc** → `architecture-diagram/` (or `excalidraw/` for hand-drawn feel)
- **Article illustration** → `baoyu-article-illustrator/`
- **Math / algorithm video** → `manim-video/`
- **ASCII anything** → `ascii-art/` (static) or `ascii-video/` (motion)
- **Need to generate an image** → `comfyui/`
