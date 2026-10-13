#!/usr/bin/env python
"""
红化脚本:把 git grep 命令字面量里的 naW3ji + cli_aaa 字面量替换成占位符
避免 GitHub secret scanner 误判
1013 跑:codex-skills/hermes-skills-backup/references/ 4 文件
"""
import re
from pathlib import Path

REPO = Path(r"C:\Users\Administrator\Desktop\yuxin-skills")
TARGETS = [
    "codex-skills/hermes-skills-backup/references/2026-08-22-evolution-run.md",
    "codex-skills/hermes-skills-backup/references/2026-08-31-evolution-run.md",
    "codex-skills/hermes-skills-backup/references/2026-09-01-evolution-run.md",
    "codex-skills/hermes-skills-backup/references/full-skill-archive.md",
]
APP_SECRET = "naW3ji6n5RMDhWTOjTPIudCRWCZ6djmn"
APP_SECRET_REDACTED = "naW***i6n5"
APPID_RE = re.compile(r"cli_aaa[a-z0-9]{12,18}")
APPID_REDACTED = "cli_aaa***"

total = 0
for rel in TARGETS:
    p = REPO / rel
    if not p.exists():
        print(f"SKIP {rel}")
        continue
    txt = p.read_text(encoding='utf-8')
    orig = txt
    # 1) AppSecret 字面量
    n1 = txt.count(APP_SECRET)
    txt = txt.replace(APP_SECRET, APP_SECRET_REDACTED)
    # 2) cli_aaa AppID 字面量(12-18 字符之间)
    matches = APPID_RE.findall(txt)
    n2 = len(matches)
    for m in set(matches):
        txt = txt.replace(m, APPID_REDACTED)
    if txt != orig:
        p.write_text(txt, encoding='utf-8')
        print(f"OK {rel}  AppSecret={n1}  AppID={n2}")
        total += n1 + n2
    else:
        print(f"NOOP {rel}")
print(f"\nTOTAL replacements: {total}")
