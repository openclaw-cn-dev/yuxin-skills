#!/usr/bin/env python3
"""
OpenAlex cites:W<id> filter retrieval + concepts.score dual-condition filter.

Use case: OpenAlex search endpoint returns 429 (Daily Budget exhausted or cluster
overloaded). Switch to citation tracking via filter endpoint, which empirically
still works (R40 verified 2026-08-31).

Pipeline:
1. Probe OpenAlex health and detect budget-exhaustion vs standard 429
2. For each seed DOI (high-fwci known paper), get its OpenAlex ID via DOI lookup
3. Run filter=cites:W<id> to get top 10 most recent citing works
4. Apply R40 concepts.score dual-condition filter (aqua_score >= 0.5 AND ai_score >= 0.5)
5. Manual review edges (title contains explicit AI terms like "stereo vision")
6. Crossref verification for accepted candidates
7. Output list of new DOIs to add to known_dois.txt

Usage:
    python3 ***SECRET***.py --seed-dois <doi1> <doi2> ...
    python3 ***SECRET***.py --from-known-dois \
        --known-dois-file /Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt \
        --fwci-min 3.0 --max-seeds 3

References:
    references/***SECRET***.md
    references/***SECRET***.md
    laomo-knowledge §3.5.13, §3.5.14
"""
import argparse
import json
import re
import sys
import time
import urllib.request

UA = "mailto:research@yuxintech.com"

# R40 verified concept sets
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

# Thresholds (R40 standard)
AQUA_THRESHOLD = 0.5
AI_THRESHOLD = 0.5


