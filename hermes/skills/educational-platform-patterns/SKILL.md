---
name: educational-platform-patterns
description: Reusable patterns for building interactive learning/training platforms — progressive depth navigation (L1→L2→L3), card+detail views, browser TTS narration, SQLite content architecture, and HTML script editing pitfalls.
category: software-development
trigger: building self-study platforms, training tutorials, flashcard apps, knowledge bases with learning depth levels, AI learning tools, educational content platforms.
---

# Educational Platform Patterns

Reusable UX and engineering patterns for building interactive learning/training platforms.

## Progressive Depth Learning (L1→L2→L3)

Three-tier progressive disclosure for educational content:

| Level | Content | Use |
|-------|---------|-----|
| 📗 L1 基础 | Card name + description | Quick scanning |
| 📘 L2 进阶 | L1 + sub-cards / children | Depth expansion |
| 📕 L3 深入 | L2 + full detail sections | Mastery |

**Implementation steps**:
1. Add `depth` (0/1/2) + `parent_id` columns to content table
2. Render depth tabs: `📗 一轮·基础 | 📘 二轮·进阶 | 📕 三轮·深入`
3. L2+: fetch children via API, show as clickable `sub-card` elements
4. L3: fetch `term_content` (detail_md, examples, pitfalls, related_terms), render in expandable `<details>` sections
5. Cache rich content in `richCards: {}` state map to avoid re-fetching on navigation

## DB Schema for Educational Content

```sql
CREATE TABLE terms (
    id TEXT PRIMARY KEY, name TEXT, en TEXT, description TEXT,
    difficulty TEXT, depth INTEGER DEFAULT 0,
    parent_id TEXT REFERENCES terms(id),  -- sub-card relationship
    group_name TEXT, labels TEXT, sort_order INTEGER
);

CREATE TABLE term_content (
    term_id TEXT PRIMARY KEY REFERENCES terms(id),
    detail_md TEXT,         -- Markdown explanation
    examples TEXT,          -- Pipe-separated: "case1 | case2"
    common_mistakes TEXT,   -- Newline-separated
    related_terms TEXT      -- "TermName T001 | TermName T002"
);
```

## Card + Detail Panel Pattern

Two-view architecture:
- **List**: grid of compact cards with depth badges (📗📘📕 colored green/blue/red)
- **Detail**: full card with depth navigation tabs, sub-cards row, collapsible detail sections

Key CSS classes: `.depth-badge`, `.detail-section` (rotating ▶ disclosure), `.sub-cards` (flex-wrap), `.depth-tabs`

## Browser TTS Voice Narration

Zero-cost text-to-speech using browser SpeechSynthesis API. See `references/browser-tts.md` for the full engine.

- Find Chinese voice: prefer "婷婷" (zh-CN)
- Rate 0.92x, pitch 1.05x for learning clarity
- Clean markdown before speaking: strip `**`, `###`, backticks; newlines → periods
Build speech text: card name → description → detail → examples → pitfalls.
Full engine code in `references/browser-tts.md`.
UI: `🔊 听讲解` button with CSS pulse animation; click again to stop.

## Pitfall: Regex Escaping in HTML Script Tags

The patch tool double-escapes backslashes in JS regex inside HTML files. `\*` becomes `\\*` (two backslash bytes), causing regex to match literal backslash+asterisk instead of escaped asterisk.

**Fix**: Use Python direct byte manipulation:
```python
BS = 0x5c  # backslash
ST = 0x2a  # asterisk
regex_bytes = bytes([0x2f, BS, ST, BS, ST]) + b'(.+?)' + bytes([BS, ST, BS, ST, 0x2f, 0x67])
# Result: /\*\*(.+?)\*\*/g
```

Verify with `browser_console`: call `.toString()` on the function and inspect regex source.
