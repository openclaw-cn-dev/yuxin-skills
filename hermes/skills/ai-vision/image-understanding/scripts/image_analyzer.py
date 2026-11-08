#!/usr/bin/env python3
"""
图片理解与解析系统 (Image Understanding System)
功能: OCR文字提取、标签生成、图片描述、人脸检测、色彩分析、二维码识别
"""
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from PIL import Image, ImageDraw
import numpy as np


@dataclass
class AnalysisResult:
    """分析结果数据结构"""
    filename: str
    width: int
    height: int
    file_size: int
    tags: List[str]
    caption: str
    ocr_text: str
    faces: List[Dict]
    main_colors: List[Tuple[int, int, int]]
    qr_codes: List[str]


class ImageAnalyzer:
    """图片分析器 - 集成多种视觉理解能力"""
    
    def __init__(self, backend: str = "local"):
        self.backend = backend
        self._ocr_reader = None
        self._face_cascade = None
        
        # 通用标签映射（基于颜色和简单启发）
        self._scene_keywords = {
            "dark": ["夜景", "黑暗", "夜晚"],
            "bright": ["明亮", "晴天", "高光"],
            "warm": ["温暖", "日落", "黄金时刻"],
            "cool": ["冷色调", "阴天", "蓝色调"],
            "high_contrast": ["高对比度", "黑白", "强烈"],
        }
    
    def _get_ocr_reader(self):
        """延迟加载 OCR 模型"""
        if self._ocr_reader is None:
            try:
                import easyocr
                print("📚 加载 OCR 模型... (首次运行需要下载)")
                self._ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            except ImportError:
                print("⚠️  EasyOCR 未安装，OCR 功能不可用")
                print("   运行: pip install easyocr")
                self._ocr_reader = None
        return self._ocr_reader
    
    def _get_face_detector(self):
        """延迟加载人脸检测器"""
        if self._face_cascade is None:
            try:
                import cv2
                # 使用 OpenCV 自带的人脸检测模型
                cascade_path = cv2.data.haarcascades + '***SECRET***.xml'
                self._face_cascade = cv2.CascadeClassifier(cascade_path)
            except ImportError:
                print("⚠️  OpenCV 未安装，人脸检测不可用")
                print("   运行: pip install opencv-python")
                self._face_cascade = None
        return self._face_cascade
    
    # === 核心分析方法 ===
    
    def analyze(self, image_path: str, tasks: Optional[List[str]] = None) -> AnalysisResult:
        """
        完整分析图片
        
        tasks: 可选，指定分析任务 ['ocr', 'tags', 'faces', 'colors', 'qr']
               默认全部执行
        """
        default_tasks = ['tags', 'colors', 'ocr', 'faces', 'qr']
        tasks = tasks or default_tasks
        
        print(f"🔍 分析图片: {Path(image_path).name}")
        
        # 读取图片基本信息
        img = Image.open(image_path)
        file_size = os.path.getsize(image_path)
        
        result = AnalysisResult(
            filename=Path(image_path).name,
            width=img.width,
            height=img.height,
            file_size=file_size,
            tags=[],
            caption="",
            ocr_text="",
            faces=[],
            main_colors=[],
            qr_codes=[],
        )
        
        # 执行各项分析
        if 'tags' in tasks:
            result.tags = self.generate_tags(img)
            print(f"  🏷️ 标签: {', '.join(result.tags[:5])}")
        
        if 'colors' in tasks:
            result.main_colors = self.analyze_colors(img, num_colors=5)
            print(f"  🎨 主色: {len(result.main_colors)} 种")
        
        if 'ocr' in tasks:
            result.ocr_text = self.extract_text(image_path)
            if result.ocr_text.strip():
                print(f"  📝 文字: {len(result.ocr_text)} 字符")
        
        if 'faces' in tasks:
            result.faces = self.detect_faces(image_path)
            if result.faces:
                print(f"  👤 人脸: {len(result.faces)} 张")
        
        if 'qr' in tasks:
            result.qr_codes = self.scan_qr(image_path)
            if result.qr_codes:
                print(f"  🔲 二维码: {len(result.qr_codes)} 个")
        
        # 生成综合描述
        result.caption = self._generate_caption(result)
        
        return result
    
    # === OCR 文字提取 ===
    
    def extract_text(self, image_path: str, detail: bool = False) -> str:
        """从图片中提取文字"""
        reader = self._get_ocr_reader()
        if reader is None:
            return ""
        
        try:
            results = reader.readtext(image_path, detail=detail)
            if detail:
                return json.dumps(results, ensure_ascii=False, indent=2)
            return "\n".join(results)
        except Exception as e:
            print(f"⚠️  OCR 失败: {e}")
            return ""
    
    # === 标签生成 ===
    
    def generate_tags(self, img: Image.Image, num_tags: int = 8, lang: str = "zh") -> List[str]:
        """基于简单启发式规则生成图片标签"""
        tags = []
        
        # 尺寸标签
        w, h = img.size
        aspect = w / h
        if abs(aspect - 1) < 0.1:
            tags.append("正方形")
        elif aspect > 1.5:
            tags.append("宽屏")
        elif aspect < 0.7:
            tags.append("竖屏")
        
        # 亮度和对比度
        img_gray = img.convert('L')
        pixels = np.array(img_gray)
        brightness = pixels.mean() / 255
        contrast = pixels.std() / 255
        
        if brightness < 0.3:
            tags.extend(["暗调", "夜景"])
        elif brightness > 0.8:
            tags.extend(["明亮", "高调"])
        else:
            tags.append("正常曝光")
        
        if contrast > 0.4:
            tags.append("高对比度")
        elif contrast < 0.2:
            tags.append("低对比度")
        
        # 色彩分析
        colors = self.analyze_colors(img, num_colors=3)
        if colors:
            color_names = self._color_names(colors[0])
            tags.extend(color_names[:2])
        
        # 模式标签
        if img.mode == 'L':
            tags.append("黑白")
        elif img.mode == 'RGBA':
            tags.append("透明背景")
        
        return tags[:num_tags]
    
    # === 人脸检测 ===
    
    def detect_faces(self, image_path: str) -> List[Dict]:
        """检测图片中的人脸"""
        detector = self._get_face_detector()
        if detector is None:
            return []
        
        try:
            import cv2
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            faces = detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return [
                {
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                }
                for (x, y, w, h) in faces
            ]
        except Exception as e:
            print(f"⚠️  人脸检测失败: {e}")
            return []
    
    # === 色彩分析 ===
    
    def analyze_colors(self, img: Image.Image, num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """分析图片主色调"""
        # 缩小图片加速计算
        small = img.resize((100, 100)).convert('RGB')
        pixels = np.array(small).reshape(-1, 3)
        
        # K-Means 聚类找主色
        from collections import Counter
        
        # 简化颜色精度到 16 级，加速聚类
        simplified = (pixels // 16) * 16
        color_tuples = [tuple(c) for c in simplified]
        most_common = Counter(color_tuples).most_common(num_colors)
        
        return [color for color, count in most_common]
    
    def _color_names(self, rgb: Tuple[int, int, int]) -> List[str]:
        """给 RGB 颜色起名字"""
        r, g, b = rgb
        brightness = (r + g + b) / 3
        
        # 简单颜色分类
        names = []
        
        if abs(r - g) < 30 and abs(g - b) < 30:
            names.append("灰色系")
            if brightness > 200:
                names.append("白色")
            elif brightness < 80:
                names.append("黑色")
        else:
            max_c = max(r, g, b)
            if max_c == r and r > g + 30 and r > b + 30:
                names.append("红色")
            elif max_c == g and g > r + 30 and g > b + 30:
                names.append("绿色")
            elif max_c == b and b > r + 30 and b > g + 30:
                names.append("蓝色")
            elif r > 180 and g > 150 and b < 100:
                names.append("暖黄")
            elif r > 150 and g > 100 and b > 100:
                names.append("粉色系")
            
            if brightness > 180:
                names.append("浅色")
            elif brightness < 80:
                names.append("深色")
        
        return names
    
    # === 二维码识别 ===
    
    def scan_qr(self, image_path: str) -> List[str]:
        """识别图片中的二维码和条形码"""
        try:
            from pyzbar.pyzbar import decode
            img = Image.open(image_path)
            codes = decode(img)
            return [code.data.decode('utf-8') for code in codes]
        except ImportError:
            return []
        except Exception as e:
            print(f"⚠️  二维码识别失败: {e}")
            return []
    
    # === 生成描述 ===
    
    def _generate_caption(self, result: AnalysisResult) -> str:
        """基于分析结果生成自然语言描述"""
        parts = []
        
        # 尺寸描述
        parts.append(f"这是一张 {result.width}x{result.height} 像素的图片")
        
        # 人脸描述
        if result.faces:
            parts.append(f"检测到 {len(result.faces)} 张人脸")
        
        # 文字描述
        if result.ocr_text and len(result.ocr_text) > 10:
            preview = result.ocr_text[:50].replace('\n', ' ')
            parts.append(f"包含文字内容，开头是：「{preview}...」")
        
        # 二维码描述
        if result.qr_codes:
            parts.append(f"包含 {len(result.qr_codes)} 个可识别的二维码/条形码")
        
        return "。".join(parts) + "。"
    
    # === 批量分析 ===
    
    def batch_analyze(
        self,
        input_dir: str,
        output_file: Optional[str] = None,
        tasks: Optional[List[str]] = None
    ) -> List[AnalysisResult]:
        """批量分析整个文件夹的图片"""
        input_path = Path(input_dir)
        results = []
        
        # 支持的格式
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']
        
        image_files = []
        for ext in extensions:
            image_files.extend(input_path.glob(ext))
            image_files.extend(input_path.glob(ext.upper()))
        
        print(f"📁 找到 {len(image_files)} 张图片\n")
        
        for i, img_path in enumerate(sorted(image_files), 1):
            print(f"[{i}/{len(image_files)}] ", end="")
            try:
                result = self.analyze(str(img_path), tasks=tasks)
                results.append(result)
            except Exception as e:
                print(f"❌ 失败: {e}")
            print()
        
        # 输出到 CSV
        if output_file:
            self._to_csv(results, output_file)
        
        return results
    
    def _to_csv(self, results: List[AnalysisResult], output_file: str):
        """导出结果到 CSV"""
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                '文件名', '宽度', '高度', '文件大小(KB)',
                '标签', '描述', '文字内容',
                '人脸数量', '主色调', '二维码'
            ])
            
            for r in results:
                writer.writerow([
                    r.filename, r.width, r.height, round(r.file_size / 1024, 1),
                    ', '.join(r.tags),
                    r.caption,
                    r.ocr_text.replace('\n', ' | ')[:200],
                    len(r.faces),
                    str(r.main_colors),
                    ', '.join(r.qr_codes)
                ])
        
        print(f"💾 结果已保存: {output_file}")


