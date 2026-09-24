#!/usr/bin/env python3
"""
Round Commit Template — R<n> 落库脚本模板

固化时间: 2026-09-24 R694 实证
出处: laomo-heartbeat/references/cron-ops-r692-p134.md §7.4

适用场景: 老莫心跳 cron R 轮次落库 (drop_n 个最旧 R chunk + append 当前 R entry)

P#130 v3 / P#131 / P#134 / P#135 四道防御全 baked:
  - entry 实测 (P#135 升格, 写后漂移贯穿 write_file→patch)
  - drop chunk 长度实测先行 (P#133 v2 补强)
  - pre-write dup 断言 + post-write 三层断言 (R<n>/R<a>/R<b>/R<b+1>)
  - archive append + count=1 闭环 (R631 wrapper 自检不可信家族)

使用方式 (R<n>=要写的新号, R<a>..R<b>=要 drop 的旧号区间):
  1. cp scripts/round_commit_template.py /tmp/r<n>_commit.py
  2. 替换模板里的 <n>/<a>/<b> 占位符
  3. python3 /tmp/r<n>_commit.py
  4. 全绿后 status_probe.sh desc 节确认 last_r/entries/range
  5. (可选, P#134 兜底) python3 scripts/archive_dedupe.py

禁忌: cron mode execute_code 被 BLOCKED, 必须走 write_file 落 /tmp + python3 调用
"""
import sqlite3
import sys

DB = '/Users/hua/.hermes/tasks.db'
ENTRY = '/tmp/r<n>_entry.txt'
ARCHIVE = '/Users/hua/.hermes/profiles/laomo/evolution/task-11-log-archive.md'
TASK_ID = 11
GATE_CHARS = 49152  # 早闸口, P#133 v2 / R181


def read_entry(path):
    with open(path, 'rb') as f:
        raw = f.read()
    return raw.decode('utf-8')


def assert_entry_shape(entry, r_n):
    """R347 头部/尾部断言 + P#135 最终实测口径"""
    assert entry.startswith(f'[R{r_n} '), \
        f'entry must start with [R{r_n} , got {entry[:30]!r}'
    assert entry.rstrip().endswith('keep_in_progress。'), \
        'entry must end with keep_in_progress。'
    return len(entry)


def fetch_desc():
    conn = sqlite3.connect(DB)
    return conn, conn.execute(f"SELECT description FROM tasks WHERE id={TASK_ID}").fetchone()[0]


def pre_write_dup_check(d, r_n, r_a, r_b):
    """P#130 v3 pre-write dup 断言"""
    assert d.count(f'[R{r_n} ') == 0, \
        f'R{r_n} must not pre-exist (count={d.count(f"[R{r_n} ")}, P#130 v3 dup)'
    assert d.count(f'[R{r_a} ') == 1, \
        f'R{r_a} must exist exactly once (count={d.count(f"[R{r_a} ")})'
    assert d.count(f'[R{r_b} ') == 1, \
        f'R{r_b} must exist exactly once (count={d.count(f"[R{r_b} ")})'


def locate_drop_index(d, r_after):
    """drop 起点定位 (R279 glue-join 坑规避: \n\n 双换行锚)"""
    marker = f'\n\n[R{r_after} '
    idx = d.find(marker)
    if idx < 0:
        idx = d.find(f'[R{r_after} ')
    assert idx >= 0, f'R{r_after} marker not found in desc'
    return idx


def build_new_desc(d, drop_idx, entry):
    """P#133 v2 + P#134 半残规避: 在 commit 之前断言 size"""
    kept = d[drop_idx:]
    new_desc = kept + '\n\n' + entry
    assert len(new_desc) <= GATE_CHARS, \
        f'new desc too large: {len(new_desc)} > {GATE_CHARS} (早闸口 FAIL, 走 drop_n+=1 重试)'
    return new_desc


