#!/usr/bin/env python3
# TODO(tech-debt): 用 Claude Code 重写时改用 yaml 库代替手写

import argparse
import os
import sys


TASK_ROOT = "/Users/hua/.hermes/state/tasks"

STATUS_DIRS = {
    "active": "active",
    "review": "active",
    "done": "done",
    "escalated": "escalated",
    "all": None,
}


def parse_yaml(filepath: str) -> dict:
    data = {}
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.startswith("#"):
            i += 1
            continue
        if ":" in line and not line.startswith(" "):
            key = line.split(":", 1)[0].strip()
            rest = line.split(":", 1)[1].strip()
            if rest == "|":
                value_lines = []
                i += 1
                while i < len(lines) and lines[i].startswith("  "):
                    value_lines.append(lines[i][2:].rstrip("\n"))
                    i += 1
                data[key] = "\n".join(value_lines)
                continue
            elif rest == "":
                items = []
                i += 1
                while i < len(lines) and lines[i].strip().startswith("- "):
                    items.append(lines[i].strip()[2:])
                    i += 1
                data[key] = items
                continue
            else:
                data[key] = rest
        i += 1
    return data


def collect_tasks(status: str, to_filter: str, from_filter: str, priority_filter: str) -> list:
    tasks = []
    dir_names = []
    if status == "all":
        for sub in ["active", "done", "escalated"]:
            d = os.path.join(TASK_ROOT, sub)
            if os.path.isdir(d):
                dir_names.append(d)
    elif status == "review":
        dir_names.append(os.path.join(TASK_ROOT, "active"))
    else:
        dir_names.append(os.path.join(TASK_ROOT, STATUS_DIRS[status]))

    for d in dir_names:
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".yaml"):
                continue
            filepath = os.path.join(d, fname)
            data = parse_yaml(filepath)
            task_id = data.get("task_id", fname.replace(".yaml", ""))
            task_to = data.get("to", "")
            task_from = data.get("from", "")
            task_priority = data.get("priority", "")
            task_status = data.get("status", "")
            task_goal = data.get("goal", "")
            task_due = data.get("due", "")
            task_context = data.get("context", "")

            # status filter for review
            if status == "review" and task_status != "review":
                continue
            if to_filter and task_to != to_filter:
                continue
            if from_filter and task_from != from_filter:
                continue
            if priority_filter and task_priority != priority_filter:
                continue

            tasks.append({
                "task_id": task_id,
                "to": task_to,
                "priority": task_priority,
                "goal": task_goal,
                "due": task_due,
                "status": task_status,
            })

    tasks.sort(key=lambda t: t["due"])
    return tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="列出任务")
    parser.add_argument("--status", default="active", choices=["active", "review", "done", "escalated", "all"], help="状态过滤 (默认 active)")
    parser.add_argument("--to", default="", help="接活方过滤")
    parser.add_argument("--from", dest="from_", default="", help="派活方过滤")
    parser.add_argument("--priority", default="", choices=["", "P0", "P1", "P2"], help="优先级过滤")

    args = parser.parse_args()
    tasks = collect_tasks(args.status, args.to, args.from_, args.priority)

    if not tasks:
        print("(无任务)")
        return

    header = f"{'task_id':<20} {'to':<12} {'priority':<10} {'goal':<40} {'due':<22} {'status':<14}"
    print(header)
    print("-" * len(header))
    for t in tasks:
        print(f"{t['task_id']:<20} {t['to']:<12} {t['priority']:<10} {t['goal']:<40} {t['due']:<22} {t['status']:<14}")


if __name__ == "__main__":
    main()
