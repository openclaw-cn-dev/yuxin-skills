#!/bin/bash
# 分身OS 生活流采集 wrapper（no_agent cron 用）
# 脚本本体：life_stream.py（同目录）
# Windows 迁移版：绝对路径防 cron PATH 劫持
cd "/d/yuxin/company/02-渔芯社区/01-产品部/01-研发/研-AI智能大脑/04-分身OS-v0.5/05-生活同步" || exit 1
"/c/Program Files/Python311/python.exe" life_stream.py
exit 0
