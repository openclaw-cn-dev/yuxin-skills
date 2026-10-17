#!/usr/bin/env python3
# TODO(tech-debt): 改由 Claude Code/Codex 重写 — 初版由宽博士心跳 #N+137 (2026-09-28) 落地
# N+158/N+160 镜像漂移审计 + 同步 + N+143 路径审计,一条命令完成。
# 背景(pitfall-N+160): 心跳 #N+137 误用 `diff dirA dirB`(内容 diff),719 个内容行被当文件名,
# shutil.copy2 崩溃 — N+153"必须复制粘贴代码块"对审计命令同样适用。
# 用法: python3 /Users/hua/.hermes/skills/quant/quantitative-research/scripts/mirror_audit_sync.py
import os, re, shutil, subprocess

MAIN = '/Users/hua/.hermes/skills/quant/quantitative-research'
REFD = MAIN + '/references'
MIRROR = '/Users/hua/.hermes/profiles/quant/skills/quantitative-research/references'

# ---- 1) N+143 路径审计: SKILL.md 引用的 references 必须存在于主位置 ----
sk_path = os.path.join(MAIN, 'SKILL.md')
sk = open(sk_path, encoding='utf-8').read()
fails = [f for f in sorted(set(re.findall(r'references/([A-Za-z0-9_+.\-]+\.md)', sk)))
         if not os.path.exists(os.path.join(REFD, f))]
print('AUDIT_PATH:', len(fails), fails if fails else 'PASS')

# ---- 2) N+158 镜像漂移: diff -rq 解析 "Only in" 行(禁止裸 diff 内容 diff, N+160) ----
if not os.path.isdir(MIRROR):
    print('MIRROR: not present, skip drift check')
else:
    r = subprocess.run(['diff', '-rq', REFD, MIRROR], capture_output=True, text=True)
    mirror_only, main_only = [], 0
    for line in r.stdout.splitlines():
        if not line.startswith('Only in '):
            continue
        path_part, _, name = line[len('Only in '):].partition(': ')
        path_norm = os.path.normpath(path_part.strip())
        if not name:
            continue
        if path_norm == os.path.normpath(MIRROR):
            mirror_only.append(name)
        elif path_norm == os.path.normpath(REFD):
            main_only += 1
    print('MIRROR_ONLY files:', len(mirror_only))
    for fn in sorted(mirror_only):
        src, dst = os.path.join(MIRROR, fn), os.path.join(REFD, fn)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            print('SYNCED mirror->main:', fn)
        else:
            print('SKIP non-file:', fn)
    print('MAIN_ONLY count (normal — new files land in main first):', main_only)
    print('DRIFT:', 'CLEARED' if not mirror_only else 'PARTIAL — rerun script')

# ---- 3) 终审复核 ----
sk = open(sk_path, encoding='utf-8').read()
fails2 = [f for f in sorted(set(re.findall(r'references/([A-Za-z0-9_+.\-]+\.md)', sk)))
          if not os.path.exists(os.path.join(REFD, f))]
print('FINAL AUDIT_PATH:', len(fails2), fails2 if fails2 else 'PASS')
