#!/usr/bin/env python3
"""SVG → PNG 转换 helper — Hermes vision_tools 修复后的标准化 pipeline。

触发场景：当 Agent 接到 SVG 矢量图要喂给 vision LLM (MiniMax-M3、OpenAI GPT-4o、Anthropic Claude 等都拒 SVG) 时用此脚本。

历史背景（2026-07-01）：
- 毛豆 CAD 出图返回 SVG，agent 直接传 → MiniMax-M3 拒 (code 2013) → session 卡 36 分钟
- 修复方案：在 hermes-agent/tools/vision_tools.py 加自动转换钩子 (已上线)
- 本脚本 = 独立 fallback，在钩子未部署的环境 (e.g. 老版本 Hermes) 用

依赖：pip install cairosvg (macOS 也可用 brew install librsvg + rsvg-convert)

用法：
    python3 svg_to_png.py input.svg                    # 默认输出到 input.png (2048px)
    python3 svg_to_png.py input.svg -o out.png         # 指定输出
    python3 svg_to_png.py input.svg --width 1024       # 指定宽度
    python3 svg_to_png.py *.svg --batch                # 批量

退出码：0 = 成功，1 = 依赖缺失，2 = 文件错，3 = SVG 解析错
"""
import argparse
import sys
from pathlib import Path


def convert_one(svg_path: Path, png_path: Path, width: int) -> None:
    """Convert single SVG to PNG. Tries cairosvg first, then rsvg-convert."""
    if not svg_path.exists():
        print(f"❌ {svg_path}: 不存在", file=sys.stderr)
        sys.exit(2)

    # Strategy 1: cairosvg (推荐，本地 Python 依赖)
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=width)
        size_in = svg_path.stat().st_size
        size_out = png_path.stat().st_size
        print(f"✅ {svg_path.name} ({size_in} B) → {png_path.name} ({size_out} B, {width}px)")
        return
    except ImportError:
        pass

    # Strategy 2: rsvg-convert (macOS brew install librsvg)
    import subprocess
    try:
        result = subprocess.run(
            ["rsvg-convert", "-w", str(width), "-o", str(png_path), str(svg_path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f"✅ {svg_path.name} → {png_path.name} ({width}px, via rsvg-convert)")
            return
        print(f"⚠️ rsvg-convert failed: {result.stderr}", file=sys.stderr)
    except FileNotFoundError:
        pass

    print("❌ 需要 cairosvg 或 rsvg-convert — pip install cairosvg 或 brew install librsvg", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="SVG → PNG for LLM vision")
    parser.add_argument("svgs", nargs="+", type=Path, help="SVG 输入文件")
    parser.add_argument("-o", "--output", type=Path, help="PNG 输出文件（单文件时）")
    parser.add_argument("--width", type=int, default=2048, help="宽度像素 (default 2048)")
    parser.add_argument("--batch", action="store_true", help="批量模式：每个 SVG 输出同目录 .png")
    args = parser.parse_args()

    for svg in args.svgs:
        if args.batch or len(args.svgs) > 1:
            png = svg.with_suffix(".png")
        else:
            png = args.output or svg.with_suffix(".png")
        convert_one(svg, png, args.width)


if __name__ == "__main__":
    main()
