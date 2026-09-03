"""Extract the last MINIMAX_CN_API_KEY=*** from hermes default .env (binary-safe).

Hermes stores the user key on the last line of ~/.hermes/.env as
'MINIMAX_CN_API_KEY=***' (120 chars). This script reads the file as bytes
and slices exactly 120 bytes after the marker — avoids all regex/line-end
issues from \r\n / multiline / trailing comment.

Writes the key to ~/minimax_key_value.txt for downstream injection.

Usage:
    python scripts/extract_minimax_key.py
"""
import sys
from pathlib import Path

ENV = Path.home() / "AppData" / "Local" / "hermes" / ".env"
OUT = Path.home() / "minimax_key_value.txt"
MARKER = b"MINIMAX_CN_API_KEY=***"  # 19 bytes
KEY_LEN = 120

data = ENV.read_bytes()
idx = data.rfind(MARKER)
if idx < 0:
    print(f"ERROR: marker not found in {ENV}")
    sys.exit(1)

start = idx + len(MARKER)
key_bytes = data[start:start + KEY_LEN]
if len(key_bytes) < KEY_LEN:
    print(f"ERROR: only {len(key_bytes)} bytes after marker (need {KEY_LEN})")
    sys.exit(1)

OUT.write_bytes(key_bytes)
print(f"Extracted {len(key_bytes)} bytes to {OUT}")
print(f"  head: {key_bytes[:8].decode('utf-8', 'replace')}")
print(f"  tail: {key_bytes[-6:].decode('utf-8', 'replace')}")
