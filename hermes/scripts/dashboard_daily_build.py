#!/usr/bin/env python3
"""总控大屏每日全量生成(08:05 no_agent) — 承接 Mac launchd com.yuxin.control-dashboard。

调用公司工具库的 control_dashboard.main() 做全量扫描并重写看板。
正常: stdout 一行结果; 异常: 退出码非 0 触发告警。
"""
import sys

TOOLS = "D:/yuxin/company/07-环境配置/03-脚本与工程工具"

sys.path.insert(0, TOOLS)
import control_dashboard  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(control_dashboard.main())
