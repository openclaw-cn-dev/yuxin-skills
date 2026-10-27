"""
knowledge_updater.py - Skill 161: ras-coldwater-aquaculture
============================================================

Self-improving knowledge crawl pipeline for the
"Recirculating Aquaculture Systems & Cold-Water Fish Health Management"
domain. Fetches candidate evidence from academic APIs and news feeds,
deduplicates against the existing knowledge base (DOI/URL, SHA256,
case/whitespace-insensitive), scores each candidate on a 0-10 composite
scale, and appends the highest-scoring new entries to the
"## 7. Knowledge Update Log" section of SECOND-KNOWLEDGE-BRAIN.md.

Design goals (production-grade):
  * Idempotent: re-running never duplicates entries (SHA256 dedup across the
    existing reference table *and* the update log).
  * Resilient: per-source retry with exponential backoff, polite rate limiting,
    and explicit User-Agent identification; network failures never abort the
    whole run - they degrade to a limitation flag instead.
  * Observable: structured logging to stdout + optional logs/ file, plus an
    optional machine-readable JSON summary.
  * Safe: --dry-run writes nothing; file IO is atomic (temp file + os.replace)
    and encoding-explicit (UTF-8, LF).
  * Testable: pure helpers (compute_hash, score_entry, format_entry) are
    importable and unit-tested; live fetchers skip cleanly when optional
    dependencies (requests/feedparser/dateutil) are absent.

Dependencies (optional, gracefully degraded if missing):
    pip install requests feedparser python-dateutil

Usage:
    python tools/knowledge_updater.py [--dry-run] [--news-only]
                                       [--keywords KW [KW ...]] [--json]
                                       [--log-file PATH]
Exit codes: 0 = ran (possibly with 0 new entries), 2 = fatal config error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import os
import re
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

# Optional dependencies - degrade gracefully when absent.
try:
    import requests  # type: ignore
except ImportError:  # pragma: no cover - environment-dependent
    requests = None  # type: ignore

try:
    import feedparser  # type: ignore
except ImportError:  # pragma: no cover - environment-dependent
    feedparser = None  # type: ignore

try:
    from dateutil import parser as dateutil_parser  # type: ignore
except ImportError:  # pragma: no cover - environment-dependent
    dateutil_parser = None  # type: ignore


# ---------------- KNOWLEDGE_CONFIG (per-project) ----------------
KNOWLEDGE_CONFIG: Dict[str, Any] = {
    "domain": "Recirculating Aquaculture Systems & Cold-Water Fish Health Management",
    "keywords": [
        "recirculating aquaculture system",
        "un-ionized ammonia fish toxicity",
        "RAS biofilter nitrification",
        "cold-water salmonid water quality",
        "arctic char sturgeon culture",
        "RAS disease early warning",
        "MBBR biofiltration aquaculture",
    ],
    # ArXiv has no dedicated aquaculture category; left empty so the ArXiv
    # fetcher skips cleanly rather than firing a malformed query.
    "arxiv_categories": [],
    "arxiv_base": "https://export.arxiv.org/api/query",
    "semantic_scholar_base": "https://api.semanticscholar.org/graph/v1/paper/search",
    "rss_feeds": [
        "https://www.fao.org/newsroom/rss",
    ],
    "authoritative_docs": [
        "Aquacultural Engineering - Elsevier (RAS design, biofilters, water treatment)",
        "Aquaculture - Elsevier (species physiology, water quality)",
        "Journal of the World Aquaculture Society - Wiley",
        "Fish & Shellfish Immunology - Elsevier (disease & immunology)",
        "Diseases of Aquatic Organisms - Inter-Research",
        "Reviews in Aquaculture - Wiley (reviews & meta-analyses)",
        "Water Research - Elsevier (biofiltration & nitrification)",
    ],
    "scoring_weights": {
        "recency": 0.4,
        "keyword_relevance": 0.4,
        "citation_count": 0.2,
    },
    "max_results_per_source": 10,
    "max_new_entries_per_run": 20,
    "request_timeout_s": 30,
    "max_retries": 3,
    "base_retry_delay_s": 2.0,
    "inter_source_delay_s": 1.0,
    "user_agent": "ras-coldwater-aquaculture/1.0 (knowledge crawler)",
}
# ---------------------------------------------------------------

BRAIN_PATH: Path = Path(__file__).resolve().parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"
LOG_DIR: Path = Path(__file__).resolve().parent.parent / "logs"

# Markers used to locate/seed the update-log section and dedup identifiers.
UPDATE_LOG_HEADING = "## 7. Knowledge Update Log"
DOI_URL_LABEL_RE = re.compile(r"\*\*DOI/URL:\*\*\s*(\S+)")
TABLE_DOI_RE = re.compile(r"(?:^|\|\s*)(10\.\d{4,9}/[^\s|)\]\\]+)", re.M)
BARE_URL_RE = re.compile(r"(?i)\bhttps?://[^\s|)\]\\]+")


# ---------------- Data structures ----------------
@dataclass
class Entry:
    """A normalised candidate evidence record from any source."""
    title: str
    authors: List[str]
    year: int
    venue: str
    doi_or_url: str
    abstract: str
    published_date: Optional[datetime]
    citation_count: int
    source: str
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "venue": self.venue,
            "doi_or_url": self.doi_or_url,
            "abstract": self.abstract,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "citation_count": self.citation_count,
            "source": self.source,
            "score": self.score,
        }


@dataclass
class RunSummary:
    started_at: str
    dry_run: bool
    news_only: bool
    finished_at: str = ""
    candidates: int = 0
    new_entries: int = 0
    appended: int = 0
    by_source: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


# ---------------- Logging ----------------
def configure_logging(log_file: Optional[Path]) -> logging.Logger:
    logger = logging.getLogger("knowledge_updater")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(fmt)
            logger.addHandler(fh)
        except OSError as exc:  # pragma: no cover - environment-dependent
            logger.warning("could not open log file %s: %s", log_file, exc)
    return logger


LOG = logging.getLogger("knowledge_updater")


# ---------------- Config validation ----------------
def validate_config(cfg: Dict[str, Any]) -> None:
    """Raise ValueError on a malformed KNOWLEDGE_CONFIG (fail fast, no silent runs)."""
    required = ["domain", "keywords", "scoring_weights", "max_new_entries_per_run"]
    for key in required:
        if key not in cfg:
            raise ValueError(f"KNOWLEDGE_CONFIG missing required key: {key}")
    if not isinstance(cfg["keywords"], list) or not cfg["keywords"]:
        raise ValueError("KNOWLEDGE_CONFIG.keywords must be a non-empty list")
    w = cfg["scoring_weights"]
    if not isinstance(w, dict) or set(w) != {"recency", "keyword_relevance", "citation_count"}:
        raise ValueError("scoring_weights must have recency/keyword_relevance/citation_count")
    total = w["recency"] + w["keyword_relevance"] + w["citation_count"]
    if not math.isclose(total, 1.0, abs_tol=1e-6):
        raise ValueError(f"scoring_weights must sum to 1.0, got {total}")
    if cfg["max_new_entries_per_run"] <= 0:
        raise ValueError("max_new_entries_per_run must be positive")


# ---------------- Hashing & dedup ----------------
def compute_hash(identifier: str) -> str:
    """SHA256 of a DOI/URL, case-insensitive and whitespace-trimmed."""
    if not identifier:
        return ""
    return hashlib.sha256(identifier.strip().lower().encode("utf-8")).hexdigest()


def _extract_identifiers(brain_text: str) -> Set[str]:
    """Collect every DOI/URL already recorded in the brain (table + log)."""
    ids: Set[str] = set()
    for m in DOI_URL_LABEL_RE.finditer(brain_text):
        ids.add(m.group(1).strip())
    for m in TABLE_DOI_RE.finditer(brain_text):
        ids.add(m.group(1).strip())
    for m in BARE_URL_RE.finditer(brain_text):
        ids.add(m.group(0).strip())
    return ids


def load_existing_hashes() -> Set[str]:
    if not BRAIN_PATH.exists():
        return set()
    text = BRAIN_PATH.read_text(encoding="utf-8")
    return {compute_hash(i) for i in _extract_identifiers(text) if i}


# ---------------- Scoring ----------------
def _to_naive(dt: datetime) -> datetime:
    """Strip tzinfo for safe arithmetic against a naive `now`."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def score_entry(entry: Dict[str, Any], keywords: Sequence[str], now: datetime) -> float:
    """Composite 0-10 score: recency(0.4) + keyword_relevance(0.4) + citations(0.2)."""
    w = KNOWLEDGE_CONFIG["scoring_weights"]
    pub = entry.get("published_date")
    recency = 0.0
    if pub is not None:
        try:
            pub_naive = _to_naive(pub)
            now_naive = _to_naive(now)
            age_days = max(0.0, (now_naive - pub_naive).days)
            recency = max(0.0, 1.0 - age_days / 730.0)
        except (TypeError, ValueError):
            recency = 0.0
    text = ((entry.get("title") or "") + " " + (entry.get("abstract") or "")).lower()
    hits = sum(1 for kw in keywords if kw.lower() in text)
    relevance = min(hits / max(len(keywords), 1), 1.0)
    cit = int(entry.get("citation_count", 0) or 0)
    cit_score = min(math.log1p(cit) / math.log1p(1000), 1.0)
    raw = recency * w["recency"] + relevance * w["keyword_relevance"] + cit_score * w["citation_count"]
    return round(raw * 10.0, 2)


