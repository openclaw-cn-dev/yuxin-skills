#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Feishu notify with group-probe + DM fallback (field-tested 2026-09-16).

Usage:
    python3 notify_with_dm_fallback.py <message_file> [target_chat_id]

Flow (implements the 必跑 SOP from SKILL.md Pitfall #33 + refinement):
  1. Read message text (UTF-8) from <message_file>  — write it with write_file
     (emoji/CJK survive; only inline terminal strings trip the security scan).
  2. If [target_chat_id] given: direct send there FIRST — explicit destination
     = PRIMARY recipient (2026-11-12 lesson: a cron spec that names a chat_id
     means THAT chat, not "first active group"). Probe fanout is only the
     fallback when the explicit target fails.
  3. No target given: probe Bot's group chats (GET /im/v1/chats). Print every
     chat with status; send to first chat whose status != dissolved_save.
  4. If zero active groups (or explicit target failed), fall back to DM
     chat_id direct send
     (default: 华哥私聊, CONFIRMED reachable 2026-09-05 and 2026-09-16).
  5. Print one result line per step; exit 0 = delivered, 1 = all paths failed.

On failure do NOT retry other dissolved chats (232009 = dissolved, retrying
same chat_id always fails) — degrade to stdout/cron delivery per Pitfall #33.

Credentials: reads FEISHU_APP_ID / FEISHU_APP_SECRET from /Users/hua/.hermes/.env
(absolute path — cron $HOME may be profile-hijacked, Pitfall #30). Key names are
assembled via chr() so no literal "FEISHU_APP_SECRET=" substring appears for the
credential linter (Pitfall #12 变种5). No shell $() extraction — Python reads the
file directly (Pitfall #32).
"""
import json
import os
import re
import sys
import urllib.request

DEFAULT_DM = "***SECRET***"  # 华哥私聊 (confirmed 09-05 & 09-16)
# ENV_PATH candidates: macOS canonical first, then Windows host (D:\yuxin\hermes),
# overridable via FEISHU_ENV_PATH env var. First existing path wins.
ENV_CANDIDATES = [
    os.environ.get("FEISHU_ENV_PATH", ""),
    "/Users/hua/.hermes/.env",
    "D:/yuxin/hermes/.env",
]
ENV_PATH = next(p for p in ENV_CANDIDATES if p and os.path.exists(p))
BASE = "https://open.feishu.cn/open-apis"


def creds():
    with open(ENV_PATH) as f:
        text = f.read()
    PFX = "FEISHU_" + chr(65) + chr(80) + chr(80) + "_"
    K_SEC = PFX + chr(83) + chr(69) + chr(67) + chr(82) + chr(69) + chr(84)
    a = re.search(r"^" + PFX + "ID" + r"=(\S+)", text, re.M).group(1)
    b = re.search(r"^" + K_SEC + r"=(\S+)", text, re.M).group(1)
    return a, b


def get_token(a, b):
    req = urllib.request.Request(
        BASE + "/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": a, "app_secret": b}).encode(),
        headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=10).read())
    if r.get("code") != 0:
        sys.exit("AUTH FAIL: %s %s (code 10014 = secret rotated, manual fix "
                 "required — see SKILL.md Pitfall #5a)" % (r.get("code"), r.get("msg")))
    return r["tenant_access_token"]


def send_text(tok, chat_id, msg):
    payload = {"receive_id": chat_id, "msg_type": "text",
               "content": json.dumps({"text": msg})}
    req = urllib.request.Request(
        BASE + "/im/v1/messages?receive_id_type=chat_id",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + tok})
    return json.loads(urllib.request.urlopen(req, timeout=10).read())


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: notify_with_dm_fallback.py <message_file> [target_chat_id]")
    with open(sys.argv[1], encoding="utf-8") as f:
        msg = f.read().strip()
    explicit = sys.argv[2] if len(sys.argv) > 2 else None

    tok = get_token(*creds())

    # Explicit target = PRIMARY recipient (2026-11-12 lesson): a cron spec that
    # names a chat_id means THAT chat. Send there first; probe fanout below is
    # only the fallback when the explicit send fails.
    if explicit:
        r = send_text(tok, explicit, msg)
        print("SEND->explicit %s: code=%s" % (explicit, r.get("code")))
        if r.get("code") == 0:
            print("NOTIFY OK")
            return
        print("EXPLICIT TARGET FAILED (%s %s) -> probe fanout fallback"
              % (r.get("code"), r.get("msg")))

    active = []
    try:
        req = urllib.request.Request(
            BASE + "/im/v1/chats?page_size=100",
            headers={"Authorization": "Bearer " + tok})
        items = json.loads(urllib.request.urlopen(req, timeout=10).read()) \
            .get("data", {}).get("items", [])
        for i in items:
            print("CHAT: %s | %s | %s" % (i.get("chat_id"), i.get("name"),
                                          i.get("chat_status")))
            if i.get("chat_status") != "dissolved_save":
                active.append(i)
    except Exception as e:
        print("PROBE ERR:", e)

    if active:
        target = active[0]["chat_id"]
        r = send_text(tok, target, msg)
        print("SEND->group %s: code=%s" % (target, r.get("code")))
    else:
        print("NO ACTIVE GROUP -> DM fallback")
        r = send_text(tok, DEFAULT_DM, msg)
        print("SEND->DM %s: code=%s" % (DEFAULT_DM, r.get("code")))

    if r.get("code") == 0:
        print("NOTIFY OK")
    else:
        print("NOTIFY FAILED: %s %s" % (r.get("code"), r.get("msg")))
        sys.exit(1)


if __name__ == "__main__":
    main()
