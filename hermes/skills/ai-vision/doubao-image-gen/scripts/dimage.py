#!/usr/bin/env python3
"""
豆包生图命令行工具
dimage "提示词" [输出文件名] [选项]
"""
import os
import sys
import argparse
from pathlib import Path

# 确保可以导入技能脚本
SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

from doubao_image import DoubaoImageGen, ImageResult


def main():
    parser = argparse.ArgumentParser(
        description="豆包生图 - 通过火山引擎生成 AI 图像",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  dimage "一只可爱的柯基犬"                     # 生成并自动命名
  dimage "海边日落" -o sunset.jpg             # 指定输出文件名
  dimage "赛博朋克城市" -s 1024x768           # 指定尺寸
  dimage "日本动漫风格的女孩" -t 动漫          # 指定风格
  dimage "四张不同风格的猫" -n 4               # 生成4张
  dimage --list-styles                         # 列出所有风格
        """
    )
    parser.add_argument("prompt", nargs="?", help="图片描述提示词")
    parser.add_argument("-o", "--output", help="输出文件名 (默认: 自动生成)")
    parser.add_argument("-s", "--size", default="1024x1024", 
                       choices=["512x512", "1024x1024", "1024x768", "768x1024"],
                       help="图片尺寸")
    parser.add_argument("-t", "--style", default="写实",
                       help="风格预设: 写实/动漫/插画/水彩/油画/3D/像素/赛博朋克/国潮/极简")
    parser.add_argument("-n", "--number", type=int, default=1,
                       help="生成数量 (1-4)")
    parser.add_argument("-q", "--quality", default="standard",
                       choices=["standard", "hd"], help="生成质量")
    parser.add_argument("--list-styles", action="store_true", help="列出所有可用风格")
    parser.add_argument("--key", help="火山引擎 API Key (也可设置 VOLCENGINE_API_KEY 环境变量)")
    
    args = parser.parse_args()
    
    # 列出风格
    if args.list_styles:
        print("🎨 可用风格预设:")
        for name, desc in DoubaoImageGen.STYLE_PRESETS.items():
            print(f"  {name:8s} → {desc}")
        return
    
    # 检查提示词
    if not args.prompt:
        parser.print_help()
        return
    
    # 初始化客户端
    try:
        gen = DoubaoImageGen(api_key=args.key)
    except ValueError as e:
        print(f"❌ 错误: {e}")
        print("💡 可以设置环境变量: export VOLCENGINE_API_KEY=\"your-key\"")
        sys.exit(1)
    
    # 生成输出文件名
    if not args.output:
        safe_prompt = "".join(c if c.isalnum() else "_" for c in args.prompt[:20])
        args.output = f"gen_{safe_prompt}.png"
    
    # 开始生成
    print(f"🎨 正在生成: {args.prompt}")
    print(f"   尺寸: {args.size}  风格: {args.style}  数量: {args.number}")
    print()
    
    try:
        result = gen.generate(
            prompt=args.prompt,
            size=args.size,
            n=args.number,
            style=args.style,
            quality=args.quality
        )
        
        print(f"✅ 生成成功! 共 {len(result)} 张图片")
        print()
        
        # 保存
        saved = result.save(args.output)
        
        print()
        print("📁 文件已保存到:")
        for p in saved:
            print(f"   {p}")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()