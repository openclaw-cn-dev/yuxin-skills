#!/usr/bin/env python3
"""RKR 知识库资料审查 —— 有效性 + 重复性 + 中间产物识别（自包含，可复用）

用法: python3 rkr_material_audit.py [ROOT] [--dup TOP_N]
默认 ROOT=/Users/hua/rkr_staging

输出:
  1. 全库统计（剪枝中间产物目录后）
  2. 文档类资料: 总数 / 空文件(0B) / 极小文件(<50B)
  3. 中间产物（扩展名黑名单）TOP 体积
  4. MD5 完全重复: 重复组数 / 多余副本数 / 浪费空间 / 最大重复组 TOP
  5. 写 /tmp/rkr_dup_groups.txt（每组保留 1 份，其余为待删）

⚠️ 关键坑（2026-11-02 实测）:
  - 文件名可能含 tab 字符 → 绝不能用 `size\\tpath` 中间清单，partition("\\t") 会错位报
    "ValueError: invalid literal"。必须 os.walk 现场 getsize，别生成中间清单。
  - postgres/redis 数据库物理文件（global/*、PG_VERSION 等 0 字节）会被 find -size 0
    误判为空文档，SKIP_DIRS 必须含 postgres / pg_logical / pgdata。
  - 全量 30 万+ 文档 MD5 读内容耗时数分钟，用 background + notify_on_complete 跑。
"""
import os, sys, hashlib
from collections import defaultdict

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/Users/hua/rkr_staging"
DUP_TOP = int(sys.argv[sys.argv.index("--dup") + 1]) if "--dup" in sys.argv else 20

DOC_EXTS = {'.md','.txt','.pdf','.docx','.doc','.html','.htm','.rst','.adoc','.tex','.org',
            '.csv','.xlsx','.xls','.pptx','.ppt','.ods','.odt'}
JUNK_EXTS = {'.npy','.mp4','.pyc','.pyo','.ds_store','.log','.pyi','.map','.ttf','.woff',
             '.woff2','.parquet','.png','.jpg','.jpeg','.gif','.svg','.mp3','.wav','.zip',
             '.tar','.gz','.7z','.zst','.dmg','.db','.sqlite','.sqlite3','.pickle','.pkl',
             '.pt','.bin','.so','.dylib','.a','.o','.class','.jar'}
SKIP_DIRS = {'venv','.venv','node_modules','.git','__pycache__','.tox','.mypy_cache',
             '.pytest_cache','chromadb','pgdata','redis','postgres','pg_logical',
             'backups','_archive','.archive','logs','log','_audit','_audit_backups',
             'cleaned','preview','manifest','digests','packages','__MACOSX'}

total_files = 0
total_size = 0
doc_files = 0
empty_docs = []
tiny_docs = []
junk = defaultdict(lambda: [0, 0])
other = defaultdict(lambda: [0, 0])
md5map = defaultdict(list)   # md5 -> [(size, path)]
skipped_dirs = 0

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames
                   if d not in SKIP_DIRS and not d.endswith('.venv')]
    skipped_dirs += len([d for d in dirnames if d in SKIP_DIRS])
    for fn in filenames:
        fp = os.path.join(dirpath, fn)
        ext = os.path.splitext(fn)[1].lower()
        try:
            size = os.path.getsize(fp)
        except OSError:
            continue
        total_files += 1
        total_size += size
        if ext in DOC_EXTS:
            doc_files += 1
            if size == 0:
                empty_docs.append(fp)
            elif size < 50:
                tiny_docs.append(fp)
            else:
                try:
                    with open(fp, "rb") as fh:
                        data = fh.read()
                    md5map[hashlib.md5(data).hexdigest()].append((size, fp))
                except OSError:
                    pass
        elif ext in JUNK_EXTS:
            junk[ext][0] += 1; junk[ext][1] += size
        else:
            other[ext][0] += 1; other[ext][1] += size

def gb(n): return f"{n/1024/1024/1024:.2f} GB"

print(f"=== 全库统计 ===")
print(f"文件总数: {total_files:,}")
print(f"总大小:   {gb(total_size)}")
print()
print(f"=== 文档类资料（md/txt/pdf/docx/html/csv/xlsx/pptx等）===")
print(f"文档文件数: {doc_files:,}")
print(f"空文件(0B): {len(empty_docs):,}")
print(f"极小文件(<50B): {len(tiny_docs):,}")
print()
print(f"=== 中间产物（建议排除）TOP15 ===")
for ext, (c, s) in sorted(junk.items(), key=lambda x: -x[1][1])[:15]:
    print(f"  {ext:10s} {c:>8,} 个  {gb(s)}")
print()
print(f"=== 其他类型（待人工判断）===")
for ext, (c, s) in sorted(other.items(), key=lambda x: -x[1][1])[:20]:
    print(f"  {ext:10s} {c:>8,} 个  {gb(s)}")

dup_groups = {k: v for k, v in md5map.items() if len(v) > 1}
dup_files = sum(len(v) for v in dup_groups.values())
wasted = sum((len(v) - 1) * v[0][0] for v in dup_groups.values())
print()
print(f"=== MD5 完全重复 ===")
print(f"唯一内容: {len(md5map):,}")
print(f"重复组数: {len(dup_groups):,}")
print(f"多余副本: {dup_files:,} (占文档 {dup_files/max(doc_files,1)*100:.1f}%)")
print(f"浪费空间: {gb(wasted)}")
print(f"\n=== 最大重复组 TOP{DUP_TOP}（按组内份数）===")
for md5, lst in sorted(dup_groups.items(), key=lambda x: -len(x[1]))[:DUP_TOP]:
    print(f"  [{len(lst):>3} 份] {lst[0][1]}")
    for _, fp in lst[1:3]:
        print(f"           └─ 重复: {fp}")

with open("/tmp/rkr_dup_groups.txt", "w") as f:
    for md5, lst in sorted(dup_groups.items(), key=lambda x: -len(x[1])):
        keep = lst[0][1]
        for _, fp in lst[1:]:
            f.write(f"{keep}\t{fp}\n")
print(f"\n[OK] 重复清单 /tmp/rkr_dup_groups.txt（{dup_files:,} 条待删，每组保留 1 份）")
