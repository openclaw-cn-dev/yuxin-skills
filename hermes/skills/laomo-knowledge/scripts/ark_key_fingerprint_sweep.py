#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VOLC_ARK_API_KEY 全盘指纹扫描器 (R227 2026-09-05 沉淀, laomo-knowledge)

用途: 凭据污染一键诊断 — 扫描 main .env / 全部 profile .env / 嵌套 home .env /
     shell rc 文件 / config.yaml / launchctl getenv, 打印每个命中处的 key 指纹
     与 BAD/GOOD/OTHER 标签。
铁律: 永不打印 key 原值, 只打印指纹三元组 (len + md5[:8] + 标签)。

用法: python3 scripts/ark_key_fingerprint_sweep.py
已知指纹 (2026-09-05 实测): BAD = len=11 md5=c62d45aa; GOOD = len=46 md5=c21eb344
     指纹轮换后可用环境变量覆盖: SWEEP_BAD_MD5 / SWEEP_GOOD_MD5
退出码: 0 = 无 BAD 命中; 1 = 发现 BAD (需按 R216 SOP 修复); 2 = 运行错误
诊断须走本脚本文件, 勿用 inline python (R135/R216 scrubber 家族坑)。
"""
import glob
import hashlib
import os
import re
import subprocess
import sys

BAD_MD5 = os.environ.get("SWEEP_BAD_MD5", "c62d45aa")
GOOD_MD5 = os.environ.get("SWEEP_GOOD_MD5", "c21eb344")
KEY_RE = re.compile(r"VOLC_ARK_API_KEY\s*[=:]\s*[\"']?([A-Za-z0-9\-\.]+)[\"']?")


def fp(v):
    if not v:
        return None
    return hashlib.md5(v.encode()).hexdigest()[:8], len(v)


def tag_of(md5):
    if md5 == BAD_MD5:
        return "BAD"
    if md5 == GOOD_MD5:
        return "GOOD"
    return "OTHER"


def scan_file(path, hits):
    try:
        with open(path, errors="ignore") as f:
            for i, line in enumerate(f, 1):
                if "VOLC_ARK" not in line:
                    continue
                m = KEY_RE.search(line)
                if m:
                    md5, ln = fp(m.group(1))
                    hits.append(f"{path}:{i} [{tag_of(md5)} len={ln} md5={md5}]")
                else:
                    hits.append(f"{path}:{i} [unparseable]")
    except OSError:
        pass  # 文件不存在 = 正常跳过


def main():
    hits = []
    candidates = {"/Users/hua/.hermes/.env", "/Users/hua/.hermes/config.yaml", "/Users/hua/.env"}
    candidates |= set(glob.glob("/Users/hua/.hermes/profiles/*/.env"))
    candidates |= set(glob.glob("/Users/hua/.hermes/profiles/*/home/.hermes/.env"))
    candidates |= set(glob.glob("/Users/hua/.hermes/profiles/*/home/.hermes/profiles/*/.env"))
    candidates |= {"/Users/hua/" + n for n in
                   (".zshrc", ".zprofile", ".zshenv", ".bash_profile", ".profile", ".bashrc")}

    for p in sorted(candidates):
        scan_file(p, hits)

    print("=== 磁盘文件扫描命中 ===")
    print("\n".join(hits) if hits else "(no hits)")

    bad = [h for h in hits if "[BAD" in h]

    print("=== session env + launchctl getenv ===")
    env_val = os.environ.get("VOLC_ARK_API_KEY")
    if env_val:
        md5, ln = fp(env_val)
        t = tag_of(md5)
        print(f"session env: [{t} len={ln} md5={md5}]")
        if t == "BAD":
            # session env BAD + 磁盘全 GOOD = 正常瞬态 (session 启动时注入的旧值),
            # 不是修复失败; definitive 探测用 env -u 绕过即可 (见 r227 reference)
            bad.append("session env [BAD] (瞬态: 磁盘修好后本 session 仍携带旧值)")
    else:
        print("session env: (unset)")
    try:
        out = subprocess.run(["launchctl", "getenv", "VOLC_ARK_API_KEY"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        if out:
            md5, ln = fp(out)
            t = tag_of(md5)
            print(f"launchctl:   [{t} len={ln} md5={md5}]")
            if t == "BAD":
                bad.append("launchctl [BAD]")
        else:
            print("launchctl:   (empty)")
    except Exception as e:
        print(f"launchctl:   ERR {type(e).__name__}")

    print(f"=== 结论: {len(bad)} 处 BAD ===")
    for b in bad:
        print(f"  -> {b}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
