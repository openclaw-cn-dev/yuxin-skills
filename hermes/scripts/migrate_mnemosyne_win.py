#!/usr/bin/env python3
"""旺财 Windows：迁移 MEMORY.md 到 Mnemosyne（玉芬提供 2026-08-18）
用法：python migrate_mnemosyne_win.py [MEMORY.md路径]
不传参数则自动探测常见位置。
"""
import os, sys, re, shutil
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get('HERMES_HOME', r'C:\Users\Administrator\.hermes'))


def split_sections(text):
    parts = re.split(r'\n?\s*§\s*\n?', text)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p.startswith('# '):
            continue
        out.append(p)
    return out


def classify_source(text):
    if any(k in text for k in ['名字', '角色', 'Profile', '身份', '我是']):
        return 'identity'
    if any(k in text for k in ['偏好', '喜欢', '优先', '习惯', '不追求', '关注']):
        return 'preference'
    if any(k in text for k in ['端口', 'PID', 'Gateway', '模型', 'API_KEY', 'cron',
                               'launchd', 'Ollama', 'Docker', 'WebSocket', '心跳', '任务计划']):
        return 'environment'
    if any(k in text for k in ['华哥', '玉芬', '同事', '团队', '上级', '汇报', '共享']):
        return 'relationship'
    return 'project'


def main():
    # 探测 MEMORY.md 位置
    candidates = [
        HERMES_HOME / 'memories' / 'MEMORY.md',
        HERMES_HOME / 'profiles' / 'wangcai' / 'memories' / 'MEMORY.md',
        HERMES_HOME / 'profiles' / 'default' / 'memories' / 'MEMORY.md',
    ]
    mem = None
    if len(sys.argv) > 1:
        mem = Path(sys.argv[1])
    else:
        for c in candidates:
            if c.exists():
                mem = c
                break
    if mem is None or not mem.exists():
        print('找不到 MEMORY.md。请手动指定：python migrate_mnemosyne_win.py <MEMORY.md完整路径>')
        return

    # 环境变量必须在 import mnemosyne 之前设置
    os.environ['MNEMOSYNE_DATA_DIR'] = str(HERMES_HOME / 'mnemosyne' / 'data')

    import mnemosyne

    text = mem.read_text(encoding='utf-8')
    sections = split_sections(text)
    print(f'[{mem}] 共 {len(sections)} 段，开始迁移...')

    stored = 0
    for sec in sections:
        if len(sec) < 3:
            continue
        src = classify_source(sec)
        try:
            mid = mnemosyne.remember(sec, source=src, importance=0.8,
                                     scope='global', trust_tier='IMPORTED')
            if mid:
                stored += 1
                print(f'  OK [{src:12s}] {sec[:40].replace(chr(10), " ")}')
            else:
                print(f'  SKIP(被过滤) {sec[:40]}')
        except Exception as e:
            print(f'  FAIL {e} | {sec[:40]}')

    # 备份 + 写占位符
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = mem.with_name(mem.name + f'.bak.mnemosyne_{ts}')
    shutil.copy2(mem, bak)
    placeholder = (f'# MEMORY (L1 已迁移)\n\n'
                   f'持久记忆已迁移至 Mnemosyne（{datetime.now().strftime("%Y-%m-%d")} 完成）。\n\n'
                   f'- Mnemosyne 为 primary，检索方式 mnemosyne_recall\n'
                   f'- 旧版备份: {bak.name}\n')
    mem.write_text(placeholder, encoding='utf-8')

    print(f'\n完成: 存 {stored} 条，备份 → {bak.name}')


if __name__ == '__main__':
    main()
