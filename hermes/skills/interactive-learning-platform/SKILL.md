---
name: interactive-learning-platform
description: "Build self-contained zero-dependency interactive learning platforms. FastAPI + SQLite + vanilla SPA. Demand-driven architecture with career paths, term cards, multi-type quizzes, SM-2 spaced repetition, and gamified dashboard. PWA-ready mobile-first responsive design."
---

# Interactive Learning Platform

Build a self-contained interactive learning platform. One directory: database, API, frontend, data. `bash start.sh` to launch.

## Architecture

```
project/
├── db/      ← SQLite (WAL mode)
├── server/  ← FastAPI (app.py + seed.py)
├── web/     ← Vanilla JS SPA + PWA manifest + SW
├── data/    ← terms-full.json + career-paths.json
└── start.sh ← One-command launcher
```

## Core Modules

### Demand-Driven Engine
Career path → reverse-designed prerequisite cards → Bloom-ordered stages. `--minimal` compresses to 2-3 core stages (15-20 cards). User picks role, engine maps to prerequisite concepts.

### Knowledge Cards
Each card: name, en, one-sentence desc, difficulty, layout type, 3-5 labels, group. Content filled later via `/api/terms/{id}/content`.

### Multi-Type Quizzes
Auto-generated from card content. True/false (swap key terms for distractor) and multiple choice (other cards' descriptions as wrong options). Post-quiz submission records per-card correctness.

### SM-2 Spaced Repetition
Quality 0-5 scoring. UI: Hard (2) / Got it (4) / Easy (5). Formula adjusts easiness factor and interval. Review schedule auto-computed per card.

### Dashboard
Stats (learned/streak/pct/quizzes), 7-day learning curve bars, per-group progress with color coding, auto-unlocked achievements at milestones, weak areas from quiz data, due review list.

### Content Ecosystem
Extension tables for AI figures hall, industry tree (upstream/midstream/downstream), creator library. All served via API with grouped display.

## Database

Core tables: terms, career_paths, path_phases, path_terms, learning_log, learning_session, quiz_log, daily_streak, achievements, term_content. Extension: ai_figures, ai_industry_tree, ai_creators.

For reseed: `PRAGMA foreign_keys=OFF` then DELETE + re-INSERT, then `PRAGMA foreign_keys=ON`.

## Mobile Design

Three breakpoints. <640px: bottom tab nav, hamburger sidebar, swipe cards, single-column. 640-1024: narrower sidebar, 2-column grids. >1024: full sidebar, multi-column. PWA with manifest + service worker. Show LAN IP on startup.

## Key Pitfalls

1. SQLite ON CONFLICT fails without UNIQUE constraint — use SELECT-then-INSERT/UPDATE
2. Foreign key cascade blocks reseed — disable temporarily with PRAGMA
3. FastAPI StaticFiles must mount AFTER all API routes
4. Vanilla JS keeps project self-contained — avoid frameworks for this class of project

## Asset Pipeline

For bulk image generation and organization workflows (4-stage pipeline, term-based naming, verification scripts), see `references/image-asset-organization.md`.
