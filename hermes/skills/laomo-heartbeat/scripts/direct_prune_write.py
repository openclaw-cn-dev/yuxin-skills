#!/usr/bin/env python3
"""Direct prune-level write for task #11 R rounds (R359 formalization).

When R344 narrow-column forensics (instr positions) has ALREADY determined the
needed --prune N (projection overage > 1.5KB -> N=2 per R342/R344/R346
precedents), call write_round.py directly with that level instead of running
write_round_wrapper.py's no-arg-first escalation chain. Benefits:
  - zero size-gate FATAL churn (R344 first-try-pass precedent);
  - zero archive duplication from escalated retries (a prune-1 FATAL followed
    by a prune-2 success double-appends the oldest entry -> dedupe needed);
  - terminal command line stays pure ASCII with zero profile-path text
    (AGENTS.md injection channel closed, R349/R351).

Usage:
    python3 direct_prune_write.py <entry.txt> <prune_n> [check_r1 ...]
    check_r*  R numbers to count in the archive post-write: the N oldest entry
              numbers plus the new R number. count>1 -> run archive_dedupe.py.

A size-gate FATAL at this N exits 1 with the FATAL text intact - re-run with a
bigger N (per R344 narrow-column shed computation), do not blind-retry.
"""
import subprocess
import sys

WRITE_ROUND = "/Users/hua/.hermes/skills/laomo-heartbeat/scripts/write_round.py"
ARCHIVE = "/Users/hua/.hermes/profiles/laomo/evolution/task-11-log-archive.md"


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("usage: direct_prune_write.py <entry.txt> <prune_n> [check_r1 ...]")
        return 2
    entry, prune_n = args[0], args[1]
    check_rs = args[2:]
    r = subprocess.run(
        [sys.executable, WRITE_ROUND, entry, "--prune", prune_n, "--archive", ARCHIVE],
        capture_output=True, text=True,
    )
    print(r.stdout[-3000:])
    if r.stderr:
        print("STDERR:", r.stderr[-900:])
    print("exit =", r.returncode)
    if r.returncode != 0:
        return 1
    if check_rs:
        lines = open(ARCHIVE, encoding="utf-8", errors="replace").readlines()
        dirty = False
        for ra in check_rs:
            c = sum(1 for l in lines if l.startswith("[R" + ra + " "))
            print("R%s count=%d" % (ra, c))
            if c > 1:
                dirty = True
        print("dups=NONE (archive_dedupe.py not needed)" if not dirty
              else "DUPS FOUND -> run scripts/archive_dedupe.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
