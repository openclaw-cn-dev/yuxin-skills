#!/usr/bin/env python3
"""rewrite_default_agents_md.py — 玉芬自己(default)AGENTS.md 的文档库引用升级到 v3"""
f = "/Users/hua/.hermes/profiles/default/AGENTS.md"
t = open(f, encoding="utf-8").read()

NEW_PRECHECK = '''## 📍 写资料前必做(v3 · 2026-09-13 更新)

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

- ✅ **直接 write_file / cp 到落位目录**(权威索引:`/Users/hua/rkr_staging/文档库/INDEX.md` v3)
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

# 1) 重写『写资料前必做』段
start = t.index("## 📍 写资料前必做(2026-08-04 新增,根因 zhenglishi 路径污染)")
end = t.index("\n---\n", start)
t = t[:start] + NEW_PRECHECK + t[end + len("\n---\n"):]

# 2) 调研清单路径(v1.7 段引用旧路径)
t = t.replace("`/Users/hua/rkr_staging/文档库/4-360行项目调研/调研项目清单.md`",
              "`/Users/hua/rkr_staging/文档库/A-渔芯科技/A3-基础设施/调研项目清单.md`(v3 位置,原 4-360行 已并入 C1)")

# 3) 写资料表
t = t.replace("| **通用知识调研** | `python3 ~/.hermes/scripts/staging_save.py --source research --agent yuxin` |",
              "| **通用知识调研** | 直接写 `~/rkr_staging/文档库/Z-共享/Z1-通用学科知识/` 贴切子目录(v3,不走中转站) |")
t = t.replace("| **玉芬整理笔记** | `python3 ~/.hermes/scripts/staging_save.py --source yuxin --agent yuxin` |",
              "| **玉芬整理笔记** | 直接写 `~/rkr_staging/文档库/A-渔芯科技/A2-公司运营/部门空间/`(v3) |")

# 4) 读资料块(三行)
old_read = """```bash
python3 ~/.hermes/scripts/staging_query.py search --query "..."
python3 ~/.hermes/scripts/staging_query.py stats
python3 ~/.hermes/scripts/staging_query.py list --lib knowledge --limit 20
```"""
new_read = """```bash
# v3: staging_query.py 已废用(RKR API 停)。直接 ls/grep 文档库找资料:
ls /Users/hua/rkr_staging/文档库/
grep -rl "<关键词>" /Users/hua/rkr_staging/文档库/A-渔芯科技/ --include="*.md" | head
```"""
t = t.replace(old_read, new_read)

# 5) 严禁清单前四条
t = t.replace("1. ❌ 直接写 `~/rkr_staging/文档库/1-通用知识/2-专业知识/4-360行项目调研/`(RKR 归档层,scanner 处理)",
              "1. ❌ 重建旧顶层目录 `1-通用知识/` `2-专业知识/` `3-公司项目资料/` `4-360行项目调研/`(已重组进 ABCZ 四版块,见 INDEX.md v3)")
t = t.replace("2. ❌ 直接读 `~/rkr_staging/文档库/通用知识库/` 文件系统(走 staging_query.py)",
              "2. ❌ 引用 `通用知识库/`、`cleaned/` 旧路径(已并入 Z-共享)")
t = t.replace("4. ❌ 写完归档层资料后 60 秒内就 `ls ~/rkr_staging/文档库/1-通用知识/` 检查(用 staging_query.py,不等)",
              "4. ❌ 写入 Z2/Z3/Z4、C2 手语数据集、`渔芯项目/`、`A3-基础设施/` 禁区")

open(f, "w", encoding="utf-8").write(t)

# 终验
bad = [line for line in t.splitlines()
       if ("staging_save" in line or "staging_query" in line or "4-360行项目调研/调研项目清单" in line)
       and "废用" not in line and "根因" not in line and "历史教训" not in line and "不再走" not in line]
print("残留功能性行:", len(bad))
for b in bad:
    print("  ", b.strip()[:100])
print("v3 标记:", "✓" if "v3" in t else "✗")
