#!/usr/bin/env python3
"""Surgical removal of intruder entries from task #11 description (A-track).

The self-evolve writer cron (c6391079131e) has twice injected its own round
entries directly into task #11 desc (R377, R382-duplicate). This tool detects
duplicate line-anchored [R<n> markers, removes the intruder chunk (archive
first -- prune discipline), optionally appends the next heartbeat entry, and
verifies post-state. Nothing is written unless every precondition holds.

Usage:
  # probe: scan for duplicate markers, write nothing
  python3 desc_intrusion_surgery.py --detect-only

  # surgery: remove the duplicate R382 chunk (identified by '22:01 CST' in
  # its header), archive it, then append the R383 entry
  python3 desc_intrusion_surgery.py --intruder-r 382 --discriminator "22:01 CST" \
      --entry /tmp/r383_entry.txt --surgery-r 383

Legitimacy heuristics (see SKILL.md section "desc intrude detect & surgery"):
  1. duplicate line-anchored [R<n> markers (round-number reuse)
  2. desc grew but updated_at was NOT refreshed (legit UPDATEs refresh it)
  3. intruder self-description is never a fact source (stale-snapshot writes)

Pure ASCII source on purpose (terminal CJK-scan tolerance, R271/R372).
"""
import argparse
import re
import sqlite3
from collections import Counter

EARLY_GATE_CHARS = 49152  # 48KB @1024, matches write_round.py EARLY_GATE_KB
ARCHIVE = '/Users/hua/.hermes/profiles/laomo/evolution/task-11-log-archive.md'
DISC_WINDOW = 160  # discriminator match window at chunk head


def marker_split(desc):
    # marker-split keeps multi-line chunks intact (R291 lesson: never filter by line)
    return re.split(r'(?=\[\R\d+ )'.replace('\\R', 'R'), desc)


def line_anchored_counts(desc):
    # line-anchored: inline [Rxxx references in prose must not pollute (R334 fix)
    return Counter(re.findall(r'(?m)^\[(\d+) '.replace('[', '[R'), desc))


def main():
    ap = argparse.ArgumentParser(description='Remove intruder duplicate entry from task 11 desc.')
    ap.add_argument('--intruder-r', type=int, help='duplicated round number')
    ap.add_argument('--discriminator', help='substring unique to the intruder chunk header')
    ap.add_argument('--entry', help='optional next-round entry file to append after surgery')
    ap.add_argument('--surgery-r', type=int, help='surgery entry round (default intruder_r + 1)')
    ap.add_argument('--db', default='/Users/hua/.hermes/tasks.db')
    ap.add_argument('--detect-only', action='store_true', help='scan duplicates, write nothing')
    a = ap.parse_args()

    conn = sqlite3.connect(a.db)
    desc, status = conn.execute('SELECT description, status FROM tasks WHERE id=11').fetchone()
    counts = line_anchored_counts(desc)

    if a.detect_only:
        dups = {r: c for r, c in counts.items() if c > 1}
        if dups:
            print('DUPLICATE_MARKERS_DETECTED:', dups)
            parts = marker_split(desc)
            for r in sorted(dups):
                for c in [p for p in parts if p.startswith('[R' + r + ' ')]:
                    head = c[:DISC_WINDOW].replace('\n', ' ')
                    print('--- [R%s candidate len=%d] %s' % (r, len(c), head))
        else:
            print('NO_DUPLICATES: all markers unique (%d entries)' % sum(counts.values()))
        return

    if not (a.intruder_r and a.discriminator):
        ap.error('--intruder-r and --discriminator required unless --detect-only')

    r = str(a.intruder_r)
    s = a.surgery_r or (a.intruder_r + 1)
    sr = str(s)

    assert status == 'in_progress', 'unexpected status: %s' % status
    assert ('[R%s ' % sr) not in desc, 'R%s already present in desc' % sr
    assert counts.get(r, 0) == 2, 'expected exactly 2 [R%s chunks, got %d' % (r, counts.get(r, 0))

    parts = marker_split(desc)
    same = [i for i, p in enumerate(parts) if p.startswith('[R' + r + ' ')]
    hits = [i for i in same if a.discriminator in parts[i][:DISC_WINDOW]]
    assert len(hits) == 1, 'discriminator matched %d chunks, need exactly 1' % len(hits)
    i = hits[0]
    intr = parts[i]
    legit_idx = [j for j in same if j != i][0]
    assert a.discriminator not in parts[legit_idx][:DISC_WINDOW], 'discriminator also matches legit chunk'
    assert len(intr) < 2000, 'intruder chunk too big (%d chars), inspect manually' % len(intr)

    entry = ''
    if a.entry:
        entry = open(a.entry, encoding='utf-8').read().strip()
        assert entry.startswith('[R%s ' % sr), 'entry file must start with [R%s marker' % sr

    kept = [p for j, p in enumerate(parts) if j != i]
    new_desc = ''.join(kept).rstrip()
    if entry:
        new_desc += '\n\n' + entry
    new_desc += '\n'
    n = len(new_desc)
    assert n < EARLY_GATE_CHARS, 'post-write %d chars >= 48KB early gate, prune first' % n
    assert 'keep_in_progress' in new_desc, 'keep_in_progress missing from new desc'

    # prune discipline: archive before drop (provenance line is ASCII and
    # suffix "-intruder" so line-anchored [R<n> counting is not polluted by it)
    with open(ARCHIVE, 'a', encoding='utf-8') as f:
        f.write('\n\n[R%s-intruder (removed from desc at R%s surgery, len=%d)]\n' % (r, sr, len(intr)))
        f.write(intr.strip() + '\n')

    conn.execute('UPDATE tasks SET description=?, updated_at=CURRENT_TIMESTAMP WHERE id=11', (new_desc,))
    conn.commit()

    d2, ua, st = conn.execute('SELECT description, updated_at, status FROM tasks WHERE id=11').fetchone()
    marks = re.findall(r'(?m)^\[(\d+) '.replace('[', '[R'), d2)
    c2 = line_anchored_counts(d2)
    print('post_chars', len(d2))
    print('entries', len(marks), 'range', marks[0] + '..' + marks[-1], 'last_r', marks[-1])
    print('R%s_count' % r, c2[r], '(expect 1; archive holds the preserved intruder copy, x1 expected there)')
    print('R%s_count' % sr, c2[sr])
    print('intruder_removed', c2[r] == 1)
    print('updated_at_utc', ua, '(+8h = CST)')
    print('status', st)


if __name__ == '__main__':
    main()
