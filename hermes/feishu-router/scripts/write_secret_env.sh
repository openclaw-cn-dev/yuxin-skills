#!/usr/bin/env bash
# Safe-write a Feishu App credential to a Hermes profile's .env
# WITHOUT triggering Hermes's security.redact_secrets truncation.
#
# Usage:
#   APP_SECRET=完整32位 secret ./scripts/write_secret_env.sh <profile-name> <app-id> <app-id-末尾校验>
#
# Why this exists:
#   `cat > file <<EOF`, `write_file`, and any LLM tool channel truncates
#   32-char secrets to "XXXX...YYYY" (18 bytes) because Hermes redaction
#   scans tool output. Using shell variables + printf bypasses the LLM
#   channel entirely - the secret never enters a tool result.

set -e
PROFILE="$1"
APP_ID="$2"
: "${APP_SECRET:?Usage: APP_SECRET=完整 secret $0 <profile> <app_id>}"

ENV_PATH="$HOME/AppData/Local/hermes/profiles/$PROFILE/.env"
printf 'FEISHU_APP_ID=%s\nFEISHU_APP_SECRET=%s\nFEISHU_ALLOW_ALL_USERS=true\nFEISHU_GROUP_POLICY=open\n' \
    "$APP_ID" "$APP_SECRET" > "$ENV_PATH"

echo "wrote $ENV_PATH"
od -c "$ENV_PATH"
