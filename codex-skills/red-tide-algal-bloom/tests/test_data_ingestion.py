"""Tests for scripts.data_ingestion (validation, transforms, dedup, manager)."""
import json
from datetime import datetime, timezone

import pytest

from data_ingestion import (
    DataIngestionManager,
    DataTransformPipeline,
    DataValidator,
    DedupChecker,
    IngestRecord,
    IngestSource,
)


def test_ingest_record_hash_is_deterministic():
    data = {"timestamp": "2026-07-16", "chl_a": 5.0, "lat": 1.0, "lon": 2.0}
    r1 = IngestRecord(source="s", timestamp=datetime.now(timezone.utc), data=data)
    r2 = IngestRecord(source="s", timestamp=datetime.now(timezone.utc), data=dict(data))
    assert r1.hash == r2.hash
    assert len(r1.hash) == 64  # sha256 hex


def test_validator_valid_satellite_record():
    v = DataValidator()
    rec = IngestRecord(
        source="sat", timestamp=datetime.now(timezone.utc),
        data={"timestamp": "2026-07-16", "chl_a": 8.5, "sst": 27.3, "lat": 29.7, "lon": -85.0},
    )
    assert v.validate_record(rec, "satellite") is True
    assert rec.validation_errors == []


def test_validator_missing_field_fails():
    v = DataValidator()
    rec = IngestRecord(
        source="sat", timestamp=datetime.now(timezone.utc),
        data={"timestamp": "2026-07-16", "chl_a": 8.5},  # missing sst, lat, lon
    )
    assert v.validate_record(rec, "satellite") is False
    assert any("sst" in e for e in rec.validation_errors)


def test_validator_out_of_range_fails():
    v = DataValidator()
    rec = IngestRecord(
        source="sat", timestamp=datetime.now(timezone.utc),
        data={"timestamp": "2026-07-16", "chl_a": 999.0, "sst": 27.3, "lat": 1.0, "lon": 2.0},
    )
    assert v.validate_record(rec, "satellite") is False
    assert any("chl_a" in e for e in rec.validation_errors)


def test_validator_knowledge_tier_range():
    v = DataValidator()
    rec = IngestRecord(
        source="kb", timestamp=datetime.now(timezone.utc),
        data={"timestamp": "2026-07-16", "citation": "x", "doi": "10.1/x", "tier": 2},
    )
    assert v.validate_record(rec, "knowledge") is True
    bad = IngestRecord(
        source="kb", timestamp=datetime.now(timezone.utc),
        data={"timestamp": "2026-07-16", "citation": "x", "doi": "10.1/x", "tier": 9},
    )
    assert v.validate_record(bad, "knowledge") is False


def test_transform_pipeline_applies_all():
    out = DataTransformPipeline.apply_transforms(
        {"chl_a": 5.0, "timestamp": "2026-07-16T12:00:00Z"},
        ["normalize_timestamps", "standardize_units", "fill_missing_metadata"],
    )
    assert out["timestamp"] == "2026-07-16T12:00:00"
    assert out["chl_a_unit"] == "mg/m\u00b3"
    assert "ingested_at" in out and out["version"] == "1.0"


def test_transform_pipeline_unknown_transform_skipped():
    out = DataTransformPipeline.apply_transforms({"a": 1}, ["does_not_exist"])
    assert out == {"a": 1}


def test_dedup_checker_round_trip(tmp_path):
    state = tmp_path / "state.json"
    d = DedupChecker(state)
    rec = IngestRecord(source="s", timestamp=datetime.now(timezone.utc), data={"x": 1})
    assert d.is_duplicate(rec) is False
    d.mark_seen(rec)
    assert d.is_duplicate(rec) is True
    d.save_state()
    d2 = DedupChecker(state)
    assert d2.is_duplicate(rec) is True


def test_manager_default_sources_and_toggle(tmp_path):
    mgr = DataIngestionManager(tmp_path)
    assert len(mgr.sources) >= 6
    names = {s.name for s in mgr.sources.values()}
    assert "satellite_chlorophyll" in names
    mgr.toggle_source("satellite_chlorophyll", False)
    assert mgr.sources["satellite_chlorophyll"].enabled is False


def test_manager_register_source(tmp_path):
    mgr = DataIngestionManager(tmp_path)
    new = IngestSource(name="custom", source_type="knowledge", endpoint="https://x")
    mgr.register_source(new)
    assert "custom" in mgr.sources
    listing = mgr.list_sources()
    assert any(item["name"] == "custom" for item in listing)


def test_manager_ingest_source_dry_run_does_not_store(tmp_path, monkeypatch):
    mgr = DataIngestionManager(tmp_path)
    # Force offline simulation so no real network call is attempted.
    monkeypatch.setattr(mgr, "_fetch_source_data", mgr._simulate_fetch)
    src = IngestSource(name="unit_sat", source_type="satellite",
                       endpoint="https://invalid.invalid/api",
                       transform_pipeline=["normalize_timestamps", "standardize_units"])
    mgr.register_source(src)
    result = mgr.ingest_source(src, dry_run=True)
    assert result.records_attempted >= 1
    assert result.records_ingested >= 1
    sat_dir = tmp_path / "data" / "satellite"
    # Nothing should have been written to disk in dry-run mode.
    assert not sat_dir.exists() or not list(sat_dir.glob("*.jsonl"))


def test_manager_ingest_all_writes_summary(tmp_path, monkeypatch):
    mgr = DataIngestionManager(tmp_path)
    # Force offline simulation so the run completes without network access.
    monkeypatch.setattr(mgr, "_fetch_source_data", mgr._simulate_fetch)
    for n in list(mgr.sources.keys()):
        if n != "knowledge_arxiv":
            mgr.toggle_source(n, False)
    results = mgr.ingest_all(source_types=["knowledge"])
    assert "knowledge_arxiv" in results
    summaries = list((tmp_path / "data" / "summaries").glob("ingest_summary_*.json"))
    assert summaries
    summary = json.loads(summaries[0].read_text(encoding="utf-8"))
    assert "total_ingested" in summary
