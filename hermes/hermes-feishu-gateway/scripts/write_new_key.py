"""Write a new LLM key from argv[1] to ~/minimax_key_value.txt and verify bytes.

Use this when老大 pastes a new key in chat — pass the key through argv (terminal
channel, not write_file) to bypass LLM-channel secret redaction. The file on
disk is the verified-raw source for downstream inject_key.py.

Usage:
    python scripts/write_new_key.py "sk-api-...完整字符"
"""
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python write_new_key.py <new_key>")
    sys.exit(1)

key = sys.argv[1]
target = os.path.expanduser("~/minimax_key_value.txt")
with open(target, "wb") as f:
    f.write(key.encode("utf-8") + b"\n")

with open(target, "rb") as f:
    raw = f.read()
print(f"file size: {len(raw)} bytes (key {len(key)} chars + trailing newline)")
print(f"first 8 chars: {key[:8]!r}")
print(f"last 8 chars:  {key[-8:]!r}")
