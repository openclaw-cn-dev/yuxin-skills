#!/usr/bin/env python3
"""SKILL.md 巨型瘦身（>100KB 触发 skill_view 静默转 persisted-output，目标 ≤90KB）。

用法:
  python3 skill_slim.py <SKILL.md路径> --keep 4     # 切节模式：保留 frontmatter+前4个##节，其余外置 references/
  python3 skill_slim.py <SKILL.md路径> --squeeze    # 长行压缩：>2000字符的行截断，全文外置 references/squeezed_lines.md
同一文件可多轮执行（R2 轮换更小的 keep）。执行前自动备份到共享根 .archive/slim_backup_<ts>/。
外置文件带 [外置章节] 标记，正文追加「已外置章节索引」，内容零丢失。
"""
import os, re, sys, shutil, datetime, argparse

LIMIT = 90 * 1024

def backup(path):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    arc = f"/Users/hua/.hermes/skills/.archive/slim_backup_{ts}"
    os.makedirs(arc, exist_ok=True)
    shutil.copy2(path, os.path.join(arc, path.replace("/", "__")))
    return arc

def parse_sections(text):
    lines = text.split("\n"); head = []; secs = []; ct = None; cb = []
    i = 0
    if lines and lines[0].strip() == "---":
        head.append(lines[0]); i = 1
        while i < len(lines) and lines[i].strip() != "---":
            head.append(lines[i]); i += 1
        if i < len(lines):
            head.append(lines[i]); i += 1
    for ln in lines[i:]:
        m = re.match(r"^## (.+)", ln)
        if m:
            if ct is not None:
                secs.append((ct, cb))
            ct, cb = m.group(1).strip(), [ln]
        else:
            (head if ct is None else cb).append(ln)
    if ct is not None:
        secs.append((ct, cb))
    return head, secs

def slim_sections(path, keep):
    text = open(path, encoding="utf-8").read()
    head, secs = parse_sections(text)
    if keep >= len(secs):
        print(f"SKIP 只有 {len(secs)} 节，切节无意义；试 --squeeze")
        return False
    refd = os.path.join(os.path.dirname(path), "references")
    os.makedirs(refd, exist_ok=True)
    adds = []
    for idx, (t, b) in enumerate(secs[keep:]):
        slug = re.sub(r"[^\w\u4e00-\u9fff]+", "_", t)[:40]
        fn = f"split_{idx:02d}_{slug}.md"
        with open(os.path.join(refd, fn), "w", encoding="utf-8") as f:
            f.write(f"# [外置章节] {t}\n\n" + "\n".join(b))
        adds.append((fn, t))
    kept = "\n".join(head) + "\n" + "\n".join("\n".join(b) for _, b in secs[:keep])
    kept += "\n\n## 已外置章节索引（瘦身）\n" + "".join(f"- `references/{fn}` ← {t}\n" for fn, t in adds)
    open(path, "w", encoding="utf-8").write(kept)
    return True

def squeeze(path, max_line=2000, keep_head=1200, keep_tail=200):
    lines = open(path, encoding="utf-8").read().split("\n")
    new, squeezed = [], []
    for idx, ln in enumerate(lines):
        if len(ln) > max_line:
            squeezed.append((idx, ln))
            new.append(ln[:keep_head] + f"\n<!-- [slimmed 原{len(ln)}字，全文见 references/squeezed_lines.md] -->\n" + ln[-keep_tail:])
        else:
            new.append(ln)
    if not squeezed:
        print("SKIP 无超长行；用 --keep N 切节")
        return False
    refd = os.path.join(os.path.dirname(path), "references")
    os.makedirs(refd, exist_ok=True)
    with open(os.path.join(refd, "squeezed_lines.md"), "w", encoding="utf-8") as f:
        for idx, ln in squeezed:
            f.write(f"\n## 原第{idx+1}行（{len(ln)}字符）\n\n{ln}\n")
    open(path, "w", encoding="utf-8").write("\n".join(new))
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--keep", type=int, default=None, help="保留前 N 个 ## 节")
    ap.add_argument("--squeeze", action="store_true", help="长行压缩模式")
    a = ap.parse_args()
    size0 = os.path.getsize(a.path)
    if size0 <= LIMIT:
        print(f"SKIP 已 ≤90KB（{size0//1024}K）")
        return
    backup(a.path)
    ok = squeeze(a.path) if a.squeeze else (slim_sections(a.path, a.keep) if a.keep is not None else (print("需要 --keep N 或 --squeeze"), False)[1])
    if ok:
        print(f"OK {a.path}: {size0//1024}K -> {os.path.getsize(a.path)//1024}K")

if __name__ == "__main__":
    main()
