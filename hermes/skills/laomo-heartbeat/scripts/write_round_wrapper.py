#!/usr/bin/env python3
"""Pure-ASCII terminal wrapper for write_round.py with auto-escalating prune.

Origin: R351 direction-4 isolation method + R357 write-call isolation + R358
formalization (this script replaces the per-round throwaway /tmp wrapper).

1. AGENTS.md injection closure (R349/R350 channel): terminal command lines that
   contain profile paths inject ~4KB AGENTS.md context into the session. Calling
   write_round.py with --archive <profile path> directly from terminal re-opens
   the channel. This wrapper keeps the terminal surface to a single ASCII command
   (python3 <wrapper> <entry> ...); all profile-path constants live in this file.

2. Size-gate escalation without hand-typing (R336 chain): early gate = 48KB chars.
   Projection over the gate needs escalating --prune N retries. This wrapper tries
   no-arg first, then --prune 1/2/3, but ONLY escalates on a size-gate FATAL
   (matches the gate marker in output). Any other non-zero exit aborts escalation
   so real errors are not masked by blind retries.

3. Post-write archive dedupe check (R336 family defense + R338 light closure):
   --prune FATALs append dropped entries to archive BEFORE rollback, so escalated
   retries can duplicate archive lines. After a successful write, counts line-start
   archive markers for each check R number passed as argv. Any count > 1 -> run
   scripts/archive_dedupe.py. R358 empirically confirmed: a no-arg FATAL leaves NO
   archive residue (new-R count=0); only --prune FATALs append.

Usage:
    python3 write_round_wrapper.py <entry.txt> [check_r1 check_r2 ...]
    <entry.txt>   absolute path of the entry text file (e.g. /tmp/..._entry.txt)
    check_r1 ...  R numbers to count in archive post-write: pass the R numbers any
                  prune level could drop (oldest N entries) PLUS the new R number.

Exit 0 = write succeeded; prints archive counts (dups=NONE or DUPS FOUND reminder).
"""
import subprocess
import sys
import time

WRITE_ROUND = "/Users/hua/.hermes/skills/laomo-heartbeat/scripts/write_round.py"
ARCHIVE = "/Users/hua/.hermes/profiles/laomo/evolution/task-11-log-archive.md"
SIZE_GATE_MARK = "\u5c3a\u5bf8\u95e8"  # gate marker text used by write_round.py FATALs

ATTEMPTS = (
    ("no-arg", ()),
    ("prune-1", ("--prune", "1")),
    ("prune-2", ("--prune", "2")),
    ("prune-3", ("--prune", "3")),
)


def archive_counts(check_rs):
    counts = {}
    try:
        with open(ARCHIVE, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        for ra in check_rs:
            counts[ra] = sum(1 for l in lines if l.startswith("[R" + ra + " "))
    except OSError as e:
        print("archive count ERR:", e)
    return counts


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: write_round_wrapper.py <entry.txt> [check_r1 check_r2 ...]")
        return 2
    entry = args[0]
    check_rs = args[1:]
    print("wrapper start:", time.strftime("%H:%M:%S"))

    ok = False
    prune_used = 0
    for name, extra in ATTEMPTS:
        if extra:
            cmd = [sys.executable, WRITE_ROUND, entry, extra[0], extra[1], "--archive", ARCHIVE]
        else:
            cmd = [sys.executable, WRITE_ROUND, entry]
        r = subprocess.run(cmd, capture_output=True, text=True)
        out = (r.stdout or "") + (r.stderr or "")
        print("=== attempt %s exit=%d ===" % (name, r.returncode))
        print(r.stdout[-2600:])
        if r.stderr:
            print("STDERR:", r.stderr[-900:])
        if r.returncode == 0:
            ok = True
            prune_used = int(extra[1]) if extra else 0
            break
        if SIZE_GATE_MARK not in out:
            print("non-size-gate failure, abort escalation")
            break

    if ok:
        counts = archive_counts(check_rs)
        print("=== post-write archive line-start counts ===")
        dirty = False
        for ra in sorted(counts):
            print("R%s count=%d" % (ra, counts[ra]))
            if counts[ra] > 1:
                dirty = True
        if dirty:
            print("DUPS FOUND -> run scripts/archive_dedupe.py")
        else:
            print("dups=NONE (archive_dedupe.py not needed, R338 light closure)")
        if prune_used:
            print("prune level used: %d (dropped %d oldest entries -> archive)" % (prune_used, prune_used))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
