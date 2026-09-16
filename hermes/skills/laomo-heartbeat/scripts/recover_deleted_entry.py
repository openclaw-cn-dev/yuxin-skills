#!/usr/bin/env python3
# 恢复被 writer cron 未归档删除的 task#11 desc R 条目（R520/R525/R521 三例验证配方）。
# 用法: cp 到 /tmp，改 CONFIG 后运行。全部断言通过才落库，任一失败即停零写入。
# 档案: references/r520-unarchived-deletion.md + references/r521-unarchived-deletion.md (laomo-heartbeat skill)
#
# ⚠️ R544 教训（R521 例实锤）：恢复条绝不能先 tail-append 进 desc 再走 write_round.py 工具链——
#   write_round.py 的 last_r = 物理末位 chunk 的编号（非 max 编号），tail-append 后 chunks[-1]=恢复条
#   → R 断言 FATAL「期望 522, 得到 544」空转一轮。本脚本 step 5 的时序回插（插在 INSERT_BEFORE 前）
#   必须发生在任何 write_round/direct_prune_write 调用之前。手动流程同守。
#
# 📌 提取源双通道（R521 例新增）：原文可能存于 messages.content 列，也可能只存于 messages.tool_calls
#   列的 write_file arguments JSON 内（writer session 走 /tmp 落盘路径）。EXTRACT_COL 选 'content'
#   或 'tool_calls'；tool_calls 路径解析 function[].arguments JSON 取 content 字段。
import sqlite3, re, json, sys

# ---------- CONFIG (每例改这四处) ----------
STATE_DB = '/Users/hua/.hermes/state.db'
VICTIM_R = '525'            # 被删的 R 编号
STATE_ROWID = 633436        # 含被删条全文的 messages rowid (先 LIKE 探测确认)
INSERT_BEFORE = '526'       # 时序回插位置: 插在该号之前 (下一个编号)
EXTRACT_COL = 'content'     # 'content' = messages.content 列; 'tool_calls' = write_file arguments JSON
# ***SECRET***

DB = '/Users/hua/.hermes/tasks.db'
ARCH = '/Users/hua/.hermes/profiles/laomo/evolution/task-11-log-archive.md'
NEW_ENTRY = None  # 可选: 本轮新 entry 全文(含尾标 keep_in_progress)。None=仅恢复不写新条。

def log(s): print(s, flush=True)

# 1) 探测 rowid (若 STATE_ROWID 未定, 手动跑这段; 双列都试):
#    sqlite3.connect('file:%s?mode=ro' % STATE_DB, uri=True)
#    conn.execute("SELECT rowid, session_id FROM messages WHERE content LIKE '%[R525 %' LIMIT 5")
#    conn.execute("SELECT rowid, session_id FROM messages WHERE tool_calls LIKE '%[R525 %' LIMIT 5")

# 2) 提取原文 (双通道)
sc = sqlite3.connect('file:%s?mode=ro' % STATE_DB, uri=True)
raw = sc.execute('SELECT %s FROM messages WHERE rowid=?' % EXTRACT_COL, (STATE_ROWID,)).fetchone()
assert raw, 'rowid %s not found' % STATE_ROWID
text = raw[0]
if EXTRACT_COL == 'tool_calls':
    arr = json.loads(text)
    text = ''
    for call in (arr if isinstance(arr, list) else []):
        fn = call.get('function', {})
        try:
            a = json.loads(fn.get('arguments', ''))
        except Exception:
            continue
        c = a.get('content', '')
        if c.startswith('[R%s ' % VICTIM_R):
            text = c
            break
    assert text, 'victim entry not found in any write_file arguments of rowid %s' % STATE_ROWID
    entry = text.rstrip() + '\n'
else:
    try:
        obj = json.loads(text); text = obj.get('output') or obj.get('content') or str(obj)
    except Exception:
        pass
    i = text.find('[R%s ' % VICTIM_R)
    assert i >= 0, 'victim marker not in rowid %s' % STATE_ROWID
    rest = text[i:]
    m = re.search(r'\n---\s*R\d+|\n\[R\d+', rest)
    entry = (rest[:m.start()] if m else rest).rstrip() + '\n'
assert entry.startswith('[R%s ' % VICTIM_R), 'head mismatch: %r' % entry[:60]
assert 'keep_in_progress' in entry[-200:], 'victim tail missing keep_in_progress'
log('extracted len=%d head=%r' % (len(entry), entry[:60]))

