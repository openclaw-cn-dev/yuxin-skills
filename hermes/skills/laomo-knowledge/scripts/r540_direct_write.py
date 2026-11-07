# -*- coding: utf-8 -*-
# r540_direct_write.py — 老莫 hourly silent round R<n> entry 写入范本
# 融合 R534 (4-tier drop 决策) + R537 (chars 口径 + precheck 主动剪枝)
# Pitfall #86/#88/#93/#95/#96/#97 五重防御 + Pitfall #100/#101 兼容
# Style: `+` 拼接模式 (Pitfall #93) + 字面量外置 .txt (Pitfall #88)
# 用法: ENTRY_PATH 改指向你的 rXXX_entry.txt, TASK_ID=11 默认
# R540 实测: entry_chars=1110, drop_n=0, desc_post=47320, margin=1832 chars, 一次通过
import sqlite3, os, re

DB_PATH = '/Users/hua/.hermes/tasks.db'
ENTRY_PATH = '/Users/hua/.hermes/profiles/laomo/.tmp/r540_entry.txt'
TASK_ID = 11

# Pitfall #97: chars 口径, 不依赖 wc 命令
new_entry = open(ENTRY_PATH, encoding='utf-8').read().rstrip('\n')
entry_chars = len(new_entry)
print('[PRE] entry_chars=' + str(entry_chars))

conn = sqlite3.connect(DB_PATH)
desc = conn.execute('SELECT description FROM tasks WHERE id=?', (TASK_ID,)).fetchone()[0]
spans = [m.start() for m in re.finditer(r'(?m)^\[R\d+ ', desc)]
chunks = [desc[a:b] for a,b in zip(spans, spans[1:]+[len(desc)])]
last_r = int(re.match(r'\[R(\d+) ', chunks[-1]).group(1))
print('[PRE] last_r=' + str(last_r) + ' chunks=' + str(len(chunks)) + ' desc=' + str(len(desc)))

# Pitfall #96 precheck + Pitfall #91 4-tier drop decision
proj_no_drop = len(desc) + 2 + entry_chars
margin_to_48k = 49152 - proj_no_drop
print('[PROJ] proj_no_drop=' + str(proj_no_drop) + ' margin_to_48KB=' + str(margin_to_48k))

drop_n = 0
if proj_no_drop >= 51200:
    drop_n = max(2, (proj_no_drop - 48104) // 3500 + 1)
    print('[DROP-TIER] >=50KB hard-cap, drop_n=' + str(drop_n))
elif proj_no_drop >= 49152:
    drop_n = 1
    print('[DROP-TIER] >=48KB early-gate, drop_n=1')
elif proj_no_drop >= 48500 and entry_chars >= 1500:
    drop_n = 1
    print('[DROP-TIER] margin < 1500 chars proactive, drop_n=1')
else:
    print('[DROP-TIER] zero (safe zone, margin=' + str(margin_to_48k) + ')')

# Apply drop (Pitfall #86 chunks[0] by position, R478 序 discipline)
if drop_n > 0:
    drop_chars = sum(len(chunks[i]) + 2 for i in range(min(drop_n, len(chunks))))
    keep_desc = ''.join(chunks[drop_n:])
    desc_after_drop = keep_desc
    print('[DROP] dropped=' + str(drop_chars) + ' chars, chunks_remain=' + str(len(chunks) - drop_n))
else:
    desc_after_drop = desc

# Final write
final_desc = desc_after_drop.rstrip('\n') + '\n\n' + new_entry + '\n'
final_chars = len(final_desc)
final_margin = 49152 - final_chars
print('[POST] final_desc=' + str(final_chars) + ' chars, margin_to_48KB=' + str(final_margin))

if final_chars > 51200:
    print('[ABORT] final > 50KB hard-cap, aborting')
    raise SystemExit(1)

conn.execute('UPDATE tasks SET description=? WHERE id=?', (final_desc, TASK_ID))
conn.commit()

# Verify (Pitfall #82 ground-truth postcheck)
desc_post = conn.execute('SELECT description FROM tasks WHERE id=?', (TASK_ID,)).fetchone()[0]
spans_post = [m.start() for m in re.finditer(r'(?m)^\[R\d+ ', desc_post)]
chunks_post = [desc_post[a:b] for a,b in zip(spans_post, spans_post[1:]+[len(desc_post)])]
last_r_post = int(re.match(r'\[R(\d+) ', chunks_post[-1]).group(1))
print('[VERIFY] desc_post=' + str(len(desc_post)) + ' chunks=' + str(len(chunks_post)) + ' last_r=' + str(last_r_post))
print('[OK] R entry written successfully')