def commit_desc(new_desc):
    """写入 + R262 commit 先于 assert"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        f"UPDATE tasks SET description=?, updated_at=CURRENT_TIMESTAMP WHERE id={TASK_ID}",
        (new_desc,)
    )
    conn.commit()
    return conn, cur


def post_write_assert(conn, r_n, r_a, r_b, r_after, new_chars):
    """P#130 v3 post-write 多维断言 (dropped/dropped/anchor preserved)"""
    d2 = conn.execute(f"SELECT description FROM tasks WHERE id={TASK_ID}").fetchone()[0]
    assert d2.count(f'[R{r_n} ') == 1, \
        f'R{r_n} must exist exactly once after write (count={d2.count(f"[R{r_n} ")})'
    assert d2.count(f'[R{r_a} ') == 0, \
        f'R{r_a} must be dropped (count={d2.count(f"[R{r_a} ")} != 0)'
    assert d2.count(f'[R{r_b} ') == 0, \
        f'R{r_b} must be dropped (count={d2.count(f"[R{r_b} ")} != 0)'
    assert d2.count(f'[R{r_after} ') == 1, \
        f'R{r_after} anchor must be preserved (count={d2.count(f"[R{r_after} ")})'
    assert len(d2) <= GATE_CHARS, f'size still over: {len(d2)}'
    assert d2.rstrip().endswith('keep_in_progress。'), 'tail preserved'
    print(f'post-write chars: {len(d2)} (pre-write prediction: {new_chars})')


def append_archive(entry, r_n):
    """archive append + count=1 闭环断言 (R609 / R338 archive chain + R631 闭环)"""
    with open(ARCHIVE, 'a', encoding='utf-8') as f:
        f.write('\n\n' + entry)
    with open(ARCHIVE, 'rb') as f:
        raw = f.read().decode('utf-8')
    count = raw.count(f'[R{r_n} ')
    assert count == 1, f'archive R{r_n} count must = 1, got {count}'
    print(f'archive appended OK, R{r_n} count in archive = 1')


def main():
    # ===== 模板参数 (按需替换) =====
    r_n = None       # 本轮新号, 例 695
    r_a = None       # 要 drop 的最旧号, 例 685 (>= drop_n=2 时设, 否则 None)
    r_b = None       # 要 drop 的最新号, 例 686
    r_after = None   # drop 后第一条, 例 687 (R<a>..R<b> drop 后 R<r_after> 应是首条)

    if r_n is None or r_b is None:
        print('ERROR: r_n / r_b 必填, r_a / r_after 按 drop_n 填')
        sys.exit(1)

    # 1. 实测 entry (P#135 升格, 写后漂移贯穿 write_file→patch)
    entry = read_entry(ENTRY)
    entry_chars = assert_entry_shape(entry, r_n)
    print(f'entry chars: {entry_chars}')

    # 2. 取 desc
    conn_pre, d = fetch_desc()
    conn_pre.close()
    print(f'pre chars: {len(d)}')

    # 3. pre-write dup 断言 (P#130 v3)
    if r_a is not None:
        pre_write_dup_check(d, r_n, r_a, r_b)

    # 4. drop 起点定位 (R279 \n\n 双换行锚, P#133 v2 补强实测 chunk 长度)
    drop_idx = locate_drop_index(d, r_after)
    print(f'R{r_after} marker idx: {drop_idx}')

    # 5. 拼接 + size 断言 (P#134 半残规避)
    new_desc = build_new_desc(d, drop_idx, entry)

    # 6. 写入 (R262 commit 先于 assert)
    conn, _ = commit_desc(new_desc)

    # 7. post-write 多维断言
    post_write_assert(conn, r_n, r_a, r_b, r_after, len(new_desc))

    # 8. archive append + count=1 闭环
    append_archive(entry, r_n)

    conn.close()
    print('\n=== ALL CHECKS PASSED ===')


if __name__ == '__main__':
    main()