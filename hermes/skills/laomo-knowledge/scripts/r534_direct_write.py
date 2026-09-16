# -*- coding: utf-8 -*-
"""R534 verified direct_prune_write 4-tier 剪枝判定脚本 (Pitfall #86/#88/#90/#91/#93 五重防御)。

⚠️ 这是 R534 hourly silent round 实战验证过的"可复制即用"范本 (2124 chars, lint OK, R 编号断言通过)。
R535+ 必修 templates/direct_prune_write.py 时**整体重写**为此风格:
  - 修 Pitfall #90 step1_projection 参数错位 bug (用 proj_no_drop 公式直接喂入决策)
  - 修 Pitfall #91 加 1500 chars 余量警戒线 (4-tier 决策 = 50KB 硬阈值 / 48KB 早闸口 / 1500 chars 余量警戒线 / zero)
  - 修 Pitfall #93 f-string 反斜杠 SyntaxError (全脚本 + 拼接模式)
  - 保持 Pitfall #86 sqlite3 直写 + chunks[0] by position drop
  - 保持 Pitfall #88 字面量外置 .txt 文件 + encoding='utf-8' 双防御

R534 实测执行: proj_no_drop=45955 < 49152 早闸口, 余 3197 > 1500 警戒线 → drop_n=0, 写入 desc=47010 chars, margin=2142。

用法:
  1. cp 此文件到 ~/.hermes/profiles/laomo/.tmp/r<n>_direct_write.py
  2. 写 ENTRY 到 ~/.hermes/profiles/laomo/.tmp/r<n>_entry.txt (encoding='utf-8')
  3. 编辑下方 EXPECTED_NEW_R = <n>
  4. python3 ~/.hermes/profiles/laomo/.tmp/r<n>_direct_write.py
"""
import sqlite3
import re

TASK_DB = '/Users/hua/.hermes/tasks.db'
TASK_ID = 11
ENTRY_FILE = '/Users/hua/.hermes/profiles/laomo/.tmp/r534_entry.txt'  # ⚠️ 改 R<n>
EXPECTED_NEW_R = 534  # ⚠️ 改 R<n>

# 阈值常量 (Pitfall #91 余量警戒线 + 48KB 早闸口 + 50KB 硬阈值)
EARLY_GATE = 49152   # 48KB 早闸口 (chars 口径, 非 bytes)
HARD = 51200         # 50KB 硬阈值
MARGIN_WARN = 1500   # 1500 chars 余量警戒线 (Pitfall #91)

# 1. 读 entry (外置字面量, Pitfall #88 方案 b)
with open(ENTRY_FILE, encoding='utf-8') as f:
    new_entry = f.read().rstrip('\n')

# 2. ground truth + chunks
conn = sqlite3.connect(TASK_DB)
desc = conn.execute('SELECT description FROM tasks WHERE id=?', (TASK_ID,)).fetchone()[0]
spans = [m.start() for m in re.finditer(r'(?m)^\[R\d+ ', desc)]
chunks = [desc[a:b] for a,b in zip(spans, spans[1:]+[len(desc)])]
last_r = int(re.match(r'\[R(\d+) ', chunks[-1]).group(1))
new_r = last_r + 1
expected_r = int(re.match(r'\[R(\d+) ', new_entry).group(1))
assert expected_r == new_r, 'R号不一致 expected=' + str(expected_r) + ' got=' + str(new_r)
assert new_r == EXPECTED_NEW_R, 'EXPECTED_NEW_R 不一致 expected=' + str(EXPECTED_NEW_R) + ' got=' + str(new_r)

# 3. 投影 (Pitfall #90 正解: proj_no_drop 公式直接算, 无参数错位)
proj_no_drop = sum(len(c) for c in chunks) + len(new_entry) + 2

# 4. 4-tier drop 决策 (Pitfall #91 余量警戒线子阈值)
drop_n = 0
if proj_no_drop >= HARD:
    drop_n = max(2, (proj_no_drop - HARD) // 4000 + 2)
elif proj_no_drop >= EARLY_GATE:
    drop_n = 1
else:
    margin_pre = EARLY_GATE - proj_no_drop
    if margin_pre < MARGIN_WARN:
        drop_n = 1  # 警戒线下也压 1 条 (R534 实证未触发此分支)

# 5. drop chunks[0] 按位置 (Pitfall #84 R478 序 discipline)
if drop_n > 0:
    chunks = chunks[drop_n:]

# 6. 重组
new_desc = '\n\n'.join(chunks) + '\n\n' + new_entry + '\n'
new_proj = len(new_desc)
margin = EARLY_GATE - new_proj

# 7. 写回 sqlite3
conn.execute('UPDATE tasks SET description=? WHERE id=?', (new_desc, TASK_ID))
conn.commit()
conn.close()

# 8. 报告 (拼接模式, 无 f-string 反斜杠, Pitfall #93 防御)
print('OK new_R=' + str(new_r) + ' drop_n=' + str(drop_n) + ' desc=' + str(new_proj) + ' margin=' + str(margin))
print('chunks_after=' + str(len(chunks) + 1) + ' first_chunk=' + (chunks[0][:60] if chunks else 'NONE').replace(chr(10), ' '))
print('new_entry_head=' + new_entry[:60].replace(chr(10), ' '))
