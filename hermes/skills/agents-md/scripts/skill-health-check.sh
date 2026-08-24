#!/usr/bin/env bash
# skill-health-check.sh — Detect stale or scope-mismatched skills in a profile.
#
# Usage:
#   ./skill-health-check.sh <profile-name>   # e.g. maodou, afu, laomo
#
# Outputs three sections:
#   1. Profile skills sorted by mtime (newest first)
#   2. Stale skills (>90 days since last touch) — needs authorization to update
#   3. Registry scope reminder (L1 auto-loaded, L3 NOT auto-loaded)
#
# Designed for cron self-evolution cycles. Exit code 0 = clean, 1 = stale skills detected.

set -e

PROFILE="${1:-maodou}"
SKILL_DIR="/Users/hua/.hermes/profiles/${PROFILE}/skills"

if [ ! -d "$SKILL_DIR" ]; then
    echo "ERROR: profile skills directory not found: $SKILL_DIR" >&2
    exit 2
fi

echo "=== Profile: $PROFILE ==="
echo "Skills dir: $SKILL_DIR"
echo

echo "--- All profile skills, newest first ---"
ls -lt "$SKILL_DIR"/*/SKILL.md 2>/dev/null | awk '{print $6, $7, $8, $9}' | head -20
echo

echo "--- Stale check (>90 days) ---"
NOW=$(date +%s)
STALE=()
while IFS= read -r skill_file; do
    MTIME=$(stat -f %m "$skill_file")
    AGE_DAYS=$(( (NOW - MTIME) / 86400 ))
    if [ "$AGE_DAYS" -gt 90 ]; then
        STALE+=("$skill_file  (${AGE_DAYS} days)")
        echo "STALE: $skill_file  ($AGE_DAYS days old)"
    fi
done < <(find "$SKILL_DIR" -name SKILL.md 2>/dev/null)

if [ ${#STALE[@]} -eq 0 ]; then
    echo "OK: no stale skills (all <90 days)"
    EXIT=0
else
    echo
    echo "ACTION: ${#STALE[@]} stale skill(s) detected."
    echo "Per AGENTS.md 铁律: do NOT silently rewrite core skills."
    echo "Encode as recommendation in the cron evolution report; request 华哥/玉芬 authorization."
    EXIT=1
fi

echo
echo "--- Registry scope reminder ---"
echo "L1 (~/.hermes/skills/) → AUTO-LOADED by Hermes registry"
echo "L3 (~/.hermes/profiles/<name>/skills/) → NOT auto-loaded; profile-local only"
echo "For 'core' skills in AGENTS.md, verify they live in L1 or have been registered with:"
echo "  hermes curator add-skill --profile $PROFILE --path $SKILL_DIR/<skill>/ --scope profile"
echo

exit $EXIT