#!/usr/bin/env python3
"""防线墙 (defense wall) ordinal count check for laomo-heartbeat (R519 codification).

Scans SKILL.md + references/wall-history-*.md as ONE union (R475 rule: the last
pair may live in any archive file), pairs R numbers with violation ordinals
(N犯), prints the tail pairs and the suggested next ordinal in Chinese numerals.

Why this exists: R518 claimed a wall insertion ("一百三十二犯") that a union
count showed never landed — wall self-reports are NOT a fact source (R519 first
proof). Run this instead of hand-counting; still eyeball-exclude prose false
positives (e.g. "R459 同型连犯") from the tail pairs before trusting the last.

Usage: python3 wall_count_check.py
"""
import glob
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r'R(\d+)[^.\n]{0,40}?([\d一二三四五六七八九十百零]{1,8})犯')
D = '零一二三四五六七八九'


def cn_to_int(s):
    """Parse a CJK ordinal (up to 999) or plain digits to int."""
    s = s.strip()
    if s.isdigit():
        return int(s)
    total = 0
    if '百' in s:
        h, s = s.split('百', 1)
        total += (D.index(h) if h else 1) * 100
        if s.startswith('零'):
            s = s[1:]
            return total + D.index(s) if s else total
    if '十' in s:
        t, s = s.split('十', 1)
        total += (D.index(t) if t else 1) * 10
    if s:
        total += D.index(s)
    return total


def cn_num(n):
    """Int (1..999) to CJK ordinal string."""
    if n < 10:
        return D[n]
    if n < 20:
        return '十' + (D[n % 10] if n % 10 else '')
    if n < 100:
        return D[n // 10] + '十' + (D[n % 10] if n % 10 else '')
    h, r = divmod(n, 100)
    s = D[h] + '百'
    if r == 0:
        return s
    if r < 10:
        return s + '零' + D[r]
    return s + cn_num(r)


def main():
    files = [os.path.join(BASE, 'SKILL.md')]
    files += sorted(glob.glob(os.path.join(BASE, 'references', 'wall-history-*.md')))
    pairs = []
    for f in files:
        try:
            t = open(f, encoding='utf-8').read()
        except OSError as e:
            print('SKIP %s (%s)' % (f, e))
            continue
        for m in PAT.finditer(t):
            pairs.append((int(m.group(1)), m.group(2), os.path.basename(f)))
    pairs.sort()
    print('files scanned: %d, total pairs: %d' % (len(files), len(pairs)))
    print('last 8 (R, ordinal, file) — eyeball-exclude prose false positives first:')
    for p in pairs[-8:]:
        print('  R%d  %s犯  (%s)' % p)
    if pairs:
        nxt = cn_to_int(pairs[-1][1]) + 1
        print('suggested next ordinal (verified last +1, R474 discipline): %s犯' % cn_num(nxt))
        print('WARNING: verify the last pair is a real wall entry, not a prose mention,')
        print('and check whether the PREVIOUS round\'s claimed insertion actually landed')
        print('(R518 gap precedent: claimed insertion absent from union = never written).')


if __name__ == '__main__':
    main()
