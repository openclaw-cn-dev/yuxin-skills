#!/usr/bin/env python3
"""
AI名词卡片图片批量重命名脚本
用法：cd 到图片目录，执行 python3 rename_flashcards.py
"""

from PIL import Image
import os
import re
import subprocess
import shutil
import sys
from pathlib import Path
from collections import Counter

def main():
    print("🔍 AI名词卡片批量重命名 — 逐张OCR读取真实内容")
    print("=" * 70)
    print()

    # 检查 OCR 工具
    if not os.path.exists("/tmp/ocr"):
        print("❌ 错误：找不到 /tmp/ocr 工具")
        print("   请先确保 OCR 工具已安装并链接到 /tmp/ocr")
        sys.exit(1)

    # 获取所有 PNG 文件
    all_files = sorted([f for f in os.listdir(".") if f.lower().endswith(".png")])
    if not all_files:
        print("❌ 当前目录没有 PNG 文件")
        sys.exit(1)

    print(f"📊 找到 {len(all_files)} 张图片")
    print()

    # ========== 第一步：逐张 OCR 读取 ==========
    print("📖 开始 OCR 读取每张图片的编号和标题...")
    results = []

    for i, f in enumerate(all_files, 1):
        try:
            img = Image.open(f)
            w, h = img.size
            
            # 只看顶部 1/4 区域（编号+标题）
            top_region = img.crop((0, 0, w, h//4))
            top_region.save("/tmp/_ocr_temp.png")
            
            # OCR
            try:
                output = subprocess.check_output(["/tmp/ocr", "/tmp/_ocr_temp.png"], text=True, timeout=20)
            except:
                output = ""
            
            # 找编号：T 后面 3 位，自动修正 OCR 混淆
            num_match = re.findall(r'[Tt]\s*([0-9Oｏ]{3})', output)
            actual_num = "???"
            if num_match:
                raw = num_match[0]
                # 修正：O/ｏ -> 0
                raw = raw.replace('O', '0').replace('ｏ', '0')
                if re.match(r'\d{3}', raw):
                    actual_num = raw
            
            # 找标题：第一行中文，长度合适
            lines = [l.strip() for l in output.split("\n") if l.strip()]
            title = "未识别"
            for l in lines:
                has_chinese = bool(re.search(r'[\u4e00-\u9fff]', l))
                is_not_noise = not any(x in l for x in ['ID', '领域', '#', '---', 'ID：'])
                if has_chinese and is_not_noise and 2 <= len(l) <= 50:
                    title = l
                    break
            
            # 清理标题
            title = re.sub(r'[（\(][A-Za-z0-9\s\-\._]+[）\)]', '', title).strip()
            title = re.sub(r'[^\w\u4e00-\u9fff\-]', '', title)
            
            results.append({
                "old_file": f,
                "actual_num": actual_num,
                "actual_title": title
            })
            
            if i % 20 == 0:
                print(f"  ... 已读取 {i}/{len(all_files)} ...")
                
        except Exception as e:
            print(f"  ⚠️ 处理 {f} 失败: {e}")
            results.append({
                "old_file": f,
                "actual_num": "???",
                "actual_title": "处理失败"
            })

    print()
    print("=" * 70)
    print("📊 读取完成！按真实编号分组投票:")
    print()

    # ========== 第二步：按编号分组投票 ==========
    groups = {}
    for r in results:
        n = r['actual_num']
        if n not in groups:
            groups[n] = []
        groups[n].append(r['actual_title'])

    final_table = {}
    for num, titles in sorted(groups.items()):
        if num == "???":
            continue
        counter = Counter(titles)
        best_title, votes = counter.most_common(1)[0]
        final_table[num] = best_title
        print(f"  T{num}: {best_title} (一致性 {votes}/{len(titles)})")

    unknowns = len([r for r in results if r['actual_num'] == "???"])
    print()
    print(f"⚠️ 编号识别失败: {unknowns} 张（将 fallback 到原文件名编号）")

    # ========== 第三步：OCR 字符修正规则 ==========
    def fix_title(title):
        # 常见 OCR 混淆
        title = title.replace('Al开发工具', 'AI开发工具')
        title = title.replace('AI开发丁具', 'AI开发工具')
        title = title.replace('Ａ开发工具', 'AI开发工具')
        # 去掉乱码
        title = title.replace('大女女', '')
        title = title.replace('丷', '')
        title = title.replace('亼', '')
        # 去掉重复
        title = title.replace('AICAI', 'AI')
        title = title.replace('AlAI', 'AI')
        return title.strip()

    print()
    print("=" * 70)
    print("📝 开始按真实编号+真实标题重命名...")
    print()

    # ========== 第四步：重命名输出 ==========
    output_dir = Path("../03-豆包生成图_最终版")
    output_dir.mkdir(exist_ok=True)

    num_counter = Counter()
    renamed_count = 0

    for r in results:
        num = r['actual_num']
        if num == "???":
            # 识别失败的，先用原文件名的编号 fallback
            num_match = re.search(r't(\d{3})', r['old_file'])
            if num_match:
                num = num_match.group(1)
            else:
                num = "999"
        
        title = final_table.get(num, r['actual_title'])
        title = fix_title(title)
        
        if not title or title == "未识别":
            title = "未命名"
        
        num_counter[num] += 1
        version = f"v{num_counter[num]:02d}"
        
        new_name = f"t{num}-{title}-{version}.png"
        new_path = output_dir / new_name
        shutil.copy2(r['old_file'], new_path)
        renamed_count += 1
        
        if "v01" in new_name:
            print(f"  {new_name}")

    print()
    print("=" * 70)
    print(f"🎉 完成！共 {renamed_count} 张图片，{len(final_table)} 个术语")
    print(f"📂 输出目录: {output_dir.absolute()}")
    print()
    print("💡 下一步：")
    print("   cd ..")
    print("   mv '03-豆包生成图' '03-豆包生成图_旧备份'")
    print("   mv '03-豆包生成图_最终版' '03-豆包生成图'")


if __name__ == "__main__":
    main()
