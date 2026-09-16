# -*- coding: utf-8 -*-
# r537_rollback.py — R537 hourly silent round R<n> entry 回滚自救范本
# Pitfall #96 (R537 新增): 首次回滚自救 SOP 模板
# R537 实战: 第一次写 2080 chars 撞 margin 7 chars 触发回滚, 恢复 desc=47060/last_r=536/chunks=19
#
# 使用方法:
#   1. 在 hourly silent round write_post_check margin < 1500 chars 时触发
#   2. 跑这个脚本: python3 r537_rollback.py
#   3. 验证 desc/last_r/chunks 三元组恢复到 pre-write 状态
#   4. 压缩重写 entry 到 <= 1200 chars, 重新走 r537_direct_write.py
#
# 注意事项:
#   - 只回滚"最后一个 chunk" (chunks[-1]), 假设它是本轮刚写的 R<n>
#   - 如果 sqlite3 中 desc 有多个连续坏 chunk, 需要循环跑这个脚本
#   - 回滚后必跑 r531_ground_truth_probe.py 验证 last_r 恢复正确
import sqlite3, re, sys

conn = sqlite3.connect('/Users/hua/.hermes/tasks.db')
desc = conn.execute('SELECT description FROM tasks WHERE id=11').fetchone()[0]

# 解析 chunks
spans = [m.start() for m in re.finditer(r'(?m)^\[R\d+ ', desc)]
chunks = [desc[a:b] for a,b in zip(spans, spans[1:]+[len(desc)])]

print('=== ROLLBACK PRE-CHECK ===')
print('current desc = ' + str(len(desc)) + ' chars')
print('current chunks = ' + str(len(chunks)))
if len(chunks) < 1:
    print('!!! ERROR: no chunks to rollback')
    sys.exit(1)
last_chunk = chunks[-1]
last_r_pre = int(re.match(r'\[R(\d+) ', last_chunk).group(1))
print('last chunk head = ' + last_chunk[:60])
print('last_r_pre = ' + str(last_r_pre))

# 计算回滚后 desc (删除最后一个 chunk + rstrip)
new_desc = desc[:desc.rfind(last_chunk)].rstrip('\n').rstrip()
print('rollback desc = ' + str(len(new_desc)) + ' chars')

# 写入
conn.execute('UPDATE tasks SET description = ? WHERE id = 11', (new_desc,))
conn.commit()

# 复核
desc_post = conn.execute('SELECT description FROM tasks WHERE id=11').fetchone()[0]
spans_post = [m.start() for m in re.finditer(r'(?m)^\[R\d+ ', desc_post)]
chunks_post = [desc_post[a:b] for a,b in zip(spans_post, spans_post[1:]+[len(desc_post)])]
last_r_post = int(re.match(r'\[R(\d+) ', chunks_post[-1]).group(1))

print('=== ROLLBACK POST-CHECK ===')
print('rollback desc (post) = ' + str(len(desc_post)) + ' chars')
print('rollback chunks (post) = ' + str(len(chunks_post)))
print('rollback last_r (post) = ' + str(last_r_post) + ' (expected ' + str(last_r_pre) + ')')
print('rollback first_chunk_head = ' + chunks_post[0][:60])
print('rollback last_chunk_head = ' + chunks_post[-1][:60])

if last_r_post != last_r_pre:
    print('!!! ERROR: rollback failed, last_r mismatch')
    sys.exit(1)
else:
    print('=== ROLLBACK SUCCESS ===')
    print('desc 恢复: ' + str(len(desc)) + ' -> ' + str(len(desc_post)) + ' chars')
    print('chunks 恢复: ' + str(len(chunks)) + ' -> ' + str(len(chunks_post)))
    print('last_r 恢复: ' + str(last_r_pre) + ' (未变)')
    print()
    print('下一步: 压缩 entry 到 <= 1200 chars, 重新跑 r537_direct_write.py')

conn.close()