def openalex_request(url, timeout=15):
    """GET request with UA. Returns (status, body_dict_or_text)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()) if e.headers.get("Content-Type", "").startswith("application/json") else {"raw": e.read().decode()[:200]}
    except Exception as e:
        return None, {"error": str(e)[:200]}


def probe_openalex_health():
    """Returns ('healthy' | 'budget_exhausted' | 'standard_429' | 'down')."""
    status, body = openalex_request("https://api.openalex.org/works?per_page=1", timeout=10)
    if status == 200:
        return "healthy", body
    if status == 429:
        if isinstance(body, dict) and ("dailyRemainingUsd" in body or "creditsRemaining" in body):
            return "budget_exhausted", body
        return "standard_429", body
    return "down", body


def get_openalex_id_from_doi(doi):
    """DOI直查, returns 'W<id>' or None."""
    url = f"https://api.openalex.org/works/doi:{doi}"
    status, body = openalex_request(url)
    if status == 200 and "id" in body:
        return body["id"].split("/")[-1]
    return None


def fetch_citing_works(oa_id, per_page=10):
    """filter=cites:W<id>, sort=publication_date:desc."""
    url = (
        f"https://api.openalex.org/works?filter=cites:{oa_id}"
        f"&per_page={per_page}&sort=publication_date:desc"
        f"&select=doi,title,fwci,cited_by_count,publication_date,primary_location,concepts"
    )
    status, body = openalex_request(url)
    if status == 200:
        return body.get("results", [])
    return []


def is_relevant_via_concepts(work, aqua_th=AQUA_THRESHOLD, ai_th=AI_THRESHOLD):
    """R40 concepts.score weighted filter."""
    concepts = work.get("concepts", [])
    aqua_score = sum(c.get("score", 0) for c in concepts
                     if c.get("display_name") in AQUA_CONCEPTS)
    ai_score = sum(c.get("score", 0) for c in concepts
                   if c.get("display_name") in AI_CONCEPTS_STRICT)
    return {
        "is_relevant": aqua_score >= aqua_th and ai_score >= ai_th,
        "aqua_score": round(aqua_score, 2),
        "ai_score": round(ai_score, 2),
    }


def has_explicit_ai_in_title(work):
    """Manual review edge case: title contains explicit AI terms."""
    title = (work.get("title") or "").lower()
    return any(term in title for term in EXPLICIT_AI_TITLE_TERMS)


def crossref_verify(doi):
    """Returns dict with status, abstract, authors, or None on error."""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        if resp.status == 200:
            data = json.loads(resp.read())
            msg = data.get("message", {})
            abstract = msg.get("abstract", "")
            abstract_clean = re.sub(r"<[^>]+>", "", abstract) if abstract else ""
            authors = [
                a.get("given", "") + " " + a.get("family", "")
                for a in msg.get("author", [])
            ][:5]
            return {
                "status": 200,
                "title": msg.get("title", [""])[0],
                "container": msg.get("container-title", [""])[0],
                "year": msg.get("published", {}).get("date-parts", [[None]])[0][0],
                "authors": authors,
                "abstract": abstract_clean,
            }
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-dois", nargs="+", default=[],
                        help="Direct seed DOIs to track citations for")
    parser.add_argument("--from-known-dois", action="store_true",
                        help="Auto-pick top-fwci seeds from known_dois.txt")
    parser.add_argument("--known-dois-file",
                        default="/Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt")
    parser.add_argument("--fwci-min", type=float, default=3.0,
                        help="Min fwci for auto-seed selection")
    parser.add_argument("--max-seeds", type=int, default=3)
    parser.add_argument("--per-page", type=int, default=10)
    parser.add_argument("--output", default="/tmp/cites_filter_results.json")
    args = parser.parse_args()

    print(f"OpenAlex R40 dual-mode retrieval at {time.strftime('%H:%M:%S UTC', time.gmtime())}")
    print("=" * 80)

    # Step 1: Probe health
    health, body = probe_openalex_health()
    print(f"OpenAlex health: {health}")
    if health == "budget_exhausted":
        retry_after = body.get("retryAfter", 14400)
        print(f"  dailyRemainingUsd: {body.get('dailyRemainingUsd')}, retryAfter: {retry_after}s")
    elif health == "standard_429":
        print(f"  standard 429 - cluster limited, may recover with sleep")
    elif health == "down":
        print(f"  OpenAlex unavailable, abort")
        sys.exit(1)
    print()

    # Step 2: Resolve seed DOIs
    seeds = list(args.seed_dois)
    if args.from_known_dois:
        print(f"Loading seeds from {args.known_dois_file} (fwci >= {args.fwci_min})")
        try:
            with open(args.known_dois_file) as f:
                known_dois = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except FileNotFoundError:
            print(f"  File not found")
            sys.exit(1)
        # Pick DOIs from recent papers, verify fwci
        for doi in known_dois[-50:]:  # most recent 50
            if doi.startswith("arxiv:") or doi.startswith("10.2139"):
                continue
            url = f"https://api.openalex.org/works/doi:{doi}"
            s, b = openalex_request(url)
            if s == 200 and b.get("fwci") and b["fwci"] >= args.fwci_min:
                seeds.append(doi)
                if len(seeds) >= args.max_seeds:
                    break
            time.sleep(0.3)

    if not seeds:
        print("No seeds provided. Use --seed-dois or --from-known-dois")
        sys.exit(1)

    print(f"Seeds ({len(seeds)}):")
    for s in seeds:
        print(f"  - {s}")
    print()

    # Step 3: For each seed, get citing works
    accepted = []
    for seed_doi in seeds:
        print(f"\n[Seed {seed_doi}]")
        oa_id = get_openalex_id_from_doi(seed_doi)
        if not oa_id:
            print(f"  ❌ Could not resolve OpenAlex ID")
            continue
        print(f"  oa_id: {oa_id}")

        citing = fetch_citing_works(oa_id, per_page=args.per_page)
        print(f"  fetched {len(citing)} citing works")

        for w in citing:
            doi = (w.get("doi") or "").replace("https://doi.org/", "")
            if not doi:
                continue
            # R40 dual-condition filter
            relevance = is_relevant_via_concepts(w)
            decision = None
            if relevance["is_relevant"]:
                decision = "ACCEPT (concepts)"
            elif (relevance["aqua_score"] >= 0.5 and has_explicit_ai_in_title(w)):
                decision = "ACCEPT (title AI + aqua)"
            if not decision:
                continue
            # Crossref verify
            cr = crossref_verify(doi)
            time.sleep(0.5)
            if cr and cr.get("status") == 200:
                print(f"    [VERIFY] {doi}: {cr['title'][:60]}")
                print(f"      {decision}, venue: {cr['container']}, year: {cr['year']}")
                accepted.append({
                    "doi": doi,
                    "title": cr["title"],
                    "venue": cr["container"],
                    "year": cr["year"],
                    "authors": cr["authors"],
                    "relevance": relevance,
                    "decision": decision,
                    "seed": seed_doi,
                })

    # Output
    print()
    print("=" * 80)
    print(f"ACCEPTED: {len(accepted)} papers")
    for a in accepted:
        print(f"  • {a['doi']}: {a['title'][:80]}")
        print(f"    {a['decision']} | venue: {a['venue']}, year: {a['year']}")

    with open(args.output, "w") as f:
        json.dump(accepted, f, indent=2, ensure_ascii=False)
    print(f"\nWritten to {args.output}")


if __name__ == "__main__":
    main()