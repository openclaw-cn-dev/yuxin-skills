# -*- coding: utf-8 -*-
"""
knowledge_updater.py — Production SECOND-KNOWLEDGE-BRAIN crawler for
aquaculture-water-quality-optimizer.

Design goals
  * Use real scholarly APIs (PubMed E-utilities, Crossref, Semantic Scholar, arXiv)
    rather than scraping search pages.
  * Idempotent: deduplicate by DOI or URL hash.
  * Resilient: each API is optional; failures in one provider do not crash the run.
  * Observable: structured logging and dry-run JSON output.
  * Rate-limited: polite delays between API calls.

Usage:
    python tools/knowledge_updater.py --dry-run
    python tools/knowledge_updater.py --providers pubmed crossref semanticscholar --since 2023-01-01
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import os
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Set

# Local schema model
from schemas import KnowledgeEntry

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.join(HERE, "..", "SECOND-KNOWLEDGE-BRAIN.md")

LOGGER = logging.getLogger("knowledge_updater")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DOMAIN_QUERIES = [
    "aquaculture water quality dissolved oxygen",
    "ammonia toxicity fish shrimp un-ionized NH3",
    "biofloc technology water quality C:N ratio",
    "recirculating aquaculture system RAS nitrification",
    "aquaculture biosecurity disease outbreak WOAH",
    "pond carrying capacity stocking density aquaculture",
    "nitrite toxicity aquaculture chloride",
    "pH alkalinity stability aquaculture",
]

VENUE_KEYWORDS = [
    "aquaculture",
    "aquacultural engineering",
    "fish",
    "shrimp",
    "biofloc",
    "recirculating",
    "water quality",
]


def _hash(url: str, doi: Optional[str] = None) -> str:
    key = (doi or "").strip().lower() + "|" + (url or "").strip().lower()
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def load_existing_hashes(path: str) -> Set[str]:
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return set(re.findall(r"<!--hash:([0-9a-f]{16})-->", text))


# ---------------------------------------------------------------------------
# API clients
# ---------------------------------------------------------------------------
class BaseProvider:
    name: str = "base"

    async def search(self, query: str, since: Optional[date] = None, max_results: int = 10) -> List[KnowledgeEntry]:
        raise NotImplementedError


class PubMedProvider(BaseProvider):
    """PubMed E-utilities: esearch -> esummary.
    No API key required for moderate use; NCBI requests a tool/email identifier.
    """

    name = "pubmed"

    def __init__(self, email: str = "dev@example.com", tool: str = "aquaculture-wq-optimizer"):
        self.email = email
        self.tool = tool

    async def search(self, query: str, since: Optional[date] = None, max_results: int = 10) -> List[KnowledgeEntry]:
        try:
            import aiohttp
        except ImportError:
            LOGGER.warning("aiohttp not installed; PubMed provider skipped")
            return []

        entries: List[KnowledgeEntry] = []
        async with aiohttp.ClientSession() as session:
            esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            date_filter = f" AND {since.year}:{date.today().year}[pdat]" if since else ""
            params = {
                "db": "pubmed",
                "term": f"({query}){date_filter}",
                "retmax": str(max_results),
                "retmode": "json",
                "tool": self.tool,
                "email": self.email,
            }
            try:
                async with session.get(esearch_url, params=params, timeout=30) as resp:
                    data = await resp.json()
            except Exception as exc:
                LOGGER.warning("PubMed esearch failed: %s", exc)
                return []

            ids = (data or {}).get("esearchresult", {}).get("idlist", []) or []
            if not ids:
                return []

            esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "json",
                "tool": self.tool,
                "email": self.email,
            }
            try:
                async with session.get(esummary_url, params=summary_params, timeout=30) as resp:
                    summary = await resp.json()
            except Exception as exc:
                LOGGER.warning("PubMed esummary failed: %s", exc)
                return []

            results = (summary or {}).get("result", {}) or {}
            for pmid in ids:
                rec = results.get(pmid, {})
                if not rec:
                    continue
                title = rec.get("title", "") or "Untitled"
                authors = ", ".join(a.get("name", "") for a in rec.get("authors", []))[:80]
                year = self._extract_year(rec.get("pubdate", "") or rec.get("sortpubdate", ""))
                doi = rec.get("elocationid", "") or ""
                if doi.startswith("doi:"):
                    doi = doi[4:]
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                entries.append(
                    KnowledgeEntry(
                        title=title,
                        authors=authors,
                        year=year,
                        venue="PubMed / " + (rec.get("fulljournalname", "") or rec.get("source", "")),
                        url=url,
                        doi=doi or None,
                        relevance=f"Matched query: {query}",
                        source_api="pubmed",
                    )
                )
            await asyncio.sleep(0.34)  # NCBI rate limit ~3 req/s without key
        return entries

    @staticmethod
    def _extract_year(date_text: str) -> int:
        match = re.search(r"(\d{4})", date_text)
        return int(match.group(1)) if match else date.today().year


class CrossrefProvider(BaseProvider):
    """Crossref REST API; polite User-Agent required."""

    name = "crossref"

    async def search(self, query: str, since: Optional[date] = None, max_results: int = 10) -> List[KnowledgeEntry]:
        try:
            import aiohttp
        except ImportError:
            LOGGER.warning("aiohttp not installed; Crossref provider skipped")
            return []

        entries: List[KnowledgeEntry] = []
        headers = {"User-Agent": "aquaculture-wq-optimizer/1.0 (mailto:dev@example.com)"}
        filter_parts = []
        if since:
            filter_parts.append(f"from-pub-date:{since.isoformat()}")
        filter_param = ":".join(filter_parts) if filter_parts else None

        url = "https://api.crossref.org/works"
        params: Dict[str, Any] = {
            "query": query,
            "rows": min(max_results, 20),
            "sort": "relevance",
            "order": "desc",
            "select": "DOI,title,author,published-print,published-online,container-title,URL",
        }
        if filter_param:
            params["filter"] = filter_param

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, params=params, timeout=30) as resp:
                    data = await resp.json()
            except Exception as exc:
                LOGGER.warning("Crossref request failed: %s", exc)
                return []

            message = (data or {}).get("message", {}) or {}
            for item in message.get("items", []) or []:
                title = self._safe_title(item.get("title"))
                authors = self._safe_authors(item.get("author", []))
                year = self._extract_year(item.get("published-print") or item.get("published-online"))
                doi = item.get("DOI", "")
                url = item.get("URL") or (f"https://doi.org/{doi}" if doi else "")
                venue = ", ".join(item.get("container-title", []) or [])
                entries.append(
                    KnowledgeEntry(
                        title=title,
                        authors=authors,
                        year=year,
                        venue=venue or "Crossref",
                        url=url,
                        doi=doi or None,
                        relevance=f"Matched query: {query}",
                        source_api="crossref",
                    )
                )
            await asyncio.sleep(1.0)  # Crossref polite pool
        return entries

    @staticmethod
    def _safe_title(titles: List[str]) -> str:
        return (titles[0] if titles else "Untitled")[:250]

    @staticmethod
    def _safe_authors(authors: List[Dict[str, Any]]) -> str:
        parts = []
        for a in authors[:4]:
            given = a.get("given", "")
            family = a.get("family", "")
            parts.append(f"{given} {family}".strip())
        return ", ".join(parts)[:100]

    @staticmethod
    def _extract_year(pub_date: Optional[Dict[str, Any]]) -> int:
        if not pub_date:
            return date.today().year
        parts = pub_date.get("date-parts", [[]])
        if parts and parts[0]:
            return parts[0][0]
        return date.today().year


class SemanticScholarProvider(BaseProvider):
    """Semantic Scholar Graph API. No key required for low-volume use."""

    name = "semanticscholar"

    async def search(self, query: str, since: Optional[date] = None, max_results: int = 10) -> List[KnowledgeEntry]:
        try:
            import aiohttp
        except ImportError:
            LOGGER.warning("aiohttp not installed; Semantic Scholar provider skipped")
            return []

        entries: List[KnowledgeEntry] = []
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params: Dict[str, Any] = {
            "query": query,
            "fields": "title,authors,year,venue,openAccessPdf,externalIds,abstract",
            "limit": min(max_results, 20),
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as resp:
                    data = await resp.json()
            except Exception as exc:
                LOGGER.warning("Semantic Scholar request failed: %s", exc)
                return []

            for item in (data or {}).get("data", []) or []:
                title = item.get("title") or "Untitled"
                authors = ", ".join(a.get("name", "") for a in item.get("authors", [])[:4])
                year = item.get("year") or date.today().year
                external = item.get("externalIds", {}) or {}
                doi = external.get("DOI")
                pdf = (item.get("openAccessPdf") or {}).get("url")
                url = pdf or (f"https://doi.org/{doi}" if doi else f"https://www.semanticscholar.org/paper/{item.get('paperId','')}")
                venue = item.get("venue") or "Semantic Scholar"
                entries.append(
                    KnowledgeEntry(
                        title=title,
                        authors=authors,
                        year=year,
                        venue=venue,
                        url=url,
                        doi=doi,
                        abstract=item.get("abstract", "")[:500],
                        relevance=f"Matched query: {query}",
                        source_api="semanticscholar",
                    )
                )
            await asyncio.sleep(1.0)
        return entries


class ArxivProvider(BaseProvider):
    """arXiv API for preprints occasionally relevant to aquaculture ML/modeling."""

    name = "arxiv"

    async def search(self, query: str, since: Optional[date] = None, max_results: int = 10) -> List[KnowledgeEntry]:
        try:
            import aiohttp
        except ImportError:
            LOGGER.warning("aiohttp not installed; arXiv provider skipped")
            return []

        entries: List[KnowledgeEntry] = []
        url = "http://export.arxiv.org/api/query"
        since_clause = f" AND submittedDate:[{since.isoformat()} TO {date.today().isoformat()}]" if since else ""
        params = {
            "search_query": f"all:{query}{since_clause}",
            "start": 0,
            "max_results": min(max_results, 20),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as resp:
                    text = await resp.text()
            except Exception as exc:
                LOGGER.warning("arXiv request failed: %s", exc)
                return []

            import xml.etree.ElementTree as ET
            root = ET.fromstring(text.encode("utf-8"))
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                title = (entry.findtext("atom:title", "", namespaces=ns) or "").strip().replace("\n", " ")
                year = self._extract_year(entry.findtext("atom:published", "", namespaces=ns))
                authors = ", ".join(a.text for a in entry.findall("atom:author/atom:name", ns) if a.text)[:100]
                id_url = entry.findtext("atom:id", "", namespaces=ns)
                url = id_url
                abstract = (entry.findtext("atom:summary", "", namespaces=ns) or "")[:500]
                entries.append(
                    KnowledgeEntry(
                        title=title,
                        authors=authors,
                        year=year,
                        venue="arXiv preprint",
                        url=url,
                        relevance=f"Matched query: {query}",
                        source_api="arxiv",
                    )
                )
            await asyncio.sleep(3.0)  # arXiv asks for 3 s between requests
        return entries

    @staticmethod
    def _extract_year(iso_text: str) -> int:
        m = re.search(r"(\d{4})", iso_text)
        return int(m.group(1)) if m else date.today().year


# ---------------------------------------------------------------------------
# Scoring, dedup, append
# ---------------------------------------------------------------------------
def score_entry(entry: KnowledgeEntry) -> float:
    """Recency + domain keyword relevance in [0,1]."""
    now = date.today().year
    recency = max(0.0, 1.0 - (now - entry.year) / 10.0) if 1900 <= entry.year <= now else 0.3
    text = f"{entry.title} {entry.abstract or ''} {entry.venue or ''}".lower()
    hits = sum(1 for k in VENUE_KEYWORDS if k in text)
    relevance = min(1.0, hits / max(1, len(VENUE_KEYWORDS)))
    return round(0.5 * recency + 0.5 * relevance, 3)


def format_entry(entry: KnowledgeEntry) -> str:
    h = _hash(entry.url or "", entry.doi)
    return (
        f"- {entry.queried_date.isoformat()} | score={score_entry(entry)} | **{entry.title}** | {entry.authors} "
        f"| {entry.year} | {entry.venue} | {entry.url or ''} "
        f"<!--hash:{h}-->"
    )


async def crawl_all(
    providers: List[str],
    queries: List[str],
    since: Optional[date] = None,
    max_per_query: int = 10,
) -> List[KnowledgeEntry]:
    """Run selected providers over all queries and merge results."""
    registry = {
        "pubmed": PubMedProvider(),
        "crossref": CrossrefProvider(),
        "semanticscholar": SemanticScholarProvider(),
        "arxiv": ArxivProvider(),
    }
    active = [registry[p] for p in providers if p in registry]
    if not active:
        LOGGER.warning("No active providers selected.")
        return []

    tasks = []
    for provider in active:
        for q in queries:
            tasks.append(provider.search(q, since=since, max_results=max_per_query))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    entries: List[KnowledgeEntry] = []
    for res in results:
        if isinstance(res, Exception):
            LOGGER.warning("Provider task failed: %s", res)
            continue
        entries.extend(res)
    return entries


def append_entries(entries: List[KnowledgeEntry], path: str) -> int:
    existing = load_existing_hashes(path)
    added = 0
    lines = []
    today = date.today().isoformat()
    for e in sorted(entries, key=score_entry, reverse=True):
        h = _hash(e.url or "", e.doi)
        if h in existing:
            continue
        existing.add(h)
        lines.append(format_entry(e))
        added += 1
    if added:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n### Crawl {today} (+{added})\n" + "\n".join(lines) + "\n")
    LOGGER.info("Appended %d new entries to %s", added, path)
    return added


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_since(text: str) -> date:
    return datetime.strptime(text, "%Y-%m-%d").date()


def main():
    ap = argparse.ArgumentParser(
        description="Crawl authoritative aquaculture sources and append new entries to SECOND-KNOWLEDGE-BRAIN.md"
    )
    ap.add_argument("--dry-run", action="store_true", help="Print candidate entries without writing")
    ap.add_argument(
        "--providers",
        nargs="+",
        default=["pubmed", "crossref", "semanticscholar"],
        choices=["pubmed", "crossref", "semanticscholar", "arxiv"],
        help="API providers to query",
    )
    ap.add_argument("--since", type=parse_since, default=None, help="Only fetch records published on/after YYYY-MM-DD")
    ap.add_argument("--max-per-query", type=int, default=10, help="Maximum results per query per provider")
    ap.add_argument("--brain", default=BRAIN, help="Path to SECOND-KNOWLEDGE-BRAIN.md")
    ap.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        entries = asyncio.run(
            crawl_all(args.providers, DOMAIN_QUERIES, since=args.since, max_per_query=args.max_per_query)
        )
    except Exception as exc:
        LOGGER.error("Crawl stage failed: %s", exc)
        entries = []

    if args.dry_run:
        payload = []
        for e in sorted(entries, key=score_entry, reverse=True):
            d = e.model_dump()
            d["score"] = score_entry(e)
            payload.append(d)
        print(json.dumps(payload, indent=2, default=str)[:4000])
        return

    append_entries(entries, args.brain)


if __name__ == "__main__":
    main()

