#!/usr/bin/env python3
"""给 8 profile 的 AGENTS.md 加"写资料前必做"防护段(2026-08-04)

用法:python3 add_path_safety_section.py [--profile <名字>] [--dry-run]
"""
import argparse
import os
import sys

SAFETY_MARKER = "## 📍 写资料前必做(2026-08-04 新增,根因 zhenglishi 路径污染)"

SAFETY_SECTION = """

## 📍 写资料前必做(2026-08-04 新增,根因 zhenglishi 路径污染)

> 历史教训:8/3 我们发现 565 个调研 .md 误写到 profile 镜像的 home/Desktop/,
> 根因是 staging_save.py 第 45 行用 `os.path.expanduser("~")` 被 profile 的 $HOME 劫持。
> 8/4 已修源码 + 归档 565 文件,以后必须自检。

### 写资料前 30 秒自检(强制)

```bash
# 1. 看 $HOME 是不是 /Users/hua
echo "HOME=$HOME"
# ✅ 应该是: HOME=/Users/hua
# ❌ 如果是: HOME=/Users/hua/.hermes/profiles/<自己>/home/, 警告

# 2. 确认 staging_save.py 已是绝对路径(已修复)
grep "STAGING_DIR = " ~/.hermes/scripts/staging_save.py | head -2
# ✅ 应该是: STAGING_DIR = Path("/Users/hua/rkr_staging/文档中转站")
# ❌ 如果是: STAGING_DIR = Path(os.path.expanduser(...)), 警告华哥

# 3. 调用 staging_save 时,显式传 --source 和 --agent
python3 ~/.hermes/scripts/staging_save.py \\
  --title "<一句话标题>" \\
  --content @<你的 .md 文件> \\
  --source research \\
  --agent <你的名字>
```

### 严禁动作

- ❌ 手动 `cp` / `mv` 到 `~/rkr_staging/...`(必须走 staging_save,触发 scanner)
- ❌ 用 `Path.home() / "rkr_staging/..."`(被劫持)
- ❌ 在脚本里用 `os.path.expanduser("~")` 解析 RKR 路径(改用绝对路径)

### 误写自检命令

```bash
# 如果怀疑自己写错了,扫一下 profile home 是否有误写
find ~/.hermes/profiles/<自己>/home -path '*rkr_staging*' -name '*.md' 2>/dev/null
# 输出文件 = 0 才算正常
```

---

"""

PROFILES = ["maodou", "xiaobao", "afu", "heidou", "laomo", "quant", "zhenglishi", "community", "default"]
HERMES_ROOT = "/Users/hua/.hermes"


def process_profile(profile_name, dry_run=False):
    agents_path = f"{HERMES_ROOT}/profiles/{profile_name}/AGENTS.md"
    if not os.path.exists(agents_path):
        return False, f"❌ {profile_name}: AGENTS.md 不存在"

    with open(agents_path, "r", encoding="utf-8") as f:
        content = f.read()

    if SAFETY_MARKER in content:
        return True, f"⏭  {profile_name}: 已有防护段,跳过"

    if dry_run:
        return True, f"🔍 {profile_name}: 干跑 OK"

    # 在 "## 🛡️ 铁律 #1" 段前插入
    if "## 🛡️ 铁律 #1" in content:
        new_content = content.replace(
            "## 🛡️ 铁律 #1",
            SAFETY_SECTION + "## 🛡️ 铁律 #1",
            1,
        )
    else:
        # 兜底:在文件末尾追加
        new_content = content + SAFETY_SECTION

    with open(agents_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True, f"✅ {profile_name}: 防护段写入成功"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", help="只处理单个 profile")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    targets = {args.profile: True} if args.profile else {p: True for p in PROFILES}
    if args.profile and args.profile not in PROFILES:
        print(f"❌ 未知 profile: {args.profile}")
        sys.exit(1)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}处理 {len(targets)} 个 profile:")
    for p in targets:
        ok, msg = process_profile(p, dry_run=args.dry_run)
        print(msg)


if __name__ == "__main__":
    main()
