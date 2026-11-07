#!/usr/bin/env bash
# Feishu API helper — get token, then call any Feishu API endpoint.
# Usage: ./feishu_api.sh <method> <path> [curl_extra_args]
#   method: GET|POST|PUT|DELETE
#   path:   e.g. /drive/v1/files?folder_token=xxx
#   curl_extra_args: extra curl flags (e.g. -d '{}', -F 'file=@x')
#
# Prerequisites: FEISHU_APP_ID and FEISHU_APP_SECRET in ~/.hermes/.env
#
# Examples:
#   ./feishu_api.sh GET  drive/v1/files?folder_token=VsMRfTb3qlj4tJd3V7ncJTL6noe
#   ./feishu_api.sh POST im/v1/messages?receive_id_type=chat_id -d '{"receive_id":"oc_xxx","msg_type":"text","content":"{\"text\":\"hi\"}"}'

set -e

ENV_FILE="${HOME}/.hermes/.env"

# Load FEISHU credentials from .env
if [[ -f "$ENV_FILE" ]]; then
  APP_ID=$(grep '^FEISHU_APP_ID=' "$ENV_FILE" | cut -d= -f2-)
  APP_SECRET=$(grep '^FEISHU_APP_SECRET=' "$ENV_FILE" | cut -d= -f2-)
else
  echo "ERROR: $ENV_FILE not found" >&2
  exit 1
fi

BASE_URL="https://open.feishu.cn/open-apis"

# Step 1: Get token
TOKEN_RESP=$(curl -s -X POST "${BASE_URL}/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"${APP_ID}\",\"app_secret\":\"${APP_SECRET}\"}")

TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tenant_access_token',''))")
if [[ -z "$TOKEN" ]]; then
  echo "ERROR: Failed to get token: $TOKEN_RESP" >&2
  exit 1
fi

# Step 2: Make the API call
METHOD="${1:-GET}"
PATH="${2:-}"
shift 2

curl -s -X "$METHOD" "${BASE_URL}/${PATH}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  "$@"
