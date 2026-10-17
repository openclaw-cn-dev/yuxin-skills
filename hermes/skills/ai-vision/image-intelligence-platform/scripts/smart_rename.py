#!/usr/bin/env python3
"""
智能图片重命名 v2.0
集成：OCR解析 + 质量检测 + 相似度分组 + 标准化命名
用法：python3 smart_rename.py /path/to/image/directory
"""

import os
import sys
import re
import subprocess
import shutil
import json
from pathlib import Path
from collections import Counter, defaultdict

try:
    from PIL import Image
    import imagehash
    import numpy as np
    from scipy import ndimage
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    print("   请运行: pip install pillow imagehash numpy scipy")
    sys.exit(1)


def robust_number_detection(ocr_text):
    """增强版编号识别，解决 0/O I/l 混淆"""
    candidates = re.findall(r'[Tt]\s*([0-9A-Za-zｏｌ]{3})', ocr_text)
    if not candidates:
        return None
    
    raw = candidates[0].upper()
    
    correction_map = {
        'O': '0', 'Ｏ': '0',
        'I': '1', 'Ｌ': '1', 'ｌ': '1',
        'Z': '2',
        'S': '5',
        'B': '8'
    }
    
    result = []
    for c in raw:
        result.append(correction_map.get(c, c))
    
    final = ''.join(result)
    if re.match(r'^\d{3}$', final):
        return final
    return None


def extract_title(ocr_text):
    """从 OCR 文本中提取标题"""
    lines = [l.strip() for l in ocr_text.split("\n") if l.strip()]
    
    for l in lines:
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', l))
        is_not_noise = not any(x in l for x in ['ID', '领域', '#', '---', 'ID：', '——'])
        if has_chinese and is_not_noise and 2 <= len(l) <= 50:
            title = l
            title = re.sub(r'[（\(][A-Za-z0-9\s\-\._]+[）\)]', '', title).strip()
            title = re.sub(r'[^\w\u4e00-\u9fff\-]', '', title)
            return title
    
    return "未命名"


def calculate_quality_score(img_path):
    """综合质量评分 0-100"""
    try:
        img = Image.open(img_path)
        img_gray = img.convert('L')
        arr = np.array(img_gray)
        
        # 1. 清晰度
        laplacian = ndimage.laplace(arr)
        clarity = np.var(laplacian)
        clarity_score = min(100, clarity / 50) * 0.3
        
        # 2. 对比度
        contrast = np.std(arr)
        contrast_score = min(100, contrast / 30) * 0.25
        
        # 3. 亮度
        mean_bright = np.mean(arr)
        if 80 <= mean_bright <= 200:
            brightness_score = 0.2
        else:
            brightness_score = max(0, 0.2 - abs(mean_bright - 140) / 300)
        
        # 4. 色彩完整性
        w, h = img.size
        footer = img.crop((0, int(h*0.85), w, h))
        footer_arr = np.array(footer.convert('HSV'))
        sat_mean = np.mean(footer_arr[:, :, 1])
        if sat_mean < 20:
            color_score = 0.075
        elif sat_mean < 50:
            color_score = 0.175
        else:
            color_score = 0.25
        
        total_score = (clarity_score + contrast_score + brightness_score + color_score) * 100
        
        return {
            "total": round(total_score, 1),
            "clarity": round(clarity_score * 100 / 0.3, 1),
            "contrast": round(contrast_score * 100 / 0.25, 1),
            "brightness": round(brightness_score * 100 / 0.2, 1),
            "color_integrity": round(color_score * 100 / 0.25, 1),
            "pass": total_score >= 70
        }
    except Exception as e:
        return {
            "total": 0,
            "error": str(e),
            "pass": False
        }


