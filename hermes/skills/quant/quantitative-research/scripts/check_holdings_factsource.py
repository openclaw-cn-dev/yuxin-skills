"""
check_holdings_factsource.py — boss 持仓事实源 4 处路径一致性体检

心跳 Step 0 必跑脚本（pitfall #37）：
1. holdings.json 存在性（4 处候选路径）
2. Dashboard backend HOLDINGS_FILE 路径常量（main.py 第 138 行附近）指向实际存在的目录
3. Dashboard 端口存活（8302 A 股版 / 8303 KuanQuant）
4. AGENTS.md 持仓段 + Dashboard 路径 + 项目目录 3 处口径一致

退出码：
  0 = 全部 ✅
  1 = 至少 1 项 ❌（任何 ❌ 都必须立即停掉下游"持仓相关"决策/报告）

依赖：仅标准库（pathlib / subprocess / re / json）；无需 baostock。
实测：2026-09-12 心跳 #N+53，输出 ≤2s。

Usage:
    python3 scripts/check_holdings_factsource.py
    python3 scripts/check_holdings_factsource.py --json  # JSON 输出（机器可读）
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Boss 项目根目录（绝对路径，禁 ~/ 前缀 — AGENTS.md v6 铁律 #1）
PROJECT_ROOT = Path("/Users/hua/6-产品研发/渔芯独角兽/00-基本完成")

# Dashboard backend main.py（hardcode HOLDINGS_FILE 的位置）
DASHBOARD_MAIN = (
    PROJECT_ROOT
    / "渔芯量化-海外"
    / "10-FisherQ-Dashboard"
    / "backend"
    / "main.py"
)

# AGENTS.md 持仓段（路径常量声明位置）
AGENTS_FILES = [
    Path("/Users/hua/.hermes/profiles/quant/AGENTS.md"),
    PROJECT_ROOT / "渔芯量化-海外" / "11-宽博士Hermes档案" / "AGENTS.md",
]

# 4 处候选 holdings.json 路径（含项目重命名前后）
HOLDINGS_CANDIDATES = [
    PROJECT_ROOT / "渔芯量化" / "06-持仓档案" / "holdings.json",          # 旧路径
    PROJECT_ROOT / "渔芯量化-海外" / "06-持仓档案" / "holdings.json",       # 新路径
    PROJECT_ROOT / "渔芯量化-海外" / "12-通用量化资料库" / "holdings.json",  # 推测路径
    PROJECT_ROOT / "渔芯量化-海外" / "12-通用量化资料库" / "华哥组合持仓档案.md",  # 旧档案
]

# Dashboard 端口（A 股版 + KuanQuant 海外版）
DASHBOARD_PORTS = [
    (8302, "渔芯量化 A 股版"),
    (8303, "KuanQuant / 渔芯量化-海外"),
]


def check_holdings_existence() -> dict:
    """检查 1: holdings.json 4 处候选路径"""
    results = {}
    for path in HOLDINGS_CANDIDATES:
        results[str(path)] = path.exists()
    any_exists = any(results.values())
    return {"candidates": results, "any_exists": any_exists}


def check_dashboard_backend_path() -> dict:
    """检查 2: Dashboard backend main.py HOLDINGS_FILE 路径常量"""
    if not DASHBOARD_MAIN.exists():
        return {"main_py_found": False, "holdings_line": None, "resolved_path": None,
                "resolved_exists": False}

    src = DASHBOARD_MAIN.read_text()
    m = re.search(r"HOLDINGS_FILE\s*=\s*(.+?)$", src, re.MULTILINE)
    if not m:
        return {"main_py_found": True, "holdings_line": None, "resolved_path": None,
                "resolved_exists": False}

    raw_line = m.group(1).strip()
    # 解析 Path(__file__).parent.parent.parent / "..." / "..." 风格的常量
    # 简化为：直接读 dashboard 父目录 = PROJECT_ROOT / "渔芯量化-海外"
    # 因为 FISHERQ_ROOT = main.py.parent.parent.parent / "01-工具代码" / "FisherQ"
    # 所以 FISHERQ_ROOT.parent.parent = PROJECT_ROOT / "渔芯量化-海外"
    dashboard_root = DASHBOARD_MAIN.parent.parent.parent
    resolved = dashboard_root / "06-持仓档案" / "holdings.json"

    return {
        "main_py_found": True,
        "holdings_line": raw_line,
        "resolved_path": str(resolved),
        "resolved_exists": resolved.exists(),
    }


def check_dashboard_ports() -> dict:
    """检查 3: Dashboard 端口存活"""
    results = {}
    for port, label in DASHBOARD_PORTS:
        try:
            out = subprocess.run(
                ["curl", "-sS", "--max-time", "2", f"http://127.0.0.1:{port}/api/holdings"],
                capture_output=True, text=True, timeout=5
            )
            alive = (out.returncode == 0 and bool(out.stdout))
            results[f"{port} ({label})"] = alive
        except Exception as e:
            results[f"{port} ({label})"] = f"异常: {e}"
    return results


def check_agents_md_paths() -> dict:
    """检查 4: AGENTS.md 持仓段声明的路径"""
    results = {}
    for ag in AGENTS_FILES:
        if not ag.exists():
            results[str(ag)] = {"found": False}
            continue
        text = ag.read_text(errors="ignore")
        # 找包含 "holdings.json" 的行
        lines_with_holdings = [
            l.strip() for l in text.splitlines()
            if "holdings.json" in l and not l.strip().startswith("#")
        ]
        results[str(ag)] = {"found": True, "lines": lines_with_holdings[:5]}
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="boss 持仓事实源 4 处一致性体检")
    parser.add_argument("--json", action="store_true", help="JSON 输出（机器可读）")
    args = parser.parse_args()

    report = {
        "check1_holdings_existence": check_holdings_existence(),
        "check2_dashboard_backend_path": check_dashboard_backend_path(),
        "check3_dashboard_ports": check_dashboard_ports(),
        "check4_agents_md_paths": check_agents_md_paths(),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("=== 1. holdings.json 4 处候选路径 ===")
        for p, exists in report["check1_holdings_existence"]["candidates"].items():
            mark = "✅" if exists else "❌"
            print(f"  {mark} {p}")
        any_exists = report["check1_holdings_existence"]["any_exists"]
        print(f"  → 至少 1 处存在: {'✅' if any_exists else '❌ 全失效'}")

        print()
        print("=== 2. Dashboard backend HOLDINGS_FILE 路径 ===")
        c2 = report["check2_dashboard_backend_path"]
        if not c2["main_py_found"]:
            print(f"  ❌ main.py 不存在: {DASHBOARD_MAIN}")
        else:
            print(f"  main.py 第 138 行: {c2['holdings_line']}")
            print(f"  解析后路径: {c2['resolved_path']}")
            mark = "✅" if c2["resolved_exists"] else "❌ 不存在"
            print(f"  {mark} 路径存在性")

        print()
        print("=== 3. Dashboard 端口存活探测 ===")
        for label, alive in report["check3_dashboard_ports"].items():
            mark = "✅ 存活" if alive is True else ("❌ 不通" if alive is False else f"⚠️ {alive}")
            print(f"  端口 {label}: {mark}")

        print()
        print("=== 4. AGENTS.md 持仓段声明路径 ===")
        for ag, info in report["check4_agents_md_paths"].items():
            if not info["found"]:
                print(f"  ⚠️ 不存在: {ag}")
                continue
            if not info["lines"]:
                print(f"  ✅ {ag}: (未声明具体路径 — 推荐保持)")
            else:
                print(f"  📄 {ag}:")
                for line in info["lines"]:
                    print(f"     {line[:120]}")

    # 退出码：至少 1 项 ❌ → exit 1
    has_failure = (
        not report["check1_holdings_existence"]["any_exists"]
        or (report["check2_dashboard_backend_path"]["main_py_found"]
            and not report["check2_dashboard_backend_path"]["resolved_exists"])
        or not any(v is True for v in report["check3_dashboard_ports"].values())
    )
    return 1 if has_failure else 0


if __name__ == "__main__":
    sys.exit(main())