# ---------------- HTTP ----------------
def fetch_with_retry(url: str, params: Optional[Dict[str, Any]] = None,
                     max_retries: int = 3, base_delay: float = 2.0,
                     timeout: int = 30) -> Optional[Any]:
    """GET with exponential backoff, rate-limit and 5xx retry. None on hard failure."""
    if requests is None:
        LOG.warning("requests not installed; skipping %s", url)
        return None
    headers = {"User-Agent": KNOWLEDGE_CONFIG.get("user_agent", "knowledge_crawler/1.0"),
               "Accept": "application/json, application/xml, */*"}
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(base_delay * (2 ** attempt))
            resp = requests.get(url, params=params or {}, headers=headers, timeout=timeout)
            if resp.status_code == 429:
                LOG.warning("429 rate-limited on %s (attempt %d)", url, attempt + 1)
                if attempt < max_retries - 1:
                    continue
                return None
            if resp.status_code >= 500:
                LOG.warning("server error %d on %s (attempt %d)", resp.status_code, url, attempt + 1)
                if attempt < max_retries - 1:
                    continue
                return None
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as exc:
            LOG.warning("request failed %s (attempt %d): %s", url, attempt + 1, exc)
            if attempt < max_retries - 1:
                time.sleep(base_delay)
            else:
                return None
        except Exception as exc:  # pragma: no cover - defensive
            LOG.warning("unexpected error %s (attempt %d): %s", url, attempt + 1, exc)
            if attempt < max_retries - 1:
                time.sleep(base_delay)
            else:
                return None
    return None


