#!/usr/bin/env python3
"""
AI Knowledge Card Smart Renamer
Uses domain knowledge TERM_MAP instead of OCR to rename files.
Handles 215 cards in format: Txxx_vxx.png → txxx-术语名-vxx.png

Usage:
    python smart_rename_ai_cards.py <input_dir> [output_dir]
"""
import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

# AI Training Platform 44 terms fixed mapping
TERM_MAP = {
    "001": "人工智能",
    "005": "机器学习",
    "006": "深度学习",
    "007": "神经网络",
    "008": "监督学习",
    "009": "无监督学习",
    "010": "强化学习",
    "011": "迁移学习",
    "012": "自然语言处理",
    "103": "Transformer",
    "104": "卷积神经网络",
    "105": "循环神经网络",
    "106": "生成对抗网络",
    "107": "注意力机制",
    "108": "BERT",
    "109": "GPT模型",
    "110": "扩散模型",
    "111": "CLIP模型",
    "112": "视觉Transformer",
    "113": "大语言模型",
    "114": "多模态模型",
    "115": "特征工程",
    "116": "模型训练",
    "117": "模型评估",
    "118": "超参数调优",
    "119": "正则化",
    "121": "梯度下降",
    "122": "反向传播",
    "123": "优化器",
    "124": "学习率",
    "125": "批量归一化",
    "126": "Dropout",
    "196": "AI工程化",
    "197": "MLOps",
    "198": "模型部署",
    "199": "推理优化",
    "200": "量化压缩",
    "201": "模型蒸馏",
    "202": "联邦学习",
    "203": "提示词工程",
    "204": "思维链",
    "205": "RAG检索增强",
    "206": "AI Agent智能体",
    "207": "AI安全对齐",
}

def rename_ai_cards(input_dir: str, output_dir: str = None):
    """Rename AI knowledge cards using domain knowledge lookup"""
    input_path = Path(input_dir)
    if output_dir is None:
        output_path = input_path.parent / (input_path.name + "_已重命名")
    else:
        output_path = Path(output_dir)
    
    output_path.mkdir(exist_ok=True)
    
    print(f"📁 开始重命名 AI 知识卡片...")
    print(f"📂 输出目录: {output_path}\n")
    
    # CSV log
    csv_path = output_path / "_重命名日志.csv"
    with open(csv_path, "w") as f:
        f.write("编号,术语,版本,新文件名,原文件名\n")
    
    count = 0
    image_files = sorted(input_path.glob("T*.png"))
    
    for img_path in image_files:
        name = img_path.name
        match = re.search(r'T(\d+)_v(\d+)', name, re.IGNORECASE)
        if match:
            t_num = match.group(1)
            v_num = match.group(2)
            
            theme = TERM_MAP.get(t_num, "未分类")
            new_name = f"t{t_num}-{theme}-v{v_num}.png"
            new_path = output_path / new_name
            
            shutil.copy2(img_path, new_path)
            print(f"✅ {name:15} → {new_name}")
            
            with open(csv_path, "a") as f:
                f.write(f"{t_num},{theme},{v_num},{new_name},{name}\n")
            
            count += 1
    
    print(f"\n🎉 完成! 共重命名 {count} 张图片")
    print(f"📋 日志文件: {csv_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python smart_rename_ai_cards.py <输入目录> [输出目录]")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    rename_ai_cards(input_dir, output_dir)