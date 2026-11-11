#!/usr/bin/env python3
"""薄启动器 -> 正身: D:\\yuxin\\company\\09-量化\\01-渔芯量化01\\14-运维守护\\watchdog.py
cron no_agent 调度只认 ~/.hermes/scripts/,本文件只做转发,逻辑一律改正身。"""
import runpy
import sys

try:
    runpy.run_path(r"D:\yuxin\company\09-量化\01-渔芯量化01\14-运维守护\watchdog.py", run_name="__main__")
except SystemExit as e:
    sys.exit(e.code or 0)