# ---------------- Source fetchers ----------------
def fetch_arxiv(keywords: Sequence[str]) -> List[Entry]:
    if requests is None or not KNOWLEDGE_CONFIG["arxiv_categories"]:
        return []
    cats = KNOWLEDGE_CONFIG["arxiv_categories"]
    q = ("(" + " OR ".join("cat:" + c for c in cats) + ") AND (" +
         " OR ".join('"' + k + '"' for k in keywords[:5]) + ")")
    resp = fetch_with_retry(
        KNOWLEDGE_CONFIG["arxiv_base"],
        {"search_query": q, "sortBy": "submittedDate", "sortOrder": "descending",
         "max_results": KNOWLEDGE_CONFIG["max_results_per_source"]},
        max_retries=KNOWLEDGE_CONFIG["max_retries"],
        base_delay=KNOWLEDGE_CONFIG["base_retry_delay_s"],
        timeout=KNOWLEDGE_CONFIG["request_timeout_s"],
    )
    if resp is None:
        return []
    import xml.etree.ElementTree as ET
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as exc:
        LOG.warning("arxiv parse error: %s", exc)
        return []
    out: List[Entry] = []
    for node in root.findall("atom:entry", ns):
        t = node.find("atom:title", ns)
        s = node.find("atom:summary", ns)
        i = node.find("atom:id", ns)
        p = node.find("atom:published", ns)
        title = (t.text or "").strip().replace("\n", " ") if t is not None else ""
        url = (i.text or "").strip() if i is not None else ""
        if not title or not url:
            continue
        pub: Optional[datetime] = None
        if p is not None and p.text and dateutil_parser is not None:
            try:
                pub = dateutil_parser.parse(p.text)
            except (ValueError, TypeError):
                pub = None
        authors = [a.find("atom:name", ns).text for a in node.findall("atom:author", ns)
                   if a.find("atom:name", ns) is not None][:3]
        out.append(Entry(
            title=title, authors=authors,
            year=pub.year if pub else datetime.now().year,
            venue="ArXiv", doi_or_url=url,
            abstract=((s.text or "")[:300]).strip() if s is not None else "",
            published_date=pub, citation_count=0, source="arxiv",
        ))
    LOG.info("arxiv: %d candidates", len(out))
    return out


