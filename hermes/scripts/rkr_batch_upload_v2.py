#!/usr/bin/env python3
"""
RKR知识库批量上传脚本 v2
- 遍历知识库目录，跳过副本/_archive/研究/养殖案例等
- 读取MD文件，提取标题和标签
- 复制到本地中转站目录，Celery自动处理

用法: python3 rkr_batch_upload_v2.py [--dir 目录名] [--all] [--dry-run]
"""
import os
import re
import shutil
import time
import argparse
from pathlib import Path
from datetime import datetime

# 配置
KB_ROOT = Path("/Users/hua/Desktop/知识库 ")
STAGING_DIR = Path("/Users/hua/Desktop/渔芯科技/团队协作/文档中转站")

# 需要跳过的目录
SKIP_DIRS = {
    "-副本", "_archive", "研究", "养殖案例", "设备3d建模库",
    "水产养殖深库", "RAS系统", "memory", "workspace",
    "progress_report", "抖音精选", ".DS_Store",
    "汇报_", "汇报.", "汇报_2", "汇报_3"
}

# 需要处理的目录及对应标签
PROCESS_DIRS = {
    "AI前端技术": ["AI前端", "前端技术", "React", "Vue"],
    "Hermes": ["Hermes", "Agent框架"],
    "ai-hermes": ["Hermes", "AI"],
    "ai-大模型": ["大模型", "LLM"],
    "大模型": ["大模型", "LLM"],
    "市场行情": ["市场行情", "行业分析"],
    "建筑AI": ["建筑AI", "AI建筑"],
    "水产养殖": ["水产养殖", " aquaculture"],
    "RAS循环水养殖": ["RAS", "循环水养殖"],
    "GitHub": ["GitHub", "开源项目"],
    "OpenClaw": ["OpenClaw", "自动化"],
    "ai-openclaw": ["OpenClaw", "AI"],
    "ai-github": ["GitHub", "AI"],
    "ai-clawhub": ["ClawHub", "AI"],
    "ClawHub": ["ClawHub"],
}


def should_skip_path(path: Path) -> bool:
    """检查是否应该跳过此路径"""
    path_str = str(path)
    for skip in SKIP_DIRS:
        if skip in path_str:
            return True
    return False


def extract_title(filename: str, content: str = "") -> str:
    """从文件名或内容提取标题"""
    # 文件名格式: uuid_标题.md 或 标题.md
    name = filename.replace('.md', '')
    
    # 去掉uuid前缀
    name = re.sub(r'^[a-f0-9]{12}_', '', name)
    name = name.replace('_', ' ')
    
    # 如果标题太长，截断
    if len(name) > 100:
        name = name[:100]
    
    return name


def get_tags_for_file(filepath: Path, dir_tags: list) -> list:
    """根据文件路径和目录确定标签"""
    tags = dir_tags.copy()
    
    # 从文件名提取额外标签
    name = filepath.stem.lower()
    if 'ras' in name:
        tags.append('RAS')
    if 'aquaculture' in name or '水产' in name:
        tags.append('水产')
    if 'ai' in name or 'llm' in name or '大模型' in name:
        tags.append('AI')
    if 'hermes' in name:
        tags.append('Hermes')
    if '建筑' in name:
        tags.append('建筑')
    
    # 去重
    return list(set(tags))[:10]


def process_directory(dir_name: str) -> list:
    """获取目录下的MD文件"""
    dir_path = KB_ROOT / dir_name
    if not dir_path.exists():
        return []
    
    md_files = []
    for f in dir_path.glob("*.md"):
        if should_skip_path(f):
            continue
        md_files.append(f)
    return md_files


