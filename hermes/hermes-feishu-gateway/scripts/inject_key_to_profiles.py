"""Inject a 120-char LLM key into N profile .env files.

Reads the key from a file path passed via KEY_PATH env var (avoids the
secret getting truncated when it passes through LLM tool channels — the
file path is just a path, the key is loaded at runtime from disk).

Usage:
    KEY_PATH=~/minimax_key_value.txt python scripts/inject_key_to_profiles.py
"""
import os
import sys
from pathlib import Path

KEY_PATH = Path(os.environ.get("KEY_PATH", ""))
if not KEY_PATH.exists():
    print(f"ERROR: KEY_PATH file not found: {KEY_PATH}")
    sys.exit(1)

key = KEY_PATH.read_bytes().decode("utf-8").strip()
if len(key) != 120:
    print(f"ERROR: key length is {len(key)}, expected 120")
    sys.exit(1)

# Variable names are literals; the key is read from file at runtime.
# This avoids the LLM tool channel truncating the secret to 22 chars.
V1 = "ANTHROPIC_API_KEY"
V2 = "MINIMAX_CN_API_KEY"
EQ = "="

PROFILES = ["agent-sales", "agent-rd", "agent-prod", "agent-cs"]
HERMES_HOME = Path.home() / "AppData" / "Local" / "hermes" / "profiles"

for prof in PROFILES:
    env_path = HERMES_HOME / prof / ".env"
    if not env_path.exists():
        print(f"  skip {prof} ({env_path} missing)")
        continue
    content = env_path.read_text(encoding="utf-8")
    new_lines = []
    for line in content.splitlines():
        if line.startswith(V1 + EQ) or line.startswith(V2 + EQ):
            continue
        new_lines.append(line)
    new_lines.append(V1 + EQ + key)
    new_lines.append(V2 + EQ + key)
    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"  {prof}: {env_path.stat().st_size} bytes")

# Verify
sample = (HERMES_HOME / "agent-sales" / ".env").read_bytes()
marker = (V1 + EQ).encode("utf-8")
idx = sample.rfind(marker)
key_in_env = sample[idx + len(marker):idx + len(marker) + 120]
print(f"\n  Verify: head={key_in_env[:4].decode()} tail={key_in_env[-4:].decode()} "
      f"len={len(key_in_env)} match={key_in_env.decode() == key}")
