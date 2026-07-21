#!/bin/bash
# 影身 v0.1 — 启动脚本
# 华哥用：yuxin_yingshen.sh ask "问题"

set -e
source ~/.hermes/hermes-agent/venv/bin/activate

CMD=${1:-help}
shift || true

cd ~/hermes/yingshen

case "$CMD" in
  ask)
    python3 ask_yingshen.py "$@"
    ;;
  add)
    python3 yingshen_rag.py add "$@"
    ;;
  add-file)
    python3 yingshen_rag.py add-file "$@"
    ;;
  search)
    python3 yingshen_rag.py search "$@"
    ;;
  stats)
    python3 yingshen_rag.py stats "$@"
    ;;
  help|*)
    echo "影身 v0.1 — 用法"
    echo ""
    echo "  yuxin_yingshen.sh ask \"问题\"            # 问影身（RAG 增强）"
    echo "  yuxin_yingshen.sh search \"关键词\"        # 检索（不带 LLM）"
    echo "  yuxin_yingshen.sh add <col> \"文字\"       # 录入一条"
    echo "  yuxin_yingshen.sh add-file <col> <文件>  # 批量录入文件"
    echo "  yuxin_yingshen.sh stats                  # 看每个 collection 条数"
    echo ""
    echo "  collection 类型：identity / history / decisions / preferences / studies"
    ;;
esac
