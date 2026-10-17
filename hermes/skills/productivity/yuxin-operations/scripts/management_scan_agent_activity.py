#!/usr/bin/env python3
"""8 项扫描第 5 项:按 profile 统计 agent 最近活动与 24h 消息量。
用法: python3 scan_agent_activity.py
注意: 各库 messages.timestamp 单位不统一(秒/毫秒),脚本已自动兼容。
"""
import sqlite3, datetime, glob, os

NOW = datetime.datetime.now()

def query(db):
    conn = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    try:
        ts = conn.execute('SELECT MAX(timestamp) FROM messages').fetchone()[0]
        if not ts: return None, 0
        scale = 1000 if ts > 1e12 else 1
        last = datetime.datetime.fromtimestamp(ts/scale)
        cutoff = int((NOW - datetime.timedelta(days=1)).timestamp()) * scale
        cnt = conn.execute('SELECT COUNT(*) FROM messages WHERE timestamp > ?', (cutoff,)).fetchone()[0]
        return last, cnt
    finally:
        conn.close()

rows = []
db = '/Users/hua/.hermes/state.db'
if os.path.exists(db):
    last, cnt = query(db)
    rows.append(('default', last, cnt))
for p in sorted(glob.glob('/Users/hua/.hermes/profiles/*/state.db')):
    name = p.split('/')[-2]
    if name == 'test': continue
    try:
        last, cnt = query(p)
        rows.append((name, last, cnt))
    except Exception as e:
        rows.append((name, None, f'ERR {e}'))

print(f'{"agent":<12} {"last_msg":<20} {"24h_msgs":<9} 状态')
for name, last, cnt in rows:
    if last is None:
        print(f'{name:<12} {"—":<20} {str(cnt):<9} 无数据')
        continue
    idle = (NOW - last).days
    if idle >= 7:
        st = f'🔴 停摆 {idle} 天 → 唤醒/归档决策'
    elif idle >= 1:
        st = f'🟡 {idle} 天前'
    else:
        st = '✅ 今日活跃' + ('(高频,查重复派单)' if cnt > 1500 else '')
    print(f'{name:<12} {str(last):<20} {str(cnt):<9} {st}')