def fix_title_ocr_errors(title):
    """修正常见 OCR 错误"""
    title = title.replace('Al开发工具', 'AI开发工具')
    title = title.replace('AI开发丁具', 'AI开发工具')
    title = title.replace('Ａ开发工具', 'AI开发工具')
    title = title.replace('大女女', '')
    title = title.replace('丷', '')
    title = title.replace('亼', '')
    title = title.replace('AICAI', 'AI')
    title = title.replace('AlAI', 'AI')
    return title.strip()


def group_by_similarity(image_paths, threshold=0.9):
    """按图片相似度分组"""
    print("🔍 计算图片感知哈希...")
    hashes = {}
    for i, path in enumerate(image_paths):
        try:
            h = imagehash.dhash(Image.open(path), hash_size=16)
            hashes[path] = h
        except:
            hashes[path] = None
        if (i+1) % 50 == 0:
            print(f"   ... 已计算 {i+1}/{len(image_paths)}")
    
    print("📊 相似度分组...")
    groups = defaultdict(list)
    grouped = set()
    
    for i, path1 in enumerate(image_paths):
        if path1 in grouped or hashes[path1] is None:
            continue
            
        h1 = hashes[path1]
        current_group = [path1]
        grouped.add(path1)
        
        for path2 in image_paths[i+1:]:
            if path2 in grouped or hashes[path2] is None:
                continue
                
            h2 = hashes[path2]
            similarity = 1 - (h1 - h2) / len(h1.hash) ** 2
            
            if similarity >= threshold:
                current_group.append(path2)
                grouped.add(path2)
        
        groups[f"group_{len(groups):03d}"] = current_group
    
    print(f"   分成 {len(groups)} 组")
    return dict(groups)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 smart_rename.py /path/to/image/directory")
        sys.exit(1)
    
    img_dir = Path(sys.argv[1])
    if not img_dir.exists():
        print(f"❌ 目录不存在: {img_dir}")
        sys.exit(1)
    
    print("=" * 70)
    print("🚀 智能图片重命名 v2.0")
    print("=" * 70)
    print()
    
    # 获取所有图片
    images = sorted([str(img_dir / f) for f in os.listdir(img_dir) 
                     if f.lower().endswith('.png')])
    print(f"📂 找到 {len(images)} 张图片")
    print()
    
    # ========== 阶段 1: OCR + 质量检测 ==========
    print("📖 阶段 1: OCR 解析 + 质量检测")
    print("-" * 50)
    
    results = []
    for i, img_path in enumerate(images, 1):
        try:
            img = Image.open(img_path)
            w, h = img.size
            
            # 只 OCR 顶部区域
            top_region = img.crop((0, 0, w, h//4))
            top_region.save("/tmp/_ocr_temp.png")
            
            try:
                ocr_text = subprocess.check_output(
                    ["/tmp/ocr", "/tmp/_ocr_temp.png"], 
                    text=True, timeout=20
                )
            except:
                ocr_text = ""
            
            num = robust_number_detection(ocr_text)
            title = extract_title(ocr_text)
            title = fix_title_ocr_errors(title)
            quality = calculate_quality_score(img_path)
            
            results.append({
                "path": img_path,
                "filename": os.path.basename(img_path),
                "detected_num": num,
                "detected_title": title,
                "quality": quality,
                "ocr_text": ocr_text[:200]
            })
            
            if i % 20 == 0:
                print(f"   ... 已处理 {i}/{len(images)}")
                
        except Exception as e:
            print(f"   ⚠️ {os.path.basename(img_path)}: {e}")
            results.append({
                "path": img_path,
                "filename": os.path.basename(img_path),
                "detected_num": None,
                "detected_title": "处理失败",
                "quality": {"total": 0, "pass": False},
                "error": str(e)
            })
    
    print()
    
    # ========== 阶段 2: 相似度分组（解决编号识别失败） ==========
    print("🔗 阶段 2: 相似度分组补全编号")
    print("-" * 50)
    
    unknown_images = [r['path'] for r in results if r['detected_num'] is None]
    print(f"   编号识别失败: {len(unknown_images)} 张")
    
    if unknown_images:
        groups = group_by_similarity(unknown_images)
        
        # 每组分配一个临时编号
        group_num_counter = 900
        for group_name, group_images in groups.items():
            for img_path in group_images:
                for r in results:
                    if r['path'] == img_path:
                        r['detected_num'] = f"G{group_num_counter}"
                        r['group_name'] = group_name
                        break
            group_num_counter += 1
        
        print(f"   已通过相似度补全 {len(unknown_images)} 张")
    
    print()
    
    # ========== 阶段 3: 按编号投票确定最终标题 ==========
    print("🗳️  阶段 3: 同编号标题投票")
    print("-" * 50)
    
    num_groups = defaultdict(list)
    for r in results:
        num = r['detected_num'] or '999'
        num_groups[num].append(r['detected_title'])
    
    final_titles = {}
    for num, titles in sorted(num_groups.items()):
        counter = Counter(titles)
        best_title, votes = counter.most_common(1)[0]
        final_titles[num] = best_title
        print(f"   {num}: {best_title} ({votes}/{len(titles)})")
    
    print()
    
    # ========== 阶段 4: 重命名输出 ==========
    print("💾 阶段 4: 重命名输出")
    print("-" * 50)
    
    output_dir = img_dir.parent / f"{img_dir.name}_final"
    output_dir.mkdir(exist_ok=True)
    
    num_counter = Counter()
    renamed = 0
    
    for r in results:
        num = r['detected_num'] or '999'
        title = final_titles.get(num, r['detected_title'])
        quality = r['quality']
        
        num_counter[num] += 1
        version = f"v{num_counter[num]:02d}"
        q_score = f"Q{quality['total']:03.0f}"
        
        new_name = f"t{num}-{title}-{version}-{q_score}.png"
        new_path = output_dir / new_name
        
        shutil.copy2(r['path'], new_path)
        r['new_filename'] = new_name
        renamed += 1
        
        if num_counter[num] == 1:
            status = "✅" if quality['pass'] else "⚠️"
            print(f"   {status} {new_name}")
    
    print()
    
    # ========== 生成报告 ==========
    print("📊 生成报告...")
    
    passed = sum(1 for r in results if r['quality']['pass'])
    avg_score = sum(r['quality']['total'] for r in results) / len(results)
    
    report = {
        "summary": {
            "total_images": len(results),
            "passed_quality": passed,
            "failed_quality": len(results) - passed,
            "average_quality_score": round(avg_score, 1),
            "unique_numbers": len(final_titles)
        },
        "titles": final_titles,
        "details": results
    }
    
    report_path = output_dir / "rename_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 人类可读摘要
    summary = f"""
{'='*70}
📊 智能重命名摘要
{'='*70}

📈 质量统计:
  总图片数: {len(results)}
  质量合格: {passed} ({passed/len(results)*100:.1f}%)
  质量不合格: {len(results)-passed}
  平均质量分: {avg_score:.1f} / 100

📝 编号统计:
  识别出 {len(final_titles)} 个唯一编号
  其中 {sum(1 for k in final_titles if k.startswith('G'))} 个为相似度分组补全

🏷️  术语列表:
"""
    for num, title in sorted(final_titles.items()):
        count = sum(1 for r in results if r['detected_num'] == num)
        summary += f"  t{num}: {title} ({count} 张)\n"
    
    summary += f"""
📂 输出目录: {output_dir.absolute()}
📄 详细报告: {report_path.name}

💡 下一步:
  1. 查看质量不合格的图片（Q070 以下）
  2. G 开头的分组需要人工分配真实编号
  3. 确认无误后替换原目录
"""
    
    summary_path = output_dir / "SUMMARY.txt"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(summary)
    print("=" * 70)
    print("✅ 全部完成！")


if __name__ == "__main__":
    main()
