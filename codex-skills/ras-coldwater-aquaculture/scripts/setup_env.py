"""scripts/setup_env.py ? local setup routine for ras-coldwater-aquaculture.

Verifies Python version, creates the logs/ directory, checks optional
dependencies, loads & validates configuration, and runs a smoke test of the
engine. Safe to re-run; no destructive operations.

Usage:
    python scripts/setup_env.py
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

OPTIONAL_DEPS = ("requests", "feedparser", "dateutil")


def _ok(msg: str) -> None:
    print(f"[OK]   {msg}")


def _warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}", file=sys.stderr)


def main() -> int:
    if sys.version_info < (3, 9):
        _fail(f"Python 3.9+ required; got {sys.version.split()[0]}")
        return 1
    _ok(f"Python {sys.version.split()[0]}")

    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    _ok(f"logs directory: {logs}")

    for dep in OPTIONAL_DEPS:
        try:
            importlib.import_module(dep)
            _ok(f"optional dependency '{dep}' available")
        except ImportError:
            _warn(f"optional dependency '{dep}' missing (crawl pipeline degrades gracefully)")

    try:
        from config import load_settings
        s = load_settings()
        _ok(f"config loaded: {s.skill_name} v{s.version}, "
            f"{len(s.species_envelopes)} species, {len(s.biofilter_media)} media")
    except Exception as exc:
        _fail(f"config load failed: {exc}")
        return 1

    try:
        from ras_aqua import Engine
        engine = Engine.from_config()
        req = {"species": "rainbow_trout", "life_stage": "growout",
               "wq": {"T_C": 13, "DO_mgL": 8.0, "pH": 7.2, "TAN_mgL": 0.3},
               "ras_config": {"biofilter_type": "mbbr_kaldnes_k1",
                              "biofilter_area_m2": 800, "tank_volume_m3": 50},
               "biomass_kg": 1000, "feed_kg_day": 10,
               "target_objective": "health_assessment", "language": "en"}
        report = engine.run(requirements=req)
        _ok(f"smoke test: verdict={report.verdict.verdict.value if report.verdict else 'n/a'}, "
            f"degradation={report.degradation_level}, "
            f"gates={sum(1 for v in report.quality_gate_results.values() if v=='pass')}/11 pass")
    except Exception as exc:
        _fail(f"smoke test failed: {exc}")
        return 1

    _ok("setup complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
