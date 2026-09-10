#!/usr/bin/env python3
r"""Merged round-data probe for laomo heartbeat rounds (consolidated at R367).

Pure-ASCII, stdlib-only replacement for the per-round hand-written /tmp probe
scripts (R351 isolation, R357 archive check, R363 merged post-write method,
R367 pre-write extension). Pick sections with flags; every section prints
entry-ready lines. CJK markers MUST be passed as \uXXXX-escaped ASCII so the
terminal command line stays pure ASCII (R347 tirith defense).

Typical pre-write round call (all-in-one data collection):

  TZ=Asia/Shanghai python3 /Users/hua/.hermes/skills/laomo-heartbeat/scripts/merged_round_probe.py \
      --dois --cron-output \
      --skills-baseline "2026-09-10 05:07:07" \
      --archive-r 356 --instr-r 357 358 366 \
      --wall-marker "\u4e09\u5341\u516d\u72af"

Typical post-write verify call:

  TZ=Asia/Shanghai python3 /Users/hua/.hermes/skills/laomo-heartbeat/scripts/merged_round_probe.py \
      --archive-r 357 --desc-stats --tail 160 \
      --wall-marker "\u6839\u6cbb\u4ecd\u7cfb\u6267\u884c\u5e8f\uff09\u3002"

Notes:
  - --skills-baseline takes CST local time (host TZ is CST; prefix TZ=Asia/Shanghai
    to be safe), convention = previous round updated_at+8h (R331/R333 baseline rule).
  - --wall-marker is repeatable; each gets count + last_pos + repr context slice
    (R354/R357: verify exact chars before patching the defense wall).
  - --archive-r counts are line-start anchored (R334/R338: loose substring counts
    are polluted by inline bracketed R references).
  - --instr-r reports entry start offset AND entry length (R344 narrow-column
    evidence for choosing a prune N without dumping desc into context).
"""
import argparse
import os
import re
import sqlite3
import time

KD = "/Users/hua/.hermes/profiles/laomo/evolution/known_dois.txt"
ARCHIVE = "/Users/hua/.hermes/profiles/laomo/evolution/task-11-log-archive.md"
TASKS_DB = "/Users/hua/.hermes/tasks.db"
TASK_ID = 11
SKILL_MD = "/Users/hua/.hermes/skills/laomo-heartbeat/SKILL.md"
SKILLS_DIRS = [("L1", "/Users/hua/.hermes/skills"),
               ("PROF", "/Users/hua/.hermes/profiles/laomo/skills")]
CRON_OUT_DIR = "/Users/hua/.hermes/cron/output/c6391079131e"
CRON_ID = "c6391079131e"
JOBS_JSON = "/Users/hua/.hermes/cron/jobs.json"


def esc(s):
    return s.encode("unicode_escape").decode("ascii")


def unesc(s):
    return s.encode("ascii").decode("unicode_escape")


def sec(title):
    print("==== " + title + " ====")


def doi_section():
    sec("known_dois (risk-window measurement, R353 discipline)")
    try:
        st = os.stat(KD)
        with open(KD, encoding="utf-8", errors="replace") as f:
            content = f.read()
        lines = content.splitlines()
        print("size=%d mtime=%s lines=%d" % (
            st.st_size,
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
            len(lines)))
        for i, ln in enumerate(lines, 1):
            print("L%d %s" % (i, esc(ln)))
    except Exception as e:
        print("ERR %r" % e)


def cron_output_section(n):
    sec("cron output newest %d (%s liveness)" % (n, CRON_ID))
    if not os.path.isdir(CRON_OUT_DIR):
        print("no output dir")
        return
    fs = []
    for x in os.listdir(CRON_OUT_DIR):
        p = os.path.join(CRON_OUT_DIR, x)
        if os.path.isfile(p):
            fs.append((os.path.getmtime(p), x, os.path.getsize(p)))
    fs.sort(reverse=True)
    for m, x, s in fs[:n]:
        print("%s %s size=%d" % (
            time.strftime("%m-%d %H:%M:%S", time.localtime(m)), x, s))


def jobs_section(window):
    sec("jobs.json enabled fields near id (window=%d)" % window)
    if not os.path.exists(JOBS_JSON):
        print("jobs.json missing")
        return
    with open(JOBS_JSON, encoding="utf-8", errors="replace") as f:
        data = f.read()
    idx = data.find(CRON_ID)
    if idx < 0:
        print("id not found")
        return
    seg = data[max(0, idx - 50): idx + window]
    fields = re.findall(r'"enabled"\s*:\s*(true|false)', seg)
    print("id_pos=%d enabled_near=%s" % (idx, fields[:3]))
    print("NOTE R367: field may sit outside the window; cron liveness via "
          "--cron-output is the fallback signal")


def skills_section(baseline_str):
    sec("skills mtime newer than baseline (direction 4)")
    try:
        base = time.mktime(time.strptime(baseline_str, "%Y-%m-%d %H:%M:%S"))
    except ValueError as e:
        print("bad baseline %r (%r) - use 'YYYY-MM-DD HH:MM:SS' CST" % (baseline_str, e))
        return
    for lab, bd in SKILLS_DIRS:
        hits = []
        for dp, dn, fns in os.walk(bd):
            for fn in fns:
                if fn.endswith(".md") or fn == ".usage.json":
                    p = os.path.join(dp, fn)
                    try:
                        m = os.path.getmtime(p)
                    except OSError:
                        continue
                    if m > base:
                        hits.append((m, p))
        hits.sort()
        if hits:
            for m, p in hits[:30]:
                print("%s %s %s" % (lab, time.strftime("%m-%d %H:%M:%S", time.localtime(m)), p))
            if len(hits) > 30:
                print("%s ... total %d hits" % (lab, len(hits)))
        else:
            print("%s 0 hits" % lab)


