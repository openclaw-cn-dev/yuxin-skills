#!/usr/bin/env python3
"""generate_profile_metadata.py — 8 profile 一键生成 profile.json

华哥 8/3 决策:每个 agent profile 必须有 profile.json 作为 L2 元数据标准件
"""
import json
import os
import re
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROFILES_DIR = Path("/Users/hua/.hermes/profiles")

# 已知 agent 角色(来自 6/30 团队架构 + 8/3 v3 AGENTS.md + 8/3 新增 community)
AGENT_ROLE_MAP = {
    "default": {"role": "全公司总负责人 / 汇报", "core": "core1+2+3", "owner": "玉芬"},
    "maodou": {"role": "产品交付 / 3D 工程 / AI 出 CAD", "core": "core1", "owner": "玉芬"},
    "xiaobao": {"role": "商务运营 / 销售 / 自媒体", "core": "core1+2", "owner": "玉芬"},
    "afu": {"role": "客服 / 异议处理 / 4-360行主理", "core": "core1+2", "owner": "玉芬"},
    "heidou": {"role": "行政 / 财务 / 法务 / 合规", "core": "core1+2+3", "owner": "玉芬"},
    "laomo": {"role": "技术运维 / 知识库 / 测试", "core": "core1+2+3", "owner": "玉芬"},
    "quant": {"role": "量化研究 / 核心 3 RAG 数据", "core": "core3", "owner": "华哥直派"},
    "zhenglishi": {"role": "个人学习 / 知识整理 / 核心 3 训练数据", "core": "core3", "owner": "华哥直派"},
    "community": {"role": "渔芯社区总负责 / 对外品牌 + 销售 + CRM", "core": "core2", "owner": "玉芬"},
}

def count_skills(profile_dir: Path) -> int:
    """统计 profile/skills/ 下所有 SKILL.md 文件"""
    skills_dir = profile_dir / "skills"
    if not skills_dir.exists():
        return 0
    return len(list(skills_dir.glob("*/SKILL.md")))

def count_memory(profile_dir: Path) -> int:
    """统计 profile/memory/ 下所有 .md 文件"""
    memory_dir = profile_dir / "memories"
    if not memory_dir.exists():
        return 0
    return len([f for f in memory_dir.glob("*.md") if f.is_file()])

def count_cron(profile_dir: Path) -> int:
    """统计 profile/cron/jobs.json 下的任务数"""
    cron_file = profile_dir / "cron" / "jobs.json"
    if not cron_file.exists():
        return 0
    try:
        data = json.load(open(cron_file))
        # 格式可能是 {"jobs": [...]} 或直接 list
        if isinstance(data, dict) and "jobs" in data:
            return len(data["jobs"])
        if isinstance(data, list):
            return len(data)
        return 0
    except Exception:
        return 0

def get_uptime_days(profile_dir: Path) -> int:
    """profile 目录最早文件的修改时间 → 估算 uptime"""
    if not profile_dir.exists():
        return 0
    earliest = datetime.now(timezone(timedelta(hours=8)))
    for f in profile_dir.rglob("*"):
        if f.is_file():
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone(timedelta(hours=8)))
                if mtime < earliest:
                    earliest = mtime
            except Exception:
                pass
    return (datetime.now(timezone(timedelta(hours=8))) - earliest).days

def main():
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    print(f"📋 扫描 9 profiles @ {now}")
    print("=" * 60)

    for profile_name, meta in AGENT_ROLE_MAP.items():
        profile_dir = PROFILES_DIR / profile_name
        if not profile_dir.exists():
            print(f"  ⚠ {profile_name} - 目录不存在,跳过")
            continue

        skills_count = count_skills(profile_dir)
        memory_count = count_memory(profile_dir)
        cron_count = count_cron(profile_dir)
        uptime_days = get_uptime_days(profile_dir)

        profile_json = {
            "name": profile_name,
            "role": meta["role"],
            "core": meta["core"],
            "owner": meta["owner"],
            "layer": "L2" if profile_name in ["default"] else "L3",
            "created_at": None,  # 后续可补
            "updated_at": now,
            "skills_count": skills_count,
            "memory_count": memory_count,
            "cron_count": cron_count,
            "uptime_days": uptime_days,
            "linked_agents": ["default"],  # 默认连玉芬
            "feishu_channel": None,  # 后续可补
        }

        output_file = profile_dir / "profile.json"
        output_file.write_text(json.dumps(profile_json, indent=2, ensure_ascii=False))
        print(f"  ✅ {profile_name:12} | skills={skills_count:3} mem={memory_count:3} cron={cron_count:2} up={uptime_days:3}d | {meta['role'][:30]}")

    print("=" * 60)
    print(f"✅ 已生成 {len(AGENT_ROLE_MAP)} 份 profile.json")

if __name__ == "__main__":
    main()
