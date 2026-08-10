#!/bin/bash
# 竞品监测管线 - 每日/每周采集
# 用法: pipeline.sh [daily|weekly]
cd /Users/hua/.hermes/kanban/workspaces/cad822f3
/usr/bin/python3 pipeline.py "${1:-daily}" 2>&1
