#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Codex ~/.codex/skills/ 目录分类脚本（1012 沿铁律 112 沉淀）

用法：
    python skill-categorize.py                    # 默认 ~/.codex/skills/
    python skill-categorize.py /path/to/skills/   # 自定义路径

输出：
    Total: N
      DEV:  N
      MKT:  N
      OTHER: N
      OTHER 列表: [...]

维护：
    - 新增 skill → 同步更新下方 dev / mkt 集合
    - 集名 lowercase + 与目录名一致
    - OTHER 桶应 ≤ 5（yuxin-* 业务 + sepia*.bak 备份）
"""
import os
import sys
from pathlib import Path

# 沿铁律 112 — dev 集合（开发 / 编程 / 测试 / 工程化）
DEV = set([
    # 核心开发
    "codex-hygiene", "fastapi-expert", "react-expert", "mcp-server-builder",
    "rag-architect", "playwright", "playwright-interactive", "screenshot",
    "grep-ts", "cli-creator", "dispatching-parallel-agents", "executing-plans",
    "finishing-a-development-branch", "fix-ci", "forward-implementation-first",
    "refactoring-ui", "receiving-code-review", "requesting-code-review",
    "search-miss-binary", "simplify-codebase", "spec-literal-execution",
    "subagent-driven-development", "systematic-debugging",
    "test-driven-development", "using-git-worktrees", "using-superpowers",
    "verification-before-completion", "verify-output-readback", "writing-plans",
    "writing-skills", "web-artifacts-builder", "tokencut", "aida",
    "trace-harness-launch-failure", "script-exec-blocked", "autoprompt",
    "no-negative-echo", "remove-ai-marks", "sloptrim",
    # 视觉 / 媒体生成
    "frontend-design", "claw-browser-anchor", "image-prompt-reverse",
    "image-story-video-wizard", "image", "video", "sureforge",
    # 知识管理 / 工具
    "llm-wiki-manager",
    # 审查 / 评审（1101 归位）
    "simple-reviewer-v1",
])

# 沿铁律 112 — mkt 集合（营销 / 内容 / 增长 / SEO）
MKT = set([
    # 营销基础
    "ab-testing", "ad-creative", "ads", "ai-seo", "analytics", "attribution",
    "audience-growth-tracker-sms", "brainstorming", "brand-guidelines",
    "canvas-design", "caption-writer-sms", "carousel-writer-sms",
    "chinese-grammar-proofreader", "churn-prevention", "clean-user-facing-text",
    "cold-email", "co-marketing", "community-marketing", "competitor-profiling",
    "competitors", "content-boom-monitor", "content-calendar-sms",
    "content-pattern-analyzer-sms", "content-repurposer-sms", "content-strategy",
    "content-strategy-sms", "copy-editing", "copywriting", "cro",
    "customer-research", "directory-submissions", "emails", "events",
    "free-tools", "hook-writer-sms", "influencer-marketing", "launch",
    "lead-gen-video-script", "lead-magnets", "marketing-council",
    "marketing-ideas", "marketing-loops", "marketing-mindset", "marketing-os",
    "marketing-plan", "marketing-psychology", "offers", "onboarding",
    "optimization-advisor-sms", "paywalls", "performance-analyzer-sms",
    "platform-strategy-sms", "popups", "post-writer-sms", "pricing",
    "product-marketing", "programmatic-seo", "prospecting", "public-relations",
    "referrals", "revops", "sales-enablement", "schema", "seo-audit",
    "seo-landing", "signup", "site-architecture", "social",
    "social-media-context-sms", "theme-factory", "thread-writer-sms",
    "xiaohongshu-concept-explainer", "xiaohongshu-layout-factory",
    "xiaoma-durex-copywriter", "douyin-image-post-scheduler", "doc-gen",
    # 研究 / 调研
    "cida", "zh-tech-writing", "super-research",
    # 营销运营类垂类（1101 cron 归位：转化追踪/外链/营销逆向拆解）
    "conversion-tracking", "link-building", "reverse-engineer-marketing",
])

# 1101 新增 — VERT 集合（4 业务线垂类：养殖 / 自媒体发布 / 内容 IP 系列）
# 养殖线 + 自媒体运营线 + 太上老君内容系列；OTHER 桶只留 yuxin-* / sepia*.bak / myoffice
VERT = set([
    # 养殖线
    "aquaculture-water-quality-optimizer", "ras-coldwater-aquaculture",
    "red-tide-algal-bloom",
    # 自媒体运营线
    "auto-xhs", "xiaohongshu-skills", "douyin-comments", "guizang-social-card",
    "last30days-cn",
    # 太上老君内容系列
    "taishang-laojun", "tslj-idea", "tslj-monetize", "tslj-open",
    "tslj-script", "tslj-select", "tslj-series", "tslj-title",
    # 1104 新增 — 短剧/漫剧/去AI味内容垂类（short-drama-factory 兄弟cron装，manju 21题材 + unslop 本cron装）
    "short-drama-factory", "unslop",
    "chongsheng-manju", "chuanyue-manju", "dushi-manju", "gongdou-manju",
    "jiating-manju", "minsu-manju", "moshi-manju", "niandai-manju",
    "quanmou-manju", "shangzhan-manju", "tianchong-manju", "wuxia-manju",
    "xiaoyuan-manju", "xihuan-manju", "xingji-manju", "xitong-manju",
    "xuanhuan-manju", "xuanyi-manju", "yule-manju", "zhaidou-manju",
    "zhongtian-manju",
])


def list_skills(skills_dir: Path) -> list:
    """列目录下所有 skill 子目录名（去重 + 排序）"""
    if not skills_dir.exists():
        print(f"❌ 目录不存在: {skills_dir}", file=sys.stderr)
        sys.exit(1)
    skills = []
    for p in sorted(skills_dir.iterdir()):
        if p.is_dir() and not p.name.startswith("."):
            skills.append(p.name)
    return skills


def categorize(skills: list) -> dict:
    """沿铁律 112 — 四桶分类 DEV / MKT / VERT / OTHER（1101 新增 VERT 垂类桶）"""
    buckets = {"DEV": [], "MKT": [], "VERT": [], "OTHER": []}
    for s in skills:
        if s in DEV:
            buckets["DEV"].append(s)
        elif s in MKT:
            buckets["MKT"].append(s)
        elif s in VERT:
            buckets["VERT"].append(s)
        else:
            buckets["OTHER"].append(s)
    return buckets


def main():
    skills_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".codex" / "skills"
    skills = list_skills(skills_dir)
    buckets = categorize(skills)

    print(f"Total: {len(skills)}")
    for k in ("DEV", "MKT", "VERT", "OTHER"):
        print(f"  {k}: {len(buckets[k])}")
    print()
    if buckets["VERT"]:
        print(f"VERT 列表: {buckets['VERT']}")
        print()
    if buckets["OTHER"]:
        print(f"OTHER 列表: {buckets['OTHER']}")

    # 返回非零 exit code 提示 OTHER 桶膨胀（> 5 需维护集合）
    if len(buckets["OTHER"]) > 5:
        print(f"\n⚠️ OTHER 桶 {len(buckets['OTHER'])} > 5，需更新 DEV/MKT 集合",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
