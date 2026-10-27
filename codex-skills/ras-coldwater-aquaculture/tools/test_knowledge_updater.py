"""
test_knowledge_updater.py - Skill 161: ras-coldwater-aquaculture
================================================================

Pure unit tests for the knowledge crawl pipeline helpers. No network, no
file writes to the real brain; everything is hermetic and deterministic so
the suite is safe to run in CI.

Run:
    python tools/test_knowledge_updater.py
Exits 0 on success, non-zero on the first failing assertion.
"""
from __future__ import annotations

import datetime
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import knowledge_updater as ku  # noqa: E402


def _run(name: str) -> None:
    print(f"[OK] {name}")


def test_hash_deterministic() -> None:
    a = ku.compute_hash("https://x.com/1")
    b = ku.compute_hash("https://x.com/1")
    assert a == b, "same input must hash equally"
    assert ku.compute_hash("https://x.com/2") != a, "different input must differ"
    _run("dedup hash deterministic")


def test_hash_normalisation() -> None:
    # Case-insensitive + whitespace-trimmed so DOIs/URLs dedup regardless of casing.
    assert ku.compute_hash("  10.1234/ABC  ") == ku.compute_hash("10.1234/abc"), (
        "hash must be case-insensitive and whitespace-trimmed"
    )
    assert ku.compute_hash("") == "", "empty identifier must hash to empty"
    _run("dedup hash normalisation")


def test_score_in_range() -> None:
    e = {"title": ku.KNOWLEDGE_CONFIG["domain"],
         "abstract": ku.KNOWLEDGE_CONFIG["domain"],
         "published_date": datetime.datetime.now(),
         "citation_count": 10}
    s = ku.score_entry(e, ku.KNOWLEDGE_CONFIG["keywords"], datetime.datetime.now())
    assert 0.0 <= s <= 10.0, f"score out of range: {s}"
    _run(f"score in range ({s})")


def test_score_recency_decay() -> None:
    now = datetime.datetime.now()
    fresh = {"title": "recirculating aquaculture system biofilter",
             "abstract": "un-ionized ammonia fish toxicity RAS biofilter nitrification",
             "published_date": now, "citation_count": 0}
    old = dict(fresh, published_date=now - datetime.timedelta(days=800))
    s_fresh = ku.score_entry(fresh, ku.KNOWLEDGE_CONFIG["keywords"], now)
    s_old = ku.score_entry(old, ku.KNOWLEDGE_CONFIG["keywords"], now)
    assert s_fresh > s_old, f"fresh must score higher than old: {s_fresh} vs {s_old}"
    _run(f"score recency decay ({s_fresh} > {s_old})")


def test_score_keyword_relevance() -> None:
    now = datetime.datetime.now()
    relevant = {"title": "RAS biofilter nitrification cold-water salmonid",
                "abstract": "un-ionized ammonia fish toxicity MBBR biofiltration aquaculture",
                "published_date": now, "citation_count": 0}
    irrelevant = {"title": "Crop yield under drought",
                  "abstract": "maize irrigation scheduling",
                  "published_date": now, "citation_count": 0}
    s_rel = ku.score_entry(relevant, ku.KNOWLEDGE_CONFIG["keywords"], now)
    s_irr = ku.score_entry(irrelevant, ku.KNOWLEDGE_CONFIG["keywords"], now)
    assert s_rel > s_irr, f"relevant must score higher: {s_rel} vs {s_irr}"
    _run(f"score keyword relevance ({s_rel} > {s_irr})")


def test_score_citation_bonus() -> None:
    now = datetime.datetime.now()
    base = {"title": "RAS biofilter nitrification cold-water salmonid",
            "abstract": "un-ionized ammonia fish toxicity MBBR biofiltration aquaculture",
            "published_date": now}
    low_cit = dict(base, citation_count=0)
    high_cit = dict(base, citation_count=500)
    s_low = ku.score_entry(low_cit, ku.KNOWLEDGE_CONFIG["keywords"], now)
    s_high = ku.score_entry(high_cit, ku.KNOWLEDGE_CONFIG["keywords"], now)
    assert s_high >= s_low, f"high citations must not score lower: {s_high} vs {s_low}"
    _run(f"score citation bonus ({s_high} >= {s_low})")


def test_score_missing_date() -> None:
    e = {"title": "RAS biofilter", "abstract": "nitrification",
         "published_date": None, "citation_count": 0}
    s = ku.score_entry(e, ku.KNOWLEDGE_CONFIG["keywords"], datetime.datetime.now())
    assert 0.0 <= s <= 10.0, f"score with missing date out of range: {s}"
    _run(f"score missing date ({s})")


def test_format_entry() -> None:
    txt = ku.format_entry({"title": "T", "authors": ["A", "B"], "year": 2026,
                           "venue": "V", "doi_or_url": "https://x",
                           "abstract": "ab"}, 5.0)
    assert "DOI/URL:" in txt, "format must include DOI/URL label"
    assert "Relevance Score:" in txt, "format must include relevance score"
    assert "5.0/10" in txt, "format must include score value"
    assert "A, B" in txt, "format must join authors"
    assert "https://x" in txt, "format must include the URL"
    _run("format entry")


def test_format_entry_unknowns() -> None:
    txt = ku.format_entry({"title": "T", "authors": [], "year": "",
                           "venue": "", "doi_or_url": "",
                           "abstract": ""}, 0.0)
    assert "Unknown" in txt, "missing authors default to Unknown"
    assert "No abstract available." in txt, "missing abstract uses placeholder"
    _run("format entry unknowns")


