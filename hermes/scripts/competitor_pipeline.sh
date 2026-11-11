#!/bin/bash
# 竞品监测管线 wrapper (Windows 重建版) - 转调 competitor_pipeline.py
# 旧版指向 macOS 宿主 /Users/hua/... 已失效, 2026-11-11 老莫重建
exec python "D:/yuxin/hermes/profiles/laomo/scripts/competitor_pipeline.py" "${1:-daily}"
