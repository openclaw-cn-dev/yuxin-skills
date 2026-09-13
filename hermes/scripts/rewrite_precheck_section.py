#!/usr/bin/env python3
"""rewrite_precheck_section.py — 重写同事 AGENTS.md 的『写资料前必做』自检段为 v3 版(去 staging_save 流程)"""
import glob

NEW_SECTION = '''## 📍 写资料前必做(v3 · 2026-09-13 更新)

> 历史教训:8/3 曾发现 565 个调研 .md 误写到 profile 镜像的 home/Desktop/(staging_save.py 被 profile 的 $HOME 劫持)。
> **2026-09-13 起 staging_save.py / staging_query.py 已废用**(RKR scanner 停机、RKR API 已停),新标准如下。

### 写资料前 30 秒自检(强制)

```bash
# 1. 看 $HOME 是不是 /Users/hua
echo "HOME=$HOME"
# ✅ 应该是: HOME=/Users/hua
# ❌ 如果是: HOME=/Users/hua/.hermes/profiles/<自己>/home/, 警告

# 2. 确认落位目录存在(用绝对路径,不用 ~/)
ls /Users/hua/rkr_staging/文档库/A-渔芯科技/A2-公司运营/部门空间/
# 不存在就先 mkdir -p 创建,再写文件
```

### v3 入库方式

- ✅ **直接 write_file / cp 到落位目录**(见下方"资料落位速查"表)
- ❌ 不再走 staging_save.py 中转站(scanner 已停,文件会死在 ~/.hermes/staging/)
- ❌ 不用 `Path.home()` / `os.path.expanduser("~")` 拼文档库路径(一律绝对路径 /Users/hua/...)

### 严禁动作

- ❌ 手动写 `~/.hermes/staging/`(死区,scanner 永远看不到)
- ❌ 用 `Path.home() / "rkr_staging/..."`(被劫持)
- ❌ 在脚本里用 `os.path.expanduser("~")` 解析 RKR 路径(改用绝对路径)

### 误写自检命令

```bash
# 如果怀疑自己写错了,扫一下 profile home 是否有误写
find ~/.hermes/profiles/<自己>/home -path '*rkr_staging*' -name '*.md' 2>/dev/null
# 输出文件 = 0 才算正常
```

---
'''

OLD_MARKERS = [
    "## 📍 写资料前必做(2026-08-04 新增,根因 zhenglishi 路径污染)",
]

for f in sorted(glob.glob("/Users/hua/.hermes/profiles/*/AGENTS.md")):
    if "/default/" in f or "/test/" in f:
        continue
    name = f.split("/")[4]
    t = open(f, encoding="utf-8").read()
    start = None
    for m in OLD_MARKERS:
        if m in t:
            start = t.index(m)
            marker = m
            break
    if start is None:
        print(f"skip(无旧段): {name}")
        continue
    # 段落终止:下一个 "---" 分隔线(独立行)
    end = t.index("\n---\n", start)
    t = t[:start] + NEW_SECTION + t[end + len("\n---\n"):]
    open(f, "w", encoding="utf-8").write(t)
    print(f"rewritten: {name}")

# 终验:功能性 staging 引用应清零
print("\n--- 终验 ---")
for f in sorted(glob.glob("/Users/hua/.hermes/profiles/*/AGENTS.md")):
    if "/default/" in f or "/test/" in f:
        continue
    t = open(f, encoding="utf-8").read()
    n = sum(1 for line in t.splitlines()
            if ("staging_save" in line or "staging_query" in line)
            and "废用" not in line and "根因" not in line and "历史教训" not in line)
    print(f.split("/")[4], n)
