#!/usr/bin/env python3
"""Direction-1 OpenAlex paper scan pipeline (R319 固化).

probe -> 5-niche STRICT scan -> dedupe vs known_dois.txt -> Crossref full metadata
-> STRICT_DUAL title verdict (union wordlist + hyphen normalization + word-boundary 'ras')
-> optional asserted append (pre-assert unique set, post-verify each DOI hits exactly 1).

Usage:
  python3 dir1_paper_scan.py                       # dry-run, print verdicts only
  python3 dir1_paper_scan.py --append --round R319 # write PASS rows to known_dois.txt
  python3 dir1_paper_scan.py --known /path/to/known_dois.txt
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, "/Users/hua/.hermes/skills/research/arxiv/references/openalex-aquaculture-queries/scripts")
from strict_filter import get_doi, search_openalex, strict_relevant  # noqa: E402

KNOWN_DEFAULT = "/Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt"
UA = {"User-Agent": "laomo-heartbeat/1.0 (mailto:research@yuxintech.com)"}

QUERIES = [
    "recirculating aquaculture system machine learning",
    "deep learning fish disease detection aquaculture",
    "machine learning water quality recirculating aquaculture",
    "computer vision fish biomass estimation aquaculture",
    "biofilter neural network aquaculture monitoring",
]

# R269 ML_KW UNION R20 STRICT_AI. The R269-only list drops yolo/segmentation/object
# detection -> real AI papers get false REJECT (R319 evidence: YOLOv11n biomass paper
# + FDMNet segmentation paper). Always match on this union.
ML_UNION = [
    "machine learning", "deep learning", "neural network", "random forest", "xgboost",
    "svm", "support vector", "transformer", "cnn", "rnn", "lstm", "gru",
    "computer vision", "reinforcement learning", "fuzzy logic", "gradient boosting",
    "artificial intelligence", "classification", "yolo", "anomaly detection",
    "object detection", "segmentation",
]
RAS_KW = [
    "aquaculture", "fish", "shrimp", "pond", "recirculating", "salmon",
    "tilapia", "trout", "prawn", "biofloc",
]


def norm_title(t):
    # hyphen variants: "machine-learning" does NOT contain substring "machine learning"
    # (R319: aquaeng dissolved-oxygen ML paper would be falsely rejected without this)
    return re.sub(r"[-\u2010\u2011\u2012\u2013]", " ", (t or "").lower())


def has_ras(t):
    # bare "ras" needs word boundary ("parasite"/"erase" substring traps, R263 precedent)
    if any(k in t for k in RAS_KW):
        return True
    return bool(re.search(r"\bras\b", t))


def load_known(path):
    entries, uniq = [], set()
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        entries.append(line)
        uniq.add(line.split("\t")[0].lower())
    return entries, uniq


def crossref(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read()).get("message", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--append", action="store_true", help="write PASS rows to known file")
    ap.add_argument("--round", default="", help="round tag for --append rows, e.g. R319")
    ap.add_argument("--known", default=KNOWN_DEFAULT)
    args = ap.parse_args()
    if args.append and not args.round:
        ap.error("--append requires --round")

    entries, uniq = load_known(args.known)
    print(f"known: entries={len(entries)} unique={len(uniq)}")

    cands = {}
    for q in QUERIES:
        works = search_openalex(q, per_page=10)
        new = 0
        for w in works:
            if not strict_relevant(w):
                continue
            doi = get_doi(w).lower()
            if doi and doi not in uniq and doi not in cands:
                cands[doi] = w.get("title") or ""
                new += 1
        print(f"Q[{q[:52]}] new_strict={new}")
    print(f"candidates after dedupe: {len(cands)}")

    passed = []
    for doi in cands:
        try:
            m = crossref(doi)
        except Exception as e:
            print(f"{doi}\tCROSSREF_FAIL\t{type(e).__name__}: {e}")
            continue
        title = (m.get("title") or [""])[0]
        t = norm_title(title)
        ras = [k for k in RAS_KW if k in t] + (["ras"] if re.search(r"\bras\b", t) else [])
        ml = [k for k in ML_UNION if k in t]
        rec = {
            "doi": doi, "title": title,
            "journal": (m.get("container-title") or [""])[0],
            "cited": m.get("is-referenced-by-count", 0),
            "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
        }
        verdict = "PASS" if ras and ml else "REJECT"
        if verdict == "PASS":
            passed.append(rec)
        print(f"{doi}\t{verdict}\tRAS={ras[:2]}\tML={ml[:2]}\tcited={rec['cited']}\t{title[:80]}")
        time.sleep(0.3)

    print(f"\nverdict: {len(passed)} PASS / {len(cands) - len(passed)} REJECT")
    if not args.append:
        print("dry-run only; re-run with --append --round R<n> to write")
        return
    if not passed:
        print("0 increment -> anti-bloat (Pitfall #39), nothing appended")
        return
    for r in passed:
        assert r["doi"] not in uniq, f"already in file: {r['doi']}"
    with open(args.known, "a", encoding="utf-8") as f:
        f.write(f"# {time.strftime('%Y-%m-%d %H:%M')} CST dir1 scan - +{len(passed)} DOI\n")
        for r in passed:
            f.write(f"{r['doi']}\t{r['title']}\tcited={r['cited']}\t{r['journal']}\t{r['year']}\t{args.round}\n")
    e2, u2 = load_known(args.known)
    assert len(e2) == len(entries) + len(passed), "entry count mismatch"
    assert len(u2) == len(uniq) + len(passed), "unique count mismatch"
    for r in passed:
        hits = sum(1 for l in e2 if l.split("\t")[0].lower() == r["doi"])
        assert hits == 1, f"post-verify fail {r['doi']}: hits={hits}"
    print(f"appended {len(passed)}: unique {len(uniq)} -> {len(u2)}, post-verify OK")


if __name__ == "__main__":
    main()
