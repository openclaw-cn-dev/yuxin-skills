#!/usr/bin/env python3
# dedup_skill_tables.py — 重复内容行批量去重 (pitfall-N+171, #N+145 实测沉淀)
#
# 背景: 心跳 #N+145 发现 SKILL.md 指针表 2611.01003 行重复(×2) + 上轮 4 篇指针行双写
#       + p0-pool 4 篇整段双写 + 头注 v1.27 增量行连续两行完全相同 — 3 处共 8 条重复行。
#       N+171 协议: 心跳批量写 SKILL.md / p0-pool 前必先 dedup-then-insert;
#       任何 insert 之后调用方必须 assert 目标 anchor 在文件中 count == 1。
#
# 用法:
#   python3 dedup_skill_tables.py                # dry-run(默认), 只报告不写
#   python3 dedup_skill_tables.py --apply        # 实际写回
#   python3 dedup_skill_tables.py --skill <path> --pool <path> --apply
#
# 去重规则(N+171):
#   - 数据行: | **<arxiv-id>** ... (指针表) 或 | <arxiv-id> | ... (P0 池) → 整行精确匹配全局去重
#   - 头注版本行: 以 "> 🤖 **v" 开头 → 整行精确匹配全局去重(内容完全相同才删, 保守)
#   - 永远 dry-run 先看报告, 确认 DUP 行全部是预期重复后再 --apply
import argparse
import re
import sys

DEFAULT_SKILL = '/Users/hua/.hermes/skills/quant/quantitative-research/SKILL.md'
DEFAULT_POOL = '/Users/hua/.hermes/skills/quant/quantitative-research/references/p0-pool-master-index.md'

# 指针表行: "| **2611.01003** | ..." ; P0 池行: "| 2611.05310 | ..." — 两种形态通吃
DATA_ROW = re.compile(r'^\| (\*\*)?\d{4}\.\d{4,5}(\*\*)? ')
HEADER_ROW_PREFIX = '> 🤖 **v'


def dedup(path, apply):
    if not path:
        return 0
    lines = open(path, encoding='utf-8').read().split('\n')
    seen, out, removed = set(), [], []
    for ln in lines:
        is_managed = bool(DATA_ROW.match(ln)) or ln.startswith(HEADER_ROW_PREFIX)
        if is_managed and ln in seen:
            removed.append(ln[:110])
            continue
        if is_managed:
            seen.add(ln)
        out.append(ln)
    print('[%s] duplicate rows: %d' % (path, len(removed)))
    for r in removed:
        print('  DUP: %s' % r)
    if apply and removed:
        open(path, 'w', encoding='utf-8').write('\n'.join(out))
        print('  -> written back (%d removed)' % len(removed))
    return len(removed)


def main():
    ap = argparse.ArgumentParser(description='N+171 duplicate-row dedup for heartbeat-edited skill tables')
    ap.add_argument('--skill', default=DEFAULT_SKILL, help='SKILL.md path')
    ap.add_argument('--pool', default=DEFAULT_POOL, help='p0-pool-master-index.md path')
    ap.add_argument('--apply', action='store_true', help='actually write back (default: dry-run)')
    args = ap.parse_args()
    total = dedup(args.skill, args.apply) + dedup(args.pool, args.apply)
    print('TOTAL duplicate rows: %d (mode: %s)' % (total, 'APPLY' if args.apply else 'DRY-RUN'))
    print('N+171 reminder: after any insert, caller must assert anchor count == 1 in target file')
    sys.exit(0)


if __name__ == '__main__':
    main()
