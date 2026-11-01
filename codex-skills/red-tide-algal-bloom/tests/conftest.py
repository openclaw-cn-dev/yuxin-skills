"""Pytest configuration: make scripts/, tools/, and config/ importable."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for sub in ("scripts", "tools", "config", "."):
    candidate = ROOT / sub if sub != "." else ROOT
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
