#!/usr/bin/env python3
# TODO(tech-debt): 用 Claude Code 重写时改用 yaml 库 + jinja2 模板代替手写字符串

"""给 7 个 profile 的 AGENTS.md 顶部加 core_skills 字段 (Week 1 Day 2)"""
import argparse
import os
import sys
import re

# 7 个 profile 的分类(玉芬 8/3 拍板)
PROFILES = {
    "xiaobao": {
        "display_name": "小宝",
        "role": "商务运营/销售",
        "core_label": "核心 1+2 主力",
        "core": [
            ("xiaobao-workflow", "小宝自己的核心工作流"),
            ("xiaobao-sales", "小宝销售方法论(49 个 B2B 技能)"),
            ("predictable-revenue", "可预测收入模型"),
            ("scorecard-marketing", "评分卡营销"),
            ("prospecting", "客户开拓"),
            ("made-to-stick", "信息黏性"),
            ("storybrand-messaging", "故事品牌信息"),
            ("maodou-product", "渔芯产品定位"),
            ("yuwei-research-protocol", "渔芯研究协议"),
            ("***SECRET***", "飞书凭据管理"),
        ],
        "domain": ["sales", "feishu-bot", "feishu-doc", "feishu-drive", "spined", "social-media",
                   "brand-guidelines", "content-creation", "mom-test", "jobs-to-be-done",
                   "negotiation", "influence-psychology", "hooked-ux", "lean-startup",
                   "traction-eos", "design-sprint", "product", "research", "note-taking",
                   "internal-comms", "github", "productivity", "knowledge-base",
                   "feishu-api-notify", "hermes-internals"],
    },
    "afu": {
        "display_name": "阿福",
        "role": "客服/异议处理",
        "core_label": "核心 1+2",
        "core": [
            ("afu-customer-service", "阿福客服核心"),
            ("***SECRET***", "阿福自进化协议"),
            ("afu-workflow", "阿福工作流"),
            ("maodou-product", "渔芯产品定位"),
            ("aquaculture", "渔芯产品领域知识"),
            ("***SECRET***", "飞书凭据管理"),
            ("yuwei-research-protocol", "渔芯研究协议"),
            ("hooked-ux", "习惯养成 UX"),
            ("influence-psychology", "说服心理学"),
            ("mom-test", "客户访谈 Mom Test"),
        ],
        "domain": ["customer-service", "objection-handling", "feishu-bot", "feishu-doc",
                   "knowledge-base", "feishu-api-notify", "social-media", "brand-guidelines",
                   "predictable-revenue", "scorecard-marketing", "made-to-stick",
                   "storybrand-messaging", "research", "note-taking", "internal-comms",
                   "lean-startup", "design-sprint", "product", "negotiation",
                   "jobs-to-be-done", "traction-eos", "productivity", "github",
                   "hermes-internals", "feishu-drive"],
    },
    "heidou": {
        "display_name": "黑豆",
        "role": "行政/财务/法务",
        "core_label": "核心 1+2+3",
        "core": [
            ("heidou-workflow", "黑豆工作流"),
            ("heidou-admin", "黑豆行政核心"),
            ("yuwei-research-protocol", "渔芯研究协议"),
            ("***SECRET***", "飞书凭据管理"),
            ("maodou-product", "渔芯产品定位"),
            ("predictable-revenue", "可预测收入"),
            ("traction-eos", "EOS 创业系统"),
            ("mom-test", "客户访谈"),
            ("negotiation", "商务谈判"),
            ("internal-comms", "内部沟通"),
        ],
        "domain": ["finance", "legal", "compliance", "admin", "feishu-doc", "feishu-drive",
                   "feishu-bot", "feishu-api-notify", "brand-guidelines", "product",
                   "research", "note-taking", "productivity", "github", "hermes-internals",
                   "knowledge-base", "social-media", "scorecard-marketing", "made-to-stick",
                   "lean-startup", "design-sprint", "jobs-to-be-done", "hooked-ux",
                   "influence-psychology", "prospecting"],
    },
    "laomo": {
        "display_name": "老莫",
        "role": "技术运维/知识库",
        "core_label": "核心 1+2+3",
        "core": [
            ("laomo-workflow", "老莫工作流"),
            ("laomo-knowledge", "老莫知识库核心"),
            ("knowledge-base", "ChromaDB 知识库"),
            ("***SECRET***", "飞书凭据管理"),
            ("yuwei-research-protocol", "渔芯研究协议"),
            ("maodou-product", "渔芯产品定位"),
            ("research", "调研"),
            ("github", "代码管理"),
            ("testing", "测试方法"),
            ("bugfix", "Bug 修复"),
        ],
        "domain": ["data-science", "jupyter-live-kernel", "mlops", "chroma",
                   "hermes-skill-library", "hermes-agent-skill-authoring", "long-running-task",
                   "devops", "docker-management", "***SECRET***",
                   "cron-health-monitor", "hermes-search-diagnosis",
                   "hermes-gateway-profile-ops", "hermes-script-env-pitfalls",
                   "hermes-profile-migration", "software-development", "productivity",
                   "note-taking", "internal-comms", "feishu-api-notify", "hermes-internals",
                   "product", "lean-startup", "design-sprint", "agent-experience"],
    },
    "quant": {
        "display_name": "宽博士",
        "role": "量化研究",
        "core_label": "核心 3 主力",
        "core": [
            ("kbs-doctor-heartbeat", "宽博士心跳工作流"),
            ("***SECRET***", "飞书凭据管理"),
            ("research", "调研"),
            ("knowledge-base", "知识库"),
            ("github", "代码管理"),
            ("productivity", "生产力工具"),
            ("note-taking", "笔记"),
            ("internal-comms", "内部沟通"),
            ("hermes-internals", "Hermes 内部"),
            ("yuwei-research-protocol", "渔芯研究协议"),
        ],
        "domain": ["quantitative-research", "jupyter-live-kernel", "data-science", "mlops",
                   "chroma", "blogwatcher", "polymarket", "hermes-search-diagnosis",
                   "product", "lean-startup"],
    },
    "zhenglishi": {
        "display_name": "学习助手",
        "role": "学习/核心 3 训练数据",
        "core_label": "核心 3 主力",
        "core": [
            ("zhenglishi-workflow", "整理师工作流"),
            ("knowledge-organizer", "知识库整理助手"),
            ("***SECRET***", "飞书凭据管理"),
            ("yuwei-research-protocol", "渔芯研究协议"),
            ("research", "调研"),
            ("note-taking", "笔记"),
            ("internal-comms", "内部沟通"),
            ("github", "代码管理"),
            ("productivity", "生产力工具"),
            ("hermes-internals", "Hermes 内部"),
        ],
        "domain": ["llm-wiki", "chinese-classics-research", "arxiv", "obsidian", "qmd",
                   "hermes-search-diagnosis", "blogwatcher", "personal-knowledge-rag",
                   "hindsight-local", "hindsight-cloud"],
    },
    "community": {
        "display_name": "社区总负责",
        "role": "渔芯社区对外品牌/销售/CRM",
        "core_label": "核心 2 主力",
        "core": [
            ("maodou-product", "渔芯产品定位"),
            ("yuwei-research-protocol", "渔芯研究协议"),
            ("***SECRET***", "飞书凭据管理"),
            ("predictable-revenue", "可预测收入"),
            ("scorecard-marketing", "评分卡营销"),
            ("made-to-stick", "信息黏性"),
            ("storybrand-messaging", "故事品牌"),
            ("brand-guidelines", "品牌指南"),
            ("social-media", "社交媒体"),
            ("prospecting", "客户开拓"),
        ],
        "domain": ["feishu-bot", "feishu-doc", "feishu-drive", "feishu-api-notify",
                   "mom-test", "jobs-to-be-done", "influence-psychology", "hooked-ux",
                   "lean-startup", "design-sprint"],
    },
}

