#!/usr/bin/env python3
"""
Codex 桌面端内存守护 (2026-08-20)

根因：ChatGPT.app(Codex 桌面端)每次启动/运行会重写 ~/.codex/config.toml，
把两条防崩溃配置冲掉：
  [features] computer_use = false
  [desktop]  ***SECRET*** = true
配置被冲掉后，Computer Use 画中画每 1.6s 拉一个 SkyComputerUseService 进程，
连不上 OpenAI(被墙) → 无限重连 → 进程堆积 → 内存耗尽 → OOM 崩溃循环。

本脚本做两件事(幂等，可反复跑)：
1. 补回被冲掉的防崩溃配置(精确 patch，不破坏 config 其他部分)
2. 清理堆积的 SkyComputerUseService 僵尸进程(>10 个)

watchdog 模式：无变化时静默(stdout 空)，有修复动作才输出一行，
配合 no_agent cron 使用，不会打扰华哥。
"""
import re
import subprocess
import sys

CONFIG = "/Users/hua/系统文件夹/Codex/config.toml"
ZOMBIE_THRESHOLD = 10


def ensure_config() -> list:
    """确保两条防崩溃配置存在。返回实际补回的项。"""
    try:
        c = open(CONFIG).read()
    except FileNotFoundError:
        return []

    changed = []

    # [desktop] 段补 ***SECRET*** = true
    if "***SECRET***" not in c:
        m = re.search(r"^\[desktop\]\s*$", c, re.M)
        if m:
            c = c[: m.end()] + "\***SECRET*** = true" + c[m.end():]
            changed.append("PiP-hide")
        else:
            # 无 [desktop] 段则追加
            c += "\n[desktop]\***SECRET*** = true\n"
            changed.append("PiP-hide(追加段)")

    # [features] 段补 computer_use = false
    if "computer_use = false" not in c:
        m = re.search(r"^\[features\]\s*$", c, re.M)
        if m:
            c = c[: m.end()] + "\ncomputer_use = false" + c[m.end():]
            changed.append("computer_use=false")
        else:
            c += "\n[features]\ncomputer_use = false\n"
            changed.append("computer_use=false(追加段)")

    if changed:
        open(CONFIG, "w").write(c)
    return changed


def zombie_count() -> int:
    """SkyComputerUseService 僵尸进程数。"""
    try:
        out = subprocess.run(
            ["pgrep", "-f", "SkyComputerUseService"],
            capture_output=True, text=True, timeout=10,
        )
        return len([l for l in out.stdout.splitlines() if l.strip()])
    except Exception:
        return 0


def main() -> None:
    msgs = []

    changed = ensure_config()
    if changed:
        msgs.append("补回配置: " + ", ".join(changed))

    n = zombie_count()
    if n > ZOMBIE_THRESHOLD:
        subprocess.run(["pkill", "-f", "SkyComputerUseService"], timeout=10)
        msgs.append(f"清理 {n} 个 SkyComputerUseService 僵尸进程")

    if msgs:
        print("Codex守护: " + "; ".join(msgs))
    # 无输出 = 静默(watchdog 模式)


if __name__ == "__main__":
    main()
