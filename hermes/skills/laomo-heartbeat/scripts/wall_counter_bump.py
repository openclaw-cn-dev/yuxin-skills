#!/usr/bin/env python3
"""Bump the live defense-wall violation counter + refresh header budget line.

R663-curator toolization of the pattern hand-written in the R661 and R663
heartbeat sessions. Runs after wall_line_insert.py on violation rounds.

Usage:
    python3 wall_counter_bump.py <old_ordinal_cjk> <new_ordinal_cjk>
    e.g.  python3 wall_counter_bump.py 二百二十二 二百二十三

Behavior (all edits in memory; file written once, only after checks pass):
  1. exact-string scan for the current-ordinal counter (CJK numerals):
         下一犯自<old>犯起计
     Expect count in {1, 2}: the live counter + the R661 pitfall-text
     EXAMPLE ordinal inside the header warning block, whose example string
     is identical to the live counter string and gets bumped along with it
     (harmless; do NOT misread it as a second independent live counter).
     Stale archive-pointer copies (一百二十九犯 / 一百三十八犯 ...) never
     contain the current ordinal, so exact matching excludes them.
  2. refuse if the NEW ordinal is already present (double-bump guard).
  3. replace ALL occurrences, then verify old-ordinal count == 0.
  4. refresh the first header budget line "wc -m 实测 N 余 M" with a
     re-measured len + same-width padding (full-width space U+3000).
     Programmatic regex replace - immune to the R541 stale-anchor manual
     refresh trap. If same-width construction fails (digit-count growth),
     the counter bump is still written and the budget line is left for
     next-session refresh (the protocol refreshes it on every opening).

Exit 0 = BUMP_OK with final file_len + margin. Nonzero = assertion failed,
nothing written.
"""
import re
import sys

DEFAULT_PATH = '/Users/hua/.hermes/skills/laomo-heartbeat/SKILL.md'
BUDGET_RE = re.compile(r'wc -m 实测 (\d+) 余 (\d+)')
TARGET = 100000


def same_width(old_s, new_s):
    if len(new_s) < len(old_s):
        return '\u3000' * (len(old_s) - len(new_s)) + new_s
    return new_s


def main(argv):
    if len(argv) != 3:
        print('usage: wall_counter_bump.py <old_ordinal_cjk> <new_ordinal_cjk>')
        return 2
    old_ord, new_ord = argv[1], argv[2]
    path = DEFAULT_PATH
    with open(path, encoding='utf-8') as f:
        t = f.read()

    cur = '下一犯自%s犯起计' % old_ord
    nxt = '下一犯自%s犯起计' % new_ord

    n = t.count(cur)
    if n not in (1, 2):
        print('FATAL: current-ordinal counter count=%d (expect 1 or 2: '
              'live counter + R661 example-ordinal passenger). '
              'Re-probe with a regex scan over 下一犯自...犯起计 before editing.' % n)
        return 1
    if t.count(nxt):
        print('FATAL: new ordinal already present - double bump guard.')
        return 1

    t = t.replace(cur, nxt)
    if t.count(cur):
        print('FATAL: old ordinal still present after replace.')
        return 1
    print('counter bumped x%d: %s %s -> %s' % (n, old_ord, new_ord, new_ord))

    m = BUDGET_RE.search(t)
    if not m:
        print('WARN: budget line not found; counter bumped, budget left stale.')
    else:
        new_len = len(t)
        remaining = TARGET - new_len
        new_line = 'wc -m 实测 %s 余 %s' % (
            same_width(m.group(1), str(new_len)),
            same_width(m.group(2), str(remaining)),
        )
        if len(new_line) == len(m.group(0)):
            t = t[:m.start()] + new_line + t[m.end():]
            print('budget line refreshed: %s' % new_line.strip())
        else:
            print('WARN: same-width mismatch (%d -> %d); budget left stale '
                  '(next session refreshes on opening).'
                  % (len(m.group(0)), len(new_line)))

    with open(path, 'w', encoding='utf-8') as f:
        f.write(t)
    print('BUMP_OK file_len=%d margin=%d' % (len(t), TARGET - len(t)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
