#!/usr/bin/env python3
"""
图片质量检测工具
用法：python3 quality_check.py /path/to/images [threshold]
默认阈值 70 分
"""

import os
import sys
import json
import shutil
from pathlib import Path
from collections import Counter

try:
    from PIL import Image
    import numpy as np
    from scipy import ndimage
except ImportError as e:
    print(f"❌ 缺少依赖: {e}")
    sys.exit(1)


def calculate_quality_score(img_path):
    """综合质量评分 0-100"""
    try:
        img = Image.open(img_path)
        img_gray = img.convert('L')
        arr = np.array(img_gray)
        
        # 1. 清晰度（拉普拉斯方差）
        laplacian = ndimage.laplace(arr)
        clarity = np.var(laplacian)
        clarity_score = min(100, clarity / 50) * 0.3
        
        # 2. 对比度（标准差）
        contrast = np.std(arr)
        contrast_score = min(100, contrast / 30) * 0.25
        
        # 3. 亮度分布
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
            "pass": total_score >= threshold
        }
    except Exception as e:
        return {
            "total": 0,
            "error": str(e),
            "pass": False
        }


def main():
    if len(sys.argv) < 2:
        print("用法: python3 quality_check.py /path/to/images [threshold]")
        print("  threshold: 质量合格分数，默认 70")
        sys.exit(1)
    
    img_dir = Path(sys.argv[1])
    global threshold
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 70
    
    print("=" * 70)
    print(f"🔍 图片质量检测 (合格线: {threshold} 分)")
    print("=" * 70)
    print()
    
    images = sorted([f for f in os.listdir(img_dir) if f.lower().endswith('.png')])
    print(f"📂 找到 {len(images)} 张图片")
    print()
    
    # 创建输出目录
    passed_dir = img_dir / "_quality_passed"
    failed_dir = img_dir / "_quality_failed"
    passed_dir.mkdir(exist_ok=True)
    failed_dir.mkdir(exist_ok=True)
    
    # 检测
    results = []
    for i, img_file in enumerate(images, 1):
        path = img_dir / img_file
        score = calculate_quality_score(path)
        
        results.append({
            "file": img_file,
            "score": score
        })
        
        if score['pass']:
            shutil.copy2(path, passed_dir / img_file)
        else:
            shutil.copy2(path, failed_dir / img_file)
        
        if i % 20 == 0:
            print(f"   ... 已检测 {i}/{len(images)}")
    
    print()
    print("=" * 70)
    
    # 统计
    passed = sum(1 for r in results if r['score']['pass'])
    avg_score = sum(r['score']['total'] for r in results) / len(results)
    
    # 分数分布
    score_ranges = Counter()
    for r in results:
        s = r['score']['total']
        if s >= 90:
            score_ranges['90-100'] += 1
        elif s >= 80:
            score_ranges['80-89'] += 1
        elif s >= 70:
            score_ranges['70-79'] += 1
        elif s >= 60:
            score_ranges['60-69'] += 1
        else:
            score_ranges['0-59'] += 1
    
    summary = f"""
📊 检测摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总图片数: {len(results)}
质量合格: {passed} ({passed/len(results)*100:.1f}%)
质量不合格: {len(results)-passed}
平均质量分: {avg_score:.1f} / 100

📈 分数分布:
"""
    for rng in ['90-100', '80-89', '70-79', '60-69', '0-59']:
        count = score_ranges.get(rng, 0)
        bar = '█' * int(count / len(results) * 30)
        summary += f"  {rng:>6s}: {bar} {count} 张\n"
    
    summary += f"""
📂 输出目录:
  合格: {passed_dir.absolute()}
  不合格: {failed_dir.absolute()}

⚠️ 质量最差 Top 10:
"""
    
    for r in sorted(results, key=lambda x: x['score']['total'])[:10]:
        if not r['score']['pass']:
            summary += f"  {r['file']}: {r['score']['total']} 分\n"
    
    print(summary)
    
    # 保存 JSON 报告
    report = {
        "threshold": threshold,
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "average_score": round(avg_score, 1),
            "score_distribution": dict(score_ranges)
        },
        "results": results
    }
    
    report_path = img_dir / "quality_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    summary_path = img_dir / "QUALITY_SUMMARY.txt"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n📄 详细报告已保存: {report_path}")


if __name__ == "__main__":
    main()
