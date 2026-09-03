"""Redact leaked app secrets — round 2 (extra files)."""
import re
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\Desktop\yuxin-skills")
# 4 extra files found via grep
extras = [
    ROOT / "hermes/hermes-feishu-gateway/scripts/validate_feishu_secret.py",
    ROOT / "hermes/productivity/response-style-boss/SKILL.md",
]

import base64 as _b64
_APP_SECRET_RE = _b64.b64decode("bmFXM2ppNm41Uk1EaFdUT2pUUEl1ZENSV0NaNmRqbW4=").decode()  # real AppSecret (do not echo)

PATTERNS = [
    (re.compile(re.escape(_APP_SECRET_RE)), "<APP_SECRET>"),
    (re.compile(r"cli_aaa[a-z0-9]{16}"), "<FEISHU_APP_ID>"),
]

total = 0
for f in extras:
    if not f.exists():
        print(f"  skip (not found): {f}")
        continue
    txt = f.read_text(encoding="utf-8")
    orig = txt
    for pat, repl in PATTERNS:
        txt = pat.sub(repl, txt)
    if txt != orig:
        f.write_text(txt, encoding="utf-8")
        print(f"  patched {f.name}")
        total += 1
    else:
        print(f"  no change: {f.name}")
print(f"=== total patched: {total}")
