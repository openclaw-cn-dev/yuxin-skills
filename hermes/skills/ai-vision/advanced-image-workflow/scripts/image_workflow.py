#!/usr/bin/env python3
"""
进阶图像工作流 - 批量处理、压缩、增强、分析
"""
import os
import sys
import hashlib
from pathlib import Path
from typing import List, Optional
from PIL import Image, ExifTags
from tqdm import tqdm

try:
    from PIL.Image import Resampling
except ImportError:
    Resampling = Image


class BatchProcessor:
    """批量图片处理器"""
    
    SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")
    
    def __init__(self, input_dir: str, output_dir: Optional[str] = None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else self.input_dir / "_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 收集所有图片
        self.images = self._collect_images()
        print(f"📸 找到 {len(self.images)} 张图片")
    
    def _collect_images(self) -> List[Path]:
        images = []
        for ext in self.SUPPORTED_FORMATS:
            images.extend(self.input_dir.glob(f"*{ext}"))
            images.extend(self.input_dir.glob(f"*{ext.upper()}"))
        return sorted(images)
    
    # === 格式转换 & 压缩 ===
    
    def compress(self, quality: int = 80, format: str = "webp"):
        """批量压缩优化"""
        print(f"\n🗜️  批量压缩 → {format.upper()} (质量 {quality})")
        
        for img_path in tqdm(self.images):
            try:
                img = Image.open(img_path)
                
                # 处理 EXIF 旋转
                img = self._fix_orientation(img)
                
                output_path = self.output_dir / f"{img_path.stem}.{format.lower()}"
                
                if format.lower() == "webp":
                    img.save(output_path, "WebP", quality=quality, lossless=False)
                elif format.lower() in ("jpg", "jpeg"):
                    img.convert("RGB").save(output_path, "JPEG", quality=quality, optimize=True)
                elif format.lower() == "png":
                    img.save(output_path, "PNG", optimize=True)
                
            except Exception as e:
                print(f"⚠️  {img_path.name}: {e}")
        
        self._print_result()
    
    def resize_all(self, width: int, height: Optional[int] = None, mode: str = "contain"):
        """
        批量调整尺寸
        
        mode:
          - contain: 等比缩放，不裁剪（默认）
          - cover: 等比缩放，居中裁剪填满
          - stretch: 拉伸变形
        """
        print(f"\n📐 批量调整尺寸 → {width}x{height or 'auto'} ({mode})")
        
        for img_path in tqdm(self.images):
            try:
                img = Image.open(img_path)
                img = self._fix_orientation(img)
                w, h = img.size
                
                if height is None:
                    # 只指定宽度，等比高度
                    ratio = width / w
                    target_h = int(h * ratio)
                    target_w, target_h = width, target_h
                else:
                    target_w, target_h = width, height
                
                if mode == "contain":
                    ratio = min(target_w / w, target_h / h)
                    new_w, new_h = int(w * ratio), int(h * ratio)
                    img = img.resize((new_w, new_h), Resampling.LANCZOS)
                    
                    # 居中放白底
                    result = Image.new("RGB", (target_w, target_h), "white")
                    result.paste(img, ((target_w - new_w) // 2, (target_h - new_h) // 2))
                    img = result
                    
                elif mode == "cover":
                    ratio = max(target_w / w, target_h / h)
                    new_w, new_h = int(w * ratio), int(h * ratio)
                    img = img.resize((new_w, new_h), Resampling.LANCZOS)
                    
                    # 居中裁剪
                    left = (new_w - target_w) // 2
                    top = (new_h - target_h) // 2
                    img = img.crop((left, top, left + target_w, top + target_h))
                    
                else:  # stretch
                    img = img.resize((target_w, target_h), Resampling.LANCZOS)
                
                output_path = self.output_dir / img_path.name
                img.save(output_path, quality=95)
                
            except Exception as e:
                print(f"⚠️  {img_path.name}: {e}")
        
        self._print_result()
    
    def rename_by_date(self, prefix: str = "img_"):
        """按拍摄日期重命名"""
        print(f"\n📅 按拍摄日期重命名")
        
        for img_path in tqdm(self.images):
            try:
                date_str = self._get_capture_date(img_path)
                if not date_str:
                    date_str = Path(img_path).stat().st_mtime.strftime("%Y%m%d_%H%M%S")
                
                # 处理重名
                counter = 0
                while True:
                    suffix = f"_{counter}" if counter > 0 else ""
                    new_name = f"{prefix}{date_str}{suffix}{img_path.suffix}"
                    new_path = self.output_dir / new_name
                    if not new_path.exists():
                        break
                    counter += 1
                
                # 复制文件
                import shutil
                shutil.copy2(img_path, new_path)
                
            except Exception as e:
                print(f"⚠️  {img_path.name}: {e}")
        
        self._print_result()
    
    def remove_duplicates(self, move_to: Optional[str] = None):
        """按 MD5 去重"""
        print(f"\n🔍 检测重复图片 (MD5)")
        
        seen = {}
        duplicates = []
        
        for img_path in tqdm(self.images):
            try:
                h = self._image_hash(img_path)
                if h in seen:
                    duplicates.append((img_path, seen[h]))
                else:
                    seen[h] = img_path
            except Exception as e:
                print(f"⚠️  {img_path.name}: {e}")
        
        print(f"找到 {len(duplicates)} 组重复图片")
        
        if move_to and duplicates:
            dup_dir = Path(move_to)
            dup_dir.mkdir(parents=True, exist_ok=True)
            
            for dup, original in duplicates:
                import shutil
                shutil.move(str(dup), str(dup_dir / dup.name))
                print(f"  📦 移动: {dup.name} → {dup_dir.name}/")
        
        return duplicates
    
    def add_watermark(
        self,
        text: str,
        position: str = "bottom-right",
        opacity: float = 0.3
    ):
        """批量添加水印"""
        print(f"\n💧 批量添加水印: '{text}'")
        
        from .image_utils import ImageEditor
        
        for img_path in tqdm(self.images):
            try:
                editor = ImageEditor(str(img_path))
                editor.add_watermark(text, position=position, opacity=opacity)
                editor.save(str(self.output_dir / img_path.name))
            except Exception as e:
                print(f"⚠️  {img_path.name}: {e}")
        
        self._print_result()
    
    # === 工具方法 ===
    
    def _fix_orientation(self, img: Image.Image) -> Image.Image:
        """修复 EXIF 旋转问题"""
        try:
            exif = img.getexif()
            if exif:
                orientation = exif.get(274)  # Orientation tag
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except:
            pass
        return img
    
    def _get_capture_date(self, img_path: Path) -> Optional[str]:
        """获取拍摄日期"""
        try:
            img = Image.open(img_path)
            exif = img.getexif()
            if exif:
                # DateTimeOriginal
                date_str = exif.get(36867) or exif.get(306)
                if date_str:
                    # 格式: "2024:07:13 14:30:25"
                    return date_str.replace(":", "").replace(" ", "_")
        except:
            pass
        return None
    
    def _image_hash(self, img_path: Path) -> str:
        """计算图片内容哈希（忽略 EXIF）"""
        img = Image.open(img_path)
        # 转成小缩略图再哈希，忽略微小差异
        thumb = img.resize((128, 128), Resampling.LANCZOS).convert("L")
        data = thumb.tobytes()
        return hashlib.md5(data).hexdigest()
    
    def _print_result(self):
        count = len(list(self.output_dir.glob("*")))
        total_size = sum(f.stat().st_size for f in self.output_dir.iterdir() if f.is_file())
        print(f"\n✅ 完成! 输出 {count} 个文件，共 {total_size / 1024 / 1024:.1f} MB")


# === 命令行入口 ===

def main():
    if len(sys.argv) < 2:
        print("""
用法:
  python image_workflow.py compress <输入目录> [输出目录] [--quality 80] [--format webp]
  python image_workflow.py resize <输入目录> <宽度>x<高度> [--mode contain|cover|stretch]
  python image_workflow.py rename <输入目录> [--pattern date]
  python image_workflow.py dedup <输入目录> [--move-to ./duplicates]
  python image_workflow.py watermark <输入目录> --text "水印文字"

示例:
  python image_workflow.py compress ./photos ./optimized
  python image_workflow.py resize ./products 1024x1024 --mode cover
""")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "compress":
        input_dir = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        quality = 80
        format = "webp"
        
        for i, arg in enumerate(sys.argv):
            if arg == "--quality": quality = int(sys.argv[i+1])
            if arg == "--format": format = sys.argv[i+1]
        
        processor = BatchProcessor(input_dir, output_dir)
        processor.compress(quality=quality, format=format)
    
    elif cmd == "resize":
        input_dir = sys.argv[2]
        size_str = sys.argv[3]
        w, h = map(int, size_str.split("x"))
        mode = "contain"
        
        for i, arg in enumerate(sys.argv):
            if arg == "--mode": mode = sys.argv[i+1]
        
        processor = BatchProcessor(input_dir)
        processor.resize_all(w, h, mode=mode)
    
    elif cmd == "rename":
        input_dir = sys.argv[2]
        processor = BatchProcessor(input_dir)
        processor.rename_by_date()
    
    elif cmd == "dedup":
        input_dir = sys.argv[2]
        move_to = None
        for i, arg in enumerate(sys.argv):
            if arg == "--move-to": move_to = sys.argv[i+1]
        
        processor = BatchProcessor(input_dir)
        processor.remove_duplicates(move_to=move_to)
    
    elif cmd == "watermark":
        input_dir = sys.argv[2]
        text = "Watermark"
        for i, arg in enumerate(sys.argv):
            if arg == "--text": text = sys.argv[i+1]
        
        processor = BatchProcessor(input_dir)
        processor.add_watermark(text)


if __name__ == "__main__":
    main()