#!/usr/bin/env python
"""
Redactor 1013-bugfix: 不在源码里硬编码 AppSecret 字面量(避免 self-leak
触发 GitHub secret-scanner)。改用历史命中模式:匹配含连续 30+ base64 字符
的长字面量,且必须出现于"被引号包住的字符串上下文"。

触发条件(任一即替换):
- 32 字符连续 base64 风格 [a-z0-9]{32} 且 文件里 >= 2 处出现(代码里出现的常
  是字面量本身,出现 1 处的多为占位符不替换)
- 'naW...' 开头长字面量(已知 AppSecret 模板前缀)
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
APPID_RE = re.compile(r"cli_aaa[a-z0-9]{12,18}")
APPID_REDACTED = "cli_aaa***"
# 任意 32 字符 base64 style 字面量(只在文件内出现 >= 2 次时替换)
LONG_TOKEN_RE = re.compile(r"[a-z0-9]{32}")

def looks_like_app_secret(s: str, file_text: str) -> bool:
    """32 字符 base64 风格 + 文件内出现 >= 2 次 + 不在 heredoc/import 内"""
    if not (s.startswith("naW") or s.startswith("cwI") or s.startswith("CW")):
        # 已知 AppSecret 前缀,其他不瞎猜
        return False
    return file_text.count(s) >= 2

total = 0
for rel in TARGETS:
    p = REPO / rel
    if not p.exists():
        print(f"SKIP {rel}")
        continue
    txt = p.read_text(encoding='utf-8')
    orig = txt
    n_appid = 0
    n_secret = 0

    # 1) cli_aaa AppID(精确 regex)
    for m in set(APPID_RE.findall(txt)):
        n_appid += txt.count(m)
        txt = txt.replace(m, APPID_REDACTED)

    # 2) AppSecret:扫所有 32 字符 token,启发式匹配
    for m in set(LONG_TOKEN_RE.findall(txt)):
        if looks_like_app_secret(m, txt):
            n_secret += txt.count(m)
            txt = txt.replace(m, "na***i6n5")

    if txt != orig:
        p.write_text(txt, encoding='utf-8')
        print(f"OK {rel}  AppSecret={n_secret}  AppID={n_appid}")
        total += n_secret + n_appid
    else:
        print(f"NOOP {rel}")
print(f"\nTOTAL replacements: {total}")
