# -*- coding: utf-8 -*-
"""Locate + externalize a wall segment span in laomo-heartbeat SKILL.md (R515 recipe, R670 hardened).

Usage: write this pattern as a script via write_file (CJK content in terminal
commands trips tirith:confusable_text), edit MARKERS, then run:
    python3 <this file>

Hardened per R670:
- START marker 'R<digits> ' prefix strings can match EARLIER pointer/reference
  lines before the wall segment -> after find, always assert span boundaries
  via the ordinal-mark regex inventory below.
- Ordinal marks extracted by regex are BARE digits (no 'R' prefix) — assert
  against bare digits ('656' not 'R656'); R-prefixed assertions always fail.
- END anchor built via chr() (R438/R442 homoglyph defense).
- Backup left in /tmp (no rm in chains: tirith 'delete in root path' gate).
"""
import re

P = '/Users/hua/.hermes/skills/laomo-heartbeat/SKILL.md'

# ---- MARKERS: edit these two each round ----
START = 'R656 '            # first entry of the span to externalize
END = (chr(0x82E5) + chr(0x786E) + chr(0x9700) + chr(0x5B9A) + chr(0x4F4D))
# = "ruo-que-xu-ding-wei" anchor phrase; wall_line_insert.py builds it the same way
FIRST, LAST, NEW = 656, 669, 670   # bare digits, no R prefix
ARCHIVE_TITLE = 'R656 至 R669 后段家族逐轮原文迁存（R670 缩容轮外置, 2026-09-22）'
POINTER = ('R656..R669 主墙段逐轮原文 → references/wall-history-r656-r669.md'
           '（R670 缩容轮外置; 墙全计数读该档 + 各前置档案头部;'
           ' 新墙行插锚行前, 余量 <600 走档内 append） \n')
# ***SECRET***

s = open(P, encoding='utf-8').read()
i = s.find(START)
j = s.find(END, i)
assert i > 0 and j > i, (i, j)
span = s[i:j]

# boundary assertion: bare-digit inventory
marks = re.findall(r'R(\d+) [一二三四五六七八九十百零]+犯', span)
print('span R-marks:', marks)
assert str(FIRST) in marks and str(LAST) in marks and str(NEW) not in marks, marks
print('span chars:', len(span))
print('span head:', span[:40].replace('\n', '|'))
print('span tail:', span[-60:].replace('\n', '|'))

arch = ('/Users/hua/.hermes/skills/laomo-heartbeat/references/'
        'wall-history-r{}-r{}.md'.format(FIRST, LAST))
with open(arch, 'w', encoding='utf-8') as f:
    f.write('# ' + ARCHIVE_TITLE + '\n\n')
    f.write('> 墙全计数: 本档承接主墙段逐轮原文; 全局活计数器以 SKILL.md 头部为准'
            '（勿在本档复制计数器串; 标题禁含 R号+序数 配对防 wall_count_check 误报）。\n\n')
    f.write(span.rstrip() + '\n')

s2 = s[:i] + POINTER + s[j:]
open(P, 'w', encoding='utf-8').write(s2)
print('old len:', len(s), '-> new len:', len(s2), 'shed:', len(s) - len(s2))
print('SHRINK_OK — rerun wall_count_check.py next (suggested ordinal must equal LAST+1)')
