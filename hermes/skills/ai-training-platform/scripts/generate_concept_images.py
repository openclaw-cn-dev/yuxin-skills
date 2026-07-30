#!/usr/bin/env python3
"""
Generate AI concept flashcard images using Python PIL.

Fallback for when Doubao/AI image generators are unavailable.
Produces 4 style variations: 科技蓝, 未来紫, 活力橙, 清新绿.

Usage:
    python3 generate_concept_images.py \
        --term-id T001 \
        --term-name "AI（人工智能）" \
        --output-dir 03-豆包生成图/
"""

import argparse
import math
import os
import random
from PIL import Image, ImageDraw


def generate_image(term_id: str, term_name: str, style_idx: int, output_dir: str) -> str:
    """Generate one concept image with the specified style index (0-3)."""
    
    # 4 style palettes: (bg_color, primary_color, name)
    styles = [
        ((10, 20, 40), (0, 120, 255), "科技蓝"),
        ((30, 10, 50), (180, 80, 255), "未来紫"),
        ((40, 20, 10), (255, 150, 50), "活力橙"),
        ((10, 40, 30), (50, 255, 180), "清新绿"),
    ]
    
    bg_color, primary_color, style_name = styles[style_idx]
    version = style_idx + 1
    
    # Create canvas
    img = Image.new('RGB', (1024, 1024), bg_color)
    draw = ImageDraw.Draw(img)
    
    center_x, center_y = 512, 512
    
    # Draw neural network nodes (5 concentric layers)
    for layer in range(5):
        radius = 80 + layer * 60
        num_nodes = 8 + layer * 4
        for n in range(num_nodes):
            angle = 2 * math.pi * n / num_nodes + random.uniform(-0.1, 0.1)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            node_size = 10 + random.randint(-3, 5)
            draw.ellipse(
                [x - node_size, y - node_size, x + node_size, y + node_size],
                fill=primary_color,
                outline=(255, 255, 255, 100)
            )
    
    # Draw connecting lines (data flow between nodes)
    for _ in range(150):
        x1 = random.randint(100, 924)
        y1 = random.randint(100, 924)
        x2 = random.randint(100, 924)
        y2 = random.randint(100, 924)
        draw.line(
            [x1, y1, x2, y2],
            fill=(primary_color[0], primary_color[1], primary_color[2], 80),
            width=1
        )
    
    # Draw center brain shape (concentric halos)
    for r in range(60, 100, 10):
        draw.ellipse(
            [center_x - r, center_y - r, center_x + r, center_y + r],
            outline=(255, 255, 255, 150),
            width=2
        )
    
    # Draw chip icon (top-left area)
    chip_x, chip_y = 200, 200
    draw.rectangle(
        [chip_x - 40, chip_y - 40, chip_x + 40, chip_y + 40],
        outline=(200, 200, 200),
        width=3
    )
    # Draw chip pins
    for pin in range(8):
        draw.line([chip_x - 40, chip_y - 30 + pin * 10, chip_x - 55, chip_y - 30 + pin * 10],
                  fill=(200, 200, 200), width=2)
        draw.line([chip_x + 40, chip_y - 30 + pin * 10, chip_x + 55, chip_y - 30 + pin * 10],
                  fill=(200, 200, 200), width=2)
    
    # Draw data stream particles (diagonal flow)
    for _ in range(20):
        start_x = random.randint(0, 1024)
        start_y = random.randint(0, 1024)
        length = random.randint(50, 150)
        for j in range(0, length, 10):
            draw.point(
                [start_x + j, start_y + j // 3],
                fill=(255, 255, 255, 100)
            )
    
    # Save with standard naming convention
    filename = f"{term_id}-{term_name}_v{version}.png"
    output_path = os.path.join(output_dir, filename)
    os.makedirs(output_dir, exist_ok=True)
    img.save(output_path)
    
    return output_path, style_name


def main():
    parser = argparse.ArgumentParser(description="Generate AI concept flashcard images")
    parser.add_argument("--term-id", required=True, help="Term ID (e.g., T001)")
    parser.add_argument("--term-name", required=True, help="Chinese term name (e.g., AI（人工智能）)")
    parser.add_argument("--output-dir", default="03-豆包生成图/", help="Output directory")
    parser.add_argument("--styles", type=int, default=4, help="Number of styles (1-4)")
    
    args = parser.parse_args()
    
    print(f"Generating {args.styles} images for {args.term_id}-{args.term_name}...")
    
    for i in range(min(args.styles, 4)):
        output_path, style_name = generate_image(
            args.term_id,
            args.term_name,
            i,
            args.output_dir
        )
        size_kb = os.path.getsize(output_path) // 1024
        print(f"  ✅ v{i+1} ({style_name}): {output_path} ({size_kb} KB)")


if __name__ == "__main__":
    main()
