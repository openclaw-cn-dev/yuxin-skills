#!/usr/bin/env python3
"""
OpenAlex concepts.score weighted dual-condition filter.

Standalone re-runnable filter for verifying whether an OpenAlex work is
aquaculture+AI relevant, based on R40 findings (2026-08-31).

Usage:
    python3 ***SECRET***.py --doi 10.1016/j.aquaeng.2026.102814
    python3 ***SECRET***.py --dois-file /tmp/candidates.txt
    cat candidates.txt | python3 ***SECRET***.py --stdin

Output (stdout): one JSON line per DOI with verdict and scores.
Exit code 0 = all accepted, 1 = all rejected, 2 = mixed.

Reference:
    references/***SECRET***.md
    laomo-knowledge §3.5.14
"""
import argparse
import json
import sys
import urllib.request

UA = "mailto:research@yuxintech.com"

# R40 verified concept sets (from empirical analysis 2026-08-31)
AQUA_CONCEPTS = {
    "Aquaculture", "Fish <Actinopterygii>", "Fishery", "Fish pond",
    "Recirculating aquaculture", "Mariculture", "Aquaponics",
    "Biofloc", "Aquatic ecology", "Penaeus", "Grouper",
}
AI_CONCEPTS_STRICT = {
    "Computer vision", "Convolutional neural network", "Deep learning",
    "Artificial intelligence", "Machine learning", "Transformer",
    "Object detection", "YOLO", "Recurrent neural network",
    "Neural network", "Computer science",
    "Feature extraction", "Pattern recognition",
}
EXPLICIT_AI_TITLE_TERMS = [
    "stereo vision", "deep learning", "machine learning",
    "yolo", "transformer", "convolutional", "neural network",
    "computer vision", "object detection", "instance segmentation",
]


def fetch_work(doi):
    url = f"https://api.openalex.org/works/doi:{doi}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.status, json.loads(resp.read())
    except Exception as e:
        return None, {"error": str(e)}


def is_relevant(work, aqua_th=0.5, ai_th=0.5):
    concepts = work.get("concepts", [])
    aqua_score = sum(c.get("score", 0) for c in concepts
                     if c.get("display_name") in AQUA_CONCEPTS)
    ai_score = sum(c.get("score", 0) for c in concepts
                   if c.get("display_name") in AI_CONCEPTS_STRICT)
    is_relevant = aqua_score >= aqua_th and ai_score >= ai_th
    title_ai = any(t in (work.get("title") or "").lower()
                   for t in EXPLICIT_AI_TITLE_TERMS)
    title_accept = aqua_score >= aqua_th and title_ai
    return {
        "is_relevant": is_relevant,
        "title_accept": title_accept,
        "aqua_score": round(aqua_score, 2),
        "ai_score": round(ai_score, 2),
        "verdict": "ACCEPT" if (is_relevant or title_accept) else "REJECT",
        "reason": (
            f"concepts_score" if is_relevant
            else f"title_ai + aqua_concept" if title_accept
            else f"aqua<{aqua_th} or ai<{ai_th}"
        ),
    }


def process_doi(doi):
    status, body = fetch_work(doi)
    if status != 200:
        return {"doi": doi, "verdict": "ERROR", "error": body.get("error", "unknown")}
    relevance = is_relevant(body)
    relevance["doi"] = doi
    relevance["title"] = (body.get("title") or "")[:100]
    relevance["fwci"] = body.get("fwci")
    relevance["publication_date"] = body.get("publication_date")
    return relevance


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--doi", help="Single DOI")
    group.add_argument("--dois-file", help="File with one DOI per line")
    group.add_argument("--stdin", action="store_true", help="Read DOIs from stdin")
    parser.add_argument("--aqua-threshold", type=float, default=0.5)
    parser.add_argument("--ai-threshold", type=float, default=0.5)
    args = parser.parse_args()

    dois = []
    if args.doi:
        dois = [args.doi]
    elif args.dois_file:
        with open(args.dois_file) as f:
            dois = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    elif args.stdin:
        dois = [line.strip() for line in sys.stdin if line.strip()]

    accepted = rejected = 0
    for doi in dois:
        result = process_doi(doi)
        print(json.dumps(result, ensure_ascii=False))
        if result["verdict"] == "ACCEPT":
            accepted += 1
        elif result["verdict"] == "REJECT":
            rejected += 1

    if accepted and not rejected:
        sys.exit(0)
    if rejected and not accepted:
        sys.exit(1)
    sys.exit(2)


if __name__ == "__main__":
    main()