#!/usr/bin/env python3
"""
RKR知识库批量上传脚本
- 遍历知识库目录，跳过副本/_archive/研究/养殖案例等
- 读取MD文件，提取元信息
- 通过 /api/v1/external/documents/text 上传到RKR中转站
"""
import os
import re
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# 配置
KB_ROOT = Path("/Users/hua/Desktop/知识库 ")
RKR_API = "http://localhost:8000/api/v1"
STAGING_PROJECT_ID = "***SECRET***"

# 需要跳过的目录
SKIP_DIRS = {
    "-副本", "_archive", "研究", "养殖案例", "设备3d建模库",
    "水产养殖深库", "RAS系统", "memory", "workspace", "汇报_",
    "progress_report", "抖音精选", ".DS_Store"
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
}


def get_jwt_token():
    """登录获取JWT token"""
    # 从环境变量或直接读取
    # 假设默认用户 admin@rkr-platform.com / Admin@2026!rkr
    resp = requests.post(
        f"{RKR_API}/auth/login",
        json={
            "email": "admin@rkr-platform.com",
            "password": "Admin@2026!rkr"
        }
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    print(f"登录失败: {resp.status_code} {resp.text}")
    return None


def extract_frontmatter(content: str):
    """提取MD文件前面的元信息"""
    meta = {"title": "", "tags": [], "category": ""}
    
    # 尝试从文件名提取标题（去掉uuid前缀）
    # 文件名格式: uuid_标题.md
    title_match = re.match(r'^[a-f0-9]{12}_(.+)\.md$', content[:200]) if content else None
    if not title_match:
        # 尝试从内容提取 # 标题
        h1 = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1:
            meta["title"] = h1.group(1).strip()
    else:
        meta["title"] = title_match.group(1).replace('_', ' ')
    
    return meta


def should_skip_path(path: Path) -> bool:
    """检查是否应该跳过此路径"""
    path_str = str(path)
    for skip in SKIP_DIRS:
        if skip in path_str:
            return True
    return False


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


def upload_document(token: str, content: str, filename: str, tags: list) -> dict:
    """上传单个文档"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 提取标题
    title = filename.replace('.md', '').split('_', 1)[-1] if '_' in filename else filename.replace('.md', '')
    # 去掉uuid前缀
    title = re.sub(r'^[a-f0-9]{12}_', '', title)
    title = title.replace('_', ' ')
    
    data = {
        "title": title[:200],
        "content": content,
        "project_id": STAGING_PROJECT_ID,
        "tags": tags,
        "source_url": f"file://{filename}",
    }
    
    try:
        resp = requests.post(
            f"{RKR_API}/external/documents/text",
            headers=headers,
            json=data,
            timeout=30
        )
        return {"status": resp.status_code, "response": resp.json() if resp.status_code < 500 else resp.text}
    except Exception as e:
        return {"status": -1, "response": str(e)}


def main():
    print("=" * 60)
    print("RKR知识库批量上传脚本")
    print("=" * 60)
    
    # 登录
    token = get_jwt_token()
    if not token:
        print("无法获取JWT token，退出")
        return
    
    print(f"✓ 登录成功")
    
    # 统计
    stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    # 处理每个目录
    for dir_name, base_tags in PROCESS_DIRS.items():
        md_files = process_directory(dir_name)
        if not md_files:
            continue
        
        print(f"\n📁 处理目录: {dir_name} ({len(md_files)} 个文件)")
        
        for f in md_files:
            stats["total"] += 1
            
            try:
                content = f.read_text(encoding='utf-8')
                
                # 跳过太大的文件
                if len(content) > 50000:
                    print(f"  ⏭️  跳过(太大): {f.name[:50]}")
                    stats["skipped"] += 1
                    continue
                
                result = upload_document(token, content, f.name, base_tags)
                
                if result["status"] == 201:
                    stats["success"] += 1
                    print(f"  ✓ 上传成功: {f.name[:50]}")
                else:
                    stats["failed"] += 1
                    print(f"  ✗ 失败({result['status']}): {f.name[:50]} - {str(result['response'])[:100]}")
                
                time.sleep(0.5)  # 避免请求过快
                
            except Exception as e:
                stats["failed"] += 1
                print(f"  ✗ 异常: {f.name[:50]} - {e}")
    
    # 处理根目录的MD文件
    print(f"\n📁 处理根目录")
    for f in KB_ROOT.glob("*.md"):
        if should_skip_path(f):
            continue
        stats["total"] += 1
        
        try:
            content = f.read_text(encoding='utf-8')
            if len(content) > 50000:
                stats["skipped"] += 1
                continue
            
            result = upload_document(token, content, f.name, ["知识库", "杂项"])
            
            if result["status"] == 201:
                stats["success"] += 1
                print(f"  ✓ 上传成功: {f.name[:50]}")
            else:
                stats["failed"] += 1
                print(f"  ✗ 失败({result['status']}): {f.name[:50]}")
            
            time.sleep(0.5)
        except Exception as e:
            stats["failed"] += 1
            print(f"  ✗ 异常: {f.name[:50]} - {e}")
    
    # 总结
    print("\n" + "=" * 60)
    print("上传完成")
    print(f"总计: {stats['total']} | 成功: {stats['success']} | 失败: {stats['failed']} | 跳过: {stats['skipped']}")
    print("=" * 60)


if __name__ == "__main__":
    main()