# 3) 读当前库态
conn = sqlite3.connect(DB)
desc = conn.execute('SELECT description FROM tasks WHERE id=11').fetchone()[0]
markers = list(re.finditer(r'(?m)^\[R(\d+)', desc))
nums = [int(x.group(1)) for x in markers]
assert nums.count(int(VICTIM_R)) == 0, 'victim already in db?!'
assert int(INSERT_BEFORE) in nums, 'insert anchor %s not in db' % INSERT_BEFORE
log('pre entries=%s len=%d' % (nums, len(desc)))

# 4) archive 注记 + 原文 (行首锚定断言零预存)
atext = open(ARCH, encoding='utf-8', errors='replace').read()
assert len(re.findall(r'\[R%s(?!\d)' % VICTIM_R, atext)) == 0, 'victim already archived — verify manually'
with open(ARCH, 'a', encoding='utf-8') as f:
    f.write('\n[R%s-recovered 恢复归档: writer cron 未归档删除, 全文自 state.db rowid=%s 提取 (R387 配方)]\n' % (VICTIM_R, STATE_ROWID))
    f.write(entry)
log('archived ok')

# 5) 时序回插
mk = [x for x in markers if x.group(1) == INSERT_BEFORE][0]
new_desc = desc[:mk.start()] + entry + desc[mk.start():]
new_desc = re.sub(r'\n+\[R', '\n[R', new_desc)  # 归一换行

# 6) 可选追加新条 + 剪枝保闸
LIMIT, TARGET = 49152, 48952  # TARGET 保守于 LIMIT (R527 教训: 勿赌临界)
def es_of(d):
    ms = list(re.finditer(r'(?m)^\[R(\d+)', d))
    return [(int(x.group(1)), x.start(), ms[j+1].start() if j+1 < len(ms) else len(d)) for j, x in enumerate(ms)]
pruned = []
cand = new_desc
if NEW_ENTRY:
    cand = cand.rstrip('\n') + '\n' + NEW_ENTRY.strip() + '\n'
proj = len(cand.rstrip('\n')) + 1
while proj > TARGET:
    es = es_of(cand)
    if not es or len(pruned) >= 4:
        sys.exit('PRUNE FAIL pruned=%s proj=%d' % (pruned, proj))
    n, s, e = es[0]
    assert n != int(VICTIM_R), 'refusing to prune recovered entry'
    with open(ARCH, 'a', encoding='utf-8') as f:
        f.write('\n[R%d-pruned 剪枝归档 (canonical 先 archive 后 drop)]\n' % n)
        f.write(cand[s:e].rstrip() + '\n')
    cand = cand[:s] + cand[e:]
    pruned.append(n)
    proj = len(cand.rstrip('\n')) + 1
final = cand
log('pruned=%s proj=%d' % (pruned, proj))

# 7) pre 断言
fe = [int(x.group(1)) for x in re.finditer(r'(?m)^\[R(\d+)', final)]
assert len(fe) == len(set(fe)), 'dupes: %s' % fe
assert fe.count(int(VICTIM_R)) == 1, 'victim count wrong'
ii = fe.index(int(VICTIM_R))
if int(INSERT_BEFORE) in fe:
    assert ii < fe.index(int(INSERT_BEFORE)), 'chronology broken'
if NEW_ENTRY:
    assert fe[-1] == int(re.match(r'\[R(\d+)', NEW_ENTRY).group(1)), 'new entry not at tail'
assert len(final) < LIMIT
log('pre-write asserts OK: %s len=%d' % (fe, len(final)))

# 8) 原子写回 + 刷锚
conn.execute("UPDATE tasks SET description=?, status='in_progress', updated_at=CURRENT_TIMESTAMP WHERE id=11", (final,))
conn.commit()
back = conn.execute('SELECT description, updated_at FROM tasks WHERE id=11').fetchone()
be = [int(x.group(1)) for x in re.finditer(r'(?m)^\[R(\d+)', back[0])]
assert be == fe, 'post mismatch'
log('POST OK entries=%s len=%d updated_at=%s' % (be, len(back[0]), back[1]))
log('DONE — 记得: 库态自述与实际执行一致 (剪枝 N/号以实际为准 scoped 回填修正)')
