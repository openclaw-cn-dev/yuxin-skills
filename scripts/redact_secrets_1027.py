#!/usr/bin/env python
"""
Redactor 1027: git grep 驱动版（沿铁律 121 force-apply 兜底）。

不硬编码 target 列表 —— 扫描范围来自:
  git diff --name-only origin/main HEAD   (待推范围)
  + 当前工作区未提交文件

匹配规则:
  - cli_aaa[a-z0-9]{12,18}  → cli_aaa***
  - 32 字符 base64 风格 + 前缀 naW/cwI/CW + 文件内出现 >= 2 次 → na***i6n5

铁律 115: 自身源码 0 字面量（正则用字符串拼接构造）
"""
import re
import subprocess
from pathlib import Path

REPO = Path(r"C:\Users\Administrator\Desktop\yuxin-skills")

# 铁律 115: 源码内不出现目标字面量 —— 用拼接构造
PREFIX = "cli_" + "aaa"
APPID_RE = re.compile(PREFIX + r"[a-z0-9]{12,18}")
APPID_REDACTED = PREFIX + "***"
LONG_TOKEN_RE = re.compile(r"[a-z0-9]{32}")
SECRET_PREFIXES = ("na" + "W", "cw" + "I", "C" + "W")
SECRET_REDACTED = "na" + "***i6n5"


def git(*args):
    r = subprocess.run(
        ["git", "-C", str(REPO)] + list(args),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return r.stdout


def collect_targets():
    """待推范围 + 工作区未提交"""
    files = set()
    out = git("diff", "--name-only", "origin/main", "HEAD")
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        p = REPO / line
        if p.is_file():
            files.add(p)
    out = git("diff", "--name-only")
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        p = REPO / line
        if p.is_file():
            files.add(p)
    out = git("ls-files", "--others", "--exclude-standard")
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        p = REPO / line
        if p.is_file():
            files.add(p)
    return sorted(files)


def looks_like_secret(s: str, text: str) -> bool:
    if not s.startswith(SECRET_PREFIXES):
        return False
    return text.count(s) >= 2


def main():
    targets = collect_targets()
    total_files = 0
    total_appid = 0
    total_secret = 0
    for p in targets:
        try:
            txt = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        orig = txt
        n_appid = 0
        n_secret = 0
        for m in set(APPID_RE.findall(txt)):
            n_appid += txt.count(m)
            txt = txt.replace(m, APPID_REDACTED)
        for m in set(LONG_TOKEN_RE.findall(txt)):
            if looks_like_secret(m, txt):
                n_secret += txt.count(m)
                txt = txt.replace(m, SECRET_REDACTED)
        if txt != orig:
            p.write_text(txt, encoding="utf-8", newline="")
            total_files += 1
            total_appid += n_appid
            total_secret += n_secret
            print(f"OK  {p.relative_to(REPO)}  AppID={n_appid} Secret={n_secret}")
    print(f"\nscanned={len(targets)} files | modified={total_files} "
          f"| AppID={total_appid} | Secret={total_secret}")


if __name__ == "__main__":
    main()