HERMES_ROOT = "/Users/hua/.hermes"
L0_PROTOCOL = f"{HERMES_ROOT}/memory_store/shared/03_collaboration_protocol.md"


def build_core_skills_section(profile_name, info):
    """构造 core_skills markdown 段"""
    lines = []
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"## 🎯 core_skills(Week 1 Day 2 新增,启动必读 {len(info['core'])} 个)")
    lines.append("")
    lines.append(f"> {info['display_name']} 的 skills 已分类为 core/domain/on-demand,启动时**只读 core**,做本职工作时按需加载 domain,**其余 on-demand 不进 context**。")
    lines.append(f"> 详见 `{L0_PROTOCOL} §七`")
    lines.append("")
    lines.append("| # | skill | 必读原因 |")
    lines.append("|---|---|---|")
    for i, (skill, reason) in enumerate(info["core"], 1):
        lines.append(f"| {i} | {skill} | {reason} |")
    lines.append("")
    lines.append(f"**domain skills({len(info['domain'])} 个,本职工作时按需加载)**:" + ", ".join(info["domain"]))
    lines.append("")
    lines.append("**on-demand**(其余,默认不加载,显式 `skill_view` 调用)")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def already_has_core_skills(content):
    """检测 AGENTS.md 是否已经有 core_skills 段(防重复)"""
    return "## 🎯 core_skills" in content or "core_skills(Week 1 Day 2" in content


