#!/usr/bin/env python3
"""
R-numbered heartbeat log prune + append (parameterized SQL primitive).

Validated end-to-end: laomo heartbeat R201 (2026-09-04 15:07 CST, tasks.db
task #11, 29 entries pruned to 25 + R201 appended, R171..R174 archived).
NOTE (R224 correction): the "official" helpers scripts/r-numbered-log-append.py
and templates/laomo_desc_prune.py were never actually lost -- they are simply
INVISIBLE to search_files/find (total_count=0 at R200, R201 AND R224, likely
.gitignore in the skill dir defeating ripgrep). Locate helpers via
skill_view('laomo-knowledge') linked_files, never via filesystem search.
This script remains the preferred one-shot prune+append (parameterized).

Usage:
  python3 r_log_prune_append.py \
    --db /Users/hua/.hermes/tasks.db \
    --task-id 11 \
    --entry-file /tmp/rN_entry.txt \
    --keep-last-n 25 \
    --archive /Users/hua/.hermes/profiles/laomo/evolution/task-11-log-archive.md

Entry file format:
  Body: "[R<NNN> YYYY-MM-DD HH:MM CST <agent> heartbeat] ..." (leading blank
  lines optional, stripped) ending with "keep_in_progress.".
  R number must be > last canonical R in the description; == last+1 preferred
  (R-skip allowed with WARN per R194 precedent; forbid via --require-plus-one).

Hard rules encoded (laomo-knowledge Pitfall #30 + R201 reference):
  * Size gate is CHARS: len(desc), NEVER len(desc.encode('utf-8')).
    CJK is ~3 bytes/char in UTF-8 -> a bytes-based gate false-trips
    (re-hit live at R201 despite Pitfall #30 existing since R147).
  * Pre-write asserts: last-R marker present, new entry absent, R monotonic.
  * Prune AFTER counting the new entry (post-append count vs keep_last_n);
    dropped entries are appended to --archive with a prune header comment.
  * Post-write verify: entry marker present, status correct, desc endswith
    keep_in_progress.
"""
import argparse
import datetime
import re
import sqlite3

ENTRY_RE = re.compile(r"\[R(\d+) \d{4}-\d{2}-\d{2} \d{2}:\d{2} CST")


def main() -> None:
    ap = argparse.ArgumentParser(description="R-numbered heartbeat log prune+append")
    ap.add_argument("--db", required=True)
    ap.add_argument("--task-id", type=int, required=True)
    ap.add_argument("--entry-file", required=True,
                    help="file containing the new entry ([R<n> ... keep_in_progress.)")
    ap.add_argument("--keep-last-n", type=int, default=25)
    ap.add_argument("--archive", default=None,
                    help="path to append pruned entries to (omit = drop without archive)")
    ap.add_argument("--status", default="in_progress")
    ap.add_argument("--early-gate-kb", type=float, default=48.0)
    ap.add_argument("--hard-gate-kb", type=float, default=50.0)
    ap.add_argument("--require-plus-one", action="store_true",
                    help="forbid R skips (default: allow with WARN, R194 precedent)")
    args = ap.parse_args()

    with open(args.entry_file, encoding="utf-8") as f:
        body = f.read().strip("\n")
    m = ENTRY_RE.search(body)
    assert m, "entry file missing '[R<n> YYYY-MM-DD HH:MM CST' header"
    new_r = int(m.group(1))
    assert body.rstrip().endswith("keep_in_progress."), \
        "entry must end with 'keep_in_progress.'"

    conn = sqlite3.connect(args.db)
    row = conn.execute("SELECT description, status FROM tasks WHERE id=?",
                       (args.task_id,)).fetchone()
    assert row, f"task #{args.task_id} not found in {args.db}"
    desc, _status = row

    # --- pre-write asserts (R124+ defense) ---
    starts = [mm.start() for mm in ENTRY_RE.finditer(desc)]
    assert starts, "no existing R entries found in description"
    last_r = int(ENTRY_RE.search(desc[starts[-1]:]).group(1))
    assert f"[R{new_r} " not in desc, f"R{new_r} entry already exists"
    assert new_r > last_r, f"R numbering not monotonic: new {new_r} <= last {last_r}"
    if new_r != last_r + 1:
        if args.require_plus_one:
            raise AssertionError(f"R skip {last_r}->{new_r} forbidden by --require-plus-one")
        print(f"WARN: R skip {last_r} -> {new_r} (R194 precedent allows skips)")

    # --- prune oldest entries beyond keep_last_n (post-append count) ---
    header = desc[: starts[0]] if starts[0] > 0 else ""
    segments = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(desc)
        segments.append((desc[s:e], int(ENTRY_RE.search(desc[s:e]).group(1))))
    post_count = len(segments) + 1
    if post_count > args.keep_last_n:
        n_drop = post_count - args.keep_last_n
        dropped, segments = segments[:n_drop], segments[n_drop:]
        if args.archive:
            first, last = dropped[0][1], dropped[-1][1]
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(args.archive, "a", encoding="utf-8") as f:
                f.write(f"\n\n<!-- pruned {now} CST by r_log_prune_append.py, R{new_r} round, "
                        f"KEEP_LAST_N={args.keep_last_n}, dropped R{first}..R{last} "
                        f"({n_drop} entries) -->\n")
                for seg, _r in dropped:
                    f.write("\n\n" + seg.rstrip() + "\n")
            print(f"archived {n_drop} entries (R{first}..R{last}) -> {args.archive}")
        else:
            print(f"WARN: dropped {n_drop} entries WITHOUT archive (no --archive given)")

    new_desc = (header + "".join(s for s, _r in segments)).rstrip() + "\n\n" + body

    # --- size gate in CHARS, never bytes (Pitfall #30, re-hit R201) ---
    kb_chars = len(new_desc) / 1024.0
    assert kb_chars < args.hard_gate_kb, \
        f"hard size gate FAIL: {kb_chars:.1f}KB chars >= {args.hard_gate_kb}KB"
    if kb_chars >= args.early_gate_kb:
        print(f"WARN: {kb_chars:.1f}KB chars >= early gate {args.early_gate_kb}KB "
              f"- prune harder next round")

    conn.execute(
        "UPDATE tasks SET description=?, status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (new_desc, args.status, args.task_id),
    )
    conn.commit()

    # --- post-write verify ---
    d2, s2 = conn.execute("SELECT description, status FROM tasks WHERE id=?",
                          (args.task_id,)).fetchone()
    assert f"[R{new_r} " in d2, "post-write: entry marker missing"
    assert s2 == args.status, "post-write: status mismatch"
    assert d2.endswith("keep_in_progress."), "post-write: endswith check FAIL"
    first_r = segments[0][1] if segments else new_r
    print(f"OK: R{new_r} appended; entries R{first_r}..R{new_r} "
          f"({len(segments) + 1}); desc {len(d2) / 1024:.1f}KB chars; status={s2}")
    conn.close()


if __name__ == "__main__":
    main()
