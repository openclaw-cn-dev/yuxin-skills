#!/usr/bin/env python3
"""
渔芯模型时段调度器 (2026-08-17 起生效)
规则：
  - 工作时段(9:00-12:00, 14:00-18:00): 玉芬(default) + Codex → deepseek-v4-flash
  - 非工作时段: 玉芬 + Codex → deepseek-v4-pro
  - 同事(7个)固定 MiniMax-M3，不在本脚本(一次性配置)

只在模型发生变化时才切换并输出；无变化静默(避免刷屏)。
"""
import subprocess
from datetime import datetime
from pathlib import Path

HERMES = "/Users/hua/.hermes/hermes-agent/venv/bin/hermes"
CONFIG = Path("/Users/hua/.hermes/config.yaml")
CODEX_CONFIG = Path("/Users/hua/.codex/config.toml")
START_DATE = datetime(2026, 8, 17).date()


def is_work_hours(hour: int) -> bool:
    return (9 <= hour < 12) or (14 <= hour < 18)


def read_yufen_model() -> str:
    try:
        import yaml
        d = yaml.safe_load(CONFIG.read_text())
        return d.get("model", "") or ""
    except Exception:
        return ""


def read_codex_model() -> str:
    try:
        for line in CODEX_CONFIG.read_text().splitlines():
            if line.startswith("model = "):
                return line.split('"')[1]
    except Exception:
        pass
    return ""


def switch_yufen(model: str) -> bool:
    r = subprocess.run([HERMES, "config", "set", "model", model],
                       capture_output=True, text=True, timeout=60)
    return r.returncode == 0


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
    if now.date() < START_DATE:
        return  # 未到开始日期，静默

    work = is_work_hours(now.hour)
    target = "deepseek-v4-flash" if work else "deepseek-v4-pro"
    period = "工作时段" if work else "非工作时段"

    changed = False
    msgs = []

    cur_yufen = read_yufen_model()
    if cur_yufen and cur_yufen != target:
        if switch_yufen(target):
            msgs.append(f"玉芬: {cur_yufen} → {target}")
            changed = True
        else:
            msgs.append(f"玉芬切换失败(当前 {cur_yufen})")

    cur_codex = read_codex_model()
    if cur_codex and cur_codex != target:
        if switch_codex(target):
            msgs.append(f"Codex: {cur_codex} → {target}")
            changed = True

    if changed:
        print(f"[{now.strftime('%m-%d %H:%M')}] {period} → {target}")
        for m in msgs:
            print(f"  {m}")


if __name__ == "__main__":
    main()
