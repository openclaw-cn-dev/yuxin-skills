#!/usr/bin/env python3
"""
豆包生成图智能重命名工具
格式: txxx-主题-vxx.png
   txxx = 编号 (t001, t002...)
   主题 = 图片内容主题的中文关键词
   vxx = 版本号 (同主题多张时递增)
"""
import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class SmartImageRenamer:
    """智能图片重命名器"""
    
    # 主题关键词映射 (根据文件名和视觉特征推断)
    THEME_KEYWORDS = {
        # 人物相关
        'teacher': '教师形象',
        'student': '学生学习',
        'business': '商务人物',
        'person': '人物肖像',
        'avatar': '人物头像',
        'girl': '女生形象',
        'boy': '男生形象',
        
        # 场景相关
        'office': '办公场景',
        'classroom': '教室场景',
        'meeting': '会议场景',
        'study': '学习场景',
        'home': '家庭场景',
        'future': '未来科技',
        'cyber': '赛博朋克',
        'nature': '自然风景',
        'city': '城市建筑',
        
        # 物品相关
        'card': '卡片设计',
        'icon': '图标设计',
        'logo': 'Logo设计',
        'ui': '界面设计',
        'product': '产品展示',
        'food': '美食摄影',
        
        # 风格相关
        '3d': '3D插画',
        'flat': '扁平化',
        'cartoon': '卡通风格',
        'anime': '动漫风格',
        'realistic': '写实摄影',
        'watercolor': '水彩风格',
        'oil': '油画风格',
        
        # 颜色
        'blue': '蓝色主题',
        'green': '绿色主题',
        'orange': '橙色主题',
        'red': '红色主题',
        'purple': '紫色主题',
    }
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self._ocr_reader = None
        self.theme_counter = defaultdict(int)
        self.results = []
    
    def _get_ocr_reader(self):
        if self._ocr_reader is None:
            try:
                import easyocr
                print("📚 加载 OCR 模型...")
                self._ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            except ImportError:
                print("⚠️  EasyOCR 未安装，使用文件名推断模式")
                self._ocr_reader = False
        return self._ocr_reader
    
    def analyze_image_theme(self, image_path: Path) -> str:
        """分析图片主题"""
        theme_hints = []
        
        # 1. 从文件名提取线索
        filename = image_path.name.lower()
        
        # 检查文件名中的关键词
        for keyword, theme_name in self.THEME_KEYWORDS.items():
            if keyword in filename:
                theme_hints.append(theme_name)
        
        # 2. 尝试 OCR 识别图片中的文字
        reader = self._get_ocr_reader()
        if reader:
            try:
                results = reader.readtext(str(image_path), detail=0)
                ocr_text = ' '.join(results).lower()
                
                # 从 OCR 文字中提取关键词
                for keyword, theme_name in self.THEME_KEYWORDS.items():
                    if keyword in ocr_text and theme_name not in theme_hints:
                        theme_hints.append(theme_name)
            except:
                pass
        
        # 3. 简单视觉特征分析
        try:
            from PIL import Image
            img = Image.open(image_path)
            
            # 尺寸特征
            w, h = img.size
            if abs(w - h) < 50:
                theme_hints.append("正方形")
            elif w > h * 1.5:
                theme_hints.append("横版")
            elif h > w * 1.5:
                theme_hints.append("竖版")
            
            # 色彩分析
            if img.mode == 'RGBA':
                theme_hints.append("透明背景")
            
        except:
            pass
        
        # 如果没找到明确主题，使用通用名
        if not theme_hints:
            return "AI生成图"
        
        # 取前 2 个最相关的主题
        return '-'.join(theme_hints[:2])
    
    def process_directory(
        self,
        input_dir: str,
        output_dir: str = None
    ):
        """批量处理目录"""
        input_path = Path(input_dir)
        
        # 输出目录
        if output_dir is None:
            output_path = input_path.parent / (input_path.name + "_已重命名")
        else:
            output_path = Path(output_dir)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 找出所有图片
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
            image_files.extend(input_path.glob(f'*{ext}'))
            image_files.extend(input_path.glob(f'*{ext.upper()}'))
        
        # 过滤掉 .DS_Store
        image_files = [f for f in image_files if not f.name.startswith('.')]
        image_files = sorted(image_files)
        
        print(f"📁 找到 {len(image_files)} 张图片")
        print(f"📂 输出目录: {output_path}")
        print("=" * 70)
        
        # 第一轮：先分析所有图片的主题
        print("🔍 第一步：分析所有图片主题...")
        theme_map = {}
        for i, img_path in enumerate(image_files, 1):
            print(f"  [{i}/{len(image_files)}] 分析: {img_path.name[:40]}...", end=" ")
            theme = self.analyze_image_theme(img_path)
            theme_map[img_path] = theme
            print(f"→ {theme}")
        
        print("\n" + "=" * 70)
        print("🗂️  主题统计:")
        theme_counts = defaultdict(int)
        for theme in theme_map.values():
            theme_counts[theme] += 1
        for theme, count in sorted(theme_counts.items(), key=lambda x: -x[1]):
            print(f"   {theme}: {count} 张")
        
        print("\n" + "=" * 70)
        print("📝 第二步：按格式重命名...")
        
        # 第二轮：重命名，同主题的加版本号
        for i, (img_path, theme) in enumerate(theme_map.items(), 1):
            self.theme_counter[theme] += 1
            version = self.theme_counter[theme]
            
            # 编号: t001, t002...
            number = f"t{i:03d}"
            
            # 版本: v01, v02...
            ver = f"v{version:02d}"
            
            # 清理主题中的特殊字符
            clean_theme = theme.replace('/', '-').replace('\\', '-')
            
            # 新文件名: txxx-主题-vxx.后缀
            ext = img_path.suffix.lower()
            new_name = f"{number}-{clean_theme}-{ver}{ext}"
            new_path = output_path / new_name
            
            print(f"  [{i}] {img_path.name[:45]:<45} → {new_name}")
            
            if not self.dry_run:
                shutil.copy2(img_path, new_path)
            
            self.results.append({
                'old_name': img_path.name,
                'new_name': new_name,
                'theme': theme,
                'number': number,
                'version': version
            })
        
        # 生成报告
        print("\n" + "=" * 70)
        print(f"✅ 处理完成! 共 {len(self.results)} 张图片")
        print(f"📂 输出目录: {output_path}")
        
        # 保存 CSV 日志
        import csv
        csv_path = output_path / "_重命名日志.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['编号', '主题', '版本', '新文件名', '原文件名'])
            for r in self.results:
                writer.writerow([
                    r['number'],
                    r['theme'],
                    r['version'],
                    r['new_name'],
                    r['old_name']
                ])
        
        print(f"📋 日志已保存: {csv_path}")


def main():
    if len(sys.argv) < 2:
        print("""
🎨 豆包生成图智能重命名工具

格式: txxx-主题-vxx.png
   txxx = 编号 (t001, t002...)
   主题 = 图片内容主题的中文关键词
   vxx = 版本号 (同主题多张时递增)

用法:
  python smart_rename.py <图片目录> [输出目录] [--dry-run]

示例:
  # 处理当前目录下的 03-豆包生成图
  python smart_rename.py "./03-豆包生成图"
  
  # 预览模式，不实际执行
  python smart_rename.py "./03-豆包生成图" --dry-run
  
  # 指定输出目录
  python smart_rename.py "./03-豆包生成图" "./已重命名"
""")
        return
    
    input_dir = sys.argv[1]
    output_dir = None
    dry_run = False
    
    for arg in sys.argv[2:]:
        if arg == '--dry-run':
            dry_run = True
        else:
            output_dir = arg
    
    if dry_run:
        print("⚠️  预览模式 - 不会实际复制文件")
        print()
    
    renamer = SmartImageRenamer(dry_run=dry_run)
    renamer.process_directory(input_dir, output_dir)


if __name__ == "__main__":
    main()