def insert_core_skills(content, section):
    """把 core_skills 段插入 AGENTS.md,在第一个 '## 🛡️ 铁律' 段前"""
    if "## 🛡️ 铁律" in content:
        new_content = content.replace("## 🛡️ 铁律", section + "## 🛡️ 铁律", 1)
    else:
        # 如果没找到铁律段,加到 '---' 第一个分隔符后
        new_content = content.replace("---\n\n", section + "---\n\n", 1)

    # 去重连续的 ---(可能在插入位置产生空行 + 重复分隔符)
    import re
    new_content = re.sub(r'(^---\n)\n*---\n', r'\1', new_content, flags=re.MULTILINE)
    return new_content


def update_version_label(content):
    """v5 → v6"""
    if "v6" in content and "Week 1 Day 2" in content:
        return content  # 已更新
    content = re.sub(
        r"v\d+ — 新增 \*\*代码开发铁律\*\*\(华哥 8/3 全公司铁律,优先级最高\)",
        "v6 — 新增 **code_skills 字段**(Week 1 Day 2 团队协作机制升级) + **代码开发铁律**(华哥 8/3 全公司铁律,优先级最高)",
        content
    )
    return content


def process_profile(profile_name, info, dry_run=False):
    """处理单个 profile"""
    agents_path = f"{HERMES_ROOT}/profiles/{profile_name}/AGENTS.md"
    if not os.path.exists(agents_path):
        return False, f"❌ {profile_name}: AGENTS.md 不存在"

    with open(agents_path, "r", encoding="utf-8") as f:
        content = f.read()

    if already_has_core_skills(content):
        return True, f"⏭  {profile_name}: 已有 core_skills 段,跳过"

    # 更新版本
    new_content = update_version_label(content)
    # 构造并插入 core_skills 段
    section = build_core_skills_section(profile_name, info)
    new_content = insert_core_skills(new_content, section)

    if dry_run:
        return True, f"🔍 {profile_name}: 干跑 OK ({len(info['core'])} core / {len(info['domain'])} domain)"

    with open(agents_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True, f"✅ {profile_name}: {len(info['core'])} core / {len(info['domain'])} domain 写入成功"


def main():
    parser = argparse.ArgumentParser(description="给 7 个 profile 加 core_skills 字段 (Week 1 Day 2)")
    parser.add_argument("--profile", help="只处理单个 profile")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写")
    args = parser.parse_args()

    profiles_to_process = {args.profile: PROFILES[args.profile]} if args.profile else PROFILES

    if args.profile and args.profile not in PROFILES:
        print(f"❌ 未知 profile: {args.profile}")
        print(f"   可选: {', '.join(PROFILES.keys())}")
        sys.exit(1)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}开始处理 {len(profiles_to_process)} 个 profile:")
    print()

    success_count = 0
    for name, info in profiles_to_process.items():
        ok, msg = process_profile(name, info, dry_run=args.dry_run)
        print(msg)
        if ok:
            success_count += 1

    print()
    print(f"完成: {success_count}/{len(profiles_to_process)} 成功")


if __name__ == "__main__":
    main()
