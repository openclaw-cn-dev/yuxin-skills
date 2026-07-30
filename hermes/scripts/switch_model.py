#!/usr/bin/env python3
"""
渔芯模型切换器 — 一键切换火山引擎 ↔ DeepSeek

用法:
  python3 switch_model.py status          # 看当前状态
  python3 switch_model.py deepseek        # 切到 DeepSeek
  python3 switch_model.py volcengine      # 切回火山引擎
"""

import subprocess, json, urllib.request, sys, os, yaml
from pathlib import Path

GATEWAY_URL = "http://127.0.0.1:18888"
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
PROFILES = ["default", "afu", "laomo", "maodou", "quant", "xiaobao", "zhenglishi"]
CODEX_CONFIG = Path.home() / ".codex" / "config.toml"
ARKCLI_MODELS = Path.home() / ".codex" / "arkcli.models.json"

# ─── 模型映射 ───
TARGETS = {
    "deepseek": {
        "label": "DeepSeek",
        "gateway_primary": "ds-openai",
        "hermes_model": "deepseek-v4-pro",
        "hermes_provider": "deepseek-cn",
        "codex_model": "deepseek-v4-pro",
    },
    "volcengine": {
        "label": "火山引擎",
        "gateway_primary": "volc-openai",
        "hermes_model": "doubao-seed-2-0-pro-260215",
        "hermes_provider": "volcengine-agent-plan",
        "codex_model": "***SECRET***",
    },
}


def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)


def gateway_call(action, route="/openai"):
    try:
        url = f"{GATEWAY_URL}/admin/switch?action={action}&route={route}"
        with urllib.request.urlopen(url, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def switch_gateway(target):
    """切换 Gateway 的 primary backend"""
    t = TARGETS[target]
    primary_backend = t["gateway_primary"]

    # 先用 flip 确保方向正确
    status = gateway_call("status")
    current_primary = status.get("primary", "")

    if current_primary == primary_backend:
        # 已经是目标 backend，只需确保 active = primary
        result = gateway_call("to-primary")
        return f"Gateway 已在 {t['label']} (primary)，无需切换"
    else:
        # 需要 flip
        result = gateway_call("flip")
        if result.get("switched"):
            return f"Gateway 已切换到 {t['label']}"
        return f"Gateway 切换失败: {result}"


def switch_hermes(target):
    """切换所有 Hermes profile"""
    t = TARGETS[target]
    results = []
    for prof in PROFILES:
        flag = f"--profile {prof}" if prof != "default" else ""
        cmd = f"hermes config set model {t['hermes_model']} {flag}"
        r = run(cmd)
        if r.returncode == 0:
            results.append(f"  {prof:12s} ✅ {t['hermes_model']}")
        else:
            results.append(f"  {prof:12s} ❌ {r.stderr.strip()}")
    return "\n".join(results)


def switch_codex(target):
    """切换 Codex 配置"""
    t = TARGETS[target]

    # 更新 config.toml
    lines = CODEX_CONFIG.read_text().splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("model = "):
            new_lines.append(f'model = "{t["codex_model"]}"')
        else:
            new_lines.append(line)
    CODEX_CONFIG.write_text("\n".join(new_lines) + "\n")

    # 更新 arkcli.models.json 里所有 deepseek/doubao 条目
    if ARKCLI_MODELS.exists():
        catalog = json.loads(ARKCLI_MODELS.read_text())
        for m in catalog.get("models", []):
            slug = m.get("slug", "")
            if "deepseek" in slug.lower() or "doubao" in slug.lower():
                m["slug"] = t["codex_model"]
        ARKCLI_MODELS.write_text(json.dumps(catalog, indent=2, ensure_ascii=False))

    return f"Codex ✅ model={t['codex_model']}, arkcli.models.json 同步"


def show_status():
    """显示当前状态"""
    gw = gateway_call("status")
    codex_model = ""
    for line in CODEX_CONFIG.read_text().splitlines():
        if line.startswith("model = "):
            codex_model = line.split('"')[1]
            break

    print(f"""
╔══════════════════════════════════╗
║     渔芯 LLM 模型状态             ║
╠══════════════════════════════════╣
║ Gateway:  {gw.get('primary', '?'):<25s} ║
║ Codex:    {codex_model:<25s} ║
╚══════════════════════════════════╝
""")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("status", "s"):
        show_status()
        return

    target = sys.argv[1]
    if target == "ds":
        target = "deepseek"
    elif target in ("volc", "volcano"):
        target = "volcengine"

    if target not in TARGETS:
        print(f"用法: {sys.argv[0]} deepseek|volcengine|status")
        print(f"缩写: ds=deepseek, volc=volcengine")
        sys.exit(1)

    t = TARGETS[target]
    print(f"\n🔄 切换到: {t['label']}\n")

    # 1. Gateway
    print("[1/3] Gateway...")
    print(switch_gateway(target))

    # 2. Hermes profiles
    print("\n[2/3] Hermes profiles...")
    print(switch_hermes(target))

    # 3. Codex
    print("\n[3/3] Codex...")
    print(switch_codex(target))

    print(f"\n✅ 全部切换到 {t['label']}！")
    print("⚠️  华哥需要重启 ChatGPT 使 Codex 生效")


if __name__ == "__main__":
    main()
