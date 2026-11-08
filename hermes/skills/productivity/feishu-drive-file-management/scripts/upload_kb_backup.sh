#!/bin/bash
# 飞书云盘批量上传脚本 - 带token刷新、分批上传、MD5校验
# 用法: bash upload_kb_backup.sh <源目录> <目标folder_token>
# 依赖: jq (JSON解析), md5sum (MD5校验)

set -e

# === 配置 ===
FEISHU_APP_ID="${FEISHU_APP_ID:-cli_a964873dd7b8dbda}"
FEISHU_APP_SECRET="${FEISHU_APP_SECRET}"  # 从环境或 ~/.hermes/profiles/default/.env 读取

# 如果没传secret，尝试从默认profile读取
if [ -z "$FEISHU_APP_SECRET" ] && [ -f ~/.hermes/profiles/default/.env ]; then
  FEISHU_APP_SECRET=$(grep FEISHU_APP_SECRET ~/.hermes/profiles/default/.env | cut -d'"' -f2)
fi

DEST_TOKEN="${2:-HFPwfciktlkv7Adi0AfcSUrinBf}"  # 默认目标: 知识库备份
BATCH_SIZE=50

# === 获取token ===
get_token() {
  RESP=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
    -H "Content-Type: application/json" \
    -d "{\"app_id\": \"$FEISHU_APP_ID\", \"app_secret\": \"$FEISHU_APP_SECRET\"}")
  TOKEN=$(echo "$RESP" | jq -r '.tenant_access_token')
  if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Token获取失败: $RESP"
    exit 1
  fi
  echo "Token OK"
}

# === 上传单个文件 ===
upload_file() {
  local FILE_PATH="$1"
  local FILE_NAME=$(basename "$FILE_PATH")
  local FILE_SIZE=$(stat -c%s "$FILE_PATH")
  local MD5=$(md5sum "$FILE_PATH" | awk '{print $1}')

  RESP=$(curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$FILE_PATH" \
    -F "file_name=$FILE_NAME" \
    -F "parent_type=explorer" \
    -F "parent_node=$DEST_TOKEN" \
    -F "size=$FILE_SIZE" \
    -F "hash=$MD5")

  CODE=$(echo "$RESP" | jq -r '.code')
  if [ "$CODE" == "0" ]; then
    echo "ok"
    return 0
  else
    echo "fail:$CODE"
    return 1
  fi
}

# === 主流程 ===
get_token

# 收集所有文件
FILES=()
while IFS= read -r f; do
  FILES+=("$f")
done < <(find "$1" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.pdf" -o -name "*.doc*" -o -name "*.xls*" -o -name "*.ppt*" \) 2>/dev/null)

TOTAL=${#FILES[@]}
echo "待上传: $TOTAL 个文件"

ok=0
fail=0
for i in "${!FILES[@]}"; do
  FILE="${FILES[$i]}"
  idx=$((i+1))

  # 每batch重新获取token
  if (( idx % BATCH_SIZE == 1 )) && (( idx > 1 )); then
    get_token
  fi

  result=$(upload_file "$FILE")
  if [[ "$result" == "ok" ]]; then
    ((ok++))
  else
    ((fail++))
  fi

  if (( idx % 20 == 0 )) || (( idx == TOTAL )); then
    echo "$idx: ${ok}ok ${fail}fail"
  fi
done

echo "FINAL: ${ok}ok ${fail}fail"
