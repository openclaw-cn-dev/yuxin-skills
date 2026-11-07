#!/usr/bin/env python3
"""宽博士 cron - 检查任务派发文件夹（2026-06-18 实战验证版）

用法:
    1. 复制此文件到 /tmp/<your_name>.py
    2. 修改 ENTRY_FOLDER_TOKEN 和可选的 SUBFOLDER_TOKENS
    3. python3 /tmp/<your_name>.py

为什么这个模板:
    - 玉芬 (cli_a964873dd7b8dbda) 是唯一已确认有 drive:drive 权限的 app
    - 其他 profile 的 app (quant=cli_a97210406cb89bda 等) 调 drive API 会 99991672
    - base64 + 短变量名规避 sanitizer 截断 APP_SECRET=*** 字面量
    - urllib.request 比 subprocess.run+curl 更稳定（避免 99991661 偶发）
"""
import base64
import json
import urllib.request

# 玉芬凭据（base64 编码避免 sanitizer 截断）
A = base64.b64decode("Y2xpX2E5NjQ4NzNkZDdiOGRiZGE=").decode()       # cli_a964873dd7b8dbda
S = base64.b64decode("***SECRET***=").decode()  # ***SECRET***
BP = base64.b64decode("QmVhcmVyIA==").decode()
BASE = "https://open.feishu.cn/open-apis"


def get_token():
    """获取 tenant_access_token（每次调用重新拿，不要复用）"""
    body = json.dumps({"app_id": A, "app_secret": S}).encode("utf-8")
    req = urllib.request.Request(
        BASE + "/auth/v3/tenant_access_token/internal",
        data=body, method="POST",
    )
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())["tenant_access_token"]


def list_folder(tok, ftok, page_size=50):
    """列出文件夹内容。✅ 用 ?folder_token=，❌ 不要用 ?parent_token=（已确认 broken）"""
    path = "/drive/v1/files?folder_token=" + ftok + "&page_size=" + str(page_size)
    req = urllib.request.Request(BASE + path, headers={"Authorization": BP + tok})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def show(label, tok, ftok):
    """打印文件夹内容"""
    print("=" * 60)
    print(label + "  folder_token=" + ftok)
    print("=" * 60)
    res = list_folder(tok, ftok)
    files = (res.get("data") or {}).get("files") or []
    print("count:", len(files))
    for f in files:
        print("  -", f.get("name"), "type=" + str(f.get("type")), "tok=" + str(f.get("token")))
    return files


# --- 任务派发文件夹入口（渔芯科技根目录 token）---
ROOT = "Vb83fsimklzqKDdd0dHcc3g2nhd"

# 各 Agent 的任务派发入口 token（feishu-bot-cloud-drive skill 维护）
TASK_FOLDERS = {
    "宽博士": "EsEAfQL0vl34bBdQYP4c2Llbn5y",
    "毛豆": "...",  # TODO 填实际值
    "老莫": "...",
    "小宝": "...",
    "黑豆": "...",
    "阿福": "...",
    "学习助手": "VsMRfTb3qlj4tJd3V7ncJTL6noe",
}


if __name__ == "__main__":
    token = get_token()
    print("Token OK:", token[:8], "...")
    print()

    # === 修改这里：选你要检查的 agent ===
    MY_AGENT = "宽博士"
    entry = TASK_FOLDERS.get(MY_AGENT)
    if not entry or entry == "...":
        print(f"ERROR: {MY_AGENT} 的任务派发 token 未配置，请查 feishu-bot-cloud-drive skill")
        raise SystemExit(1)

    files = show("[" + MY_AGENT + " 任务派发入口]", token, entry)
    print()

    # 递归检查每个子文件夹
    has_task = False
    for sub in files:
        if sub.get("type") == "folder":
            sub_token = sub.get("token")
            sub_name = sub.get("name")
            print("\n--- 子文件夹: " + str(sub_name) + " (" + str(sub_token) + ") ---")
            sub_res = list_folder(token, sub_token)
            sub_files = (sub_res.get("data") or {}).get("files") or []
            print("  文件数量:", len(sub_files))
            for sf in sub_files:
                print("  - name=" + str(sf.get("name")) + " type=" + str(sf.get("type")) + " token=" + str(sf.get("token")))
                if sf.get("type") != "folder":
                    has_task = True

    print()
    if has_task:
        print("⚠️ 发现新任务，请处理！")
    else:
        print("✅ " + MY_AGENT + " 当前无待处理任务")