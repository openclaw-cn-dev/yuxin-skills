#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kanban_task_ops.py — 渔芯任务池统一操作入口 v2
派发引擎说明: kanban 派发器已内置于 gateway (dispatch_in_gateway 默认 true),
每 60 秒自动 claim ready 任务并 spawn worker。本脚本不再拉起独立 daemon。

用法:
  下发: python kanban_task_ops.py dispatch --to laomo --title "[科技] xxx" --body "..." --priority 1 --due 4h
  看板: python kanban_task_ops.py board
  汇总: python kanban_task_ops.py summary        (每日18:00 cron 用)
  监控: python kanban_task_ops.py supervise      (每30分钟 cron 用: gateway存活+派发器健康+超时预警+资源水位)
"""
import subprocess, sys, json, argparse, datetime, os

KANBAN = ["hermes", "kanban"]
# 并发/资源红线 (章程 §1.4)
MAX_WORKERS = 4
MEM_FLOOR_GB = 8.0
CPU_CEIL = 80.0

def run(args, timeout=60):
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                       shell=False, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def _ps(cmd_list):
    """call hermes kanban subcommand"""
    return run(KANBAN + cmd_list)

def gateway_alive():
    """gateway 进程是否存活 (hermes.exe)"""
    code, out = run(["tasklist", "/FI", "IMAGENAME eq hermes.exe"]) if sys.platform == "win32" else run(["ps", "aux"])
    return "hermes.exe" in out or "hermes " in out

def dispatcher_healthy():
    """派发器最近一 tick 是否有异常: 通过 diagnostics 判断"""
    code, out = _ps(["diagnostics"])
    return code == 0, out.strip()

def cmd_dispatch(a):
    args = KANBAN + ["create", a.title, "--assignee", a.to, "--json",
                     "--created-by", a.created_by, "--priority", str(a.priority)]
    if a.body:
        args += ["--body", a.body]
    if a.due:
        args += ["--max-runtime", a.due]
    for s in (a.skill or []):
        args += ["--skill", s]
    code, out = _ps(args[2:])
    print(out)
    return code

def cmd_board(a):
    code, out = _ps(["list"])
    print(out)

def cmd_summary(a):
    """每日汇报: 统计+未完结+资源水位"""
    code, out = _ps(["stats"])
    print("== 任务池统计 ==")
    print(out)
    code, out = _ps(["list"])
    lines = out.splitlines()
    interesting = [l for l in lines if any(k in l for k in
                   ("in_progress", "running", "blocked", "ready", "triage", "pending"))]
    print("== 未完结任务 ==")
    print("\n".join(interesting) if interesting else "(空) 全部完结")
    try:
        import psutil
        m = psutil.virtual_memory(); c = psutil.cpu_percent(interval=0.5)
        print(f"\n== 资源水位 ==\n内存 {m.available/1024**3:.1f}GB 可用 ({m.percent}%) | CPU {c}%")
        if m.available/1024**3 < MEM_FLOOR_GB:
            print("⚠️ 内存低于红线 8GB，派发器应降并发")
    except ImportError:
        pass

def cmd_supervise(a):
    """守护: 1) gateway 存活 2) 派发器健康 3) 运行中/阻塞任务预警 4) 资源水位"""
    now = f"[{datetime.datetime.now():%F %T}]"
    problems = []
    if not gateway_alive():
        problems.append("❌ gateway 进程不存活 — kanban 派发停摆，任务将无人认领！请: hermes gateway start")
    else:
        print(f"{now} gateway 正常 (派发器内置, 60s/tick, 并发上限 {MAX_WORKERS})")
    ok, diag = dispatcher_healthy()
    if not ok:
        problems.append(f"❌ kanban diagnostics 异常:\n{diag}")
    code, out = _ps(["list"])
    for line in out.splitlines():
        if "running" in line or "in_progress" in line:
            print(f"[运行中] {line.strip()}")
        if "blocked" in line:
            problems.append(f"[阻塞任务] {line.strip()}")
    try:
        import psutil
        m = psutil.virtual_memory(); c = psutil.cpu_percent(interval=0.5)
        warn = []
        if m.available/1024**3 < MEM_FLOOR_GB:
            warn.append(f"内存不足({m.available/1024**3:.1f}GB<8GB)")
        if c > CPU_CEIL:
            warn.append(f"CPU过高({c}%>{CPU_CEIL}%)")
        line = f"水位: 内存{m.available/1024**3:.1f}GB可用 CPU{c}% " + ("⚠️" + ";".join(warn) if warn else "✓正常")
        print(line)
        if warn:
            problems.append(line)
    except ImportError:
        pass
    if problems:
        print("\n".join("⚠️ " + p for p in problems))
        sys.exit(1)   # 让 cron 以 error 状态记录，便于追踪
    print(f"{now} 监控通过")

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dispatch")
    d.add_argument("--to", required=True)
    d.add_argument("--title", required=True)
    d.add_argument("--body", default="")
    d.add_argument("--priority", type=int, default=2)
    d.add_argument("--due", default="")   # e.g. 4h / 2d
    d.add_argument("--skill", action="append")
    d.add_argument("--created-by", default="玉芬")
    sub.add_parser("board")
    sub.add_parser("summary")
    sub.add_parser("supervise")
    a = p.parse_args()
    sys.exit({"dispatch": cmd_dispatch, "board": cmd_board,
              "summary": cmd_summary, "supervise": cmd_supervise}[a.cmd](a))

if __name__ == "__main__":
    main()
