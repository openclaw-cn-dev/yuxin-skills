#!/usr/bin/env python3
"""kb-watchdog-launcher.py — launchd兼容的中文路径包装器"""
import subprocess
import sys

script = "/Users/hua/Desktop/渔芯科技/6-产品研发/02-LookForge/scripts/kb_watchdog.py"
args = sys.argv[1:] if len(sys.argv) > 1 else ["--daemon"]

result = subprocess.run(
    ["/Users/hua/.hermes/hermes-agent/venv/bin/python3", script] + args,
    capture_output=False
)
sys.exit(result.returncode)
