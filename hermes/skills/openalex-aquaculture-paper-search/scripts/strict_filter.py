#!/usr/bin/env python3
"""STRICT double-condition filter for OpenAlex AI×aquaculture papers.

Use when first-pass wide filter (AI_KEYWORDS containing "model", "prediction",
"sensor", "monitoring") returns precision <50%.

Empirically validated on 2026-08-14 (laomo cron R20):
  - Wide filter on 25 keywords -> 4 candidates, 0 true AI papers (precision 0%)
  - STRICT filter on 8 keywords -> 4 candidates, 4 true AI papers (precision 100%)
"""

import urllib.request
import urllib.error
import urllib.parse
import json
import time
from pathlib import Path

UA = "mailto:research@yuxintech.com"

# STRICT AI: 16 词, 仅 ML/DL 明确方法名
STRICT_AI = [
    "machine learning", "deep learning", "neural network", "random forest",
    "xgboost", "yolo", "transformer", "lstm", "cnn", "rnn", "gru",
    "computer vision", "reinforcement learning", "svm", "gradient boosting",
    "anomaly detection", "object detection", "segmentation",
]

# STRICT AQUA: 14 词, RAS + 海淡水主要养殖种
STRICT_AQUA = [
    "aquaculture", "recirculating", "tilapia", "salmon",
    "catfish", "trout", "carp", "shrimp", "prawn",
    "sea bass", "seabream", "macrobrachium",
    "hatchery", "biofilter",
]


def _reconstruct_abstract(work):
    aidx = work.get("abstract_inverted_index") or {}
    if not aidx:
        return ""
    words = sorted([(pos, w) for w, ps in aidx.items() for pos in ps])
    return " ".join(w.lower() for _, w in words)


def strict_relevant(work):
    title = (work.get("title") or "").lower()
    abstract = _reconstruct_abstract(work)
    concepts = " ".join(
        c.get("display_name", "").lower()
        for c in (work.get("concepts") or [])[:10]
    )
    full = f"{title} {abstract} {concepts}"
    has_ai = any(kw in full for kw in STRICT_AI)
    has_aqua = any(kw in full for kw in STRICT_AQUA)
    return has_ai and has_aqua


def get_doi(work):
    d = work.get("doi") or ""
    return d[len("https://doi.org/"):] if d.startswith("https://doi.org/") else d


def search_openalex(query, sort="relevance_score:desc", per_page=10,
                    pub_year="2024-2026", from_date="2025-09-01"):
    enc = urllib.parse.quote(query)
    url = (
        f"https://api.openalex.org/works?search={enc}"
        f"&sort={sort}&per_page={per_page}"
        f"&filter=publication_year:{pub_year},from_publication_date:{from_date}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        return json.loads(urllib.request.urlopen(req, timeout=20).read()).get("results", [])
    except urllib.error.HTTPError as e:
        print(f"  [{query[:50]}] HTTP {e.code}")
        return []
    except Exception as e:
        print(f"  [{query[:50]}] ERROR: {type(e).__name__}")
        return []


def filter_papers(queries, known_dois_path=None, top_n=5):
    """Run queries, apply STRICT double-condition, return fresh papers.

    Args:
        queries: list of search query strings
        known_dois_path: path to known_dois.txt for cross-round dedup
        top_n: how many top results per query to consider (default 5)

    Returns:
        list of dicts: {doi, title, venue, pub_date, fwci, cited_by}
    """
    kdoi = set()
    if known_dois_path and Path(known_dois_path).exists():
        kdoi = set(Path(known_dois_path).read_text().strip().split("\n"))

    seen = set()
    fresh = []
    for q in queries:
        rs = search_openalex(q)
        if not rs:
            time.sleep(1.0)
            continue
        for w in rs[:top_n]:
            if not strict_relevant(w):
                continue
            doi = get_doi(w)
            if not doi or doi in kdoi or doi in seen:
                continue
            seen.add(doi)
            pl = w.get("primary_location") or {}
            src = pl.get("source") or {}
            fresh.append({
                "doi": doi,
                "title": (w.get("title") or "")[:140],
                "venue": src.get("display_name"),
                "pub_date": w.get("publication_date"),
                "fwci": w.get("fwci"),
                "cited_by": w.get("cited_by_count", 0),
            })
        time.sleep(0.6)
    return fresh


if __name__ == "__main__":
    import sys
    queries = sys.argv[1:] if len(sys.argv) > 1 else [
        "machine learning aquaculture water quality",
        "deep learning fish disease detection",
    ]
    fresh = filter_papers(
        queries,
        known_dois_path="/Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt",
    )
    print(f"\nFound {len(fresh)} fresh papers")
    for p in fresh:
        print(f"  {p['doi']} | fwci={p['fwci']} | {p['title']}")
