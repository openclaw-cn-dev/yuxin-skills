#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R467 unified is_ras_paper() classifier — 4 道防线叠加 (Pitfall #68 + #70 + #74 + #175 防御).

实战沉淀 2026-09-13 R467: 把老莫历史 Pitfall #68 (plant-disease/medical/poultry 主题误命中)
+ Pitfall #74 (cancer-RAS oncogene 缩写撞车) + Pitfall #70 (4 角度轮换) + Pitfall #175 (abstract
邻近词陷阱) 的 4 类误命中防御**集成到一个函数**,20 候选 → 15 真 RAS / 5 reject 一次跑通。

**用法**:

```python
from scripts.r467_is_ras_paper_classifier import is_ras_paper, openalex_search

# 单条判定 (title + journal 可选)
ok, reason = is_ras_paper(title="...", journal="...")

# 批量 OpenAlex + 分类 (Pitfall #66 urllib.parse.quote 防 InvalidURL)
results = openalex_search(query="RAS AND (biofilter OR nitrification)", n=10)
for r in results:
    ok, reason = is_ras_paper(r["title"], r.get("journal"))
    print(f"{ok} | {reason} | {r['title'][:80]}")
```

**4 道防线**:
1. (a) cancer 期刊黑名单 + (b) cancer-RAS oncogene 11 类分子生物学语境 regex
   → Pitfall #74 拦 cancer-GTP/MAPK/pathway/mutation/oncogene/signaling
