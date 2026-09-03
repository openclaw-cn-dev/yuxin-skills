"""Redact cli_aaa IDs across yuxin-skills. Catches varying lengths (12-18 chars after cli_aaa)."""
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\Desktop\yuxin-skills")

# cli_aaa followed by 12-18 chars (Feishu app IDs vary)
CLI_RE = re.compile(r"cli_aaa[a-z0-9]{12,18}")

# Files known from grep
targets = [
    ROOT / "hermes/daily-cron-architecture/SKILL.md",
    ROOT / "hermes/daily-cron-architecture/references/cron_8am_explosive_v2.md",
    ROOT / "hermes/daily-cron-architecture/references/verified-sources-water-briefing.md",
    ROOT / "hermes/daily-cron-architecture/scripts/feishu_push.py",
    ROOT / "hermes/devops/hermes-secret-handling/scripts/setup_per_profile_env.bat",
    ROOT / "hermes/hermes-feishu-gateway/references/agent-teardown-recipe.md",
    ROOT / "hermes/mlops/chinese-rag-pipeline/SKILL.md",
    ROOT / "hermes/productivity/feishu-open-api/references/api-endpoints-verified.md",
]

total_files = 0
total_subs = 0
for f in targets:
    if not f.exists():
        print(f"  SKIP (missing): {f.relative_to(ROOT)}")
        continue
    txt = f.read_text(encoding="utf-8", errors="ignore")
    orig = txt
    matches = CLI_RE.findall(txt)
    if not matches:
        continue
    txt = CLI_RE.sub("<FEISHU_APP_ID>", txt)
    f.write_text(txt, encoding="utf-8")
    subs = len(matches)
    total_files += 1
    total_subs += subs
    print(f"  patched {f.relative_to(ROOT)} ({subs} subs)")

print(f"\n=== total: {total_files} files, {total_subs} substitutions")
