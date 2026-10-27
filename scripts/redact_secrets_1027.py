#!/usr/bin/env python
"""
Redactor 1027: git 驱动版（沿铁律 121 force-apply 兜底 / 145 git grep 驱动）。

扫描范围（全部来自 git 状态，不硬编码）:
  - 待推范围: git diff --name-only origin/main HEAD
  - 工作区:   git diff --name-only
  - 未跟踪:   git ls-files --others --exclude-standard

匹配:
  - cli_aaa[a-z0-9]{12,18}                      -> cli_aaa***
  - 32 字符 base64 风格 + 前缀 naW/cwI/CW      -> na***i6n5
    (仅当同一文件内出现 >= 2 次, 沿铁律 115/116)

铁律 115: 自身源码 0 目标字面量（正则/前缀用字符串拼接构造）。
"""
import re
import subprocess
from pathlib import Path

REPO = Path(r"C:\Users\Administrator\Desktop\yuxin-skills")

PREFIX = "cli_" + "aaa"
APPID_RE = re.compile(PREFIX + r"[a-z0-9]{12,18}")
APPID_REDACTED = PREFIX + "***"
LONG_TOKEN_RE = re.compile(r"[A-Za-z0-9]{32}")
SECRET_PREFIXES = ("na" + "W", "cw" + "I", "C" + "W")
SECRET_REDACTED = "na" + "***i6n5"


def git(*args):
    # core.quotePath=false —— 否则非 ASCII 路径被转义成 "\346\227\272..."，
    # REPO / 转义串 不存在 → 中文名文件全部漏扫（1027 验证实测）
    r = subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", str(REPO)] + list(args),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return r.stdout


def collect_targets():
    """待推范围 + 工作区未提交 + 未跟踪"""
    files = set()
    for cmd in (
        ("diff", "--name-only", "origin/main", "HEAD"),
        ("diff", "--name-only"),
        ("ls-files", "--others", "--exclude-standard"),
    ):
        for line in git(*cmd).splitlines():
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


def redact_text(txt: str):
    """-> (new_txt, n_appid, n_secret)"""
    n_appid = n_secret = 0
    for m in set(APPID_RE.findall(txt)):
        n_appid += txt.count(m)
        txt = txt.replace(m, APPID_REDACTED)
    for m in set(LONG_TOKEN_RE.findall(txt)):
        if looks_like_secret(m, txt):
            n_secret += txt.count(m)
            txt = txt.replace(m, SECRET_REDACTED)
    return txt, n_appid, n_secret


def process(p: Path):
    """字节级处理，保留原行尾符（text 模式会把 CRLF 洗成 LF）"""
    raw = p.read_bytes()
    try:
        txt = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    # 保留原始行尾：用 newline='' 语义 —— 手动拆分
    crlf = b"\r\n" in raw
    txt = txt.replace("\r\n", "\n")
    new, n_appid, n_secret = redact_text(txt)
    if new == txt:
        return None
    out = new.replace("\n", "\r\n") if crlf else new
    p.write_bytes(out.encode("utf-8"))
    return n_appid, n_secret


def main():
    targets = collect_targets()
    total_files = total_appid = total_secret = 0
    for p in targets:
        res = process(p)
        if res is None:
            continue
        n_appid, n_secret = res
        total_files += 1
        total_appid += n_appid
        total_secret += n_secret
        print(f"OK  {p.relative_to(REPO)}  AppID={n_appid} Secret={n_secret}")
    print(f"\nscanned={len(targets)} files | modified={total_files} "
          f"| AppID={total_appid} | Secret={total_secret}")


if __name__ == "__main__":
    main()
