#!/usr/bin/env python3
# TODO(tech-debt): 用 Claude Code 重写时改用 yaml 库代替手写

import argparse
import os
import sys
from datetime import datetime, timezone


BASE_DIR = "/Users/hua/.hermes/state/tasks/active"


def next_task_id() -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(BASE_DIR, exist_ok=True)
    existing = [f for f in os.listdir(BASE_DIR) if f.startswith(f"T-{today}-") and f.endswith(".yaml")]
    max_n = 0
    for fname in existing:
        try:
            n = int(fname.split("-")[-1].replace(".yaml", ""))
            if n > max_n:
                max_n = n
        except ValueError:
            pass
    return f"T-{today}-{max_n + 1:03d}"


def write_yaml(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for key, value in data.items():
            if isinstance(value, list):
                f.write(f"{key}:\n")
                for item in value:
                    f.write(f"  - {item}\n")
            elif isinstance(value, str) and "\n" in value:
                f.write(f"{key}: |\n")
                for line in value.splitlines():
                    f.write(f"  {line}\n")
            else:
                f.write(f"{key}: {value}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="创建任务 yaml")
    parser.add_argument("--from", dest="from_", default="yuxin", help="派活方 (默认 yuxin)")
    parser.add_argument("--to", required=True, help="接活方")
    parser.add_argument("--priority", default="P1", choices=["P0", "P1", "P2"], help="优先级 (默认 P1)")
    parser.add_argument("--goal", required=True, help="任务目标一句话")
    parser.add_argument("--context", default="", help="背景文字")
    parser.add_argument("--deliverable", action="append", required=True, help="验收物 (可用多次)")
    parser.add_argument("--due", required=True, help="截止时间 ISO 格式")
    parser.add_argument("--escalate", default="yuxin → huage", help="升级路径")

    args = parser.parse_args()
    task_id = next_task_id()
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    data = {
        "task_id": task_id,
        "from": args.from_,
        "to": args.to,
        "priority": args.priority,
        "goal": args.goal,
        "context": args.context,
        "deliverable": args.deliverable,
        "due": args.due,
        "escalate": args.escalate,
        "status": "assigned",
        "created_at": created_at,
    }

    filepath = os.path.join(BASE_DIR, f"{task_id}.yaml")
    write_yaml(filepath, data)
    print(f"✅ Task created: {task_id} 路径: {filepath}")


if __name__ == "__main__":
    main()
