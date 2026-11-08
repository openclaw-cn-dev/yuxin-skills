"""Inject a new LLM key into ONE profile's .env, preserving all other lines.

Single-profile surgical edit (complements inject_key_to_profiles.py which
targets 4 fixed profiles by name). Use this when:
  - You have just ONE profile whose key needs updating
  - You don't want to clobber other profiles
  - The .env already has FEISHU_* and other settings you want to keep
  - You want to see before/after and a masked verification dump

The key is passed as a positional argv — NOT embedded in source — to avoid
LLM-channel secret redaction. If you got the key from a write_file / cat
echo channel, you've probably already lost the last 100+ chars. Always
verify with `od -c <env_path> | tail` after running.

Usage:
    python inject_key_to_single_profile.py <profile_name> <new_key>
    # e.g.
    python inject_key_to_single_profile.py boss-control sk-api-...do3-w
"""
import os
import re
import sys

if len(sys.argv) != 3:
    print("Usage: python inject_key_to_single_profile.py <profile_name> <new_key>")
    sys.exit(1)

profile = sys.argv[1]
new_key = sys.argv[2].strip()

# Sanity: not a truncated/reducted value
if len(new_key) < 50:
    print(f"ERROR: key length {len(new_key)} chars is suspiciously short")
    print("       (redacted values come out ~22 chars; real keys are 108/120/126+)")
    sys.exit(1)

env_path = (
    f"C:\\Users\\Administrator\\AppData\\Local\\hermes\\profiles\\{profile}\\.env"
)
if not os.path.exists(env_path):
    print(f"ERROR: {env_path} does not exist")
    sys.exit(1)

# Read existing
with open(env_path, "rb") as f:
    raw = f.read().decode("utf-8")

# Walk lines, replace ANTHROPIC_API_KEY and MINIMAX_CN_API_KEY values
target_vars = {"ANTHROPIC_API_KEY", "MINIMAX_CN_API_KEY"}
replaced = []
new_lines = []
for line in raw.splitlines(keepends=False):
    m = re.match(r"^([A-Z_]+)=(.*)$", line)
    if m and m.group(1) in target_vars:
        new_lines.append(f"{m.group(1)}={new_key}")
        replaced.append(m.group(1))
    else:
        new_lines.append(line)

# If neither var was present, append both at the end
if not replaced:
    print(f"WARN: {profile} .env had no ANTHROPIC_API_KEY or MINIMAX_CN_API_KEY; appending both")
    new_lines.append("ANTHROPIC_API_KEY=***    new_lines.append("MINIMAX_CN_API_KEY=***    replaced = ["ANTHROPIC_API_KEY", "MINIMAX_CN_API_KEY"]

# Write back (preserve trailing newline if input had one)
trailing_nl = raw.endswith("\n")
with open(env_path, "wb") as f:
    f.write("\n".join(new_lines).encode("utf-8") + (b"\n" if trailing_nl else b""))

# Verify
with open(env_path, "rb") as f:
    verify = f.read().decode("utf-8")

print(f"profile:   {profile}")
print(f"replaced:  {sorted(replaced)}")
print(f"key len:   {len(new_key)} chars")
print(f"file size: {len(verify)} bytes (was {len(raw)} bytes)")
print()
print("=== masked dump (FEISHU_*, API_KEY, APP_SECRET lines) ===")
for line in verify.splitlines():
    if "=" in line and any(
        s in line for s in ("API_KEY", "APP_SECRET", "APP_ID", "FEISHU_")
    ):
        k, _, v = line.partition("=")
        if len(v) > 8:
            print(f"  {k}={v[:4]}...{v[-2:]}  ({len(v)} chars)")
        else:
            print(f"  {k}={v}")
print()
print("Next: hermes gateway stop -p <profile>  (NOT --all — that kills siblings)")
print("      then: hermes chat -p <profile> -q 'hi'  to verify LLM 200")
print("      then: hermes gateway run -p <profile>")