def fetch_semantic_scholar(keywords: Sequence[str]) -> List[Entry]:
    if requests is None:
        return []
    resp = fetch_with_retry(
        KNOWLEDGE_CONFIG["semantic_scholar_base"],
        {"query": " ".join(keywords[:4]),
         "fields": "title,authors,year,venue,externalIds,abstract,citationCount",
         "limit": KNOWLEDGE_CONFIG["max_results_per_source"]},
        max_retries=KNOWLEDGE_CONFIG["max_retries"],
        base_delay=KNOWLEDGE_CONFIG["base_retry_delay_s"],
        timeout=KNOWLEDGE_CONFIG["request_timeout_s"],
    )
    if resp is None:
        return []
    try:
        data = resp.json()
    except (ValueError, json.JSONDecodeError) as exc:
        LOG.warning("semantic scholar json error: %s", exc)
        return []
    out: List[Entry] = []
    for p in data.get("data", []) or []:
        title = p.get("title") or ""
        if not title:
            continue
        year = p.get("year") or datetime.now().year
        ext = p.get("externalIds", {}) or {}
        doi = ext.get("DOI") or (f"https://arxiv.org/abs/{ext['ArXiv']}" if ext.get("ArXiv") else "")
        if not doi:
            doi = "https://www.semanticscholar.org/paper/" + str(p.get("paperId", ""))
        try:
            year_int = int(year)
        except (TypeError, ValueError):
            year_int = datetime.now().year
        out.append(Entry(
            title=title,
            authors=[a.get("name", "") for a in (p.get("authors", []) or [])[:3]],
            year=year_int,
            venue=p.get("venue") or "Unknown",
            doi_or_url=doi,
            abstract=(p.get("abstract") or "")[:300],
            published_date=datetime(year_int, 1, 1),
            citation_count=int(p.get("citationCount", 0) or 0),
            source="semantic_scholar",
        ))
    LOG.info("semantic_scholar: %d candidates", len(out))
    return out


def fetch_rss() -> List[Entry]:
    if feedparser is None or not KNOWLEDGE_CONFIG["rss_feeds"]:
        return []
    out: List[Entry] = []
    for url in KNOWLEDGE_CONFIG["rss_feeds"]:
        try:
            feed = feedparser.parse(url)
        except Exception as exc:  # pragma: no cover - feedparser edge cases
            LOG.warning("rss %s failed: %s", url, exc)
            continue
        for item in getattr(feed, "entries", [])[:10]:
            title = item.get("title", "")
            link = item.get("link", "")
            if not title or not link:
                continue
            pp = item.get("published_parsed")
            pub: Optional[datetime] = None
            if pp and len(pp) >= 6:
                try:
                    pub = datetime(*pp[:6])
                except (TypeError, ValueError):
                    pub = None
            if pub is None:
                pub = datetime.now()
            out.append(Entry(
                title=title, authors=["Editorial"], year=pub.year, venue="RSS",
                doi_or_url=link, abstract=(item.get("summary", ""))[:200],
                published_date=pub, citation_count=0, source="rss",
            ))
    LOG.info("rss: %d candidates", len(out))
    return out


# ---------------- Formatting & persistence ----------------
def format_entry(entry: Dict[str, Any], score: float) -> str:
    """Markdown block for a single appended entry (UTF-8, em-dash)."""
    stamp = datetime.now().strftime("%Y-%m-%d")
    authors = ", ".join(entry.get("authors") or []) or "Unknown"
    return (
        "\n### " + stamp + " - " + (entry.get("title") or "Untitled") + "\n"
        "- **Authors:** " + authors + "\n"
        "- **Year:** " + str(entry.get("year", "")) + "\n"
        "- **Venue:** " + (entry.get("venue") or "Unknown") + "\n"
        "- **DOI/URL:** " + (entry.get("doi_or_url") or "") + "\n"
        "- **Relevance Score:** " + str(score) + "/10\n"
        "- **Key Finding:** " + (entry.get("abstract") or "No abstract available.") + "\n"
    )


