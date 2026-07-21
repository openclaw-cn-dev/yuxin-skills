# Batch Image Renaming Script
# For Doubao (豆包) AI-generated flashcard images
# Usage: cd /Users/hua/6-产品研发/23-AI培训教程 && python3 scripts/rename_images.py

import os
import re
import shutil

source_dir = "02-豆包生图Prompt"
target_dir = "03-豆包生成图"

# Ensure target directory exists
os.makedirs(target_dir, exist_ok=True)

# T-ID to Chinese name mapping
# Update this as new terms are generated
T_NAMES = {
    "T001": "AI（人工智能）",
    "T002": "机器学习",
    "T003": "深度学习",
    "T004": "大语言模型(LLM)",
    "T005": "生成式AI",
    "T006": "AGI（通用人工智能）",
    "T007": "神经网络",
    "T008": "参数",
    "T009": "算力",
    "T010": "数据集",
    "T011": "标签",
    "T012": "特征",
    # Add more as you generate
}

def sort_key(filename):
    """Sort images: no parentheses = v1, then by number in parentheses."""
    if "(" not in filename:
        return 0
    match = re.search(r'\((\d+)\)', filename)
    if match:
        return int(match.group(1))
    return 999

def main():
    # All PNG files
    png_files = sorted([f for f in os.listdir(source_dir) if f.endswith('.png')])
    print(f"Found {len(png_files)} images\n")

    # Group by T-ID
    groups = {}
    for filename in png_files:
        match = re.match(r'^t(\d{3})', filename, re.IGNORECASE)
        if match:
            t_id = f"T{match.group(1).upper()}"
        else:
            t_id = "T001"  # No prefix = T001 (first batch)
        
        if t_id not in groups:
            groups[t_id] = []
        groups[t_id].append(filename)

    # Print grouping summary
    for t_id in sorted(groups.keys()):
        print(f"{t_id}: {len(groups[t_id])} images")
    print("\n" + "="*60 + "\n")

    # Rename and copy each group
    total = 0
    for t_id in sorted(groups.keys()):
        if t_id not in T_NAMES:
            print(f"⚠️  Skipping {t_id}: unknown term name")
            continue
        
        term_name = T_NAMES[t_id]
        group_files = sorted(groups[t_id], key=sort_key)
        
        print(f"Processing {t_id} - {term_name}...")
        for idx, old_name in enumerate(group_files, 1):
            new_name = f"{t_id}-{term_name}_v{idx}.png"
            old_path = os.path.join(source_dir, old_name)
            new_path = os.path.join(target_dir, new_name)
            shutil.copy2(old_path, new_path)
            print(f"  {old_name:50s} -> {new_name}")
            total += 1
        print()

    print("="*60)
    print(f"\nDone! {total} images copied to {target_dir}/")
    
    # Verify
    target_count = len([f for f in os.listdir(target_dir) if f.endswith('.png')])
    print(f"\nVerification: {target_count} PNG files in target directory")

if __name__ == "__main__":
    main()
