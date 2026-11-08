#!/usr/bin/env python3
"""FindEra (and similar project-monitor) watchdog state diff.

Combines two passes:
  1. Structural-noise pre-filter that handles the two false-positive sources
     that fire on EVERY cron run when nothing has actually changed:
       - top-level `timestamp` (the probe's own clock)
       - `container.raw_status` uptime drift from `docker ps` text that changes
         every minute ("Up 49 seconds" -> "Up About an hour" -> "Up 2 hours")
  2. Recursive semantic diff of the remaining structure.

CLI:
    findera_state_diff.py <last.json> <current.json>

Exit codes:
    0 = NO_CHANGE (silent — do not notify)
    1 = CHANGED    (print summary; surface to Feishu)
    2 = usage error / missing file

Why a second pass is needed on top of the watchdog_diff.py referenced by
`feishu-api-notify`: that helper is a CLI that does recursive semantic diff
only. It will spuriously flag timestamp + uptime drift as "real changes"
on every run. Combine: this script's pre-filter (handles structural noise)
+ the helper's CLI (handles API-code-type drift per feishu-api-notify
Pitfall #25).

Field-tested 2026-06-17 against /tmp/findera_last_state.json and
/tmp/findera_current.json; fixture test: identical files -> NO_CHANGE,
synthetic `api.health: 200 -> 500` on a fixture COPY (not the live file)
-> CHANGED with the right field.

See references/findera-watchdog-diff.md for the two-bug fix recipe and
the fixture-test recipe that MUST pass before deploying.
"""
import json
import re
import sys


def strip_uptime(s):
    """Strip `Up <duration> (status)` from docker ps raw_status text.

    The naive recipe `re.sub(r"Up \\d+ \\w+", "Up", s)` only matches
    single-word units like "30 minutes" or "5 hours". Docker also emits
    multi-word phrasings: "About an hour", "2 hours", "Less than a second".
    Use a greedy match for any non-paren, non-newline text between `Up`
    and the `(` that always follows.
    """
    if not isinstance(s, str):
        return s
    return re.sub(r"Up[^()\n]+(?=\s*\()", "Up", s)


def prefilter(obj):
    """Strip structural noise from a state-snapshot dict (recursive).

    - Drops top-level `timestamp` (the probe's clock, not a state change).
    - Rewrites `raw_status` uptime strings wherever they appear (top-level
      OR nested OR inside lists — the naive top-level-only walk misses
      `container.raw_status` because it's nested).
    """
    if isinstance(obj, dict):
        return {
            k: prefilter(v)
            for k, v in obj.items()
            if k != "timestamp"
        }
    if isinstance(obj, list):
        return [prefilter(x) for x in obj]
    if isinstance(obj, str):
        return strip_uptime(obj)
    return obj


def diff(a, b, path=""):
    """Recursive semantic diff. Yields (path, a_val, b_val) tuples."""
    if isinstance(a, dict) and isinstance(b, dict):
        keys = set(a) | set(b)
        for k in sorted(keys):
            yield from diff(a.get(k), b.get(k), f"{path}.{k}" if path else k)
        return
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield (path, a, b)
            return
        for i, (x, y) in enumerate(zip(a, b)):
            yield from diff(x, y, f"{path}[{i}]")
        return
    if a != b:
        yield (path, a, b)


def main():
    if len(sys.argv) != 3:
        print("usage: findera_state_diff.py <last.json> <current.json>",
              file=sys.stderr)
        return 2
    last_path, curr_path = sys.argv[1], sys.argv[2]
    try:
        with open(last_path) as f:
            last_raw = json.load(f)
        with open(curr_path) as f:
            curr_raw = json.load(f)
    except FileNotFoundError as e:
        print(f"missing state file: {e}", file=sys.stderr)
        return 2

    last = prefilter(last_raw)
    curr = prefilter(curr_raw)
    changes = list(diff(last, curr))

    if not changes:
        print("NO_CHANGE")
        return 0

    print("CHANGED:")
    for path, a, b in changes:
        a_s = json.dumps(a, ensure_ascii=False) if not isinstance(a, str) else a
        b_s = json.dumps(b, ensure_ascii=False) if not isinstance(b, str) else b
        if len(a_s) > 80:
            a_s = a_s[:77] + "..."
        if len(b_s) > 80:
            b_s = b_s[:77] + "..."
        print(f"  {path}: {a_s} -> {b_s}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
