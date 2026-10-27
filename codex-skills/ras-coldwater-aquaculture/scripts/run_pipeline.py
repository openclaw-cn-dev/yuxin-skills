"""scripts/run_pipeline.py ? CLI entry point for the ras_aqua engine.

Runs a full analysis from a JSON requirements file (or stdin) and prints the
structured report as JSON. Designed for local use, CI, and cron-driven
batch analysis.

Usage:
    python scripts/run_pipeline.py --input requirements.json
    python scripts/run_pipeline.py --stdin < requirements.json
    python scripts/run_pipeline.py --input requirements.json --pretty
    python scripts/run_pipeline.py --describe        # print engine capabilities

Exit codes: 0 = analysis produced; 1 = input/config error.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Make src importable when run as a script.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from ras_aqua import Engine  # noqa: E402
from ras_aqua.errors import RasAquaError  # noqa: E402


def _load_input(args) -> dict:
    if args.stdin:
        raw = sys.stdin.read()
    elif args.input:
        raw = Path(args.input).read_text(encoding="utf-8-sig")
    else:
        raise SystemExit("error: provide --input PATH or --stdin")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: invalid JSON input: {exc}") from exc


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the ras-coldwater-aquaculture analysis pipeline.")
    ap.add_argument("--input", help="Path to a JSON requirements file.")
    ap.add_argument("--stdin", action="store_true", help="Read JSON requirements from stdin.")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print the JSON report.")
    ap.add_argument("--describe", action="store_true", help="Print engine capabilities and exit.")
    ap.add_argument("--message", help="Optional free-text user message (for routing).")
    ap.add_argument("--log-level", default=None, help="Override log level (DEBUG/INFO/WARNING/ERROR).")
    args = ap.parse_args()

    if args.log_level:
        os.environ["RAS_LOG_LEVEL"] = args.log_level

    try:
        engine = Engine.from_config()
    except RasAquaError as exc:
        print(json.dumps({"error": exc.to_dict()}), file=sys.stderr)
        return 1

    if args.describe:
        print(json.dumps(engine.describe(), indent=2, ensure_ascii=False))
        return 0

    try:
        req = _load_input(args)
    except SystemExit as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    try:
        report = engine.run(user_message=args.message or "", requirements=req)
    except RasAquaError as exc:
        print(json.dumps({"error": exc.to_dict()}), file=sys.stderr)
        return 1

    out = report.to_dict()
    indent = 2 if args.pretty else None
    print(json.dumps(out, indent=indent, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