def test_config_valid() -> None:
    # The shipped config must validate (fail fast on contract drift).
    ku.validate_config(ku.KNOWLEDGE_CONFIG)
    _run("config valid")


def test_config_rejects_bad_weights() -> None:
    bad = dict(ku.KNOWLEDGE_CONFIG)
    bad["scoring_weights"] = {"recency": 0.5, "keyword_relevance": 0.5, "citation_count": 0.5}
    try:
        ku.validate_config(bad)
    except ValueError:
        _run("config rejects bad weights")
    else:
        raise AssertionError("validate_config must reject weights that do not sum to 1.0")


def test_config_rejects_empty_keywords() -> None:
    bad = dict(ku.KNOWLEDGE_CONFIG)
    bad["keywords"] = []
    try:
        ku.validate_config(bad)
    except ValueError:
        _run("config rejects empty keywords")
    else:
        raise AssertionError("validate_config must reject empty keywords")


def test_extract_identifiers_from_table_and_log() -> None:
    sample = """# Brain

## 2. Key Research Papers

| Title | DOI/URL | Tier |
|-------|---------|------|
| Aqueous ammonia equilibrium | 10.1139/f75-274 | 1 |
| DO saturation | https://doi.org/10.4319/lo.1984.29.3.0620 | 1 |

## 7. Knowledge Update Log

### 2026-01-01 - New finding
- **DOI/URL:** https://example.org/paper/1
- **Key Finding:** ...
"""
    ids = ku._extract_identifiers(sample)
    assert "10.1139/f75-274" in ids, "table DOI must be extracted"
    assert "https://doi.org/10.4319/lo.1984.29.3.0620" in ids, "table URL must be extracted"
    assert "https://example.org/paper/1" in ids, "log DOI/URL label must be extracted"
    _run("extract identifiers from table + log")


def test_load_existing_hashes_real_brain() -> None:
    # The real brain ships >=4 DOI-cited references; dedup must pick them up.
    hashes = ku.load_existing_hashes()
    assert len(hashes) >= 4, f"expected >=4 existing hashes, got {len(hashes)}"
    _run(f"load existing hashes from real brain ({len(hashes)})")


def test_append_dry_run_no_write(tmp_path: Path = None) -> None:
    # Point BRAIN_PATH at a temp brain so the real brain is never mutated.
    tmp = Path(tempfile.mkdtemp())
    brain = tmp / "SECOND-KNOWLEDGE-BRAIN.md"
    brain.write_text("# Brain\n\n## 7. Knowledge Update Log\n", encoding="utf-8")
    orig = ku.BRAIN_PATH
    try:
        ku.BRAIN_PATH = brain
        entries = [ku.Entry(title="New RAS paper", authors=["A"], year=2026,
                            venue="V", doi_or_url="https://unique.example/1",
                            abstract="recirculating aquaculture system biofilter nitrification",
                            published_date=datetime.datetime.now(),
                            citation_count=5, source="semantic_scholar")]
        n = ku.append_to_brain(entries, dry_run=True)
        assert n == 1, f"dry-run must report 1 new entry, got {n}"
        # Dry-run must NOT modify the brain.
        assert "https://unique.example/1" not in brain.read_text(encoding="utf-8"), (
            "dry-run must not write to the brain"
        )
        # Second dry-run must still report 1 (no dedup persistence between dry runs).
        n2 = ku.append_to_brain(entries, dry_run=True)
        assert n2 == 1, f"second dry-run must still report 1, got {n2}"
    finally:
        ku.BRAIN_PATH = orig
    _run("append dry-run no write")


def test_append_real_writes_and_dedups() -> None:
    tmp = Path(tempfile.mkdtemp())
    brain = tmp / "SECOND-KNOWLEDGE-BRAIN.md"
    brain.write_text("# Brain\n\n## 7. Knowledge Update Log\n", encoding="utf-8")
    orig = ku.BRAIN_PATH
    try:
        ku.BRAIN_PATH = brain
        e = ku.Entry(title="New RAS paper", authors=["A"], year=2026,
                     venue="V", doi_or_url="https://unique.example/2",
                     abstract="recirculating aquaculture system biofilter nitrification",
                     published_date=datetime.datetime.now(),
                     citation_count=5, source="semantic_scholar")
        n1 = ku.append_to_brain([e], dry_run=False)
        assert n1 == 1, f"first append must write 1, got {n1}"
        text = brain.read_text(encoding="utf-8")
        assert "https://unique.example/2" in text, "entry must be persisted"
        # Second append of the same identifier must be deduped to 0.
        n2 = ku.append_to_brain([e], dry_run=False)
        assert n2 == 0, f"second append must dedup to 0, got {n2}"
    finally:
        ku.BRAIN_PATH = orig
    _run("append real writes + dedup")


def main() -> int:
    tests = [
        test_hash_deterministic,
        test_hash_normalisation,
        test_score_in_range,
        test_score_recency_decay,
        test_score_keyword_relevance,
        test_score_citation_bonus,
        test_score_missing_date,
        test_format_entry,
        test_format_entry_unknowns,
        test_config_valid,
        test_config_rejects_bad_weights,
        test_config_rejects_empty_keywords,
        test_extract_identifiers_from_table_and_log,
        test_load_existing_hashes_real_brain,
        test_append_dry_run_no_write,
        test_append_real_writes_and_dedups,
    ]
    for t in tests:
        t()
    print(f"all knowledge_updater tests passed ({len(tests)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
