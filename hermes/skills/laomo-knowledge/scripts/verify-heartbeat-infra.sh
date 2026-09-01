#!/bin/bash
# 老莫心跳 round 的基础设施 + 核心能力一键体检脚本
# 用法: bash scripts/verify-heartbeat-infra.sh
# 输出每一行的健康状态，方便心跳时粘贴进 tasks.description 的 [R<n>] 日志。
# 与 references/heartbeat-workflow.md 的「blocked 任务心跳标准动作」第 1-2 步一一对应。

set -u

echo "=== 核心能力 (火山引擎 doubao 方案) ==="
for f in "$HOME/.hermes/.env" "$HOME/.hermes/profiles/laomo/.env"; do
  if [ -f "$f" ]; then
    v=$(grep -E '^VOLC_ARK_API_KEY=' "$f" | head -1 | cut -d= -f2-)
    printf "  %s: LEN=%d prefix=%s\n" "$f" "${#v}" "${v:0:12}"
  else
    echo "  $f: MISSING"
  fi
done

PR="$HOME/.hermes/profiles/laomo/scripts/photo_restore.py"
if [ -f "$PR" ]; then
  printf "  photo_restore.py: present (%dB)\n" "$(wc -c < "$PR" | tr -d ' ')"
else
  echo "  photo_restore.py: MISSING"
fi

if [ -d "$HOME/.hermes/skills/ai-vision/doubao-image-gen" ]; then
  echo "  doubao-image-gen skill: present @ skills/ai-vision"
else
  echo "  doubao-image-gen skill: MISSING"
fi

echo "=== 基础设施 ==="
code() { curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$1"; }
echo "  API  :8000 /api/health    = $(code http://localhost:8000/api/health)"
echo "  API  :8000 /api/v1/health = $(code http://localhost:8000/api/v1/health)"
echo "  LLM  :18888 /health       = $(code http://localhost:18888/health)"
echo "  Ollama :11434             = $(code http://localhost:11434/)"

if docker info >/dev/null 2>&1; then
  echo "  Docker daemon: UP"
  echo "  RKR 容器:"
  docker ps --format '    {{.Names}}  {{.Status}}' 2>/dev/null | grep -E 'rkr-|geo-|zhiyu|pgvector|redis' || echo "    (无 rkr/相关容器)"
else
  echo "  Docker daemon: DOWN (需 open -a Docker 恢复)"
fi

echo "  msg GW laomo:"
launchctl list 2>/dev/null | grep -i laomo || echo "    (launchctl 无 laomo 服务)"

echo "=== 完成 ==="
