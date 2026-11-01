"""Tests for tools.knowledge_updater (hashing, scoring, formatting, dedup)."""
from datetime import datetime, timedelta

import pytest

import knowledge_updater as ku


def test_compute_hash_is_deterministic_and_normalized():
    a = ku.compute_hash("10.1234/ABC.001")
    b = ku.compute_hash("  10.1234/abc.001 \n")
    assert a == b
    assert len(a) == 64


def test_compute_hash_different_inputs():
    assert ku.compute_hash("a") != ku.compute_hash("b")


def test_score_entry_recency_and_relevance():
    now = datetime(2026, 7, 16)
    entry = {
        "title": "Red tide harmful algal bloom satellite chlorophyll",
        "abstract": "Aquaculture HAB alert thresholds monitoring.",
        "published_date": now - timedelta(days=30),
        "citation_count": 5,
    }
    score = ku.score_entry(entry, ku.KNOWLEDGE_CONFIG["keywords"], now)
    assert isinstance(score, float)
    assert 0 < score <= 10.0


def test_score_entry_missing_date_still_scores():
    now = datetime(2026, 7, 16)
    entry = {"title": "HAB", "abstract": "", "citation_count": 0}
    score = ku.score_entry(entry, ku.KNOWLEDGE_CONFIG["keywords"], now)
    assert score >= 0.0


def test_score_entry_relevance_boosts_score():
    now = datetime(2026, 7, 16)
    low = ku.score_entry(
        {"title": "weather", "abstract": "unrelated", "published_date": now},
        ku.KNOWLEDGE_CONFIG["keywords"], now,
    )
    high = ku.score_entry(
        {"title": "red tide harmful algal bloom satellite chlorophyll",
         "abstract": "HAB toxin monitoring aquaculture alert thresholds",
         "published_date": now},
        ku.KNOWLEDGE_CONFIG["keywords"], now,
    )
    assert high > low


def test_format_entry_returns_markdown_block():
    entry = {
        "title": "Sample HAB paper",
        "authors": ["Author A", "Author B"],
        "year": 2024,
        "venue": "Harmful Algae",
        "doi_or_url": "10.1234/sample.001",
        "abstract": "An abstract about red tide.",
        "source": "arxiv",
    }
    md = ku.format_entry(entry, 7.5)
    assert "Sample HAB paper" in md
    assert "10.1234/sample.001" in md
    assert "7.5" in md


def test_load_existing_hashes_returns_set():
    hashes = ku.load_existing_hashes()
    assert isinstance(hashes, set)


def test_load_existing_hashes_dedup(tmp_path, monkeypatch):
    brain = tmp_path / "BRAIN.md"
    brain.write_text(
        "## Entry\n- **DOI/URL:** 10.1/x\n- **DOI/URL:** 10.2/y\n", encoding="utf-8"
    )
    monkeypatch.setattr(ku, "BRAIN_PATH", brain)
    hashes = ku.load_existing_hashes()
    assert len(hashes) == 2
    assert ku.compute_hash("10.1/x") in hashes


def test_fetch_arxiv_offline_returns_empty(monkeypatch):
    # Default config has empty arxiv_categories -> must return [] without network.
    monkeypatch.setitem(ku.KNOWLEDGE_CONFIG, "arxiv_categories", [])
    assert ku.fetch_arxiv(ku.KNOWLEDGE_CONFIG["keywords"]) == []


def test_fetch_rss_offline_returns_empty(monkeypatch):
    monkeypatch.setitem(ku.KNOWLEDGE_CONFIG, "rss_feeds", [])
    assert ku.fetch_rss() == []


def test_append_to_brain_dry_run(tmp_path, monkeypatch):
    brain = tmp_path / "BRAIN.md"
    brain.write_text("# Knowledge Brain\n", encoding="utf-8")
    monkeypatch.setattr(ku, "BRAIN_PATH", brain)
    entries = [{
        "title": "Dry run paper",
        "authors": ["A"],
        "year": 2024,
        "venue": "J",
        "doi_or_url": "10.1/dry",
        "abstract": "ab",
        "source": "test",
    }]
    ku.append_to_brain(entries, dry_run=True)
    # Dry run must not modify the brain file.
    assert "Dry run paper" not in brain.read_text(encoding="utf-8")
