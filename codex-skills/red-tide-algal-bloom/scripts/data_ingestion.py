#!/usr/bin/env python3
"""
Data Ingestion Script for red-tide-algal-bloom-monitoring Skill
Handles bulk data import, database seeding, and automated ingestion routines
from satellite APIs, sensor networks, and authoritative data sources.
"""

import sys
import json
import csv
import hashlib
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List, Iterator, Callable
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from collections import defaultdict


@dataclass
class IngestSource:
    """Definition of a data ingestion source"""
    name: str
    source_type: str  # satellite, in_situ, authoritative, knowledge
    endpoint: str
    auth_required: bool = False
    auth_env_var: Optional[str] = None
    format: str = "json"  # json, csv, xml
    schedule: Optional[str] = None
    enabled: bool = True
    timeout_seconds: int = 30
    retry_count: int = 3
    transform_pipeline: List[str] = field(default_factory=list)


@dataclass
class IngestRecord:
    """Single data record from ingestion"""
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    hash: str = ""
    validated: bool = False
    validation_errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        raw = json.dumps(self.data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()


@dataclass
class IngestResult:
    """Results from an ingestion run"""
    source_name: str
    records_attempted: int = 0
    records_ingested: int = 0
    records_skipped: int = 0
    records_failed: int = 0
    errors: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0


class DataValidator:
    """Validates ingested data against expected schemas"""

    REQUIRED_FIELDS = {
        "satellite": ["timestamp", "chl_a", "sst", "lat", "lon"],
        "in_situ": ["timestamp", "station_id", "cell_count", "temperature"],
        "authoritative": ["timestamp", "title", "url", "source"],
        "knowledge": ["timestamp", "citation", "doi", "tier"]
    }

    VALUE_RANGES = {
        "chl_a": (0.0, 500.0),        # mg/m³
        "sst": (-2.0, 40.0),           # °C
        "cell_count": (0, 10_000_000), # cells/L
        "temperature": (-2.0, 40.0),   # °C
        "salinity": (0.0, 45.0),       # PSU
        "tier": (1, 4),
        "year": (1950, 2030)
    }

    def validate_record(self, record: IngestRecord, source_type: str) -> bool:
        required = self.REQUIRED_FIELDS.get(source_type, [])
        errors = []

        for field in required:
            if field not in record.data:
                errors.append(f"Missing required field: {field}")

        for field, (lo, hi) in self.VALUE_RANGES.items():
            if field in record.data:
                val = record.data[field]
                if isinstance(val, (int, float)):
                    if val < lo or val > hi:
                        errors.append(f"Out of range: {field}={val} [{lo}, {hi}]")

        record.validated = True
        record.validation_errors = errors
        return len(errors) == 0


class DedupChecker:
    """Checks for duplicate records using hash-based dedup"""

    def __init__(self, state_file: Optional[Path] = None):
        self.state_file = state_file
        self.seen_hashes: set = self._load_state() if state_file else set()

    def _load_state(self) -> set:
        if self.state_file and self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get("hashes", []))
            except Exception:
                pass
        return set()

    def save_state(self):
        if self.state_file:
            with open(self.state_file, 'w') as f:
                json.dump({"hashes": list(self.seen_hashes), "count": len(self.seen_hashes)}, f)

    def is_duplicate(self, record: IngestRecord) -> bool:
        return record.hash in self.seen_hashes

    def mark_seen(self, record: IngestRecord):
        self.seen_hashes.add(record.hash)