def archive_section(rnums):
    sec("archive line-start counts (R338/R360 prune closure)")
    if not os.path.exists(ARCHIVE):
        print("archive missing")
        return
    counts = {}
    with open(ARCHIVE, encoding="utf-8", errors="replace") as f:
        for ln in f:
            m = re.match(r"^\[(R\d+) ", ln)
            if m:
                counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    for r in rnums:
        print("R%d count=%d" % (r, counts.get("R%d" % r, 0)))


def desc_section(rnums, tail_n):
    sec("desc stats (chars/entries/range/last_r + entry offsets)")
    conn = sqlite3.connect(TASKS_DB)
    desc = conn.execute("SELECT description FROM tasks WHERE id=?", (TASK_ID,)).fetchone()[0]
    status = conn.execute("SELECT status FROM tasks WHERE id=?", (TASK_ID,)).fetchone()[0]
    conn.close()
    offs = {}
    order = []
    pos = 0
    for ln in desc.splitlines(keepends=True):
        m = re.match(r"^\[R(\d+) ", ln)
        if m:
            rid = int(m.group(1))
            offs[rid] = pos
            order.append(rid)
        pos += len(ln)
    if order:
        print("chars=%d entries=%d range=%d..%d last_r=%d status=%s" % (
            len(desc), len(order), order[0], order[-1], order[-1], status))
    else:
        print("chars=%d entries=0 status=%s" % (len(desc), status))
    for r in rnums:
        if r in offs:
            later = [o for o in offs.values() if o > offs[r]]
            elen = (min(later) - offs[r]) if later else (len(desc) - offs[r])
            print("R%d pos=%d entry_len=%d" % (r, offs[r], elen))
        else:
            print("R%d pos=-1 (not in desc)" % r)
    if tail_n:
        print("tail=%s" % esc(desc[-tail_n:]))


def wall_section(markers, before, after):
    sec("wall anchor repr (defense-wall patch prep, R354/R357)")
    with open(SKILL_MD, encoding="utf-8") as f:
        txt = f.read()
    print("filelen=%d" % len(txt))
    for mk in markers:
        real = unesc(mk)
        cnt = txt.count(real)
        pos = txt.rfind(real)
        print("marker=%s count=%d last_pos=%d" % (mk, cnt, pos))
        if pos >= 0:
            lo = max(0, pos - before)
            hi = min(len(txt), pos + len(real) + after)
            print("ctx=%s" % esc(txt[lo:hi]))


def main():
    ap = argparse.ArgumentParser(
        description="merged round-data probe (pure-ASCII output, laomo heartbeat)")
    ap.add_argument("--dois", action="store_true",
                    help="known_dois.txt stat + full content")
    ap.add_argument("--cron-output", type=int, nargs="?", const=3, default=0, metavar="N",
                    help="newest N files in writer-cron output dir (liveness)")
    ap.add_argument("--jobs-check", type=int, nargs="?", const=500, default=0, metavar="WIN",
                    help="grep enabled fields near cron id in jobs.json (may miss, R367)")
    ap.add_argument("--skills-baseline", metavar="TS",
                    help="'YYYY-MM-DD HH:MM:SS' CST; scan skills dirs for newer md")
    ap.add_argument("--archive-r", type=int, nargs="*", default=[], metavar="R",
                    help="line-start counts for R numbers in task-11 archive")
    ap.add_argument("--instr-r", type=int, nargs="*", default=[], metavar="R",
                    help="entry start offset + length for R numbers in desc")
    ap.add_argument("--desc-stats", action="store_true",
                    help="desc chars/entries/range/last_r/status")
    ap.add_argument("--tail", type=int, default=0, metavar="N",
                    help="print last N chars of desc (escaped)")
    ap.add_argument("--wall-marker", action="append", default=[], metavar="ESC",
                    help="\\uXXXX-escaped marker to locate in SKILL.md (repeatable)")
    ap.add_argument("--before", type=int, default=300)
    ap.add_argument("--after", type=int, default=460)
    a = ap.parse_args()
    if not any([a.dois, a.cron_output, a.jobs_check, a.skills_baseline,
                a.archive_r, a.instr_r, a.desc_stats, a.tail, a.wall_marker]):
        ap.print_help()
        return
    if a.dois:
        doi_section()
    if a.cron_output:
        cron_output_section(a.cron_output)
    if a.jobs_check:
        jobs_section(a.jobs_check)
    if a.skills_baseline:
        skills_section(a.skills_baseline)
    if a.archive_r:
        archive_section(a.archive_r)
    if a.instr_r or a.desc_stats or a.tail:
        desc_section(a.instr_r, a.tail)
    if a.wall_marker:
        wall_section(a.wall_marker, a.before, a.after)


if __name__ == "__main__":
    main()
