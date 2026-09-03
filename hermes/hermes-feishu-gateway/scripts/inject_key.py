"""Inject a new LLM key into ONE profile's .env, replacing both ANTHROPIC_API_KEY
and MINIMAX_CN_API_KEY while preserving all other lines (FEISHU_*, etc.) intact.

Args:
    argv[1] = new key (avoids LLM-channel redaction; passed through terminal, not
              write_file)
    argv[2] (optional) = profile name (default: boss-control)

Usage:
    python scripts/inject_key.py "sk-api-...完整"
    python scripts/inject_key.py "sk-api-...完整" agent-sales

Does NOT hardcode key length — warns only if < 50 chars (truncation signal).
Does NOT hardcode profile name — defaults to boss-control, override via argv[2].
"""
import os
import re
import sys

if len(sys.argv) < 2:
    print("Usage: python inject_key.py <new_key> [profile_name]")
    sys.exit(1)

new_key = sys.argv[1].strip()
if len(new_key) < 50:
    print(f"WARN: key length {len(new_key)} is suspiciously short — likely truncated")
    sys.exit(1)

profile = sys.argv[2] if len(sys.argv) > 2 else "boss-control"
env_path = (
    Path.home() / "AppData" / "Local" / "hermes" / "profiles" / profile / ".env"
)
if not env_path.exists():
    print(f"ERROR: {env_path} not found")
    sys.exit(1)

# 1. Read existing .env
raw = env_path.read_text(encoding="utf-8")

# 2. Walk lines, replace ANTHROPIC_API_KEY and MINIMAX_CN_API_KEY values
replaced = set()
new_lines = []
for line in raw.splitlines():
    m = re.match(r"^(ANTHROPIC_API_KEY|MINIMAX_CN_API_KEY)=(.*)$", line)
    if m:
        new_lines.append(f"{m.group(1)}={new_key}")
        replaced.add(m.group(1))
    else:
        new_lines.append(line)

# 3. If neither was present, append both
if not replaced:
    print("WARN: no existing ANTHROPIC_API_KEY / MINIMAX_CN_API_KEY found, appending both")
    new_lines.append(f"ANTHROPIC_API_KEY={new_key}")
    new_lines.append(f"MINIMAX_CN_API_KEY={new_key}")
    replaced = {"ANTHROPIC_API_KEY", "MINIMAX_CN_API_KEY"}

# 4. Write back (preserve trailing newline if present)
trailing_nl = raw.endswith("\n")
env_path.write_bytes(
    ("\n".join(new_lines) + ("\n" if trailing_nl else "")).encode("utf-8")
)

# 5. Verify + mask dump
verify = env_path.read_text(encoding="utf-8")
print(f"\nreplaced keys: {sorted(replaced)}")
print(f".env size: {len(verify)} bytes (was {len(raw)} bytes)\n")
print("=== masked dump ===")
for line in verify.splitlines():
    if "=" in line and any(s in line for s in ("API_KEY", "APP_SECRET", "APP_ID")):
        k, _, v = line.partition("=")
        if len(v) > 8:
            print(f"{k}={v[:4]}...{v[-2:]}  ({len(v)} chars)")
        else:
            print(f"{k}={v}")
    else:
        print(line)
