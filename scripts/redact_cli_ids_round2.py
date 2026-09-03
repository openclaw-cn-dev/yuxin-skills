"""Iterate git grep results to catch all remaining cli_aaa IDs."""
import re
import subprocess
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\Desktop\yuxin-skills")
CLI_RE = re.compile(r"cli_aaa[a-z0-9]{12,18}")

r = subprocess.run(
    ["git", "-C", str(ROOT), "grep", "-lnE", r"cli_aaa[a-z0-9]{12,18}"],
    capture_output=True, text=True)

files = [ROOT / line.strip().replace("/", "\\")
         for line in r.stdout.strip().splitlines() if line.strip()]

print(f"files to patch: {len(files)}")
for f in files:
    if not f.exists():
        print(f"  SKIP (missing): {f}")
        continue
    txt = f.read_text(encoding="utf-8", errors="ignore")
    matches = CLI_RE.findall(txt)
    if not matches:
        continue
    txt = CLI_RE.sub("<FEISHU_APP_ID>", txt)
    f.write_text(txt, encoding="utf-8")
    print(f"  patched {f.relative_to(ROOT)} ({len(matches)} subs)")

# Final check
r2 = subprocess.run(
    ["git", "-C", str(ROOT), "grep", "-nE", r"cli_aaa[a-z0-9]{12,18}"],
    capture_output=True, text=True)
print("---residual leaks---")
print(r2.stdout if r2.stdout.strip() else "(none)")
