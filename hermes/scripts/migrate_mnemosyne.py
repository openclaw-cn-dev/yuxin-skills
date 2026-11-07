#!/usr/bin/env python3
"""迁移单个 profile 的 MEMORY.md 到 Mnemosyne（玉芬执行，2026-08-18）
用法: python3 migrate_mnemosyne.py <profile_name>
"""
import os, sys, re, shutil
from datetime import datetime
from pathlib import Path

ROOT = Path("/Users/hua/.hermes")


def split_sections(text):
    """按 § 拆分 MEMORY.md，返回非空段落列表"""
    parts = re.split(r'\n?\s*§\s*\n?', text)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # 跳过文件头（如 "# 阿福 MEMORY（自动注入每轮对话）"）
        if p.startswith("# "):
            continue
        # 去掉段落内残留的标题符号行首，保留正文
        out.append(p)
    return out


def classify_source(text):
    if any(k in text for k in ["名字", "角色", "Profile", "身份", "我是"]):
        return "identity"
    if any(k in text for k in ["偏好", "喜欢", "优先", "习惯", "不追求", "关注"]):
        return "preference"
    if any(k in text for k in ["端口", "PID", "Gateway", "模型", "API_KEY", "cron",
                               "launchd", "Ollama", "Docker", "WebSocket", "心跳",
                               "复活", "launchctl", ".env"]):
        return "environment"
    if any(k in text for k in ["华哥", "玉芬", "同事", "团队", "上级", "汇报", "共享"]):
        return "relationship"
    return "project"


def main():
    profile = sys.argv[1]
    profile_home = ROOT / "profiles" / profile
    mem = profile_home / "memories" / "MEMORY.md"
    if not mem.exists():
        print(f"[{profile}] 无 MEMORY.md，跳过")
        return

    # 环境变量必须在 import mnemosyne 之前设置
    os.environ["HERMES_HOME"] = str(ROOT)  # 共享 default 的 fastembed 缓存，避免重复下载
    os.environ["MNEMOSYNE_DATA_DIR"] = str(profile_home / "mnemosyne" / "data")

    import mnemosyne

    text = mem.read_text()
    sections = split_sections(text)
    print(f"[{profile}] 共 {len(sections)} 段记忆，开始迁移...")

    stored = 0
    for sec in sections:
        if len(sec) < 3:
            continue
        src = classify_source(sec)
        try:
            mid = mnemosyne.remember(sec, source=src, importance=0.8,
                                     scope="global", trust_tier="IMPORTED")
            if mid:
                stored += 1
                print(f"  ✓ [{src:12s}] {mid} | {sec[:40].replace(chr(10),' ')}")
            else:
                print(f"  ⊘ 被写过滤器拦截 | {sec[:40].replace(chr(10),' ')}")
        except Exception as e:
            print(f"  ✗ 失败 {e} | {sec[:40].replace(chr(10),' ')}")

    # 备份 + 写占位符
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = mem.with_name(mem.name + f".bak.mnemosyne_{ts}")
    shutil.copy2(mem, bak)

    placeholder = (
        f"# MEMORY (L1 已迁移)\n\n"
        f"持久记忆已迁移至 Mnemosyne（{datetime.now().strftime('%Y-%m-%d')} 完成）。\n\n"
        f"- Mnemosyne 为 primary，检索方式 `mnemosyne_recall`（语义检索）\n"
        f"- L2 长文档完整版: `~/hermes/memory_store/`\n"
        f"- 旧版备份: `{bak.name}`\n"
    )
    mem.write_text(placeholder)

    print(f"[{profile}] 完成: 存 {stored} 条，备份 → {bak.name}")


if __name__ == "__main__":
    main()
