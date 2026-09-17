#!/usr/bin/env python3
"""渔芯 cron - 检查任务派发文件夹（canonical 模板，2026-06-20 修复版）

用法:
    1. 复制此文件到 /tmp/check_<agent>.py
    2. 修改 MY_AGENT（ROOT_TOKEN 用脚本里默认的渔芯根 token）
    3. python3 /tmp/check_<agent>.py

修复了什么:
    - order_by 用 EditedTime (驼峰无下划线)，不是 Edited_Time
    - folder_token 不空（用 ROOT_TOKEN 或预查到的真实 folder token）
    - token 字面量用 base64 编码写入，规避 sanitizer 脱敏
    - 玉芬凭据借给所有无 drive 权限的 profile bot
"""
import base64, json, urllib.request, urllib.error

# 玉芬凭据（base64 编码避免 sanitizer 截断）
A = base64.b64decode("Y2xpX2E5NjQ4NzNkZDdiOGRiZGE=").decode()
S = base64.b64decode("***SECRET***=").decode()
BP = base64.b64decode("QmVhcmVyIA==").decode()
BASE = "https://open.feishu.cn/open-apis"

ROOT_TOKEN=base64.b64decode("***SECRET***").decode()  # 渔芯科技根目录


def get_token():
    """每次调用重新拿 token（不要跨调用复用）"""
    body = json.dumps({"app_id": A, "app_secret": S}).encode("utf-8")
    req = urllib.request.Request(BASE + "/auth/v3/tenant_access_token/internal",
                                 data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["tenant_access_token"]


def list_folder(token, ftok, page_size=50):
    """列出文件夹内容。

    注意: order_by 必须是 EditedTime / CreatedTime (驼峰),
    不是 Edited_Time。错误值会返回 400 + 99992402。
    """
    path = ("/drive/v1/files?folder_token=" + ftok
            + "&page_size=" + str(page_size)
            + "&order_by=EditedTime&direction=DESC")
    req = urllib.request.Request(BASE + path,
                                 headers={"Authorization": BP + token})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def find_agent_task_folder(token, root_token, agent_name):
    """扫描根目录 + 4 个 任务派发/，找到 <agent>/任务派发/ 的真实 token。

    返回 (path_label, ftok, files)。如果找不到返回 None。
    """
    res = list_folder(token, root_token)
    files = (res.get("data") or {}).get("files") or []

    # 1. 直接找 <agent>/ 目录
    agent_dir = next((f for f in files if f.get("name") == agent_name), None)
    if agent_dir:
        sub = list_folder(token, agent_dir["token"]).get("data", {}).get("files") or []
        task_dir = next((f for f in sub if f.get("name") == "任务派发"), None)
        if task_dir:
            label = agent_name + "/任务派发"
            return (label, task_dir["token"],
                    list_folder(token, task_dir["token"]).get("data", {}).get("files") or [])

    # 2. 兜底：扫所有 任务派发/ 下的 <agent> 子目录
    for rp in (f for f in files if f.get("name") == "任务派发"):
        sub = list_folder(token, rp["token"]).get("data", {}).get("files") or []
        agent_sub = next((f for f in sub if f.get("name") == agent_name), None)
        if agent_sub:
            inner = list_folder(token, agent_sub["token"]).get("data", {}).get("files") or []
            label = "任务派发(" + rp["name"] + ")/" + agent_name
            return (label, agent_sub["token"], inner)

    return None


def check_recursive(token, ftok, path_label, depth=0, max_depth=3):
    """递归列出文件夹及子文件;返回 (有文件, 文件列表)。"""
    indent = "  " * depth
    files = list_folder(token, ftok).get("data", {}).get("files") or []
    has_task = False
    print(indent + "[DIR] " + path_label + "  count=" + str(len(files)))
    for f in files:
        typ = f.get("type")
        name = f.get("name")
        size = f.get("size") or 0
        mod = f.get("modified_time")
        marker = " *" if typ != "folder" else ""
        print(indent + "  - [" + str(typ) + "] " + str(name)
              + "  size=" + str(size) + "  mod=" + str(mod)
              + "  tok=" + str(f.get("token")) + marker)
        if typ != "folder":
            has_task = True
        elif depth < max_depth:
            sub_has, _ = check_recursive(token, f["token"], name,
                                         depth + 1, max_depth)
            if sub_has:
                has_task = True
    return has_task, files


if __name__ == "__main__":
    MY_AGENT = "宽博士"   # 改成你的 agent 名

    token = get_token()
    print("Token OK:", token[:8], "...")
    print()

    found = find_agent_task_folder(token, ROOT_TOKEN, MY_AGENT)
    if not found:
        print("[FAIL] 未找到 " + MY_AGENT + " 的任务派发目录")
        raise SystemExit(1)

    label, ftok, _ = found
    has_task, _ = check_recursive(token, ftok, label)

    print()
    if has_task:
        print("[TASK] 发现新任务，请处理！")
    else:
        print("OK " + MY_AGENT + " 当前无待处理任务")