#!/usr/bin/env python3
"""
渔芯模型时段调度器 (2026-08-17 峰谷定价版)

DeepSeek 峰谷定价（2026-08-17 00:00 生效）：
  - 高峰(高价)时段：北京时间 9:00-12:00、14:00-18:00（价格 = 空闲 2 倍）
  - 空闲(低价)时段：其余时间（半价）

调度规则（华哥 2026-08-17 定，2026-08-17 修订）：
  - 同事(8人) → MiniMax-M3（固定，一次性配置，不在本脚本）
  - 玉芬(default) → MiniMax-M3 + minimax-cn（直接写在 config.yaml，**永远不被本脚本切换**，
                  华哥 8/17 明确要求"直接配置 minimax，不要走 cc switch"，
                  玉芬是核心 agent 不允许因切换脚本波动）
  - Codex → 峰谷调度（仅本脚本管理）：
      高峰(高价)时段 → deepseek-v4-flash
      空闲(低价)时段 → deepseek-v4-pro

提醒：高价时段 Codex 切换到 DeepSeek 时输出提醒（no_agent 直发飞书）。
只在模型变化时输出；无变化静默。
"""
import subprocess
from datetime import datetime
from pathlib import Path

HERMES = "/Users/hua/.hermes/hermes-agent/venv/bin/hermes"
YUFEN_CONFIG = Path("/Users/hua/.hermes/config.yaml")
CODEX_CONFIG = Path("/Users/hua/.codex/config.toml")


def is_work_hours(hour: int) -> bool:
    return (9 <= hour < 12) or (14 <= hour < 18)


def read_yufen_model() -> str:
    for line in YUFEN_CONFIG.read_text().splitlines():
        if line.startswith("model: "):
            return line.split(":", 1)[1].strip()
    return ""


def read_yufen_provider() -> str:
    for line in YUFEN_CONFIG.read_text().splitlines():
        if line.startswith("provider: "):
            return line.split(":", 1)[1].strip()
    return ""


def read_codex_model() -> str:
    for line in CODEX_CONFIG.read_text().splitlines():
        if line.startswith("model = "):
            return line.split('"')[1]
    return ""


def switch_yufen(model: str, provider: str) -> bool:
    """已废弃：玉芬(default)固定 minimax-cn，不走自动切换。华哥 8/17 明确"直接配置 minimax，不要走 cc switch"。
    保留函数仅用于兼容旧调用，永远 return False 并打印警告，让任何残留调用都不会改玉芬 config。"""
    print("⚠️ switch_yufen() 已禁用：玉芬(default)固定 MiniMax-M3 + minimax-cn，不再被脚本切换。"
          "如需修改玉芬模型，请直接编辑 /Users/hua/.hermes/config.yaml。",
          flush=True)
    return False


def switch_codex(model: str) -> bool:
    lines = CODEX_CONFIG.read_text().splitlines()
    new_lines, changed = [], False
    for line in lines:
        if line.startswith("model = "):
            nl = f'model = "{model}"'
            if line != nl:
                changed = True
                new_lines.append(nl)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    if changed:
        CODEX_CONFIG.write_text("\n".join(new_lines) + "\n")
    return changed


def main():
    now = datetime.now()
    work = is_work_hours(now.hour)

    # 玉芬(default)固定 minimax-cn，本脚本不触碰。
    # 只切 Codex（Codex 才是 DeepSeek 峰谷调度的主体）。
    codex_model = "deepseek-v4-flash" if work else "deepseek-v4-pro"
    period = "高峰(高价)时段" if work else "空闲(低价)时段"

    cur_codex = read_codex_model()
    if not cur_codex or cur_codex == codex_model:
        return  # 无变化，静默

    changed = False
    msgs = []
    ***SECRET*** = False

    if switch_codex(codex_model):
        msgs.append(f"Codex: {cur_codex} → {codex_model}")
        changed = True
        if work:
            ***SECRET*** = True

    if not changed:
        return

    if work and ***SECRET***:
        print(f"⚠️【高价时段提醒】{now.strftime('%m-%d %H:%M')} 进入 DeepSeek 高峰时段(9-12/14-18，价格=空闲2倍)")
        print(f"   Codex 已切 {codex_model}（高价时段使用 DeepSeek）")
        print(f"   玉芬保持 MiniMax-M3/minimax-cn（不切换）")
    else:
        print(f"[{now.strftime('%m-%d %H:%M')}] 进入{period}")
        print(f"   Codex: {cur_codex} → {codex_model}")
        print(f"   玉芬保持 MiniMax-M3/minimax-cn（不切换）")


if __name__ == "__main__":
    main()
