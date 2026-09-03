#!/usr/bin/env python3
"""老莫心跳 description 剪枝脚本（R140 实战触发,47.9KB 临界）
当 description 进入 (b) 区间 (40-50KB) 时,本轮 append 前先执行剪枝:
- 读 description,定位最早 R<n> 起点
- 把 R<n>..R<n+24> 共 25 轮归档到
  ~/.hermes/profiles/laomo/evolution/task-<TASK_ID>-log-archive.md
- description 只保留最近 ~50 轮

设计要点(R140 实战验证):
- 用 re.findall(r"\\[R(\\d+) 20\\d\\d-\\d\\d-\\d\\d", desc) 定位主条目
  (避开 R129/R137 prose 误判 + NOTE 形式误判)
- 归档文件追加模式(open 'a'),避免覆盖历史
- 归档时同步写 meta 行(剪枝时间、归档 R 范围、description 前后长度)
- 剪枝后必须 UPDATE description + 重新 SELECT 验证 last_r 不变
- 若剪枝失败,严禁 silent round 跳过 — 老莫 in_progress 任务
  description 必须保留可追溯性

用法:
  1. 复制到 /tmp/laomo_prune_<r>.py
  2. 改 TASK_ID、archive_path_suffix、keep_recent 三个变量
  3. python3 /tmp/laomo_prune_<r>.py
  4. 再走 r-numbered-log-append.py 追加本轮 R<n>

参数建议(40-50KB 区间):
  keep_recent=50  # 保留最近 50 轮 (约 25KB)
  archive_path_suffix = f"task-{TASK_ID}-log-archive.md"
"""
import os
import re
import sqlite3
from datetime import datetime

# === 必改的 3 个变量 ===
TASK_ID = 11
keep_recent = 50  # 保留最近 N 轮主条目
ARCHIVE_DIR = "/Users/hua/.hermes/profiles/laomo/evolution"
archive_filename = f"task-{TASK_ID}-log-archive.md"

DB = "/Users/hua/.hermes/tasks.db"

# === 读 description ===
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT description FROM tasks WHERE id = ?", (TASK_ID,))
row = c.fetchone()
if not row:
    print(f"FATAL: 任务 {TASK_ID} 不存在")
    exit(1)
desc = row[0] or ""

# === 定位所有主条目起头位置 (R137 防御:含日期戳) ===
pattern = re.compile(r"\[R(\d+) 20\d\d-\d\d-\d\d")
matches = list(pattern.finditer(desc))
print(f"INFO: 当前 description 含 {len(matches)} 条 R 主条目")

desc_size_kb = len(desc.encode("utf-8")) / 1024
print(f"INFO: description 大小 {desc_size_kb:.1f} KB")

if len(matches) <= keep_recent:
    print(f"SKIP: 主条目数 {len(matches)} <= keep_recent {keep_recent},无需剪枝")
    conn.close()
    exit(0)

# === 计算剪枝边界 ===
prune_count = len(matches) - keep_recent
first_pruned = matches[0]
last_kept = matches[prune_count]
cut_pos = last_kept.start()

pruned_section = desc[first_pruned.start():cut_pos]
kept_section = desc[cut_pos:]

pruned_r_nums = [int(m.group(1)) for m in matches[:prune_count]]
kept_r_nums = [int(m.group(1)) for m in matches[prune_count:]]
print(f"PLAN: 剪枝 R{pruned_r_nums[0]}-R{pruned_r_nums[-1]} ({prune_count} 条) → 归档")
print(f"      保留 R{kept_r_nums[0]}-R{kept_r_nums[-1]} ({len(kept_r_nums)} 条)")

# === 确保归档目录存在 ===
os.makedirs(ARCHIVE_DIR, exist_ok=True)
archive_path = os.path.join(ARCHIVE_DIR, archive_filename)

# === 写归档文件(append 模式)===
now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
meta_line = (
    f"\n\n===== 剪枝批次 {now_iso} =====\n"
    f"任务 ID: {TASK_ID}\n"
    f"剪枝范围: R{pruned_r_nums[0]} - R{pruned_r_nums[-1]} ({prune_count} 条)\n"
    f"保留范围: R{kept_r_nums[0]} - R{kept_r_nums[-1]} ({len(kept_r_nums)} 条)\n"
    f"剪枝前 description: {desc_size_kb:.1f} KB\n"
    f"----- 以下为归档内容 -----\n"
)
with open(archive_path, "a", encoding="utf-8") as f:
    f.write(meta_line)
    f.write(pruned_section)
    f.write("\n----- 归档结束 -----\n")

print(f"OK: 已归档 {len(pruned_section)} bytes 到 {archive_path}")

# === UPDATE description(只保留 kept_section)===
c.execute(
    "UPDATE tasks SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
    (kept_section, TASK_ID),
)
conn.commit()

# === 写后 SELECT verify ===
c.execute("SELECT description FROM tasks WHERE id = ?", (TASK_ID,))
verify_desc = c.fetchone()[0]
verify_matches = pattern.findall(verify_desc)
verify_nums = [int(n) for n in verify_matches]
verify_last = max(verify_nums) if verify_nums else 0
verify_size_kb = len(verify_desc.encode("utf-8")) / 1024

# last_r 应保持不变(最大 R 编号在保留范围内)
assert verify_last == kept_r_nums[-1], (
    f"剪枝后 last R 不匹配: verify_last={verify_last} != expected={kept_r_nums[-1]}"
)
assert verify_nums[0] == kept_r_nums[0], (
    f"剪枝后 first R 不匹配: verify_first={verify_nums[0]} != expected={kept_r_nums[0]}"
)
assert len(verify_nums) == keep_recent, (
    f"剪枝后 R 条目数不匹配: {len(verify_nums)} != {keep_recent}"
)

print(f"OK: 剪枝完成")
print(f"    description: {desc_size_kb:.1f} KB → {verify_size_kb:.1f} KB")
print(f"    保留 R{verify_nums[0]}-R{verify_last} ({len(verify_nums)} 条)")
print(f"    归档文件: {archive_path}")

conn.close()