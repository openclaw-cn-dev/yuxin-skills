#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""渔芯知识库自同步（no_agent watchdog）：扫描 rkr_staging 新笔记 → kb_ingest 增量上传。

- 幂等：状态文件记录已上传 sha256，重跑不重复（服务端另有内容哈希去重兜底）。
- 静默：无新文件时 stdout 为空，cron 不推送；有上传/错误才输出。
- domain 路径先验（保守）：明确养殖目录→aqua、工程目录→eng、AI 关键词→ai、其余→life。
  细粒度精确判域由 agent 主动上传（skill yuxin-kb-ingest）负责，本脚本只兜底漏传。

用法：python3 kb_auto_sync.py          # 增量上传新笔记
      python3 kb_auto_sync.py --dry-run # 只列待上传，不写库
"""
import json
import os
import re
import sys
import time
import hashlib
import urllib.request
import urllib.error

ROOT = "/Users/hua/rkr_staging/文档库"
ENV = "/Users/hua/.hermes/.env"
API = "https://lookforge.net/v1/admin/ingest"
STATE = "/Users/hua/.hermes/scripts/.kb_sync_state.json"
LOOKBACK_DAYS = 7  # 只同步最近 N 天内落盘的新笔记（增量兜底，旧笔记已在全量入库）

# 不扫描的目录（基础设施/未分类/管道产物/低质碎片/旧顶层/备份）
EXCLUDE_DIRS = {
    "A3-基础设施", "Z2-未分类堆积", "Z3-管道产物", "Z4-低质抓取碎片",
    "_audit", "_audit_backups", "cleaned", "通用知识库", "渔芯项目",
    "3-公司项目资料", "C-渔芯独雄兽", ".git", "__pycache__", "node_modules",
}
SKIP_FILENAMES = {"README.md", "INDEX.md"}
# 永久失败（内容问题，重试无用）：垃圾/空内容/超大/不存在
PERMANENT_CODES = {400, 404, 413, 422}


def load_token():
    try:
        with open(ENV, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("KB_ADMIN_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except OSError:
        return ""
    return ""


def judge_domain(path: str) -> str:
    p = path
    if "钓鱼" in p:  # 休闲钓鱼（非养殖）→ life
        return "life"
    if "B2-建筑" in p or "工程知识库" in p or "建筑" in p:
        return "eng"
    if re.search(r"养殖|RAS|循环水|土塘|水产|渔业|渔医|病害|水质|鱼病|饲料|增氧", p, re.I):
        return "aqua"
    if re.search(r"AI|智能|算法|机器学习|深度学习|大模型|提示词|神经网络|量化|Agent|开源|GitHub|代码|爬虫", p, re.I):
        return "ai"
    return "life"


def load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"done": {}}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE)


def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_md():
    cutoff = time.time() - LOOKBACK_DAYS * 86400
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if not fn.endswith(".md") or fn in SKIP_FILENAMES:
                continue
            abs_p = os.path.join(dirpath, fn)
            try:
                if os.path.getmtime(abs_p) < cutoff:
                    continue
            except OSError:
                continue
            out.append((abs_p, judge_domain(abs_p)))
    return out


def ingest(token, title, content, domain, source_url):
    payload = {"title": title, "content": content, "domain": domain}
    if source_url:
        payload["source_url"] = source_url
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        API, data=data, method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + token,
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


def main():
    dry = "--dry-run" in sys.argv
    token = load_token()
    if not token:
        print("✗ KB_ADMIN_TOKEN 缺失（/Users/hua/.hermes/.env）")
        sys.exit(1)

    state = load_state()
    done = state.get("done", {})
    files = scan_md()

    new = []
    for p, d in files:
        if sha256_file(p) not in done:
            new.append((p, d))

    if not new:
        return  # 静默：无新文件

    if dry:
        print(f"dry-run：待上传 {len(new)} 篇（共扫描 {len(files)} 篇）")
        for p, d in new[:50]:
            print(f"  [{d}] {os.path.relpath(p, ROOT)}")
        return

    ok = fail = skip = 0
    lines = []
    for p, domain in new:
        h = sha256_file(p)
        rel = os.path.relpath(p, ROOT)
        try:
            with open(p, encoding="utf-8") as f:
                content = f.read()
            if not content.strip():
                done[h] = True
                skip += 1
                continue
            # 跳过 PDF 二进制垃圾（寻元采集误把 PDF 字节存成 .md）
            head = content.lstrip()[:512]
            if head.startswith("%PDF") or "\x00" in head:
                done[h] = True
                skip += 1
                continue
            title = os.path.splitext(os.path.basename(p))[0][:300]
            res = ingest(token, title, content, domain, f"file://{p}")
            if res.get("ok"):
                ok += 1
                done[h] = True
                lines.append(f"✓ [{domain}] {rel} → {res.get('doc_id')} (dup={res.get('duplicate')})")
            else:
                fail += 1
                lines.append(f"✗ [{domain}] {rel}: {str(res)[:120]}")
        except urllib.error.HTTPError as e:
            if e.code in PERMANENT_CODES:
                done[h] = True  # 永久失败（垃圾/超大），标记已处理，避免 cron 无限重试
                skip += 1
                lines.append(f"⊘ [{domain}] {rel}: HTTP {e.code}（永久跳过）")
            else:
                fail += 1
                lines.append(f"✗ [{domain}] {rel}: HTTP {e.code}（待重试）")
        except Exception as e:  # noqa: BLE001
            fail += 1
            lines.append(f"✗ [{domain}] {rel}: {e}")
        time.sleep(2.0)  # 写限流 30/min，留余量

    save_state({"done": done})
    print(f"kb自同步：{ok} 成功 / {skip} 空跳过 / {fail} 失败（扫描 {len(files)} 篇，新增 {len(new)} 篇）")
    for l in lines:
        print(l)
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
