#!/usr/bin/env python3
"""
图像处理工具集
提供缩放、裁剪、滤镜、拼接、水印、调色等常用功能
"""
from typing import List, Tuple, Optional, Union
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
import colorsys


class ImageEditor:
    """图片编辑器 - 流式 API"""
    
    def __init__(self, image: Union[str, Image.Image]):
        if isinstance(image, str):
            self.img = Image.open(image)
        else:
            self.img = image.copy()
        
        self.original = self.img.copy()
    
    # === 基础变换 ===
    
    def resize(self, width: int, height: int, resample=Image.Resampling.LANCZOS) -> "ImageEditor":
        """缩放图片"""
        self.img = self.img.resize((width, height), resample)
        return self
    
    def resize_max(self, max_width: Optional[int] = None, max_height: Optional[int] = None) -> "ImageEditor":
        """按最大边等比缩放"""
        w, h = self.img.size
        if max_width and w > max_width:
            ratio = max_width / w
            h = int(h * ratio)
            w = max_width
        if max_height and h > max_height:
            ratio = max_height / h
            w = int(w * ratio)
            h = max_height
        return self.resize(w, h)
    
    def crop(self, x: int, y: int, width: int, height: int) -> "ImageEditor":
        """裁剪 (x, y, width, height)"""
        self.img = self.img.crop((x, y, x + width, y + height))
        return self
    
    def center_crop(self, width: int, height: int) -> "ImageEditor":
        """中心裁剪"""
        w, h = self.img.size
        x = (w - width) // 2
        y = (h - height) // 2
        return self.crop(x, y, width, height)
    
    def rotate(self, degrees: int, expand: bool = True) -> "ImageEditor":
        """旋转"""
        self.img = self.img.rotate(degrees, expand=expand, resample=Image.Resampling.BILINEAR)
        return self
    
    def flip_horizontal(self) -> "ImageEditor":
        """水平翻转"""
        self.img = self.img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return self
    
    def flip_vertical(self) -> "ImageEditor":
        """垂直翻转"""
        self.img = self.img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        return self
    
    # === 滤镜与色彩 ===
    
    def filter(self, filter_name: str, **kwargs) -> "ImageEditor":
        """
        应用滤镜
        
        支持: grayscale, sepia, blur, sharpen, contour, edge_enhance, smooth"""
        filters = {
            "grayscale": lambda: self.img.convert("L").convert("RGB"),
            "sepia": self._sepia,
            "blur": lambda: self.img.filter(ImageFilter.GaussianBlur(kwargs.get("radius", 2))),
            "sharpen": lambda: self.img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)),
            "contour": lambda: self.img.filter(ImageFilter.CONTOUR),
            "edge_enhance": lambda: self.img.filter(ImageFilter.EDGE_ENHANCE_MORE),
            "smooth": lambda: self.img.filter(ImageFilter.SMOOTH_MORE),
        }
        
        if filter_name in filters:
            self.img = filters[filter_name]()
        return self
    
    def _sepia(self) -> Image.Image:
        """复古滤镜"""
        img = self.img.convert("RGB")
        pixels = img.load()
        for x in range(img.width):
            for y in range(img.height):
                r, g, b = pixels[x, y]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
        return img
    
    def brightness(self, factor: float) -> "ImageEditor":
        """调整亮度 (1.0=原图, <1变暗, >1变亮)"""
        enhancer = ImageEnhance.Brightness(self.img)
        self.img = enhancer.enhance(factor)
        return self
    
    def contrast(self, factor: float) -> "ImageEditor":
        """调整对比度 (1.0=原图)"""
        enhancer = ImageEnhance.Contrast(self.img)
        self.img = enhancer.enhance(factor)
        return self
    
    def saturation(self, factor: float) -> "ImageEditor":
        """调整饱和度 (1.0=原图, 0=灰度)"""
        enhancer = ImageEnhance.Color(self.img)
        self.img = enhancer.enhance(factor)
        return self
    
    def hue_rotate(self, degrees: int) -> "ImageEditor":
        """色相旋转 (-180 ~ 180度)"""
        img = self.img.convert("HSV")
        pixels = img.load()
        for x in range(img.width):
            for y in range(img.height):
                h, s, v = pixels[x, y]
                h = (h + int(degrees / 360 * 255)) % 255
                pixels[x, y] = (h, s, v)
        self.img = img.convert("RGB")
        return self
    
    def vignette(self, strength: float = 0.5) -> "ImageEditor":
        """添加暗角"""
        w, h = self.img.size
        gradient = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(gradient)
        draw.ellipse((0, 0, w, h), fill=255)
        gradient = gradient.filter(ImageFilter.GaussianBlur(min(w, h) * strength))
        self.img.putalpha(gradient)
        return self
    
    # === 文字与绘图 ===
    
    def add_text(
        self,
        text: str,
        x: int,
        y: int,
        font_size: int = 32,
        color: str = "#ffffff",
        font_path: Optional[str] = None,
        stroke_width: int = 0,
        stroke_color: str = "#000000"
    ) -> "ImageEditor":
        """添加文字"""
        draw = ImageDraw.Draw(self.img)
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                # 尝试系统中文字体
                for font_name in [
                    "/System/Library/Fonts/PingFang.ttc",
                    "/System/Library/Fonts/STHeiti Light.ttc",
                    "/Library/Fonts/Arial Unicode.ttf"
                ]:
                    try:
                        font = ImageFont.truetype(font_name, font_size)
                        break
                    except:
                        continue
                else:
                    font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        draw.text((x, y), text, font=font, fill=color,
                  stroke_width=stroke_width, stroke_fill=stroke_color)
        return self
    
    def add_watermark(
        self,
        text: str,
        position: str = "bottom-right",
        opacity: float = 0.3
    ) -> "ImageEditor":
        """添加水印
        
        position: top-left, top-right, bottom-left, bottom-right, center
        """
        w, h = self.img.size
        
        # 创建水印层
        watermark = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        font_size = min(w, h) // 20
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        positions = {
            "top-left": (20, 20),
            "top-right": (w - tw - 20, 20),
            "bottom-left": (20, h - th - 20),
            "bottom-right": (w - tw - 20, h - th - 20),
            "center": ((w - tw) // 2, ((h - th) // 2),
        }
        
        tx, ty = positions.get(position, positions["bottom-right"])
        
        # 半透明白色文字
        alpha = int(255 * opacity)
        draw.text((tx, ty), text, font=font, fill=(255, 255, 255, alpha))
        
        # 黑色描边
        draw.text((tx+1, ty), text, font=font, fill=(0, 0, 0, alpha//2))
        
        self.img = Image.alpha_composite(self.img.convert("RGBA"), watermark)
        return self
    
    # === 图片拼接 ===
    
    @staticmethod
    def grid(
        image_paths: List[str],
        cols: int = 2,
        padding: int = 10,
        bg_color: str = "#ffffff"
    ) -> "ImageEditor":
        """网格拼接多张图片"""
        images = [Image.open(p) for p in image_paths]
        
        # 统一尺寸（按第一张）
        target_w, target_h = images[0].size
        images = [img.resize((target_w, target_h), Image.Resampling.LANCZOS) for img in images]
        
        rows = (len(images) + cols - 1) // cols
        
        total_w = cols * target_w + (cols + 1) * padding
        total_h = rows * target_h + (rows + 1) * padding
        
        result = Image.new("RGB", (total_w, total_h), bg_color)
        
        for i, img in enumerate(images):
            row = i // cols
            col = i % cols
            x = padding + col * target_w
            y = padding + row * target_h
            result.paste(img, (x, y))
        
        return ImageEditor(result)
    
    @staticmethod
    def concat(
        image_paths: List[str],
        vertical: bool = True,
        padding: int = 0
    ) -> "ImageEditor":
        """垂直/水平拼接图片"""
        images = [Image.open(p) for p in image_paths]
        
        if vertical:
            max_w = max(img.width for img in images)
            total_h = sum(img.height for img in images) + padding * (len(images) - 1)
            result = Image.new("RGB", (max_w, total_h), "#ffffff")
            y = 0
            for img in images:
                result.paste(img, ((max_w - img.width) // 2, y)
                y += img.height + padding
        else:
            max_h = max(img.height for img in images)
            total_w = sum(img.width for img in images) + padding * (len(images) - 1)
            result = Image.new("RGB", (total_w, max_h), "#ffffff")
            x = 0
            for img in images:
                result.paste(img, (x, (max_h - img.height) // 2))
                x += img.width + padding
        
        return ImageEditor(result)
    
    # === 输出 ===
    
    def save(self, path: str, quality: int = 95):
        """保存图片"""
        p = Path(path)
        if p.suffix.lower() in (".jpg", ".jpeg"):
            self.img.convert("RGB").save(path, quality=quality, optimize=True)
        elif p.suffix.lower() == ".png":
            self.img.save(path, optimize=True)
        else:
            self.img.save(path)
        print(f"💾 已保存: {path} ({self.img.width}x{self.img.height})")
        return self
    
    def show(self):
        """显示图片"""
        self.img.show()
        return self
    
    @property
    def image(self) -> Image.Image:
        """获取 PIL Image 对象"""
        return self.img
    
    @property
    def size(self) -> Tuple[int, int]:
        """图片尺寸"""
        return self.img.size


# —— 快捷函数 ——

def open_image(path: str) -> ImageEditor:
    """打开图片"""
    return ImageEditor(path)


def thumbnail(image_path: str, max_size: int = 512, output_path: Optional[str] = None):
    """生成缩略图"""
    img = ImageEditor(image_path)
    img.resize_max(max_width=max_size, max_height=max_size)
    if output_path:
        img.save(output_path)
    return img


def make_collage(
    image_dir: str,
    output_path: str,
    cols: int = 3,
    max_images: int = 9
):
    """从文件夹生成拼图"""
    from glob import glob
    
    patterns = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
    images = []
    for p in patterns:
        images.extend(glob(str(Path(image_dir) / p)))
    
    images = images[:max_images]
    result = ImageEditor.grid(images, cols=cols)
    result.save(output_path)
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        cmd = sys.argv[1]
        if cmd == "grid":
            # python image_utils.py grid output.jpg a.jpg b.jpg c.jpg...
            output = sys.argv[2]
            inputs = sys.argv[3:]
            result = ImageEditor.grid(inputs, cols=2 if len(inputs) <= 4 else 3)
            result.save(output)
        elif cmd == "concat":
            output = sys.argv[2]
            inputs = sys.argv[3:]
            result = ImageEditor.concat(inputs, vertical=True)
            result.save(output)
        print("✅ 完成!")
    else:
        print("用法:")
        print("  拼图: python image_utils.py grid output.jpg 1.jpg 2.jpg 3.jpg...")
        print("  拼接: python image_utils.py concat output.jpg 1.jpg 2.jpg...")