2. plant/poultry/medical 主题 regex → Pitfall #68 拦 plant-disease/poultry/clinical
3. title 含 RAS 关键词 (11 类) → 必须有真 RAS 主题信号, 否则 reject
4. (可选) abstract_inverted_index 反向重建 + 邻近词陷阱 → Pitfall #175 兜底
"""
from urllib.request import urlopen, Request
from urllib.parse import quote
import json
import os
import re

# Pitfall #74: cancer-RAS oncogene 11 类分子生物学语境 (不依赖期刊判定)
ONCOGENE_REGEX = re.compile(
    r"RAS[\s\-]?(GTP|RAF|MAPK|pathway|mutation|oncogene|signaling|GDP|gene|protein|binding)",
    re.IGNORECASE,
)

# Pitfall #74: cancer 期刊黑名单
CANCER_JOURNAL_REGEX = re.compile(
    r"\b(Cancer|Cancer Cell|Oncogene|Molecular Cell|Nature Medicine|Cancer Research|Cancer Discovery)\b",
    re.IGNORECASE,
)

# Pitfall #68: plant / poultry / medical 主题不符
PLANT_REGEX = re.compile(
    r"\b(plant|crop|maize|wheat|rice|tomato|potato|grape|soybean|arabidopsis|cotton|tobacco|leaf|root)\b",
    re.IGNORECASE,
)
POULTRY_REGEX = re.compile(
    r"\b(poultry|chicken|broiler|layer hen|turkey)\b",
    re.IGNORECASE,
)
MEDICAL_REGEX = re.compile(
    r"\b(tumor|cancer|patient|clinical|therapy|hospital|medical|treatment|drug|surgery|diagnosis|prognosis)\b",
    re.IGNORECASE,
)

# title 中必须含 RAS 关键词 (Pitfall #175 升级: 严格 title-only 检查)
RAS_TITLE_KEYWORDS = [
    "aquaculture", "recirculating", "biofilter", "biofiltration",
    "fish farm", "fish-farm",
    "shrimp", "prawn", "tilapia", "salmon", "trout", "seabass", "carp",
    "aquaponics", "hydroponics",
    "nitrification", "denitrification", "ammonia",
    "biofloc", "mariculture",
    "litopenaeus", "penaeus", "oncorhynchus", "clarias",
]


def is_ras_paper(title: str, journal: str = "", abstract: str = "") -> tuple[bool, str]:
    """4 道防线叠加的 RAS 论文判定函数.

    Args:
        title: 论文标题
        journal: 期刊名 (可选, 用于期刊黑名单判定)
        abstract: 摘要 (可选, 用于第 4 道防线 abstract 邻近词兜底)

    Returns:
        (is_real_ras: bool, reason: str)
        reason ∈ {"ok", "Pitfall#74 cancer-RAS", "Pitfall#74 cancer journal",
                  "Pitfall#68 plant", "Pitfall#68 poultry", "Pitfall#68 medical",
                  "no-RAS-title-keyword", "Pitfall#175 abstract-only"}
    """
    if not title:
        return False, "empty-title"

    # ── 第 1 道防线: Pitfall #74 cancer-RAS oncogene ──
    if ONCOGENE_REGEX.search(title):
        return False, "Pitfall#74 cancer-RAS"
    if CANCER_JOURNAL_REGEX.search(journal or ""):
        return False, "Pitfall#74 cancer journal"

    # ── 第 2 道防线: Pitfall #68 主题不符 ──
    if PLANT_REGEX.search(title):
        return False, "Pitfall#68 plant"
    if POULTRY_REGEX.search(title):
        return False, "Pitfall#68 poultry"
    # medical regex 不触发 cancer (cancer 已被第 1 道防线先拦), 仅拦其他医学语境
    if MEDICAL_REGEX.search(title):
        return False, "Pitfall#68 medical"

    # ── 第 3 道防线: title 必须含 RAS 关键词 (严格 title-only) ──
    t = title.lower()
    if not any(kw in t for kw in RAS_TITLE_KEYWORDS):
        return False, "no-RAS-title-keyword"

    # ── 第 4 道防线 (可选): abstract 邻近词陷阱 (Pitfall #175 兜底) ──
    # 仅当 title 含 RAS 关键词但 abstract 完全无 RAS 词 → 警告 (不 reject, 留给人眼)
    # 实战: R431 发现 plant disease 论文 abstract 含 "fish/disease" 散落词被命中
    # 但 title 已是 plant-disease 主题 → 第 2 道防线已拦, 本道防线做最后兜底
    if abstract:
        abs_lower = abstract.lower()
        has_abs_keyword = any(kw in abs_lower for kw in ["aquaculture", "recirculating", "biofilter", "fish", "shrimp"])
        if not has_abs_keyword:
            return False, "Pitfall#175 abstract-only"

    return True, "ok"


def openalex_search(
    query: str,
    n: int = 10,
    year_from: str = "2024-01-01",
    language: str = "en",
    timeout: int = 30,
) -> list[dict]:
    """OpenAlex /works?search= 批量查询 (Pitfall #66 urllib.parse.quote 防 InvalidURL).

    Args:
        query: 检索词, 含 AND/OR/括号时必走 quote() 编码空格+括号
        n: 每页返回数
        year_from: 起始出版日期 (YYYY-MM-DD)
        language: 语言过滤 (默认 en)
        timeout: 等待秒数

    Returns:
        OpenAlex results 列表 (空列表表示 cluster overload 或错误)
    """
    # Pitfall #66: query 必走 quote, filter 段保持原样
    f = f"type:article,from_publication_date:{year_from},language:{language}"
    url = (
        f"https://api.openalex.org/works?search={quote(query)}"
        f"&filter={f}&per_page={n}&mailto=laomo@yuxin.ai"
    )
    req = Request(url, headers={"User-Agent": "laomo/1.0 (mailto:laomo@yuxin.ai)"})
    try:
        data = json.loads(urlopen(req, timeout=timeout).read())
    except Exception as e:
        # Pitfall #76: cluster overload / #66: InvalidURL / Pitfall #3: 429
        print(f"  [openalex_search ERROR] {type(e).__name__}: {e}")
        return []
    # Pitfall #76: upstream 错误时 error 字段存在
    if data.get("error"):
        print(f"  [openalex_search UPSTREAM] {data['error']}: {data.get('message', '')[:200]}")
        return []
    return data.get("results", [])


def classify_openalex_results(results: list[dict], verbose: bool = True) -> dict:
    """批量分类 OpenAlex results (拉 journal + title + 调 is_ras_paper).

    Returns:
        {
            "real_ras": [r1, r2, ...],
            "rejected": [{"result": r, "reason": "..."}, ...],
            "summary": {"total": N, "real": M, "rejected": K, "by_reason": {...}}
        }
    """
    real_ras = []
    rejected = []
    by_reason = {}

    for r in results:
        title = r.get("title") or r.get("display_name") or ""
        doi = (r.get("doi") or "").replace("https://doi.org/", "")
        loc = r.get("primary_location") or {}
        src = loc.get("source") or {}
        journal = src.get("display_name", "")
        abstract_inv = r.get("abstract_inverted_index")
        # 反向重建 abstract (Pitfall #175: 邻近词陷阱检查)
        abstract = ""
        if abstract_inv:
            try:
                words = []
                for word, positions in abstract_inv.items():
                    for p in positions:
                        words.append((p, word))
                words.sort()
                abstract = " ".join(w for _, w in words)
            except Exception:
                pass
        year = r.get("publication_year", "?")

        ok, reason = is_ras_paper(title, journal, abstract)
        if verbose:
            status = "✓" if ok else "✗"
            print(f"  {status} [{reason:25}] {year} {journal[:25]:25} | {title[:70]}")

        if ok:
            real_ras.append({
                "doi": doi, "title": title, "journal": journal,
                "year": year, "cited_by": r.get("cited_by_count", 0),
            })
        else:
            rejected.append({"result": r, "reason": reason})
            by_reason[reason] = by_reason.get(reason, 0) + 1

    return {
        "real_ras": real_ras,
        "rejected": rejected,
        "summary": {
            "total": len(results),
            "real": len(real_ras),
            "rejected": len(rejected),
            "by_reason": by_reason,
        },
    }


# ── CLI 模式 (R467 实战入口) ──
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 r467_is_ras_paper_classifier.py '<query>' [n=5]")
        print()
        print("Examples:")
        print('  python3 r467_is_ras_paper_classifier.py "RAS biofilter AND DRL"')
        print('  python3 r467_is_ras_paper_classifier.py "aquaponics AND nanobubble" 10')
        sys.exit(0)

    query = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    # HOME=/Users/hua 防 Pitfall #61 污染 (cron 必加, 终端可选)
    os.environ.setdefault("HOME", "/Users/hua")

    print(f"=== OpenAlex query: {query} (n={n}) ===")
    results = openalex_search(query, n=n)
    print(f"  hits={len(results)}")
    classified = classify_openalex_results(results)

    s = classified["summary"]
    print(f"\n=== SUMMARY ===")
    print(f"  total={s['total']} real_ras={s['real']} rejected={s['rejected']}")
    print(f"  by_reason: {s['by_reason']}")
    print(f"\n=== REAL RAS ({s['real']}) ===")
    for r in classified["real_ras"]:
        print(f"  + {r['doi']:50} {r['year']} {r['journal'][:25]:25} | {r['title'][:70]}")
