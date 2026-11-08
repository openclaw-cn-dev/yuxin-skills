# -*- coding: utf-8 -*-
"""R529 verified direct_prune_write template (Pitfall #86 兜底 + #88 中文编码 + #93 f-string 反斜杠 三重防御)。

⚠️ 这是 R529 hourly silent round 实战验证过的"可复制即用"范本 (2310 chars, lint OK, R 编号断言通过)。
R530+ 必修 templates/direct_prune_write.py 时**整体重写**为此范本风格:
  - 修 Pitfall #90 step1_projection 参数错位 bug
  - 修 Pitfall #93 f-string 反斜杠 SyntaxError (全脚本改 + 拼接模式)
  - 保持 Pitfall #88 字面量外置 .txt 文件 + encoding='utf-8' 双防御

用法:
  1. cp 此文件到 ~/.hermes/profiles/laomo/.tmp/r<n>_direct_prune_write.py
  2. 写 ENTRY 到 ~/.hermes/profiles/laomo/.tmp/r<n>_entry.txt (encoding='utf-8')
  3. python3 /Users/hua/.hermes/profiles/laomo/.tmp/r<n>_direct_prune_write.py
"""
import sqlite3, re, datetime

DB = '/Users/hua/.hermes/tasks.db'
ENTRY_FILE = '/Users/hua/.hermes/profiles/laomo/.tmp/r529_entry.txt'  # ⚠️ 改 R<n>
ARCHIVE = '/Users/hua/.hermes/profiles/laomo/evolution/task11_archive.log'
EXPECTED_NEW_R = 529  # ⚠️ 改 R<n>

with open(ENTRY_FILE, encoding='utf-8') as f:
    new_entry = f.read().rstrip() + '\n'

conn = sqlite3.connect(DB)
desc = conn.execute('SELECT description FROM tasks WHERE id=11').fetchone()[0]
spans = [m.start() for m in re.finditer(r'(?m)^\[R\d+ ', desc)]
chunks = [desc[a:b] for a,b in zip(spans, spans[1:]+[len(desc)])]

last_r_pre = re.match(r'\[R(\d+) ', chunks[-1]).group(1)
print('[PRE] desc=' + str(len(desc)) + ' chunks=' + str(len(chunks)) + ' last_R=' + last_r_pre)

# Pitfall #84(a) R478 序 discipline: drop chunks[0] (最旧)
dropped_r = re.match(r'\[R(\d+) ', chunks[0]).group(1)
surviving_chunks = chunks[1:]
new_desc = ''.join(surviving_chunks) + new_entry

print('[DROP] chunks[0] = R' + dropped_r + ' (' + str(len(chunks[0])) + ' chars)')
print('[POST] desc=' + str(len(new_desc)) + ' 余量=' + str(49152 - len(new_desc)))

# 49KB 早闸口 + 50KB 硬阈值防御
assert len(new_desc) < 51200, '硬阈值触发: ' + str(len(new_desc))

conn.execute('UPDATE tasks SET description = ? WHERE id = 11', (new_desc,))
conn.commit()

# archive append
ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
with open(ARCHIVE, 'a', encoding='utf-8') as f:
    f.write('\n\n=== R' + str(EXPECTED_NEW_R) + ' drop R' + dropped_r + ' at ' + ts + ' ===\n')
    f.write('desc_pre=' + str(len(desc)) + ' → desc_post=' + str(len(new_desc)) + '\n')
    f.write('ENTRY (' + str(len(new_entry)) + ' chars):\n' + new_entry + '\n')

# 复核 ground-truth
desc2 = conn.execute('SELECT description FROM tasks WHERE id=11').fetchone()[0]
spans2 = [m.start() for m in re.finditer(r'(?m)^\[R\d+ ', desc2)]
chunks2 = [desc2[a:b] for a,b in zip(spans2, spans2[1:]+[len(desc2)])]
last_r_new = int(re.match(r'\[R(\d+) ', chunks2[-1]).group(1))
print('[VERIFY] desc=' + str(len(desc2)) + ' chunks=' + str(len(chunks2)) + ' last_R=' + str(last_r_new))
assert last_r_new == EXPECTED_NEW_R, 'last_R mismatch: expected ' + str(EXPECTED_NEW_R) + ' got ' + str(last_r_new)
print('[OK] R' + str(EXPECTED_NEW_R) + ' written, R 编号断言通过')
conn.close()