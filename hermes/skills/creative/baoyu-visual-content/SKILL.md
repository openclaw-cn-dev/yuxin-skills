---
name: baoyu-visual-content
description: Baoyu 风格视觉内容生成四件套 — 文章配图（type × style × palette 一致性）、知识漫画（educational/biography/tutorial）、信息图（21 layouts × 21 styles）、教育知识卡片（风格匹配 + 多版式 + 配色主题）。触发条件：要为文章/教程/产品生成插画、漫画、信息图、知识卡片时加载；或需要一致的视觉风格系统时。
---

# Baoyu 视觉内容生成（类级）

四种 Baoyu 风格视觉产出共用 type × style × palette 设计系统。2026-09-02 curator 合并：原 4 个独立 skill 整档收纳于 `references/`（含各自的 styles 模板库与 prompts），按产出类型取用。

## 产出类型路由

| 产出 | 读什么 | 说明 |
|---|---|---|
| 文章配图 | `references/baoyu-article-illustrator/` | type × style × palette 一致性；含 prompts/ 提示词库 |
| 知识漫画 | `references/baoyu-comic/` | educational / biography / tutorial 三类知识漫画 |
| 信息图 | `references/baoyu-infographic/` | 21 layouts × 21 styles 组合（信息图/可视化） |
| 知识卡片 | `references/knowledge-card-design/` | 教育知识卡片：风格匹配 + 多版式可视化 + 配色主题；含 scripts/ |

## 使用纪律

- 同一篇文章/项目内的多种视觉产出应锁定同一 style/palette，保持系列一致性（各 references/ 内的 style 库可交叉引用）。
- 出图前先读对应 `references/` 的 style 索引与 prompts，再调用 image_gen。