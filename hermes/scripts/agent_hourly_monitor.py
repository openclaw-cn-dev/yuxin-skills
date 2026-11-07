#!/usr/bin/env python3
"""
每小时Agent状态监控 + 自我提升任务分配

逻辑：
1. 读取所有Agent的MEMORY.md最后修改时间（活跃度指标）
2. 读取本地任务队列状态（task_queue.json）
3. 判断空闲Agent → 写自我提升内容到其文件夹
4. 判断有任务但超时的 → 触发提醒
5. 汇总状态，写入共享状态文件供dashboard读取
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

TEAM_DIR = "/Users/hua/Desktop/渔芯科技/团队协作"
STATUS_FILE = f"{TEAM_DIR}/agent_hourly_status.json"

# 各Agent的MEMORY.md路径
AGENT_MEMORY = {
    "毛豆": "/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付/memory/MEMORY.md",
    "老莫": "/Users/hua/Desktop/渔芯科技/4-部门空间/老莫-技术运维/memory/MEMORY.md",
    "小宝": "/Users/hua/Desktop/渔芯科技/4-部门空间/小宝-商务运营/memory/MEMORY.md",
    "黑豆": "/Users/hua/Desktop/渔芯科技/4-部门空间/黑豆-行政财务法务/memory/MEMORY.md",
    "阿福": "/Users/hua/Desktop/渔芯科技/4-部门空间/阿福-客服/memory/MEMORY.md",
}

# 各Agent的文件夹（用于写自我提升内容）
AGENT_FOLDERS = {
    "毛豆": "/Users/hua/Desktop/渔芯科技/4-部门空间/毛豆-产品交付",
    "老莫": "/Users/hua/Desktop/渔芯科技/4-部门空间/老莫-技术运维",
    "小宝": "/Users/hua/Desktop/渔芯科技/4-部门空间/小宝-商务运营",
    "黑豆": "/Users/hua/Desktop/渔芯科技/4-部门空间/黑豆-行政财务法务",
    "阿福": "/Users/hua/Desktop/渔芯科技/4-部门空间/阿福-客服",
}

# 各Agent的擅长领域（用于分配常规任务）
AGENT_DOMAINS = {
    "毛豆": ["LookForge", "产品", "开发", "Phase", "ChromaDB", "向量", "SaaS"],
    "老莫": ["知识库", "调研", "研究", "文档", "测试", "基础设施", "Docker"],
    "小宝": ["销售", "自媒体", "内容", "运营", "推广", "素材", "客户"],
    "黑豆": ["行政", "财务", "法务", "合规", "合同", "制度", "流程"],
    "阿福": ["测试", "客服", "验收", "演示", "功能", "回归"],
}

# 空闲时分配的常规自我提升任务
SELF_IMPROVEMENT_TASKS = {
    "毛豆": [
        ("LookForge产品体验优化建议.md", """# LookForge产品体验优化建议

分析当前LookForge产品的用户体验，提出至少5条可落地的改进建议。

要求：
- 从用户角度出发
- 每条建议附带优先级（P1/P2/P3）
- 包含竞品参考
- 保存到本文件夹
"""),
    ],
    "老莫": [
        ("RAS行业技术自查报告.md", """# RAS循环水养殖技术自查报告

对照行业最新技术标准，检查公司现有知识库的覆盖度和准确度。

要求：
- 列出知识盲区清单
- 标注需要更新的内容
- 补充3个新技术方向
- 保存到本文件夹
"""),
    ],
    "小宝": [
        ("竞品内容营销分析.md", """# 竞品内容营销分析

分析3家竞品的自媒体内容策略：选题/风格/频率/转化。

要求：
- 每家竞品一个独立章节
- 总结可借鉴点
- 提出我方差异化方向
- 保存到本文件夹
"""),
    ],
    "黑豆": [
        ("公司制度漏洞排查.md", """# 公司制度漏洞排查

检查现有公司制度流程，识别3-5个潜在风险点或执行漏洞。

要求：
- 每个漏洞说明风险等级
- 提出改进建议
- 保存到本文件夹
"""),
    ],
    "阿福": [
        ("客服FAQ优化建议.md", """# 客服FAQ优化建议

分析现有客服FAQ，识别高频问题和回答质量改进空间。

要求：
- 列出Top10高频问题
- 评估当前回答质量（1-5分）
- 给出优化后的标准回答
- 保存到本文件夹
"""),
    ],
}

sys.path.insert(0, TEAM_DIR)

def get_agent_status() -> dict:
    """获取各Agent状态"""
    now = time.time()
    agents = []

    for name, mem_path in AGENT_MEMORY.items():
        if os.path.exists(mem_path):
            mtime = os.path.getmtime(mem_path)
            age_min = (now - mtime) / 60
            folder = AGENT_FOLDERS[name]

            # 检查是否有最近生成的自我提升内容
            self_improvement_file = Path(folder) / f"{SELF_IMPROVEMENT_TASKS.get(name, [None])[0][0] if SELF_IMPROVEMENT_TASKS.get(name) else None}"

            agents.append({
                "name": name,
                "memory_age_min": int(age_min),
                "memory_path": mem_path,
                "folder": folder,
                "domains": AGENT_DOMAINS.get(name, []),
                "status": "active" if age_min < 30 else ("idle" if age_min < 120 else "absent"),
            })
        else:
            agents.append({
                "name": name,
                "memory_age_min": -1,
                "status": "no_record",
            })

    return agents


def assign_self_improvement(agent_name: str) -> list:
    """为某Agent分配自我提升任务，返回生成的文件列表"""
    folder = AGENT_FOLDERS.get(agent_name)
    tasks = SELF_IMPROVEMENT_TASKS.get(agent_name, [])
    if not folder or not tasks:
        return []

    created = []
    for filename, content in tasks:
        filepath = Path(folder) / filename
        if not filepath.exists():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            full_content = f"{content}\n\n---\n*由玉芬自动生成于 {timestamp} | 如已完成可删除此文件*"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            created.append(str(filepath))
    return created


def run():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始每小时Agent监控...")

    agents = get_agent_status()

    status = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "agents": agents,
        "idle_agents": [],
        "active_agents": [],
        "self_improvement_created": [],
        "message": "",
    }

    for a in agents:
        if a["status"] == "idle":
            status["idle_agents"].append(a["name"])
            # 为空闲Agent分配自我提升任务
            created = assign_self_improvement(a["name"])
            if created:
                status["self_improvement_created"].extend(created)
                print(f"  [{a['name']}] 空闲 → 分配自我提升任务: {', '.join([Path(c).name for c in created])}")
        elif a["status"] == "active":
            status["active_agents"].append(a["name"])

    # 写入状态文件
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

    # 汇总消息
    active_count = len(status["active_agents"])
    idle_count = len(status["idle_agents"])
    si_count = len(status["self_improvement_created"])

    status["message"] = (
        f"监控完成 | 活跃{active_count} | 空闲{idle_count} | "
        f"{'已分配自我提升任务' if si_count > 0 else '无自我提升分配'}"
    )
    print(f"  {status['message']}")
    print(f"  状态文件: {STATUS_FILE}")

    return status


if __name__ == "__main__":
    run()