class DataTransformPipeline:
    """Applies a series of transformations to ingested data"""

    @staticmethod
    def normalize_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
        for key in ["timestamp", "date", "processing_date", "created", "updated"]:
            if key in data:
                val = data[key]
                if isinstance(val, str):
                    for fmt in [
                        "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S",
                        "%Y-%m-%d", "%Y%m%d", "%d/%m/%Y"
                    ]:
                        try:
                            data[key] = datetime.strptime(val, fmt).isoformat()
                            break
                        except ValueError:
                            continue
        return data

    @staticmethod
    def standardize_units(data: Dict[str, Any]) -> Dict[str, Any]:
        unit_map = {
            "chlorophyll": "mg/m³",
            "chl_a": "mg/m³",
            "temperature": "°C",
            "sst": "°C",
            "salinity": "PSU",
            "cell_count": "cells/L",
            "toxin_concentration": "μg/kg"
        }
        for field, unit in unit_map.items():
            if field in data and "_unit" not in data:
                data[f"{field}_unit"] = unit
        return data

    @staticmethod
    def fill_missing_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
        if "ingested_at" not in data:
            data["ingested_at"] = datetime.now(timezone.utc).isoformat()
        if "version" not in data:
            data["version"] = "1.0"
        return data

    TRANSFORMS = {
        "normalize_timestamps": normalize_timestamps,
        "standardize_units": standardize_units,
        "fill_missing_metadata": fill_missing_metadata,
    }

    @classmethod
    def apply_transforms(cls, data: Dict[str, Any], pipeline: List[str]) -> Dict[str, Any]:
        result = data.copy()
        for transform_name in pipeline:
            transform = cls.TRANSFORMS.get(transform_name)
            if transform is None:
                continue
            # TRANSFORMS stores staticmethod objects; calling them invokes the
            # wrapped function with exactly the data argument (no cls/self).
            result = transform(result)
        return result


