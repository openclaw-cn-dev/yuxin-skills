---
name: openalex-aquaculture-paper-search
description: '老莫 cron 论文检索的 OpenAlex 查询策略包 — STRICT/宽泛 双词表过滤、批量查询、DOI 去重、Crossref 二次验证、publication_date 排序技巧、Zenodo/Figshare 假论文辨别。触发条件: 老莫 cron 启用论文检索;运行 OpenAlex/Semantic Scholar/Crossref API 检索 AI×水产养殖相关论文;需要 recall 检索策略词表;已知 DOI 去重需求。'
license: MIT
metadata:
  author: 渔芯科技
  version: "1.0.0"
  parent_skill: laomo-knowledge (default profile)
---

# OpenAlex × 水产养殖论文检索策略

> 老莫 cron 论文检索核心策略包。从 laomo-knowledge §3.5 提取为可独立调用的工具包。
> 配合 `laomo-knowledge` 主 skill 使用。

## 快速开始

```bash
# 默认严格双条件检索 (R20+ 推荐)
python3 /Users/hua/.hermes/skills/openalex-aquaculture-paper-search/scripts/strict_filter.py \
  "machine learning aquaculture water quality" \
  "deep learning fish disease detection"
```

## 词表版本

### STRICT_AI (16 词) — 仅 ML/DL 明确方法名
```python
STRICT_AI = [
    "machine learning", "deep learning", "neural network", "random forest",
    "xgboost", "yolo", "transformer", "lstm", "cnn", "rnn", "gru",
    "computer vision", "reinforcement learning", "svm", "gradient boosting",
    "anomaly detection", "object detection", "segmentation",
]
```

### STRICT_AQUA (14 词) — RAS+海淡水主要养殖种
```python
STRICT_AQUA = [
    "aquaculture", "recirculating", "tilapia", "salmon",
    "catfish", "trout", "carp", "shrimp", "prawn",
    "sea bass", "seabream", "macrobrachium",
    "hatchery", "biofilter",
]
```

### 宽泛 AI_KEYWORDS (14 词,含 model/prediction/sensor)
仅在 STRICT precision 低时启用 (经验:宽泛 precision 通常 <50%)。

## 已知陷阱

| 陷阱 | 模式 | 应对 |
|---|---|---|
| **宽泛过滤污染** | `model`/`prediction`/`modeling` 命中非 ML 论文 | 用 STRICT_AI 替代 |
| **`water quality` 通用词霸榜** | OpenAlex top 5 全是植物病害/遥感水质 | 加 `+ aquaculture` 限定 + STRICT 词表 |
| **`RAS` 缩写污染** | 癌症 RAS 基因/工业 RAS 霸榜 | 用 `recirculating aquaculture system` 全称 |
| **`RAS + aquaculture` 双词** | 经常混入污水处理/数字孪生非水产 | 后过滤层做 aqua+AI 双条件 |
| **`precision feeding` 通用词** | 精准农业/食品工程污染 | 改用 `uneaten feed detection` / `FCR prediction` |
| **Zenodo 假论文** | 占位符作者 + 空 description | §3.1 Zenodo 4 步鉴别法 |
| **Figshare DUP** | `type=other` + 与主论文作者完全一致 | §3.1.3 Figshare 2 强信号 |
| **OpenAlex 503** | "Search cluster recovers from heavy load" | §3.5.11 SOP: 等待 60-90s 重试,503 ≠ 400 ≠ 429 |
| **OpenAlex 400 (filter)** | `filter=publication_year:2024,2025,2026` 错误 | 用 `2024-2026` 范围或 `2024|2025|2026` pipe |
| **OpenAlex publication_date 排序霸榜** | top 5 全是最新 CS 通用论文 | 改用 `sort=relevance_score:desc` |

## 验证流程

1. OpenAlex 检索 (本文档脚本)
2. DOI 去重 vs `/Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt`
3. 双条件 STRICT_AI × STRICT_AQUA AND 判定
4. Crossref API 验证:`https://api.crossref.org/works/<DOI>` → 200 OK ✅
5. 重建 OpenAlex 倒排索引摘要 或 DOI redirect HTML 拿摘要
6. Zenodo/Figshare 假论文鉴别 (按 DOI 前缀)
7. 写入 known_dois.txt (按 §3.6 "Write file FIRST, then report" 协议)

## 配套

- `scripts/strict_filter.py` — 主要 STRICT 双条件过滤脚本
- `references/r20_strict_filter_evidence.md` — R20 实证对比数据
- `references/known_dois_protocol.md` — known_dois.txt 写入契约 (§3.6)
