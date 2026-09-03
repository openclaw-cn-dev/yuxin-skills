#!/usr/bin/env python3
# FindEra→RKR 同步单次执行（no_agent 子脚本）
# 调用 POST /api/v1/scheduler/rkr-sync-now，仅 pushed>0 时输出（供 cron 投递）
# 其余情况静默（stdout 空）
import json
import sys
import urllib.request

URL = "http://localhost:8003/api/v1/scheduler/rkr-sync-now"

try:
    req = urllib.request.Request(
        URL,
        data=json.dumps({}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        result = json.loads(resp.read())
    res = result.get("result", result)
    pushed = res.get("pushed", 0)
    errors = res.get("errors", 0)
    if pushed > 0:
        print(f"FindEra→RKR 同步: pushed={pushed} errors={errors}")
    # pushed==0 → 静默
except Exception as e:
    err = str(e)
    # 404/超时/502/500/429 均静默（下游临时故障或限流，非同步失败）
    if any(k in err for k in ("404", "timed out", "502", "500", "429")):
        sys.exit(0)
    # 其他异常也静默，避免夜间告警轰炸；真正的基础设施故障由健康监控 cron 负责
    sys.exit(0)
