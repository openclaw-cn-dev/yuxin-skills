#!/usr/bin/env python3
"""巨型 SKILL.md 瘦身：>100KB 入口文件降到 ≤90KB（persisted-output 饿死红线）
用法: 编辑 TARGETS 白名单（(path, keep_sections或None, note)）后 python3 skill_slim_exec.py
- keep=N: 按 ## 节切分保留前 N 节，其余外置 references/split_NN_slug.md + 正文留索引
- keep=None: 长行压缩模式（>2000字符的行截断外置 references/squeezed_lines.md）
- 二轮瘦身: 对仍超限的文件用更小 keep 再跑（round2 模式，脚本内注释）
配套 SOP: skill-curation-mechanics SKILL.md「巨型 SKILL.md 瘦身法」
2026-09-29 实测: 17 个巨型全部降到 ≤90KB（afu自进化175K→77K、老莫心跳164K→37K、zhenglishi-workflow 358K→54K）
"""
import os, re, shutil, datetime, json

TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
LIMIT = 90 * 1024

# (path, keep_sections 或 None=长行压缩, 说明)
TARGETS = [
    # 示例（跑前按当时实际 >100KB 文件清单重填）:
    # ("/Users/hua/.hermes/skills/afu-self-evolution-protocol/SKILL.md", 3, "patch陷阱+HOME劫持防御外置"),
]

def split_by_sections(text, keep):
    lines = text.split("\n")
    out_head, sections, cur_title, cur_body = [], [], None, []
    i = 0
    if lines and lines[0].strip() == "---":
        out_head.append(lines[0]); i = 1
        while i < len(lines) and lines[i].strip() != "---":
            out_head.append(lines[i]); i += 1
        if i < len(lines):
            out_head.append(lines[i]); i += 1
    for ln in lines[i:]:
        m = re.match(r"^## (.+)", ln)
        if m:
            if cur_title is not None:
                sections.append((cur_title, cur_body))
            cur_title, cur_body = m.group(1).strip(), [ln]
        else:
            if cur_title is None:
                out_head.append(ln)
            else:
                cur_body.append(ln)
    if cur_title is not None:
        sections.append((cur_title, cur_body))
    if keep is None or keep >= len(sections):
        return None, sections
    kept_text = "\n".join(out_head) + "\n" + "\n".join("\n".join(b) for _, b in sections[:keep])
    return kept_text, sections[keep:]

def squeeze_long_lines(text, max_line=2000, keep_head=1200, keep_tail=200):
    lines = text.split("\n")
    new_lines, squeezed = [], []
    for idx, ln in enumerate(lines):
        if len(ln) > max_line:
            squeezed.append((idx, len(ln), ln))
            new_lines.append(ln[:keep_head] + f"\n<!-- [slimmed 原行 {len(ln)} 字符，完整内容见 references/squeezed_lines.md] -->\n" + ln[-keep_tail:])
        else:
            new_lines.append(ln)
    return "\n".join(new_lines), squeezed

def main():
    arc = f"/Users/hua/.hermes/skills/.archive/slim_backup_{TS}"
    os.makedirs(arc, exist_ok=True)
    report = []
    for path, keep, note in TARGETS:
        if not os.path.exists(path):
            report.append({"path": path, "status": "MISSING"}); continue
        size0 = os.path.getsize(path)
        if size0 <= LIMIT:
            report.append({"path": path, "status": "SKIP-already-small"}); continue
        text = open(path, encoding="utf-8").read()
        ref_dir = os.path.join(os.path.dirname(path), "references")
        os.makedirs(ref_dir, exist_ok=True)
        shutil.copy2(path, os.path.join(arc, path.replace("/", "__")))
        if keep is not None:
            kept_text, moved = split_by_sections(text, keep)
            if kept_text is None:
                report.append({"path": path, "status": "SKIP-few-sections"}); continue
            entries = []
            for idx, (title, body) in enumerate(moved):
                slug = re.sub(r"[^\w\u4e00-\u9fff]+", "_", title)[:40]
                fn = f"split_{idx:02d}_{slug}.md"
                open(os.path.join(ref_dir, fn), "w", encoding="utf-8").write(
                    f"# [外置章节] {title}\n\n> 原 SKILL.md 章节，瘦身后外置。全文备份: .archive/slim_backup_{TS}/\n\n" + "\n".join(body))
                entries.append(fn)
            kept_text += "\n\n## 已外置章节索引（瘦身）\n" + "".join(f"- `{fn}` ← {t}\n" for (t, _), fn in zip(moved, entries))
        else:
            squeezed_text, squeezed = squeeze_long_lines(text)
            kept_text = squeezed_text
            if squeezed:
                with open(os.path.join(ref_dir, "squeezed_lines.md"), "w", encoding="utf-8") as f:
                    for idx, ln_len, ln in squeezed:
                        f.write(f"\n## 原第{idx+1}行（{ln_len} 字符）\n\n{ln}\n")
                kept_text += f"\n\n> [瘦身说明] {len(squeezed)} 条超长行已压缩，完整内容见 `references/squeezed_lines.md`\n"
        open(path, "w", encoding="utf-8").write(kept_text)
        report.append({"path": path, "status": "OK", "kb_before": size0//1024, "kb_after": os.path.getsize(path)//1024, "note": note})
    json.dump(report, open("/tmp/slim_report.json", "w"), ensure_ascii=False, indent=1)
    for r in report:
        print(r)

if __name__ == "__main__":
    main()