# === 命令行入口 ===

def main():
    if len(sys.argv) < 2:
        print("""
🎨 图片理解与解析系统

用法:
  python image_analyzer.py analyze <图片路径>      # 完整分析
  python image_analyzer.py ocr <图片路径>          # 提取文字
  python image_analyzer.py tags <图片路径> [N]     # 生成标签 (默认8个)
  python image_analyzer.py faces <图片路径>         # 人脸检测
  python image_analyzer.py colors <图片路径>        # 色彩分析
  python image_analyzer.py qr <图片路径>            # 识别二维码
  python image_analyzer.py describe <图片路径>      # 生成描述
  python image_analyzer.py batch <目录> [输出.csv]  # 批量分析

示例:
  python image_analyzer.py analyze photo.jpg
  python image_analyzer.py ocr screenshot.png | pbcopy
  python image_analyzer.py batch ./photos result.csv
""")
        return
    
    command = sys.argv[1]
    image_path = sys.argv[2] if len(sys.argv) > 2 else ""
    
    analyzer = ImageAnalyzer()
    
    if command == "analyze":
        result = analyzer.analyze(image_path)
        print("\n" + "="*50)
        print(f"📊 分析结果: {result.filename}")
        print(f"📐 尺寸: {result.width}x{result.height}")
        print(f"🏷️ 标签: {', '.join(result.tags)}")
        print(f"📝 描述: {result.caption}")
        if result.ocr_text.strip():
            print(f"\n📖 提取的文字:\n{result.ocr_text}")
        if result.faces:
            print(f"\n👤 人脸位置:")
            for i, face in enumerate(result.faces, 1):
                print(f"   人脸{i}: ({face['x']}, {face['y']}) {face['width']}x{face['height']}")
        if result.qr_codes:
            print(f"\n🔲 二维码内容:")
            for code in result.qr_codes:
                print(f"   {code}")
    
    elif command == "ocr":
        text = analyzer.extract_text(image_path)
        print("\n📖 提取的文字:")
        print("-" * 40)
        print(text)
        print("-" * 40)
    
    elif command == "tags":
        num = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        img = Image.open(image_path)
        tags = analyzer.generate_tags(img, num_tags=num)
        print(f"\n🏷️ 标签: {', '.join(tags)}")
    
    elif command == "faces":
        faces = analyzer.detect_faces(image_path)
        print(f"\n👤 检测到 {len(faces)} 张人脸")
        for i, face in enumerate(faces, 1):
            print(f"   人脸{i}: 位置({face['x']}, {face['y']}), 尺寸 {face['width']}x{face['height']}")
    
    elif command == "colors":
        img = Image.open(image_path)
        colors = analyzer.analyze_colors(img, num_colors=5)
        print(f"\n🎨 主色调 (RGB):")
        for color in colors:
            hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
            print(f"   RGB{color}  {hex_color}")
    
    elif command == "qr":
        codes = analyzer.scan_qr(image_path)
        print(f"\n🔲 检测到 {len(codes)} 个二维码/条形码")
        for code in codes:
            print(f"   内容: {code}")
    
    elif command == "describe":
        result = analyzer.analyze(image_path)
        print(f"\n📝 {result.caption}")
    
    elif command == "batch":
        output = sys.argv[3] if len(sys.argv) > 3 else "analysis_result.csv"
        analyzer.batch_analyze(image_path, output_file=output)


if __name__ == "__main__":
    main()