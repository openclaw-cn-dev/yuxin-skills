#!/usr/bin/env python3
"""Dedupe the task-11 log archive: keep only the LAST occurrence of each [R<n> entry.

Why this exists: write_round.py --prune N appends dropped entries to the archive
BEFORE the size gate runs. A FATAL (gate rejection) rolls back the desc UPDATE
but NOT the archive append, so escalating N across retries duplicates entries
(R336 measured: --prune 1 FATAL, --prune 2 FATAL, --prune 3 PASS left
R316 x3 / R317 x2 / R318 x1 in the archive).

Run this after ANY successful escalated retry (--prune N where N > 1), then
verify `dups=NONE` in the output. Exit code 0 = clean, 1 = duplicates remain.

Usage:
    python3 archive_dedupe.py [archive_path]

Default archive: /Users/hua/.hermes/profiles/laomo/evolution/task-11-log-archive.md
"""
import re
import sys
from collections import Counter

DEFAULT_ARCHIVE = "/Users/hua/.hermes/profiles/laomo/evolution/task-11-log-archive.md"
# Line-start anchored marker: inline prose references like "see [R312 in..." must
# NOT be treated as entry boundaries (R334 lesson: loose regex poisoned last_r).
MARKER = re.compile(r"(?m)(?=^\[R\d+ )")
HEAD = re.compile(r"^\[R(\d+)\s")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ARCHIVE
    with open(path, encoding="utf-8") as f:
        text = f.read()

    parts = MARKER.split(text)
    header = parts[0] if parts and not parts[0].startswith("[R") else ""
    blocks = [p for p in parts if p.startswith("[R")]

    last = {}   # R number -> block text (last occurrence wins)
    order = []  # final ordering; ints deduped, non-marker blocks kept in place
    for b in blocks:
        m = HEAD.match(b)
        if not m:
            order.append(b)
            continue
        rn = int(m.group(1))
        if rn not in last:
            order.append(rn)
        last[rn] = b

    kept = [last.get(rn, rn) if isinstance(rn, int) else rn for rn in order]
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + "".join(kept))

    with open(path, encoding="utf-8") as f:
        t2 = f.read()
    c = Counter(re.findall(r"(?m)^\[R(\d+) ", t2))
    dups = {k: v for k, v in c.items() if v > 1}
    print("total_entries=%d dups=%s" % (sum(c.values()), dups if dups else "NONE"))
    sys.exit(1 if dups else 0)


if __name__ == "__main__":
    main()
