"""scripts/ingest_water_log.py ? ingest a water-quality CSV/JSON log into a
requirements JSON file for the engine.

Accepts a CSV with columns matching the water-quality fields (T_C, DO_mgL, pH,
TAN_mgL, NO2_mgL, NO3_mgL, alkalinity_mgL, CO2_mgL, salinity_ppt) plus optional
metadata columns (species, life_stage, tank_volume_m3, ...), takes the most
recent row, and writes a requirements JSON file ready for run_pipeline.py.

Usage:
    python scripts/ingest_water_log.py --log water.csv --species rainbow_trout \\
        --life-stage growout --out requirements.json
    python scripts/ingest_water_log.py --log water.json --out requirements.json
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

WQ_FIELDS = ("T_C", "DO_mgL", "pH", "TAN_mgL", "NO2_mgL", "NO3_mgL",
             "alkalinity_mgL", "CO2_mgL", "salinity_ppt")
META_FIELDS = ("species", "life_stage", "tank_volume_m3", "makeup_pct",
               "biofilter_type", "biofilter_area_m2", "biofilter_media_volume_m3",
               "flow_lpm", "biomass_kg", "feed_kg_day", "feed_protein_pct",
               "target_objective", "language")


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _from_csv(path: Path) -> list:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _from_json(path: Path) -> list:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):
        data = [data]
    return data


def _build(rows: list, args) -> dict:
    if not rows:
        raise SystemExit("error: log contains no rows")
    # Most recent row: prefer a timestamp/datetime column, else last row.
    ts_key = next((k for k in rows[0] if k.lower() in ("timestamp", "datetime", "date", "time")), None)
    if ts_key:
        rows.sort(key=lambda r: r.get(ts_key) or "", reverse=True)
    row = rows[0]
    wq = {}
    for f in WQ_FIELDS:
        if f in row and row[f] not in (None, ""):
            wq[f] = _num(row[f])
    if "T_C" not in wq or wq["T_C"] is None:
        raise SystemExit("error: T_C is required in the water-quality log")
    ras = {}
    for f in ("tank_volume_m3", "makeup_pct", "biofilter_type", "biofilter_area_m2",
              "biofilter_media_volume_m3", "flow_lpm"):
        if f in row and row[f] not in (None, ""):
            ras[f] = _num(row[f]) if f != "biofilter_type" else row[f]
    req = {
        "species": args.species or row.get("species") or "",
        "life_stage": args.life_stage or row.get("life_stage") or "",
        "wq": wq,
        "ras_config": ras,
        "biomass_kg": _num(row.get("biomass_kg")) if "biomass_kg" in row else None,
        "feed_kg_day": _num(row.get("feed_kg_day")) if "feed_kg_day" in row else None,
        "feed_protein_pct": _num(row.get("feed_protein_pct")) if "feed_protein_pct" in row else None,
        "target_objective": args.objective or row.get("target_objective") or "health_assessment",
        "language": args.language or row.get("language") or "en",
        "notes": f"Ingested from {args.log} at {datetime.utcnow().isoformat()}Z",
    }
    return req


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest a water-quality log into a requirements JSON.")
    ap.add_argument("--log", required=True, help="Path to CSV or JSON water-quality log.")
    ap.add_argument("--species", help="Override species key.")
    ap.add_argument("--life-stage", dest="life_stage", help="Override life stage.")
    ap.add_argument("--objective", default="health_assessment", help="Target objective.")
    ap.add_argument("--language", default="en", help="Output language (en/vi).")
    ap.add_argument("--out", required=True, help="Output requirements JSON path.")
    args = ap.parse_args()

    path = Path(args.log)
    if not path.is_file():
        print(json.dumps({"error": f"log not found: {path}"}), file=sys.stderr)
        return 1
    rows = _from_csv(path) if path.suffix.lower() == ".csv" else _from_json(path)
    try:
        req = _build(rows, args)
    except SystemExit as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    Path(args.out).write_text(json.dumps(req, indent=2, ensure_ascii=False),
                              encoding="utf-8")
    print(json.dumps({"ok": True, "out": args.out, "species": req["species"],
                      "T_C": req["wq"]["T_C"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
