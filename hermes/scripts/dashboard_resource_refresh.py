#!/usr/bin/env python3
"""总控大屏·资源板块轻量刷新(每4h no_agent)。

只重写 渔芯总控看板.md 中「## 十、电脑资源分配与使用情况」一段,
复用 control_dashboard.section_resources() 同一份代码,零漂移。
不动公司树、不跑全量扫描(那是每日 08:05 全量生成任务的活)。

watchdog 纪律: 水位健康 → stdout 空(静默); ⚠️ 紧张/板块缺失 → 输出一行告警。
"""
import sys
from pathlib import Path

DASH = Path("D:/yuxin/company/渔芯总控看板.md")
TOOLS = Path("D:/yuxin/company/07-环境配置/03-脚本与工程工具")

MARK = "## 十、"


def main() -> int:
    sys.path.insert(0, str(TOOLS))
    import control_dashboard as cd

    if not DASH.exists():
        print("[资源刷新] 看板文件不存在, 等待每日全量生成")
        return 1
    md = DASH.read_text(encoding="utf-8")
    start = md.find(MARK)
    if start < 0:
        print("[资源刷新] 看板缺少资源板块(旧版生成物), 等待下次全量生成覆盖")
        return 1
    nxt = md.find("\n## ", start + len(MARK))
    end = nxt + 1 if nxt >= 0 else len(md)  # 保留后续章节(含换行), 当前十是末段时取 EOF

    new_section = "\n".join(cd.section_resources())
    DASH.write_text(md[:start] + new_section + md[end:], encoding="utf-8")
    if "⚠" in new_section:
        # 只在紧张时输出 → 飞书告警; 正常静默
        for ln in new_section.splitlines():
            if "⚠" in ln or ln.startswith("| 内存") or ln.startswith("| CPU"):
                print(ln)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
