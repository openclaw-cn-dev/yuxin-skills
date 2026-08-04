#!/usr/bin/env python3
# TODO(tech-debt): 用 Claude Code 重写时改用 yaml 库代替手写

import argparse
import os
import shutil
import sys
from datetime import datetime, timezone


ACTIVE_DIR = "/Users/hua/.hermes/state/tasks/active"
DONE_DIR = "/Users/hua/.hermes/state/tasks/done"
ESCALATED_DIR = "/Users/hua/.hermes/state/tasks/escalated"

VALID_STATUSES = {"assigned", "in_progress", "review", "done", "escalated", "revise"}

STATUS_DIR_MAP = {
    "done": DONE_DIR,
    "escalated": ESCALATED_DIR,
}

STAY_STATUSES = {"assigned", "in_progress", "review", "revise"}


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


def find_task(task_id: str) -> str:
    for root, dirs, files in os.walk("/Users/hua/.hermes/state/tasks"):
        for fname in files:
            if fname == f"{task_id}.yaml":
                return os.path.join(root, fname)
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="改任务状态")
    parser.add_argument("--task-id", required=True, help="任务 ID")
    parser.add_argument("--status", required=True, choices=sorted(VALID_STATUSES), help="新状态")
    parser.add_argument("--note", default="", help="备注")

    args = parser.parse_args()

    filepath = find_task(args.task_id)
    if not filepath:
        print(f"❌ 未找到任务: {args.task_id}", file=sys.stderr)
        sys.exit(1)

    data = parse_yaml(filepath)
    data["status"] = args.status
    if args.note:
        existing_notes = data.get("notes", "")
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        note_entry = f"[{timestamp}] {args.note}"
        if existing_notes:
            if isinstance(existing_notes, list):
                data["notes"] = existing_notes + [note_entry]
            else:
                data["notes"] = [existing_notes, note_entry]
        else:
            data["notes"] = [note_entry]

    target_dir = STATUS_DIR_MAP.get(args.status)
    if target_dir:
        new_path = os.path.join(target_dir, f"{args.task_id}.yaml")
        os.makedirs(target_dir, exist_ok=True)
        write_yaml(new_path, data)
        os.remove(filepath)
    else:
        write_yaml(filepath, data)

    print(f"✅ Task updated: {args.task_id} → {args.status}")


if __name__ == "__main__":
    main()
