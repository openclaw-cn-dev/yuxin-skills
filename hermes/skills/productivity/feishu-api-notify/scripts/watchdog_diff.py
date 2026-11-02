#!/usr/bin/env python3
"""watchdog_diff.py — Reusable diff helper for silent watchdog crons.

Compares a 'last' and 'current' JSON state snapshot and prints either:
  - "NO_CHANGE" if the snapshots are semantically equal (per normalize), or
  - "CHANGED:" followed by one line per field that differs.

Handles four classes of false-positive sources (confirmed across
2026-06-17 FindEra health-check runs):
  1. API status codes written as strings ("000") by curl vs ints (0) by
     urllib.request — both mean "unreachable", both normalize to None.
  2. Last-error fields that may be empty string vs missing key — both
     normalize to "".
  3. Top-level "timestamp" field — the probe's own clock; changes every
     run. Always filtered out before comparison.
  4. "container.raw_status" contains "Up N (unit)" text that drifts
     every minute ("Up 49 seconds" -> "Up 30 minutes") even when nothing
     restarted. The "Up N" prefix is replaced with "Up" before comparison
     so the structural change becomes invisible.

Usage:
  python3 watchdog_diff.py /tmp/<project>_last_state.json /tmp/<project>_current.json

Exit code:
  0 — no change (or no baseline yet; first run establishes baseline)
  1 — change detected
  2 — usage error

The watchdog cron should run this script and use stdout + exit code to
decide whether to send a Feishu alert. Pair with SKILL.md Pitfall #25
('State-snapshot type drift produces false-positive diff alerts in silent
watchdog crons') and Pitfall #26 ('watchdog_diff.py is a CLI, not a
library — and it does NOT filter structural noise').

This script intentionally does NOT do any Feishu I/O — keep that in the
caller, so this stays a pure-function diff helper.
"""
import json
import re
import sys


def _norm_code(v):
    """0 / '000' / 0.0 / '' all mean 'endpoint unreachable'. Coerce to None."""
    if v in (0, 0.0, "", "000", None):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return v


def _norm_text(v):
    """Empty string and missing key are the same thing."""
    if v is None:
        return ""
    return str(v)


def _norm_value(v):
    """Recursively normalize a value."""
    if isinstance(v, dict):
        return {k: _norm_value(vv) for k, vv in sorted(v.items())}
    if isinstance(v, list):
        return [_norm_value(x) for x in v]
    if isinstance(v, (int, float)):
        return _norm_code(v)
    return _norm_text(v)


# Matches the "Up N <unit>" substring in docker ps raw_status output,
# e.g. "Up 30 minutes" / "Up 49 seconds" / "Up 3 hours". The replacement
# ("Up") preserves the structural shape of the line so a restart (which
# produces a fresh "Up N" pair) is still detectable while minute-level
# drift is invisible.
_UPTIME_RE = re.compile(r"Up \d+ \w+(?=\s*\()")


def _strip_structural_noise(snapshot):
    """Return a copy of `snapshot` with the two known structural-noise
    sources removed/replaced. Does not mutate the input.

    - Drops top-level "timestamp" (probe's own clock — always changes).
    - Replaces "Up N <unit>" inside container.raw_status with "Up"
      (drifts every minute, no semantic value).
    """
    out = json.loads(json.dumps(snapshot))  # deep copy
    out.pop("timestamp", None)
    container = out.get("container")
    if isinstance(container, dict):
        raw = container.get("raw_status")
        if isinstance(raw, str):
            container["raw_status"] = _UPTIME_RE.sub("Up", raw)
    return out


def diff(last, curr):
    """Return a list of 'field: old -> new' strings for fields that differ
    after normalization. Empty list means no real change.
    """
    changes = []
    keys = set(last) | set(curr)
    for k in sorted(keys):
        lv = _norm_value(last.get(k))
        cv = _norm_value(curr.get(k))
        if lv != cv:
            changes.append(
                f"{k}: {json.dumps(lv, ensure_ascii=False)} -> "
                f"{json.dumps(cv, ensure_ascii=False)}"
            )
    return changes


def main(argv):
    if len(argv) != 3:
        print(
            f"usage: {argv[0]} <last_state.json> <current_state.json>",
            file=sys.stderr,
        )
        return 2

    last_path, curr_path = argv[1], argv[2]
    try:
        with open(last_path) as f:
            last_raw = json.load(f)
    except FileNotFoundError:
        # First-ever run — no baseline. Treat as "no change" so the cron
        # just establishes the baseline and stays silent.
        print("NO_BASELINE")
        return 0
    except (json.JSONDecodeError, OSError) as e:
        print(
            f"CHANGED: last_state unreadable "
            f"({type(e).__name__}: {e})",
            file=sys.stderr,
        )
        return 1

    try:
        with open(curr_path) as f:
            curr_raw = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(
            f"CHANGED: current_state unreadable "
            f"({type(e).__name__}: {e})",
            file=sys.stderr,
        )
        return 1

    # Filter structural noise (timestamp + raw_status uptime drift) BEFORE
    # type/value normalization, so the recursive walk only sees semantic
    # fields. See SKILL.md Pitfall #26.
    last = _strip_structural_noise(last_raw)
    curr = _strip_structural_noise(curr_raw)

    changes = diff(last, curr)

    if not changes:
        print("NO_CHANGE")
        return 0

    print("CHANGED:")
    for c in changes:
        print(f"  - {c}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