def _atomic_write(path: Path, content: str) -> None:
    """Write via temp file + os.replace for crash-safe replacement."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def append_to_brain(entries: Sequence[Entry], dry_run: bool = False,
                    summary: Optional[RunSummary] = None) -> int:
    if not BRAIN_PATH.exists():
        LOG.error("brain not found: %s", BRAIN_PATH)
        return 0
    existing_hashes = load_existing_hashes()
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    new: List[Entry] = []
    for e in entries:
        if not e.doi_or_url:
            continue
        h = compute_hash(e.doi_or_url)
        if not h or h in existing_hashes:
            continue
        existing_hashes.add(h)
        e.score = score_entry({"title": e.title, "abstract": e.abstract,
                               "published_date": e.published_date,
                               "citation_count": e.citation_count},
                              KNOWLEDGE_CONFIG["keywords"], now)
        new.append(e)

    if not new:
        LOG.info("no new entries to append")
        if summary is not None:
            summary.new_entries = 0
        return 0

    new.sort(key=lambda x: x.score, reverse=True)
    kept = new[: KNOWLEDGE_CONFIG["max_new_entries_per_run"]]
    text = "".join(format_entry(e.to_dict(), e.score) for e in kept)

    if dry_run:
        LOG.info("[dry-run] would append %d entries", len(kept))
        if summary is not None:
            summary.new_entries = len(kept)
        return len(kept)

    content = BRAIN_PATH.read_text(encoding="utf-8")
    if UPDATE_LOG_HEADING in content:
        content += text
    else:
        content = content.rstrip() + "\n\n" + UPDATE_LOG_HEADING + "\n" + text
    try:
        _atomic_write(BRAIN_PATH, content)
    except OSError as exc:
        LOG.error("failed to write brain: %s", exc)
        if summary is not None:
            summary.errors.append(f"write failed: {exc}")
        return 0
    LOG.info("appended %d entries", len(kept))
    if summary is not None:
        summary.new_entries = len(kept)
        summary.appended = len(kept)
    return len(kept)


# ---------------- CLI ----------------
def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Knowledge crawl pipeline for skill 161.")
    ap.add_argument("--dry-run", action="store_true", help="compute but write nothing")
    ap.add_argument("--news-only", action="store_true", help="skip academic sources, RSS only")
    ap.add_argument("--keywords", nargs="+", default=KNOWLEDGE_CONFIG["keywords"],
                    help="override crawl keywords")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON summary")
    ap.add_argument("--log-file", type=Path, default=LOG_DIR / "knowledge_update.log",
                    help="path to append a structured log")
    ap.add_argument("--no-log-file", action="store_true", help="disable file logging")
    return ap


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = build_arg_parser()
    args = ap.parse_args(argv)

    log_file = None if args.no_log_file else args.log_file
    configure_logging(log_file)

    try:
        validate_config(KNOWLEDGE_CONFIG)
    except ValueError as exc:
        LOG.error("invalid config: %s", exc)
        return 2

    summary = RunSummary(started_at=datetime.now(timezone.utc).isoformat(),
                         dry_run=args.dry_run, news_only=args.news_only)

    LOG.info("start dry=%s news=%s keywords=%d", args.dry_run, args.news_only, len(args.keywords))

    all_entries: List[Entry] = []
    if not args.news_only:
        try:
            all_entries += fetch_arxiv(args.keywords)
        except Exception as exc:  # pragma: no cover - defensive
            LOG.error("arxiv source crashed: %s", exc)
            summary.errors.append(f"arxiv: {exc}")
        time.sleep(KNOWLEDGE_CONFIG["inter_source_delay_s"])
        try:
            all_entries += fetch_semantic_scholar(args.keywords)
        except Exception as exc:  # pragma: no cover - defensive
            LOG.error("semantic_scholar source crashed: %s", exc)
            summary.errors.append(f"semantic_scholar: {exc}")
        time.sleep(KNOWLEDGE_CONFIG["inter_source_delay_s"])
    try:
        all_entries += fetch_rss()
    except Exception as exc:  # pragma: no cover - defensive
        LOG.error("rss source crashed: %s", exc)
        summary.errors.append(f"rss: {exc}")

    summary.candidates = len(all_entries)
    summary.by_source = {}
    for e in all_entries:
        summary.by_source[e.source] = summary.by_source.get(e.source, 0) + 1

    n = append_to_brain(all_entries, args.dry_run, summary)
    summary.finished_at = datetime.now(timezone.utc).isoformat()
    LOG.info("done candidates=%d appended=%d", summary.candidates, n)

    if args.json:
        print(json.dumps(asdict(summary), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
