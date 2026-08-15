#!/usr/bin/env python3
"""OpenAlex strict title-level filter with word-boundary fix (R27 实战沉淀).

Reusable script for laomo-knowledge paper search.
Captures R27 R23 word-boundary bug fix: 'iot' in 'paraprobiotics' returns True
due to substring match. Single-token AI keywords MUST use \\b regex.

Usage:
    python3 openalex-word-boundary-filter.py --candidates /tmp/r27_candidates.json

Output:
    /tmp/<basename>_word_boundary_pass.json with verified candidates
"""
import json
import re
import sys
from pathlib import Path


# === 关键词表 (R19 扩词 + R26/R27 调整) ===

# Aquaculture — 子串匹配 OK（rare false positives, e.g. "biofilter" 歧义陷阱见 R26）
AQUA_TITLE = [
    "aquaculture", "aquaponics", "recirculating", "tilapia", "salmon",
    "catfish", "trout", "carp", "shrimp", "prawn", "seaweed",
    "fish farm", "fish tank", "sea bass", "seabream", "fish pond",
    "hatchery", "fish nursery", "aquaculture pond",
]

# AI — 多词短语用子串匹配，单 token 必须 word-boundary
AI_TITLE_PHRASE = [
    "machine learning", "deep learning", "neural network",
    "artificial intelligence", "computer vision",
    "lstm", "xgboost", "random forest", "yolo", "transformer",
    "reinforcement learning", "chatgpt", "rag",
    "graph neural", "timegan", "digital twin",
]
AI_TITLE_SHORT = ["iot", "ai", "llm"]


def has_ai_strict(title_lower):
    """Match AI keywords with word boundary for short tokens (R23/R27 fix).

    Bug avoided: 'iot' substring in 'paraprobiotics' / 'antibiotics' / 'patriot'.
    """
    # Multi-word phrases: substring match is fine
    for kw in AI_TITLE_PHRASE:
        if kw in title_lower:
            return True
    # Single short tokens: MUST use word boundary
    for kw in AI_TITLE_SHORT:
        if re.search(rf"\b{re.escape(kw)}\b", title_lower):
            return True
    return False


def is_title_relevant(title):
    """STRICT double-condition title-level filter."""
    title_lower = title.lower()
    has_aqua = any(kw in title_lower for kw in AQUA_TITLE)
    has_ai = has_ai_strict(title_lower)
    return has_aqua and has_ai


def filter_candidates(input_path, output_path=None):
    """Filter OpenAlex candidate papers by STRICT title-level double-condition."""
    candidates = json.loads(Path(input_path).read_text())

    if output_path is None:
        output_path = str(Path(input_path).with_name(
            Path(input_path).stem + "_word_boundary_pass.json"))

    passed = []
    rejected = []
    for c in candidates:
        title = c.get("title") or ""
        if is_title_relevant(title):
            c["filter_stage"] = "title_word_boundary_pass"
            passed.append(c)
        else:
            c["filter_stage"] = "title_word_boundary_reject"
            rejected.append(c)

    Path(output_path).write_text(json.dumps(passed, indent=2, ensure_ascii=False))

    print(f"📊 三级过滤漏斗 (R27 实证):")
    print(f"   输入: {len(candidates)} candidates")
    print(f"   通过: {len(passed)} ({len(passed)/max(len(candidates),1)*100:.1f}%)")
    print(f"   拒绝: {len(rejected)} ({len(rejected)/max(len(candidates),1)*100:.1f}%)")
    print(f"   输出: {output_path}")
    return passed, rejected


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="R27 word-boundary title filter")
    parser.add_argument("--candidates", required=True, help="OpenAlex candidate JSON")
    parser.add_argument("--output", help="Output JSON path")
    args = parser.parse_args()
    filter_candidates(args.candidates, args.output)