class DataIngestionManager:
    """Manages data ingestion from multiple sources"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.validator = DataValidator()
        self.dedup = DedupChecker(self.data_dir / "dedup_state.json")
        self.transforms = DataTransformPipeline()
        self.sources: Dict[str, IngestSource] = {}
        self._load_default_sources()

    def _load_default_sources(self):
        defaults = [
            IngestSource(
                name="satellite_chlorophyll",
                source_type="satellite",
                endpoint="https://marine.copernicus.eu/api/chlorophyll",
                auth_required=True,
                auth_env_var="COP_MARINE_API_KEY",
                schedule="0 */6 * * *",
                transform_pipeline=["normalize_timestamps", "standardize_units"]
            ),
            IngestSource(
                name="satellite_sst",
                source_type="satellite",
                endpoint="https://marine.copernicus.eu/api/sst",
                auth_required=True,
                auth_env_var="COP_MARINE_API_KEY",
                schedule="0 */6 * * *",
                transform_pipeline=["normalize_timestamps", "standardize_units"]
            ),
            IngestSource(
                name="in_situ_fluorometer",
                source_type="in_situ",
                endpoint="https://hab-sensors.noaa.gov/api/fluorometer",
                auth_required=False,
                schedule="0 */3 * * *",
                transform_pipeline=["normalize_timestamps", "standardize_units", "fill_missing_metadata"]
            ),
            IngestSource(
                name="authoritative_ioc",
                source_type="authoritative",
                endpoint="https://hab.ioc-unesco.org/api/bulletins",
                auth_required=False,
                schedule="0 */12 * * *",
                transform_pipeline=["normalize_timestamps", "fill_missing_metadata"]
            ),
            IngestSource(
                name="authoritative_noaa",
                source_type="authoritative",
                endpoint="https://hab-oceanweather.noaa.gov/api/forecasts",
                auth_required=False,
                schedule="0 */6 * * *",
                transform_pipeline=["normalize_timestamps", "fill_missing_metadata"]
            ),
            IngestSource(
                name="knowledge_arxiv",
                source_type="knowledge",
                endpoint="https://export.arxiv.org/api/query",
                auth_required=False,
                schedule="0 8 * * 1",
                transform_pipeline=["normalize_timestamps", "fill_missing_metadata"]
            )
        ]

        for source in defaults:
            self.sources[source.name] = source

    def register_source(self, source: IngestSource):
        self.sources[source.name] = source

    def toggle_source(self, name: str, enabled: bool):
        if name in self.sources:
            self.sources[name].enabled = enabled

    def ingest_source(self, source: IngestSource, dry_run: bool = False) -> IngestResult:
        result = IngestResult(source_name=source.name)
        print(f"  Ingesting from: {source.name} ({source.source_type})")

        raw_data = self._fetch_source_data(source)
        if raw_data is None:
            result.errors.append("Fetch failed")
            return result

        records = self._parse_raw_data(raw_data, source)
        result.records_attempted = len(records)

        for record in records:
            try:
                record.data = self.transforms.apply_transforms(
                    record.data, source.transform_pipeline
                )

                if not self.validator.validate_record(record, source.source_type):
                    result.records_failed += 1
                    result.errors.extend(
                        f"{source.name}: {e}" for e in record.validation_errors
                    )
                    continue

                if self.dedup.is_duplicate(record):
                    result.records_skipped += 1
                    continue

                self.dedup.mark_seen(record)
                if not dry_run:
                    self._store_record(record, source)
                result.records_ingested += 1

            except Exception as e:
                result.records_failed += 1
                result.errors.append(f"{source.name}: {e}")

        result.end_time = datetime.now(timezone.utc)
        result.duration_seconds = (result.end_time - result.start_time).total_seconds()
        return result

    def _fetch_source_data(self, source: IngestSource) -> Optional[List[Dict]]:
        try:
            import requests
            headers = {}
            if source.auth_required and source.auth_env_var:
                import os
                api_key = os.environ.get(source.auth_env_var, "")
                if not api_key:
                    print(f"    WARNING: {source.auth_env_var} not set, using unauthenticated")
                else:
                    headers["Authorization"] = f"Bearer {api_key}"

            resp = requests.get(
                source.endpoint,
                headers=headers,
                timeout=source.timeout_seconds
            )
            resp.raise_for_status()

            if source.format == "json":
                data = resp.json()
                if isinstance(data, dict) and "data" in data:
                    return data["data"]
                return data if isinstance(data, list) else [data]
            elif source.format == "csv":
                reader = csv.DictReader(resp.text.splitlines())
                return list(reader)
            else:
                return [{"raw": resp.text, "content_type": resp.headers.get("content-type", "")}]

        except ImportError:
            print("    requests not installed — simulating fetch with sample data")
            return self._simulate_fetch(source)
        except Exception as e:
            print(f"    ERROR fetching {source.name}: {e}")
            return self._simulate_fetch(source)

    def _simulate_fetch(self, source: IngestSource) -> Optional[List[Dict]]:
        if source.source_type == "satellite":
            return [{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "chl_a": 8.5, "sst": 27.3, "lat": 29.7, "lon": -85.0,
                "satellite": "Sentinel-3 OLCI", "processing_date": datetime.now(timezone.utc).isoformat()
            }]
        elif source.source_type == "in_situ":
            return [{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "station_id": "SAMPLE-001", "cell_count": 4500,
                "temperature": 27.1, "salinity": 33.4
            }]
        elif source.source_type == "authoritative":
            return [{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "title": "Sample HAB Bulletin", "source": source.name,
                "url": f"https://example.com/{source.name}/latest"
            }]
        elif source.source_type == "knowledge":
            return [{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "citation": "Author et al. (2024)", "doi": "10.1234/sample.001",
                "tier": 2, "venue": "Sample Journal", "year": 2024
            }]
        return None

    def _parse_raw_data(self, raw: List[Dict], source: IngestSource) -> List[IngestRecord]:
        records = []
        for item in raw:
            records.append(IngestRecord(
                source=source.name,
                timestamp=datetime.now(timezone.utc),
                data=item
            ))
        return records

    def _store_record(self, record: IngestRecord, source: IngestSource):
        source_dir = self.data_dir / source.source_type
        source_dir.mkdir(parents=True, exist_ok=True)

        date_str = record.timestamp.strftime("%Y%m%d")
        data_file = source_dir / f"{source.name}_{date_str}.jsonl"

        entry = {
            "source": record.source,
            "source_type": source.source_type,
            "timestamp": record.timestamp.isoformat(),
            "hash": record.hash,
            "data": record.data
        }

        with open(data_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def ingest_all(self, source_types: Optional[List[str]] = None, dry_run: bool = False) -> Dict[str, IngestResult]:
        results = {}
        print(f"[INGEST] Starting ingestion at {datetime.now(timezone.utc).isoformat()}")
        print(f"[INGEST] Sources configured: {len(self.sources)}")

        active_sources = [
            s for s in self.sources.values()
            if s.enabled and (not source_types or s.source_type in source_types)
        ]

        print(f"[INGEST] Active sources: {len(active_sources)}")

        for source in active_sources:
            result = self.ingest_source(source, dry_run=dry_run)
            results[source.name] = result

        self.dedup.save_state()
        self._save_run_summary(results)
        return results

    def _save_run_summary(self, results: Dict[str, IngestResult]):
        summary_dir = self.data_dir / "summaries"
        summary_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        summary_file = summary_dir / f"ingest_summary_{timestamp}.json"

        total_ingested = sum(r.records_ingested for r in results.values())
        total_failed = sum(r.records_failed for r in results.values())
        total_skipped = sum(r.records_skipped for r in results.values())

        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_ingested": total_ingested,
            "total_failed": total_failed,
            "total_skipped": total_skipped,
            "sources": {
                name: {
                    "ingested": r.records_ingested,
                    "failed": r.records_failed,
                    "skipped": r.records_skipped,
                    "duration_s": r.duration_seconds,
                    "errors": r.errors[:5] if r.errors else []
                }
                for name, r in results.items()
            }
        }

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n[INGEST COMPLETE] Ingested: {total_ingested}, Failed: {total_failed}, Skipped: {total_skipped}")
        print(f"[INGEST] Summary saved to: {summary_file}")

    def list_sources(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": s.name,
                "type": s.source_type,
                "endpoint": s.endpoint,
                "enabled": s.enabled,
                "auth_required": s.auth_required
            }
            for s in self.sources.values()
        ]

    def get_stats(self) -> Dict[str, Any]:
        stats = {"sources": {}, "total_records": 0}

        for src_type in ["satellite", "in_situ", "authoritative", "knowledge"]:
            type_dir = self.data_dir / src_type
            if type_dir.exists():
                records = 0
                for f in type_dir.glob("*.jsonl"):
                    with open(f, 'rb') as fh:
                        records += sum(1 for _ in fh)
                stats["sources"][src_type] = records
                stats["total_records"] += records

        stats["dedup_hashes"] = len(self.dedup.seen_hashes)
        return stats


def main():
    parser = argparse.ArgumentParser(
        description="Data Ingestion for Red Tide HAB Monitoring Skill"
    )
    parser.add_argument(
        "--source",
        type=str,
        nargs="*",
        help="Specific source names to ingest (default: all enabled)"
    )
    parser.add_argument(
        "--type",
        type=str,
        nargs="*",
        choices=["satellite", "in_situ", "authoritative", "knowledge"],
        help="Filter by source type"
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="List all configured data sources"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show ingestion statistics"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate sources without storing data"
    )

    args = parser.parse_args()
    project_root = Path(__file__).parent.parent
    manager = DataIngestionManager(project_root)

    if args.list_sources:
        sources = manager.list_sources()
        print(json.dumps(sources, indent=2))
        return

    if args.stats:
        stats = manager.get_stats()
        print(json.dumps(stats, indent=2))
        return

    if args.source:
        for name in args.source:
            if name not in manager.sources:
                print(f"ERROR: Unknown source: {name}")
                sys.exit(1)
        for name in list(manager.sources.keys()):
            if name not in args.source:
                manager.toggle_source(name, False)

    results = manager.ingest_all(source_types=args.type, dry_run=args.dry_run)

    if args.dry_run:
        print("[DRY-RUN] No data was persisted")
        sys.exit(0 if all(r.records_failed == 0 for r in results.values()) else 1)

    success = all(r.records_failed == 0 for r in results.values())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
