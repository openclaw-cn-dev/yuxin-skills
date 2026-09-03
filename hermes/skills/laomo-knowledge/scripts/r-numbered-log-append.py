#!/usr/bin/env python3
"""老莫心跳 R<N> 日志追加脚本模板 — 通过 R132 实战验证（R124/R125/R128/R129 全防御体系）

用法：
  1. 复制到 /tmp/<profile>_r<NNN>_append.py
  2. 改 3 个变量：TASK_ID, new_r（本轮号码）, entry 字符串
  3. python3 /tmp/<...>.py

设计要点（按踩坑顺序）：
  - 防御 R119 模式 1: f-string 占位符未渲染 → assert f"[R{new_r} " in entry
  - 防御 R119 模式 2: split vs re.findall → 用 re.findall(r"\[R(\d+)", desc) + max(int)
  - 防御 R124 #5 模式: 写前 assert 三条 (last_r+1, entry marker, not exists)
  - 防御 R125: re.findall 返 str 不是 int → max(int(n) for n in nums)
  - 防御 R129 #6: 重复检测用 canonical 日期戳正则 (R151 升级：原 `\[R(\d+) ` 宽松模式会被 prose 引用误判)
  - 防御 R129 #7: commit 早于 assert 失败 → 写后再 SELECT verify + 残留剥离路径
  - 防御 R148: KB 软预警用字符口径 `len(desc)` 而非字节 `len(desc.encode('utf-8'))`

实战首跑通过：R132 (2026-09-01) 一跑成功零回滚、所有 assert 全绿、5KB 写入 description。
R151 升级（2026-09-02 14:05 CST）：canonical 日期戳正则替换宽松模式，详见 Pitfall #32 + references/***SECRET***.md。
"""
import sqlite3
import re
from collections import Counter

# === 必改的 3 个变量 ===
TASK_ID = 11  # tasks.db 里的任务 ID
new_r = 132   # 本轮号码（必须递增，禁止复用）
# entry 字符串构造（用 f-string，[R{new_r} 必须占用占位符）
now_str = "2026-09-01 14:05 CST"  # 本轮时间
entry = (
    f"\n\n[R{new_r} {now_str} laomo heartbeat] (在此写本轮内容，"
    f"f-string 占位符必须用实际变量填充)\n"
)

# === R151 升级：canonical 日期戳正则（区分主条目 vs prose 引用）===
# canonical 主条目格式：[R<n> YYYY-MM-DD HH:MM CST laomo heartbeat]
# prose 引用格式：[R<n> <非日期戳文本>]（如 [R128 headless limit continues]）
# 宽松模式 `\[R(\d+) ` 会同时捕获两者 → 触发 dup_check 假阳性
# Pitfall #32：必须用 canonical 日期戳正则
CANONICAL_RE = r"\[R(\d+) 20\d\d-\d\d-\d\d \d\d:\d\d CST laomo heartbeat\]"

DB = "/Users/hua/.hermes/tasks.db"

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("SELECT description FROM tasks WHERE id = ?", (TASK_ID,))
row = c.fetchone()
if not row:
    print(f"FATAL: 任务 {TASK_ID} 不存在")
    exit(1)
desc = row[0] or ""

# === 解析 last R number（R125 防御: int() 包裹；R151 升级: canonical pattern）===
nums = re.findall(CANONICAL_RE, desc)
nums = [int(n) for n in nums]
last_r = max(nums) if nums else 0

# === R129 #6 防御: 重复检测用 canonical 日期戳正则（R151 升级）===
# 之前用 `\[R(\d+) ` 宽松模式，会被 prose 引用（如 [R128 headless limit continues]）误判为 canonical 条目
# 触发假阳性 assert fail，导致整个 append 脚本中断（R151 实战踩坑：description 42.5KB 含 R128 6 次引用）
# 修复：使用 CANONICAL_RE 只匹配主条目，prose 引用不在防御范围
canon_marks = re.findall(CANONICAL_RE, desc)
canon_check = [int(n) for n in canon_marks]
canon_counter = Counter(canon_check)
canon_dups = {n: c for n, c in canon_counter.items() if c > 1}
assert not canon_dups, f"发现重复 canonical R 编号: {canon_dups}"

# === R124 #5 三条 assert ===
assert new_r == last_r + 1, f"R 编号模板失败: new_r={new_r} != last_r+1={last_r+1}"
assert f"[R{new_r} " in entry, "entry 缺少 [R<n> 标记 — f-string 占位符未渲染"
assert f"[R{new_r} " not in desc, f"R{new_r} 已存在，禁止复用"

# === 写库 ===
c.execute(
    "UPDATE tasks SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
    (desc + entry, TASK_ID),
)
conn.commit()

# === R129 #7 防御: 写后 SELECT verify（R151 升级：canonical pattern 一致）===
c.execute("SELECT description FROM tasks WHERE id = ?", (TASK_ID,))
verify_desc = c.fetchone()[0]
verify_nums = re.findall(CANONICAL_RE, verify_desc)
verify_last = max(int(n) for n in verify_nums) if verify_nums else 0
assert verify_last == new_r, f"写库后 last R 不匹配: verify_last={verify_last} != new_r={new_r}"
assert f"[R{new_r} " in verify_desc, "写库后未找到 [R<n> 标记 — 残留剥离需要?"

# === 30KB 软预警（pitfall #27-bis，R132 实战触发）===
# R148 patch: 用字符口径 `len(desc)` 而非字节 `len(desc.encode('utf-8'))`,
# 与 templates/laomo_desc_prune.py R141 协议 / Pitfall #30 保持一致。
# 中文描述每字 3 字节 UTF-8, 字节口径会偏大三倍过早预警。
desc_size_chars = len(verify_desc)
print(f"OK: R{new_r} 已写入 任务 #{TASK_ID}")
print(f"    description 长度: {desc_size_chars / 1024:.1f} KB chars (字符口径)")
print(f"    R 编号序列最后 3 条: {verify_nums[-3:]}")

conn.close()