#!/usr/bin/env python3
"""
R29 反向校验脚本（2026-08-15 沉淀）

解决问题：OpenAlex 双条件过滤（aqua + AI）会把真水产+AI 论文过滤掉。
当 round 1 双条件过滤 0 命中时，本脚本手动 inspect top 5-10 候选，
按 venue 白名单 + concepts[0].display_name + title 长尾词判定是否纳入 Crossref 验证。

用法：
  python3 scripts/r29-reverse-check.py <keyword> [--top 8]

示例：
  python3 scripts/r29-reverse-check.py "Cutting-edge technologies fish diseases"
  python3 scripts/r29-reverse-check.py "digital twin aquaculture" --top 10

输出：
  - JSON 格式的候选列表，每条带 reverse_check_score (0-3) 和 decision (REJECT/CROSSREF-VERIFY/P0-FORCE)
  - reverse_check_score ≥ 1 → 进入 Crossref 验证
  - reverse_check_score == 3 + P0 期刊 → 强制纳入（P0-FORCE）
"""

import sys
import urllib.request
import urllib.parse
import json
import re
import argparse
import time

UA = "mailto:research@yuxintech.com"

# R29 扩词表（跨领域期刊友好度）
AQUACULTURE_KEYWORDS = [
    "aquaculture", "aquaponics", "recirculating", "tilapia", "salmon",
    "catfish", "trout", "carp", "shrimp", "prawn", "seaweed",
    "pond", "biofloc", "fish farm", "fish tank",
    "sea bass", "seabream", "fish pond",
    "plankton", "marine biology", "algae", "seaweed farming",
    "macroalgae", "microalgae", "hatchery",
    # R29 扩词
    "fish disease", "fish health", "aquatic", "fishery",
]

# P0 水产核心期刊白名单（强制纳入）
P0_JOURNALS = [
    "Aquaculture",
    "Aquacultural Engineering",
    "Aquaculture Reports",
    "Journal of the World Aquaculture Society",
    "Reviews in Aquaculture",
    "Aquaculture International",
    "Journal of Aquatic Food Product Technology",
]

# P1 水产相关期刊（双条件通过即纳入）
P1_JOURNALS = [
    "Fishes",
    "Marine Biotechnology",
    "Journal of Fish Biology",
    "Fish & Shellfish Immunology",
    "Aquaculture Nutrition",
    "Aquatic Toxicology",
]


def text_has_ai(text_lower):
    """R23 word-boundary aware AI keyword detection."""
    for kw in ["machine learning", "deep learning", "neural network",
               "artificial intelligence", "computer vision", "random forest",
               "machine-learning", "deep-learning", "graph neural"]:
        if kw in text_lower:
            return True
    for token in ["lstm", "xgboost", "yolo", "transformer",
                  "iot", "ai", "dl", "ml", "cv", "nn", "xai"]:
        if re.search(rf"\b{token}\b", text_lower):
            return True
    return False


def reverse_check(work):
    """
    R29 反向校验：对 OpenAlex work 做 3 信号判定。
    返回 (score, decision, signals_hit)
    """
    score = 0
    signals_hit = []

    # 信号 1: venue.display_name 含 P0/P1 水产词
    venue = ((work.get("primary_location") or {}).get("source") or {}).get("display_name", "")
    venue_lower = venue.lower()

    for p0 in P0_JOURNALS:
        if p0.lower() in venue_lower:
            score += 2
            signals_hit.append(f"P0 journal: {p0}")
            break
    else:
        for p1 in P1_JOURNALS:
            if p1.lower() in venue_lower:
                score += 1
                signals_hit.append(f"P1 journal: {p1}")
                break
        else:
            # 通用水产词
            for kw in ["aquaculture", "fishery", "aquatic", "fish"]:
                if kw in venue_lower:
                    score += 1
                    signals_hit.append(f"venue aqua keyword: {kw}")
                    break

    # 信号 2: concepts[0].display_name == "Aquaculture"
    concepts = work.get("concepts", [])
    if concepts and concepts[0].get("display_name") == "Aquaculture":
        score += 1
        signals_hit.append("concept[0] == Aquaculture")

    # 信号 3: title 含 fish/shrimp/tilapia/salmon 等水产词
    title_lower = (work.get("title") or "").lower()
    for kw in ["fish", "shrimp", "tilapia", "salmon", "catfish", "trout",
               "carp", "prawn", "sea bass", "seabream", "aquaculture",
               "fish disease", "fish health", "aquatic"]:
        if kw in title_lower:
            # 必须同时命中 AI 关键词
            if text_has_ai(title_lower):
                score += 1
                signals_hit.append(f"title+AI: '{kw}' + AI token")
                break

    # 决策
    if score >= 3 and any("P0 journal" in s for s in signals_hit):
        decision = "P0-FORCE"
    elif score >= 2:
        decision = "CROSSREF-VERIFY"
    elif score >= 1:
        decision = "CROSSREF-VERIFY-LOW"
    else:
        decision = "REJECT"

    return score, decision, signals_hit


