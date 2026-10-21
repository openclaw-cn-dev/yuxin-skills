#!/usr/bin/env python3
"""SKILL.md 超 90KB 自动瘦身（curator pass 配套）。

原理：按 '## ' 切节，保留 frontmatter+前 40% 核心节，其余节整体外置到
同目录 references/split_overflow.md，正文留外置索引——内容零丢失。

用法:
  python3 auto_slim_skillmd.py path/to/SKILL.md [more...]   # 指定文件
  python3 auto_slim_skillmd.py                              # 扫描当前目录树全部超标文件(跳过 .archive)

验收: 瘦身后 find . -name SKILL.md -not -path "*.archive*" -size +90k | wc -l 应为 0

2026-10-20 首战实测: 99→86KB / 98→63KB / 92→17KB。
注意: 单节即超重（无法切节）的会打 [warn]，需手工按长行截断法处理（见 SKILL.md 长行型条目）。
"""
import os
import re
import sys

THRESHOLD = 90 * 1024


def slim(path):
    text = open(path, encoding='utf-8').read()
    size = len(text.encode('utf-8'))
    if size <= THRESHOLD:
        return '[skip] {} {}KB 已达标'.format(path, size // 1024)
    parts = re.split(r'\n(?=## )', text)
    head, sections = parts[0], parts[1:]
    keep_n = max(1, int(len(sections) * 0.4))
    keep, move = sections[:keep_n], sections[keep_n:]
    if not move:
        return '[warn] {} 单节超重无法切节，需手工长行截断'.format(path)
    refdir = os.path.join(os.path.dirname(path), 'references')
    os.makedirs(refdir, exist_ok=True)
    refpath = os.path.join(refdir, 'split_overflow.md')
    mode = 'a' if os.path.exists(refpath) else 'w'
    with open(refpath, mode, encoding='utf-8') as f:
        if mode == 'a':
            f.write('\n\n---\n\n')
        f.write('# 外置章节（{} 瘦身自动外置）\n\n'.format(
            os.path.basename(os.path.dirname(os.path.abspath(path)))) + '\n'.join(move))
    index = ('\n\n## 已外置章节索引\n\n'
             '以下 {} 节已外置到 references/split_overflow.md（超90KB瘦身，内容零丢失）：\n'.format(len(move)))
    for s in move:
        index += '- {}\n'.format(s.splitlines()[0].replace('## ', '').strip()[:60])
    newtext = head + '\n'.join(keep) + index
    open(path, 'w', encoding='utf-8').write(newtext)
    return '[OK] {} {}KB → {}KB（外置 {} 节）'.format(
        path, size // 1024, len(newtext.encode('utf-8')) // 1024, len(move))


def find_oversized(root='.'):
    found = []
    for r, dirs, files in os.walk(root):
        if '.archive' in r.split(os.sep):
            continue
        if os.sep + 'references' in r:
            continue
        for f in files:
            if f == 'SKILL.md':
                p = os.path.join(r, f)
                if os.path.getsize(p) > THRESHOLD:
                    found.append(p)
    return found


if __name__ == '__main__':
    targets = sys.argv[1:] or find_oversized('.')
    if not targets:
        print('无超标 SKILL.md')
    for p in targets:
        print(slim(p))
