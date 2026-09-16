#!/usr/bin/env python3
"""desc integrity one-shot scan for laomo heartbeat (consolidated at R522).

Line-anchored marker scan over a range + chunk lengths + MISSING gap list +
three-piece check (suppression section / Ark anchor / keep_in_progress tail)
+ archive line-anchored counts + SKILL.md size. Born from the R522 /tmp probe
that detected the first un-archived deletion (R520 removed from desc by the
writer cron bypass write, absent from archive too). stdlib-only, pure ASCII.

Usage:
  python3 desc_integrity_scan.py --range 500-524
  python3 desc_integrity_scan.py --range 500-524 --three-piece 521,522
"""
import argparse
import re
import sqlite3
import sys

DB = "/Users/hua/.hermes/tasks.db"
ARCHIVE = "/Users/hua/.hermes/profiles/laomo/evolution/task-11-log-archive.md"
SKILL_MD = "/Users/hua/.hermes/skills/laomo-heartbeat/SKILL.md"

p = argparse.ArgumentParser()
p.add_argument("--range", default="500-524", help="A-B inclusive marker range")
p.add_argument("--three-piece", default="",
               help="comma-separated R numbers for 3-piece check")
a = p.parse_args()
lo, hi = (int(x) for x in a.range.split("-"))

con = sqlite3.connect(DB)
desc, ua = con.execute(
    "SELECT description, updated_at FROM tasks WHERE id=11").fetchone()
print("desc chars: %d | updated_at: %s" % (len(desc), ua))

print("== marker scan %d..%d (lineanchor/raw) ==" % (lo, hi))
pos = {}
for n in range(lo, hi + 1):
    la = len(re.findall(r"(?m)^\[R%d " % n, desc))
    raw = desc.count("[R%d " % n)
    if la or raw:
        print("  R%d: lineanchor=%d raw=%d" % (n, la, raw))
    i = desc.find("\n[R%d " % n)
    if i >= 0:
        pos[n] = i + 1
    elif desc.startswith("[R%d " % n):
        pos[n] = 0

ns = sorted(pos)
print("== chunk lengths (newline-anchored, -1 separator) ==")
for x, y in zip(ns, ns[1:]):
    print("  R%d len=%d" % (x, y - pos[x] - 1))
if ns:
    print("  R%d len=%d (tail->end)" % (ns[-1], len(desc) - pos[ns[-1]]))
    gaps = [x for x in range(ns[0], ns[-1] + 1) if x not in pos]
    print("range %d..%d | present=%d | MISSING: %s"
          % (ns[0], ns[-1], len(ns), gaps or "none"))

for n in [int(x) for x in a.three_piece.split(",") if x.strip()]:
    if n not in pos:
        print("R%d three-piece: NOT IN DESC" % n)
        continue
    k = ns.index(n)
    end = pos[ns[k + 1]] - 1 if k + 1 < len(ns) else len(desc)
    seg = desc[pos[n]:end]
    print("R%d three-piece: suppress=%s ark=%s tail=%s" % (
        n,
        "Y" if "self-evolve prompt" in seg else "N",
        "Y" if ("Ark" in seg and ("403" in seg or "<4h" in seg)) else "N",
        "Y" if re.search(r"keep_in_progress[.\u3002]\s*$", seg) else "N"))

try:
    arc = open(ARCHIVE, encoding="utf-8").read()
except OSError:
    print("archive: NOT FOUND")
    sys.exit(0)
cnt = {}
for n in range(lo, hi + 1):
    c = len(re.findall(r"(?m)^\[R%d " % n, arc))
    if c:
        cnt[n] = c
print("archive line-anchored counts %d..%d: %s" % (lo, hi, cnt))
print("archive total entries:", len(re.findall(r"(?m)^\[R\d+ ", arc)))
try:
    s = open(SKILL_MD, encoding="utf-8").read()
    print("SKILL.md chars: %d (margin to 100K: %d)" % (len(s), 100000 - len(s)))
except OSError:
    print("SKILL.md: NOT FOUND")
