"""Tests for scripts.export_results (multi-format export + flattening)."""
import json
from pathlib import Path

import pytest

from export_results import ExportConfig, ResultsExporter


SAMPLE = {
    "metadata": {"region": "Vietnam-Central", "analyst": "skill-308"},
    "analysis": {
        "detection": {"method": "Sentinel-3 OLCI", "chl_a": 12.4},
        "triggers": {"sst": 28.1, "nutrients": "high"},
    },
    "conclusion": {"category": "Monitor (elevated)", "summary": "Elevated bloom risk."},
    "recommendations": [
        {"action": "Increase sampling frequency", "priority": "High"},
        {"action": "Prepare harvest contingency", "priority": "Medium"},
    ],
    "evidence_chain": [
        {"claim": "Chl-a above threshold", "evidence": ["Sentinel-3 overpass", "in-situ fluorometer"]},
    ],
    "disclosure": {"limitations": ["Cloud cover gaps"], "uncertainties": ["Wind mixing unknown"]},
}


@pytest.fixture
def exporter(tmp_path):
    return ResultsExporter(tmp_path)


def test_export_json_writes_file(exporter, tmp_path):
    cfg = ExportConfig(format="json", output_dir=tmp_path, filename_prefix="t",
                       include_timestamp=False)
    out = exporter.export(SAMPLE, cfg)
    assert out.suffix == ".json"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["conclusion"]["category"] == "Monitor (elevated)"


def test_export_markdown_has_required_sections(exporter, tmp_path):
    cfg = ExportConfig(format="markdown", output_dir=tmp_path, filename_prefix="t",
                       include_timestamp=False)
    out = exporter.export(SAMPLE, cfg)
    text = out.read_text(encoding="utf-8")
    assert "# Red Tide Analysis Results" in text
    assert "## Conclusion" in text
    assert "Monitor (elevated)" in text
    assert "## Recommendations" in text
    assert "## Evidence Chain" in text
    assert "## Limitations & Disclosure" in text


def test_export_html_valid_structure(exporter, tmp_path):
    cfg = ExportConfig(format="html", output_dir=tmp_path, filename_prefix="t",
                       include_timestamp=False)
    out = exporter.export(SAMPLE, cfg)
    html = out.read_text(encoding="utf-8")
    assert html.startswith("<!DOCTYPE html>")
    assert "Monitor (elevated)" in html
    assert "</html>" in html


def test_export_csv_single_record(exporter, tmp_path):
    cfg = ExportConfig(format="csv", output_dir=tmp_path, filename_prefix="t",
                       include_timestamp=False)
    out = exporter.export(SAMPLE, cfg)
    text = out.read_text(encoding="utf-8")
    assert "conclusion_category" in text.splitlines()[0]  # flattened header


def test_export_csv_batch_with_metadata(exporter, tmp_path):
    batch = {
        "cases": [
            {"case_id": "c1", "success": True, "duration_seconds": 1.2,
             "metadata": {"region": "VN"}},
            {"case_id": "c2", "success": False, "duration_seconds": 0.4,
             "error_message": "boom"},
        ]
    }
    cfg = ExportConfig(format="csv", output_dir=tmp_path, filename_prefix="t",
                       include_timestamp=False, include_metadata=True)
    out = exporter.export(batch, cfg)
    lines = out.read_text(encoding="utf-8").splitlines()
    assert "case_id" in lines[0]
    assert "region" in lines[0]  # metadata column flattened in
    assert any("c1" in line for line in lines)
    assert any("c2" in line for line in lines)


def test_export_unknown_format_raises(exporter, tmp_path):
    cfg = ExportConfig(format="xml", output_dir=tmp_path, filename_prefix="t")
    with pytest.raises(ValueError):
        exporter.export(SAMPLE, cfg)


def test_load_result_round_trip(exporter, tmp_path):
    cfg = ExportConfig(format="json", output_dir=tmp_path, filename_prefix="t",
                       include_timestamp=False)
    out = exporter.export(SAMPLE, cfg)
    loaded = exporter.load_result(out)
    assert loaded["conclusion"]["category"] == "Monitor (elevated)"


def test_md_alias_routes_to_markdown(exporter, tmp_path):
    cfg = ExportConfig(format="md", output_dir=tmp_path, filename_prefix="t",
                       include_timestamp=False)
    out = exporter.export(SAMPLE, cfg)
    assert out.suffix == ".md"
