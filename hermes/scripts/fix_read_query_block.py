#!/usr/bin/env python3
"""fix_read_query_block.py — 替换同事 AGENTS.md 里残留的多行 staging_query 读资料块"""
import re, glob

files = [p for p in glob.glob("/Users/hua/.hermes/profiles/*/AGENTS.md")
         if "/default/" not in p and "/test/" not in p]

read_new = '''```bash
# v3: staging_query.py 已废用(RKR API 停)。直接 ls/grep 文档库找资料:
ls /Users/hua/rkr_staging/文档库/
grep -rl "<关键词>" /Users/hua/rkr_staging/文档库/A-渔芯科技/ --include="*.md" | head
```'''

for f in files:
    t = open(f, encoding="utf-8").read()
    orig = t
    t = re.sub(r'```bash\npython3 ~/\.hermes/scripts/staging_query\.py search[^\n]*\npython3 ~/\.hermes/scripts/staging_query\.py stats\n```',
               read_new, t)
    t = re.sub(r'```bash\npython3 ~/\.hermes/scripts/staging_query\.py search[^\n]*\n```',
               read_new, t)
    if t != orig:
        open(f, "w", encoding="utf-8").write(t)
        print("fixed:", f.split("/")[4])

print("\n--- 残留统计(功能性引用,排除声明/历史行) ---")
for f in sorted(files):
    t = open(f, encoding="utf-8").read()
    n = 0
    for line in t.splitlines():
        if ("staging_save" in line or "staging_query" in line):
            if "废用" in line or "根因" in line or "历史教训" in line:
                continue
            n += 1
    print(f.split("/")[4], n)
