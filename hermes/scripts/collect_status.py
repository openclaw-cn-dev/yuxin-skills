#!/usr/bin/env python3
"""collect_status.py — 采集 9 profile + 工具仓库 + token 状态 → agent_status.json

每 30 分钟跑一次(玉芬自进化扫描 cron `a09e4917b16e` 集成)

v1.1 (2026-08-06): gateway_up 改用 HTTP 端口探测 + skills_count 自动数目录
"""
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROFILES_DIR = Path("/Users/hua/.hermes/profiles")
STATE_DIR = Path("/Users/hua/.hermes/state")
TOOL_REPO_DIR = Path("/Users/hua/.hermes/tool-repo")

# 每个 profile gateway 的 HTTP 端口（从 gateway_state.json 或约定推断）
GATEWAY_PORT_START = 15721


def _probe_http_gateway(profile_name: str) -> bool:
    """多层探测 gateway 是否在线。

    策略（按优先级）：
    1. 读取 gateway_state.json 检查 gateway_state=="running" 且 pid 存活
    2. HTTP 端口探测 /health 端点
    3. fallback 到 launchctl 检查
    """
    state_file = PROFILES_DIR / profile_name / "gateway_state.json"

    # 方式 1: gateway_state.json 状态 + PID 存活检查
    if state_file.exists():
        try:
            gs = json.load(open(state_file))
            if gs.get("gateway_state") == "running":
                pid = gs.get("pid")
                if pid:
                    try:
                        os.kill(pid, 0)  # 信号 0 只检查进程是否存在
                        return True
                    except OSError:
                        pass  # PID 不存在，继续尝试其他方式
        except Exception:
            pass

    # 方式 2: HTTP /health 端点
    if state_file.exists():
        try:
            gs = json.load(open(state_file))
            port = gs.get("port")
            if port:
                url = f"http://127.0.0.1:{port}/health"
                try:
                    with urllib.request.urlopen(url, timeout=3) as resp:
                        if resp.status == 200:
                            return True
                except Exception:
                    pass
        except Exception:
            pass

    # 方式 3: 按约定端口扫描
    profile_order = ["default", "maodou", "xiaobao", "afu", "heidou", "laomo", "quant", "zhenglishi", "community"]
    try:
        idx = profile_order.index(profile_name)
        port = GATEWAY_PORT_START + idx
        url = f"http://127.0.0.1:{port}/health"
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
    except ValueError:
        pass

    # 方式 4: fallback 到 launchctl 检查
    launchd_plist = Path.home() / "Library" / "LaunchAgents" / f"ai.hermes.gateway-{profile_name}.plist"
    if launchd_plist.exists():
        try:
            r = subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=5)
            if f"ai.hermes.gateway-{profile_name}" in r.stdout:
                return True
        except Exception:
            pass

    return False


def _count_skills(profile_name: str) -> int:
    """自动数 ~/.hermes/profiles/{name}/skills/ 下非隐藏子目录数（排除 .archive .curator_backups 等）"""
    skills_dir = PROFILES_DIR / profile_name / "skills"
    if not skills_dir.exists():
        return 0
    count = 0
    try:
        for child in skills_dir.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                count += 1
    except PermissionError:
        pass
    return count


def collect_profile_status(profile_name: str) -> dict:
    """采集单个 profile 状态"""
    profile_dir = PROFILES_DIR / profile_name
    profile_json_file = profile_dir / "profile.json"
    if not profile_json_file.exists():
        return {"name": profile_name, "status": "missing_profile_json"}

    data = json.load(open(profile_json_file))

    # HTTP 端口探测 gateway 是否在线
    gateway_up = _probe_http_gateway(profile_name)

    # 自动采集 skills_count（不再依赖 profile.json 中的手填值）
    data["skills_count"] = _count_skills(profile_name)

    # 检查最近 memory
    memory_dir = profile_dir / "memories"
    last_memory = None
    if memory_dir.exists():
        memories = sorted(memory_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if memories:
            last_memory = memories[0].name

    data["gateway_up"] = gateway_up
    data["last_memory"] = last_memory
    data["status"] = "ok" if gateway_up else "gateway_down"
    return data

def collect_tool_status() -> dict:
    """采集工具仓库状态"""
    status = {"last_check_at": datetime.now(timezone(timedelta(hours=8))).isoformat()}

    # Claude Code 版本
    try:
        r = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=5)
        status["claude_code"] = {"version": r.stdout.strip() or "unknown", "status": "ok"}
    except Exception as e:
        status["claude_code"] = {"version": "not_found", "status": "error", "error": str(e)}

    # Codex 版本
    try:
        r = subprocess.run(["codex", "--version"], capture_output=True, text=True, timeout=5)
        status["codex"] = {"version": r.stdout.strip() or "unknown", "status": "ok"}
    except Exception as e:
        status["codex"] = {"version": "not_found", "status": "error", "error": str(e)}

    # Hermes Agent（从全局 config 读实际模型）
    try:
        import yaml
        cfg = yaml.safe_load(Path("/Users/hua/.hermes/config.yaml").read_text()) or {}
        ha_model = cfg.get("model", "deepseek-v4-pro")
    except Exception:
        ha_model = "deepseek-v4-pro"
    status["hermes_agent"] = {"version": ha_model, "status": "ok"}

    return status

def main():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()

    # 1. 9 profile 状态
    profiles_status = {}
    for name in ["default", "maodou", "xiaobao", "afu", "heidou", "laomo", "quant", "zhenglishi", "community"]:
        profiles_status[name] = collect_profile_status(name)

    # 2. 工具仓库状态
    tool_status = collect_tool_status()

    # 3. Cron 任务统计
    cron_file = Path("/Users/hua/.hermes/cron/jobs.json")
    cron_stats = {"total": 0, "ok": 0, "err": 0, "ids": []}
    if cron_file.exists():
        try:
            cron_data = json.load(open(cron_file))
            jobs = cron_data.get("jobs", []) if isinstance(cron_data, dict) else cron_data
            cron_stats["total"] = len(jobs)
            for j in jobs:
                if j.get("last_status") == "ok":
                    cron_stats["ok"] += 1
                elif j.get("last_status") == "error":
                    cron_stats["err"] += 1
                cron_stats["ids"].append(j.get("id", "?")[:12])
        except Exception as e:
            cron_stats["error"] = str(e)

    # 4. 综合输出
    output = {
        "last_collect_at": now,
        "profiles": profiles_status,
        "tools": tool_status,
        "cron_stats": cron_stats,
    }

    out_file = STATE_DIR / "agent_status.json"
    out_file.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"✅ 已写入 {out_file}")
    print(f"   profiles: {len(profiles_status)} 个 | cron: {cron_stats['total']} 个 (ok={cron_stats['ok']}, err={cron_stats['err']})")
    print(f"   tools: claude_code={tool_status['claude_code']['version']}, codex={tool_status['codex']['version']}")

if __name__ == "__main__":
    main()