def main():
    parser = argparse.ArgumentParser(description="R29 reverse-check for OpenAlex papers")
    parser.add_argument("keyword", help="Search keyword")
    parser.add_argument("--top", type=int, default=8, help="Top N candidates to inspect (default: 8)")
    parser.add_argument("--year", default="2024-2026", help="Publication year filter (default: 2024-2026)")
    args = parser.parse_args()

    print(f"🔍 Searching OpenAlex: '{args.keyword}' (top {args.top}, year: {args.year})")
    print()

    url = (
        f"https://api.openalex.org/works?search={urllib.parse.quote(args.keyword)}"
        f"&sort=relevance_score:desc,fwci:desc&per_page={args.top}"
        f"&filter=publication_year:{args.year}"
    )

    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        resp = urllib.request.urlopen(req, timeout=20)
    except urllib.error.HTTPError as e:
        print(f"❌ OpenAlex HTTP {e.code}: {e.read()[:200]}")
        sys.exit(1)

    data = json.loads(resp.read())
    results = data.get("results", [])
    total = data.get("meta", {}).get("count", "?")

    print(f"📊 OpenAlex total: {total}, inspecting top {len(results)} candidates")
    print()

    reverse_checked = []
    for w in results:
        doi = (w.get("doi") or "").replace("https://doi.org/", "")
        title = (w.get("title") or "")[:100]
        venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "?")
        fwci = w.get("fwci")
        cited = w.get("cited_by_count")
        year = (w.get("publication_date") or "")[:4]
        concepts_top = ", ".join(c.get("display_name", "?") for c in w.get("concepts", [])[:3])

        score, decision, signals = reverse_check(w)

        emoji = {
            "P0-FORCE": "🔴",
            "CROSSREF-VERIFY": "🟢",
            "CROSSREF-VERIFY-LOW": "🟡",
            "REJECT": "⚪",
        }.get(decision, "?")

        print(f"{emoji} [{decision}] score={score} | {year} fwci={fwci} cited={cited}")
        print(f"   DOI: {doi}")
        print(f"   Title: {title}")
        print(f"   Venue: {venue}")
        print(f"   Concepts[0:3]: {concepts_top}")
        print(f"   Signals: {'; '.join(signals) if signals else '(none)'}")
        print()

        reverse_checked.append({
            "doi": doi,
            "title": title,
            "venue": venue,
            "fwci": fwci,
            "cited": cited,
            "year": year,
            "score": score,
            "decision": decision,
            "signals": signals,
        })

        time.sleep(0.3)

    # 总结
    print("=" * 60)
    print(f"📋 Reverse-check summary:")
    print(f"   P0-FORCE:          {sum(1 for r in reverse_checked if r['decision'] == 'P0-FORCE')}")
    print(f"   CROSSREF-VERIFY:   {sum(1 for r in reverse_checked if r['decision'] == 'CROSSREF-VERIFY')}")
    print(f"   CROSSREF-VERIFY-LOW: {sum(1 for r in reverse_checked if r['decision'] == 'CROSSREF-VERIFY-LOW')}")
    print(f"   REJECT:            {sum(1 for r in reverse_checked if r['decision'] == 'REJECT')}")
    print()

    # 输出 JSON 供后续 Crossref 验证
    candidates_for_verify = [
        r for r in reverse_checked
        if r["decision"] in ("P0-FORCE", "CROSSREF-VERIFY", "CROSSREF-VERIFY-LOW")
    ]

    if candidates_for_verify:
        print(f"✅ {len(candidates_for_verify)} candidates to verify via Crossref:")
        for r in candidates_for_verify:
            print(f"   - {r['doi']} (score={r['score']}, {r['decision']})")
        with open("/tmp/r29_reverse_check.json", "w") as f:
            json.dump(candidates_for_verify, f, indent=2)
        print()
        print(f"💾 Saved to /tmp/r29_reverse_check.json")
    else:
        print("❌ No candidates to verify — true saturation per §3.5.11 stage 5")


if __name__ == "__main__":
    main()