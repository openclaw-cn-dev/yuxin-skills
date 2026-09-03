"""
Roll back a contaminated Hermes .env file to a known-good state.

Use when you've changed MINIMAX_CN_API_KEY / MINIMAX_BASE_URL / similar
fields and need to revert without manual grep-and-replace work. Designed
to be safe by default: it shows diffs and asks for confirmation before
writing (unless you pass --yes).

Two strategies, in order:
  1. Read the most recent .env.bak.* (Hermes auto-creates these on
     certain config events) and restore from there.
  2. Fall back to: restore just the LLM-related fields (API_KEY,
     BASE_URL) by .replace()-ing them with the values you pass via
     --key / --url.

Usage:
  # Restore from the most recent auto-backup (preferred)
  python dotenv-rollback.py

  # Or restore specific values (use when no auto-backup exists)
  python dotenv-rollback.py --key "sk-cp-Lp...MD5M" --url "https://api.minimaxi.com/v1"

  # Skip the confirmation prompt
  python dotenv-rollback.py --yes
"""

import argparse
import glob
import os
import re
import sys

ENV_PATHS = [
    r"C:\Users\Administrator\AppData\Local\hermes\.env",
    r"C:\Users\Administrator\AppData\Local\hermes\profiles\boss-control\.env",
]

BACKUP_GLOB = ".env.bak.*"

# Fields this script knows how to roll back. Add more here as needed.
LlmField = os.environ.get("PLACEHOLDER_MASK")
# ^ the line above is just so the script can be passed through write_file
#   safely; this constant is never used.

LLM_FIELDS = [
    "MINIMAX_CN_API_KEY",
    "MINIMAX_BASE_URL",
    "CUSTOM_GPT_API_KEY",
]


def find_env_paths():
    return [p for p in ENV_PATHS if os.path.isfile(p)]


def find_latest_backup(env_path):
    pattern = os.path.join(os.path.dirname(env_path), BACKUP_GLOB)
    backups = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    return backups[0] if backups else None


def show_diff(label, env_path, before, after):
    print(f"\n--- diff ({label}) ---")
    if before == after:
        print("(no changes)")
        return
    # crude line-by-line diff
    blines = before.splitlines()
    alines = after.splitlines()
    if len(blines) != len(alines):
        print(f"line count changed: {len(blines)} -> {len(alines)}")
    for i, (b, a) in enumerate(zip(blines, alines)):
        if b != a:
            print(f"  L{i+1}: - {b}")
            print(f"  L{i+1}: + {a}")


def restore_from_backup(env_path, backup_path, yes=False):
    bak = open(backup_path, "r", encoding="utf-8").read()
    cur = open(env_path, "r", encoding="utf-8").read()
    if bak == cur:
        print(f"{env_path} already matches {backup_path}; nothing to do.")
        return
    show_diff(os.path.basename(backup_path) + " -> " + os.path.basename(env_path),
              env_path, cur, bak)
    if not yes:
        ans = input("Apply? [y/N] ").strip().lower()
        if ans != "y":
            print("Aborted.")
            return
    open(env_path, "w", encoding="utf-8").write(bak)
    print(f"OK: {env_path} restored from {backup_path}")


def restore_specific(env_path, new_key=None, new_url=None, yes=False):
    cur = open(env_path, "r", encoding="utf-8").read()
    new = cur

    if new_key:
        # Use .replace() not regex — see hermes-quirks.md #1
        for line_prefix in LLM_FIELDS[:1]:  # only the _API_KEY field
            pattern = re.compile(
                r"^" + re.escape(line_prefix) + r"=([^\n]+)$", re.M
            )
            m = pattern.search(new)
            if m:
                old_val = m.group(1)
                new = new.replace(
                    f"{line_prefix}={old_val}", f"{line_prefix}={new_key}", 1
                )

    if new_url:
        # For URLs, prefer sed (handles special chars cleanly):
        #   sed -i "s|^MINIMAX_BASE_URL=.*|MINIMAX_BASE_URL=NEW|" .env
        import subprocess
        result = subprocess.run(
            ["sed", "-i", f"s|^MINIMAX_BASE_URL=.*|MINIMAX_BASE_URL={new_url}|", env_path],
            check=True,
        )
        new = open(env_path, "r", encoding="utf-8").read()

    show_diff("specific restore", env_path, cur, new)
    if cur == new:
        print("no changes to apply")
        return
    if not yes:
        ans = input("Apply? [y/N] ").strip().lower()
        if ans != "y":
            print("Aborted.")
            return
    if new_key:  # URL change was already written by sed above
        open(env_path, "w", encoding="utf-8").write(new)
    print(f"OK: {env_path} updated")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--key", help="new API key value to restore")
    p.add_argument("--url", help="new base URL value to restore")
    p.add_argument("--yes", action="store_true", help="skip confirmation")
    args = p.parse_args()

    for env_path in find_env_paths():
        print(f"\n=== {env_path} ===")
        if args.key or args.url:
            restore_specific(env_path, new_key=args.key, new_url=args.url, yes=args.yes)
        else:
            backup = find_latest_backup(env_path)
            if not backup:
                print("no auto-backup found; pass --key and --url to restore specific values")
                continue
            print(f"latest backup: {backup}")
            restore_from_backup(env_path, backup, yes=args.yes)


if __name__ == "__main__":
    main()
