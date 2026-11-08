#!/usr/bin/env python3
"""
卡片编号自动重命名工具
功能: 识别图片中的编号文字，自动将文件重命名为编号
用法: python rename_by_card_number.py <图片目录> [输出目录]
"""
import os
import re
import sys
import shutil
from pathlib import Path
from typing import Optional, Tuple


class CardNumberRenamer:
    """卡片编号识别与重命名"""
    
    # 常见的编号模式：纯数字、字母+数字、带分隔符
    NUMBER_PATTERNS = [
        r'\bNO[.:：\s]*(\d{3,8})\b',      # NO.12345、NO：12345
        r'\b编号[.:：\s]*(\d{3,8})\b',     # 编号: 12345
        r'\bCard[.\s]*(\d{3,8})\b',        # Card 12345
        r'\b卡号[.:：\s]*(\d{3,8})\b',      # 卡号: 12345
        r'\bID[.:：\s]*(\d{3,8})\b',        # ID: 12345
        r'\b(\d{6,12})\b',                 # 纯 6-12 位数字（兜底）
    ]
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self._ocr_reader = None
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'duplicate': 0
        }
        self.used_numbers = set()
    
    def _get_ocr_reader(self):
        """延迟加载 OCR"""
        if self._ocr_reader is None:
            try:
                import easyocr
                print("📚 加载 OCR 模型... (首次运行需要下载模型)")
                self._ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            except ImportError:
                print("❌ 请先安装 OCR 依赖: pip install easyocr")
                sys.exit(1)
        return self._ocr_reader
    
    def extract_number(self, image_path: str) -> Optional[str]:
        """从图片中提取编号"""
        reader = self._get_ocr_reader()
        
        try:
            # 读取文字
            results = reader.readtext(image_path, detail=0)
            full_text = ' '.join(results)
            
            # 按优先级匹配编号模式
            for pattern in self.NUMBER_PATTERNS:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            # 如果没有匹配到特定模式，返回第一个找到的数字串
            all_numbers = re.findall(r'\d{4,}', full_text)
            if all_numbers:
                return all_numbers[0]  # 返回最长的那个
            
            return None
            
        except Exception as e:
            print(f"⚠️  识别失败 {Path(image_path).name}: {e}")
            return None
    
    def process_file(
        self,
        file_path: Path,
        output_dir: Path
    ) -> Tuple[bool, str]:
        """处理单个文件"""
        self.stats['total'] += 1
        
        print(f"\n[{self.stats['total']}] 📄 {file_path.name}")
        
        # 提取编号
        number = self.extract_number(str(file_path))
        
        if not number:
            print(f"   ❌ 未能识别编号")
            self.stats['failed'] += 1
            
            # 失败的文件复制到 output/failed/
            failed_dir = output_dir / "failed"
            failed_dir.mkdir(exist_ok=True)
            if not self.dry_run:
                shutil.copy2(file_path, failed_dir / file_path.name)
            return False, ""
        
        print(f"   ✅ 识别到编号: {number}")
        
        # 处理重名
        final_number = number
        counter = 1
        while final_number in self.used_numbers:
            final_number = f"{number}_{counter}"
            counter += 1
        
        if counter > 1:
            print(f"   ⚠️  编号重复，使用: {final_number}")
            self.stats['duplicate'] += 1
        
        self.used_numbers.add(final_number)
        
        # 重命名文件
        ext = file_path.suffix.lower()
        new_name = f"{final_number}{ext}"
        new_path = output_dir / new_name
        
        if self.dry_run:
            print(f"   🎯 [预览] 将重命名为: {new_name}")
        else:
            shutil.copy2(file_path, new_path)
            print(f"   🎯 已保存为: {new_name}")
        
        self.stats['success'] += 1
        return True, final_number
    
    def process_directory(
        self,
        input_dir: str,
        output_dir: Optional[str] = None
    ):
        """批量处理整个目录"""
        input_path = Path(input_dir)
        
        # 输出目录默认在输入目录下的 _renamed
        if output_dir is None:
            output_path = input_path / "_renamed"
        else:
            output_path = Path(output_dir)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 找出所有图片
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']
        image_files = []
        for ext in extensions:
            image_files.extend(input_path.glob(ext))
            image_files.extend(input_path.glob(ext.upper()))
        
        if not image_files:
            print(f"❌ 在 {input_dir} 中未找到图片文件")
            return
        
        print(f"📁 找到 {len(image_files)} 张图片")
        print(f"📂 输出目录: {output_path}")
        print("=" * 60)
        
        # 处理每张图片
        results = []
        for img_path in sorted(image_files):
            success, number = self.process_file(img_path, output_path)
            results.append({
                'original': img_path.name,
                'number': number,
                'success': success
            })
        
        # 输出报告
        print("\n" + "=" * 60)
        print(f"\n📊 处理完成报告:")
        print(f"   总计: {self.stats['total']} 张")
        print(f"   ✅ 成功: {self.stats['success']} 张")
        print(f"   ❌ 失败: {self.stats['failed']} 张")
        print(f"   ⚠️  重复: {self.stats['duplicate']} 张")
        print(f"\n   成功率: {self.stats['success']/self.stats['total']*100:.1f}%")
        
        # 保存映射表
        import csv
        csv_path = output_path / "_rename_log.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['原文件名', '识别编号', '状态'])
            for r in results:
                writer.writerow([
                    r['original'],
                    r['number'],
                    '成功' if r['success'] else '失败'
                ])
        
        print(f"\n📋 重命名日志已保存: {csv_path}")
        print(f"📂 处理后的文件在: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("""
🃏 卡片编号自动重命名工具

功能: 识别卡片图片中的编号文字，自动将文件重命名为对应编号

用法:
  python rename_by_card_number.py <图片目录> [输出目录] [--dry-run]

参数:
  <图片目录>       存放卡片图片的文件夹
  [输出目录]       重命名后文件保存位置（可选，默认在输入目录下 _renamed）
  --dry-run        预览模式，不实际执行重命名

支持的编号格式:
  NO.12345、编号: 12345、卡号 12345、Card 12345、纯数字串

示例:
  # 处理 cards 文件夹，输出到 cards/_renamed
  python rename_by_card_number.py ./cards

  # 指定输出目录
  python rename_by_card_number.py ./cards ./cards_renamed

  # 预览效果，不实际重命名
  python rename_by_card_number.py ./cards --dry-run
""")
        return
    
    input_dir = sys.argv[1]
    output_dir = None
    dry_run = False
    
    # 解析参数
    for arg in sys.argv[2:]:
        if arg == '--dry-run':
            dry_run = True
        else:
            output_dir = arg
    
    if dry_run:
        print("⚠️  预览模式 - 不会实际修改文件")
    
    renamer = CardNumberRenamer(dry_run=dry_run)
    renamer.process_directory(input_dir, output_dir)


if __name__ == "__main__":
    main()