def process_file(src_file: Path, tags: list, dry_run: bool = False) -> dict:
    """处理单个文件"""
    try:
        content = src_file.read_text(encoding='utf-8')
        
        # 提取标题
        title = extract_title(src_file.name, content)
        
        # 构建输出文件名: tag1_tag2_标题.md
        safe_tags = []
        for tag in tags[:3]:
            safe_tag = re.sub(r'[^\w\u4e00-\u9fff-]', '', tag)[:10]
            if safe_tag:
                safe_tags.append(safe_tag)
        
        tag_prefix = '_'.join(safe_tags)
        if tag_prefix:
            output_name = f"{tag_prefix}_{title}.md"
        else:
            output_name = f"{title}.md"
        
        # 清理文件名中的非法字符
        output_name = re.sub(r'[<>:"/\\|?*]', '_', output_name)
        output_name = output_name[:200]  # 限制长度
        
        output_path = STAGING_DIR / output_name
        
        if dry_run:
            return {
                "status": "dry_run",
                "src": str(src_file),
                "dst": str(output_path),
                "title": title,
                "size": len(content),
            }
        
        # 添加RKR frontmatter
        frontmatter = f"""---
title: {title}
tags: {tags}
source: 知识库整理
date: {datetime.now().strftime('%Y-%m-%d')}
---

"""
        new_content = frontmatter + content
        
        # 写入中转站
        output_path.write_text(new_content, encoding='utf-8')
        
        return {
            "status": "success",
            "src": str(src_file.name),
            "dst": output_name,
            "title": title,
            "size": len(new_content),
        }
        
    except Exception as e:
        return {
            "status": "error",
            "src": str(src_file),
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description='RKR知识库批量上传')
    parser.add_argument('--dir', help='只处理指定目录')
    parser.add_argument('--all', action='store_true', help='处理所有目录（包括根目录）')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要处理的文件，不实际复制')
    parser.add_argument('--limit', type=int, default=0, help='每个目录限制处理数量（0=不限）')
    args = parser.parse_args()
    
    print("=" * 60)
    print("RKR知识库批量上传脚本 v2")
    print(f"知识库: {KB_ROOT}")
    print(f"中转站: {STAGING_DIR}")
    print(f"模式: {'干跑' if args.dry_run else '实际执行'}")
    print("=" * 60)
    
    # 统计
    stats = {"total": 0, "success": 0, "skipped": 0}
    
    # 确定要处理的目录
    if args.dir:
        dirs_to_process = {args.dir: []}
    else:
        dirs_to_process = PROCESS_DIRS
    
    # 处理每个目录
    for dir_name, base_tags in dirs_to_process.items():
        md_files = process_directory(dir_name)
        if not md_files:
            continue
        
        print(f"\n📁 处理目录: {dir_name} ({len(md_files)} 个文件)")
        
        count = 0
        for f in md_files:
            if args.limit > 0 and count >= args.limit:
                print(f"  ⏭️  达到限制({args.limit})，停止此目录")
                break
                
            stats["total"] += 1
            
            # 获取文件级标签
            tags = get_tags_for_file(f, base_tags)
            
            result = process_file(f, tags, dry_run=args.dry_run)
            
            if result["status"] == "dry_run":
                stats["success"] += 1
                print(f"  🔍 干跑: {f.name[:60]} → {result['dst'][:60]}")
            elif result["status"] == "success":
                stats["success"] += 1
                print(f"  ✓ 上传: {f.name[:50]} → {result['dst'][:50]}")
                time.sleep(0.3)  # 避免太快
            elif result["status"] == "error":
                print(f"  ✗ 失败: {f.name[:50]} - {result['error']}")
            
            count += 1
    
    # 处理根目录的MD文件
    if args.all or args.dir == "root":
        print(f"\n📁 处理根目录")
        root_files = list(KB_ROOT.glob("*.md"))
        root_files = [f for f in root_files if not should_skip_path(f)]
        
        count = 0
        for f in root_files:
            if args.limit > 0 and count >= args.limit:
                break
            stats["total"] += 1
            tags = ["知识库", "杂项"]
            
            result = process_file(f, tags, dry_run=args.dry_run)
            
            if result["status"] in ("dry_run", "success"):
                stats["success"] += 1
                print(f"  ✓ {f.name[:60]}")
            time.sleep(0.3)
            count += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("上传完成")
    print(f"总计: {stats['total']} | 成功: {stats['success']}")
    print("=" * 60)
    print(f"\n💡 Celery beat每2分钟扫描一次中转站")
    print(f"💡 可用 --dry-run 先预览，或 --limit N 限制数量")
    
    # 列出中转站当前文件
    staging_files = list(STAGING_DIR.glob("*.md"))
    print(f"\n当前中转站有 {len(staging_files)} 个MD文件")


if __name__ == "__main__":
    main()