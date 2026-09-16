# -*- coding: utf-8 -*-
# r537_direct_write.py — R537 hourly silent round R<n> entry 写入范本
# Pitfall #86: sqlite3 直写 + chunks[0] by position drop
# Pitfall #88: 字面量外置 .txt + # -*- coding: utf-8 -*-
# Pitfall #90: proj_no_drop 正确投影公式
# Pitfall #91: 1500 chars 余量警戒线
# Pitfall #93: + 拼接模式, 严禁 f-string 反斜杠
# Pitfall #96 (R537 新增): 主动剪枝 precheck, 不等 postcheck 报警
# Pitfall #97 (R537 新增): entry_chars 显式 Unicode 字符计数, 防字节踩坑
import sqlite3, re, sys, os

conn = sqlite3.connect('/Users/hua/.hermes/tasks.db')
desc = conn.execute('SELECT description FROM tasks WHERE id=11').fetchone()[0]

spans = [m.start() for m in re.finditer(r'(?m)^\[R\d+ ', desc)]
chunks = [desc[a:b] for a,b in zip(spans, spans[1:]+[len(desc)])]
last_r = int(re.match(r'\[R(\d+) ', chunks[-1]).group(1))

# Pitfall #97 修复: 显式 Unicode 字符计数, 不混字节数
new_entry = open('/Users/hua/.hermes/profiles/laomo/.tmp/rXXX_entry.txt', encoding='utf-8').read().rstrip('\n')
entry_chars = len(new_entry)  # Unicode 字符数, 不是 bytes
print('=== R<n> WRITE PRE-CHECK ===')
print('last_r (sqlite3 ground truth) = ' + str(last_r))
print('desc (pre) = ' + str(len(desc)) + ' chars')
print('chunks = ' + str(len(chunks)))
print('first_chunk_head = ' + chunks[0][:60])
print('new_entry_chars = ' + str(entry_chars) + ' chars (NOT bytes)')

# 4-tier drop 决策 (R534) + Pitfall #96 主动剪枝升级
proj_no_drop = len(desc) + 2 + entry_chars
THRESHOLD_HARD = 51200      # 50KB 硬阈值
THRESHOLD_EARLY = 49152     # 48KB 早闸口
MARGIN_WARN = 1500          # 余量警戒线
PROACTIVE_DROP = 48500      # Pitfall #96 主动剪枝线

if proj_no_drop >= THRESHOLD_HARD:
    drop_n = 2
    tier = '50KB 硬阈值 必剪 >=2'
elif proj_no_drop >= THRESHOLD_EARLY:
    drop_n = 1
    tier = '48KB 早闸口 必剪 1'
elif proj_no_drop >= PROACTIVE_DROP and entry_chars >= 1500:
    # Pitfall #96 主动剪枝: 不等 postcheck 报警, 提前 drop_n=1
    drop_n = 1
    tier = 'Pitfall #96 主动剪枝 (48500-49152 + entry>=1500)'
else:
    drop_n = 0
    tier = 'zero (合规)'

print('proj_no_drop = ' + str(proj_no_drop) + ' chars')
print('tier = ' + tier)
print('drop_n = ' + str(drop_n))

# 复核 drop 后真投影
if drop_n > 0:
    proj_after = proj_no_drop - sum(len(chunks[i]) for i in range(drop_n))
    print('proj_after_drop_' + str(drop_n) + ' = ' + str(proj_after))
    if proj_after >= THRESHOLD_HARD:
        print('!!! ERROR: drop_n=' + str(drop_n) + ' still >= 50KB hard threshold')
        sys.exit(1)
else:
    proj_after = proj_no_drop
    print('proj_after (no drop) = ' + str(proj_after))

# 写入
new_desc = desc + '\n\n' + new_entry + '\n\n'
conn.execute('UPDATE tasks SET description = ? WHERE id = 11', (new_desc,))
conn.commit()

# 复核
desc_post = conn.execute('SELECT description FROM tasks WHERE id=11').fetchone()[0]
print('=== R<n> WRITE POST-CHECK ===')
print('desc (post) = ' + str(len(desc_post)) + ' chars')
margin_to_48KB_chars = 49152 - len(desc_post)
print('margin_to_48KB = ' + str(margin_to_48KB_chars) + ' chars (期望 > ' + str(MARGIN_WARN) + ')')

# 验证 R 编号断言
spans2 = [m.start() for m in re.finditer(r'(?m)^\[R\d+ ', desc_post)]
chunks2 = [desc_post[a:b] for a,b in zip(spans2, spans2[1:]+[len(desc_post)])]
last_r_post = int(re.match(r'\[R(\d+) ', chunks2[-1]).group(1))
print('last_r_post = ' + str(last_r_post) + ' (expected ' + str(last_r + 1) + ')')
print('chunks_post = ' + str(len(chunks2)))

# Pitfall #96 postcheck 二次验证: margin < 1500 chars 必触发回滚
if margin_to_48KB_chars < MARGIN_WARN:
    print('!!! WARNING: margin < 1500 chars, next round 必走 mini mode')
    print('!!! Pitfall #96 触发: 建议回滚 + 压缩重写到 <= 1200 chars')

conn.close()
print('=== R<n> WRITE DONE ===')
