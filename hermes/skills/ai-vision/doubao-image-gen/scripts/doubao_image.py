#!/usr/bin/env python3
"""
豆包生图 API 客户端
通过火山引擎豆包 API 生成高质量 AI 图像
"""
import os
import requests
import base64
from io import BytesIO
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("⚠️  请安装 Pillow: pip install pillow")
    raise


class DoubaoImageGen:
    """豆包生图 API 客户端"""
    
    # 风格预设 - 自动追加到提示词
    STYLE_PRESETS = {
        "写实": ", 写实风格, 摄影, 高清, 细节丰富",
        "动漫": ", 动漫风格, 二次元, 新海诚风格, 精美插画",
        "插画": ", 手绘插画, 艺术风格, 色彩丰富, 细腻",
        "水彩": ", 水彩画, 透明质感, 柔和色彩, 艺术感",
        "油画": ", 油画质感, 笔触明显, 厚重色彩, 古典艺术",
        "3D": ", 3D渲染, Pixar风格, 体积光, 材质细腻",
        "像素": ", 像素艺术, 8-bit风格, 复古游戏, 点阵",
        "赛博朋克": ", 赛博朋克风格, 霓虹灯, 未来都市, 高科技感",
        "国潮": ", 国潮风格, 中国风, 传统元素, 东方美学",
        "极简": ", 极简主义, 简洁, 干净, 留白, 高级感",
    }
    
    def __init__(self, api_key: Optional[str] = None, endpoint_id: Optional[str] = None, endpoint: Optional[str] = None):
        # 2026-08-13 laomo 修正: 用 VOLC_ARK_API_KEY，无需 endpoint_id
        self.api_key = api_key or os.getenv("VOLC_ARK_API_KEY")
        self.endpoint_id = endpoint_id or os.getenv("VOLCENGINE_ENDPOINT_ID")
        
        if not self.api_key:
            raise ValueError("请设置 VOLC_ARK_API_KEY 环境变量 (config.yaml minimax-custom 同款 ark key)")
        # 默认模型 doubao-seedream-5-0-260128（已激活），尺寸需 >=2048x2048
        
        self.endpoint = endpoint or "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        # 默认模型: 已激活的 Seedream 5.0（2026-08-13 实测可用）
        self.model = endpoint_id or "doubao-seedream-5-0-260128"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def _apply_style(self, prompt: str, style: str = "写实") -> str:
        """应用风格预设"""
        if style in self.STYLE_PRESETS:
            return prompt + self.STYLE_PRESETS[style]
        return prompt
    
    def generate(
        self,
        prompt: str,
        size: str = "2048x2048",
        n: int = 1,
        style: str = "写实",
        quality: str = "standard",
        response_format: str = "b64_json"
    ) -> "ImageResult":
        """
        文生图
        
        Args:
            prompt: 文字描述
            size: 图片尺寸 (512x512, 1024x1024, 1024x768, 768x1024)
            n: 生成数量 (1-4)
            style: 风格预设 (写实/动漫/插画/水彩/油画/3D/像素/赛博朋克/国潮/极简)
            quality: 质量 (standard/hd)
            response_format: 返回格式 (b64_json/url)
        """
        full_prompt = self._apply_style(prompt, style)
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "size": size,
            "n": n,
            "quality": quality,
            "response_format": response_format
        }
        
        resp = self.session.post(self.endpoint, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        
        return ImageResult(data, self)
    
    def generate_batch(
        self,
        prompts: List[str],
        size: str = "1024x1024",
        style: str = "写实",
        **kwargs
    ) -> List["ImageResult"]:
        """批量生成图片"""
        results = []
        for prompt in prompts:
            try:
                result = self.generate(prompt, size=size, n=1, style=style, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"⚠️  生成失败: {prompt[:30]}... - {e}")
        return results
    
    def image_to_image(
        self,
        image_path: str,
        prompt: str,
        strength: float = 0.7,
        size: str = "2048x2048",
        style: str = "写实"
    ) -> "ImageResult":
        """
        图生图（参考图 + 提示词）
        
        Args:
            image_path: 参考图片路径
            prompt: 描述文字
            strength: 变化强度 (0.0-1.0)，越大偏离原图越多
            size: 输出尺寸
            style: 风格预设
        """
        # 读取并编码图片
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()
        
        full_prompt = self._apply_style(prompt, style)
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "image": image_b64,
            "strength": strength,
            "size": size,
            "n": 1,
            "response_format": "b64_json"
        }
        
        resp = self.session.post(self.endpoint, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        
        return ImageResult(data, self)


class ImageResult:
    """生成结果封装"""
    
    def __init__(self, data: Dict[str, Any], client: DoubaoImageGen):
        self.raw_data = data
        self.client = client
        self.images: List[Image.Image] = []
        
        for item in data.get("data", []):
            if "b64_json" in item:
                img_data = base64.b64decode(item["b64_json"])
                self.images.append(Image.open(BytesIO(img_data)))
            elif "url" in item:
                resp = requests.get(item["url"])
                self.images.append(Image.open(BytesIO(resp.content)))
    
    def __len__(self) -> int:
        return len(self.images)
    
    def __getitem__(self, idx: int) -> Image.Image:
        return self.images[idx]
    
    def save(self, path: str, quality: int = 95) -> List[str]:
        """
        保存所有图片
        
        Args:
            path: 保存路径，如果多张会自动加 _1, _2 后缀
            quality: JPEG 质量 (1-100)
            
        Returns:
            保存的文件路径列表
        """
        saved = []
        p = Path(path)
        base = p.stem
        ext = p.suffix.lower()
        
        for i, img in enumerate(self.images):
            if len(self.images) == 1:
                save_path = str(p)
            else:
                save_path = str(p.with_name(f"{base}_{i+1}{ext}"))
            
            if ext in (".jpg", ".jpeg"):
                img.convert("RGB").save(save_path, quality=quality)
            else:
                img.save(save_path)
            saved.append(save_path)
            print(f"💾 已保存: {save_path} ({img.size[0]}x{img.size[1]})")
        
        return saved
    
    def show(self):
        """显示所有图片（仅本地有图形界面时可用）"""
        for img in self.images:
            img.show()


# —— 快捷函数 ——

def generate(prompt: str, **kwargs) -> ImageResult:
    """快捷生成单张图片"""
    gen = DoubaoImageGen()
    return gen.generate(prompt, **kwargs)


def quick_save(prompt: str, filename: str, **kwargs):
    """生成并一键保存"""
    result = generate(prompt, **kwargs)
    return result.save(filename)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python doubao_image.py \"提示词\" [输出文件名]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "output.png"
    
    print(f"🎨 正在生成: {prompt[:50]}...")
    result = generate(prompt)
    result.save(output)
    print("✅ 完成!")