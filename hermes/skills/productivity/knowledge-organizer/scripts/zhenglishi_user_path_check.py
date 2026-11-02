#!/usr/bin/env python3
"""整理师 cron 心跳 — 用户指定路径 + 标准路径双重验证（2026-07-30）。

When cron prompt specifies a NON-STANDARD path (e.g. `任务派发/整理师/`) instead
of the standard `任务派发/学习助手/`, this script:

  1. Validates user-specified root token is accessible (catches typos / drift).
  2. Enumerates ALL `任务派发` candidate tokens at that root (currently 4 in
     华哥's drive — duplicate from historical RKR_PROBE_TEST, LookForge, etc.).
  3. For each candidate, searches both:
       - the user-specified subfolder (e.g. `整理师`)
       - the standard subfolder (`学习助手`)
  4. Reports independently and prints the standard
     `✅ 学习助手 当前无待处理任务` string EVEN IF the user-specified path is
     empty — because cron grep contracts depend on that exact output.

Reuses canonical functions via importlib so we don't duplicate credentials / token
logic from `zhenglishi_task_check.py`. See `references/cron-mode-constraints.md`
for the importlib pattern rationale.

Exit codes:
  0 = no tasks anywhere
  1 = tasks found (any folder)
  2 = API/credential error

Output expectations (cron grep pattern):
  ✅ 学习助手 当前无待处理任务     (verbatim, must include)
  === 找到 任务派发 文件夹: N 个 === (debug visibility)
  整理师子文件夹: M 个              (per-candidate)
  学习助手子文件夹: K 个            (per-candidate)
"""
import importlib.util
import sys

CANON = "/Users/hua/.hermes/skills/productivity/knowledge-organizer/scripts/zhenglishi_task_check.py"
USER_ROOT = "Vb83fsimklzqKDdd0dHcc3g2nhd"
STANDARD = "VsMRfTb3qlj4tJd3V7ncJTL6noe"  # `任务派发/学习助手/`


def load_canon():
    spec = importlib.util.spec_from_file_location("ko_task_check", CANON)
    if spec is None or spec.loader is None:
        raise RuntimeError("canonical task checker unavailable at " + CANON)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def files_of(mod, token, folder):
    res = mod.list_folder(token, folder, page_size=100)
    if res.get("code", 0) != 0:
        raise RuntimeError("Feishu API error for folder " + folder + ": " + str(res))
    return (res.get("data") or {}).get("files") or []


def main():
    user_subfolder = sys.argv[1] if len(sys.argv) > 1 else "整理师"

    mod = load_canon()
    token = mod.get_token()

    root_files = files_of(mod, token, USER_ROOT)
    print("=== 用户指定路径验证 ===", flush=True)
    print("根目录可访问: yes; 根条目: " + str(len(root_files)), flush=True)

    candidates = [x for x in root_files
                  if x.get("type") == "folder" and x.get("name") == "任务派发"]
    print("=== 找到 任务派发 文件夹: " + str(len(candidates)) + " 个 ===", flush=True)

    user_hits = []
    standard_hits = []
    for parent in candidates:
        children = files_of(mod, token, parent.get("token"))
        user_kids = [x for x in children
                     if x.get("type") == "folder" and x.get("name") == user_subfolder]
        standard_kids = [x for x in children
                         if x.get("type") == "folder" and x.get("name") == "学习助手"]
        print("任务派发 " + str(parent.get("token"))
              + " | " + user_subfolder + "子文件夹: " + str(len(user_kids))
              + " | 学习助手子文件夹: " + str(len(standard_kids)), flush=True)
        for folder in user_kids:
            user_hits.extend([x for x in files_of(mod, token, folder.get("token"))
                              if x.get("type") != "folder"])
        for folder in standard_kids:
            standard_hits.extend([x for x in files_of(mod, token, folder.get("token"))
                                  if x.get("type") != "folder"])

    print("指定路径" + user_subfolder + "待处理文件数: " + str(len(user_hits)), flush=True)
    print("标准学习助手入口待处理文件数: " + str(len(standard_hits)), flush=True)

    for item in user_hits:
        print("[TASK][" + user_subfolder + "] " + str(item.get("name"))
              + " | " + str(item.get("token")), flush=True)
    for item in standard_hits:
        print("[TASK][学习助手] " + str(item.get("name"))
              + " | " + str(item.get("token")), flush=True)

    if not standard_hits:
        print("✅ 学习助手 当前无待处理任务", flush=True)

    return 1 if user_hits or standard_hits else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("FEISHU_PATH_CHECK_ERROR: " + repr(exc), flush=True)
        raise SystemExit(2)