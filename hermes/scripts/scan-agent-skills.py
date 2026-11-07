#!/usr/bin/env python3
"""
scan-agent-skills.py
全面扫描 Hermes/Claude Agent 技能生态，发现新技能自动安装。
覆盖范围：
  1. VoltAgent 官方技能仓库（37个）—— 每周三09:00全量扫描
  2. Hermes 生态热点项目 stars 监控
  3. GitHub topic 趋势发现（hermes-skill/claude-skill/agent-skill）
  4. awesome-hermes-agent 列表跟踪
  5. 每日增量扫描 priority repos
"""
import subprocess
import json
import os
import sys
import importlib.util
import shutil
import re
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Callable, Optional

HERMES_SKILLS = Path.home() / ".hermes" / "skills"
SOURCES = Path.home() / ".cache" / "hermes-skill-sources"
LOG_FILE = Path.home() / ".hermes" / "logs" / "skill-scan.log"
STATE_FILE = Path.home() / ".cache" / "hermes-skill-sources" / "scan_state.json"

# ─── 全量扫描列表（37个 VoltAgent 官方技能仓库）───────────────────────────────
ALL_VOLT_REPOS = [
    ("anthropics",       "https://github.com/anthropics/skills.git",              "skills"),
    ("vercel-labs",      "https://github.com/vercel-labs/skills.git",             "skills"),
    ("angular",          "https://github.com/angular/skills.git",                 "skills"),
    ("supabase",         "https://github.com/supabase/skills.git",                "skills"),
    ("stripe",           "https://github.com/stripe/stripe-skills.git",           "skills"),
    ("callstackincubator","https://github.com/callstackincubator/skills.git",    "skills"),
    ("better-auth",      "https://github.com/better-auth/skills.git",            "skills"),
    ("tinybirdco",       "https://github.com/tinybirdco/skills.git",             "skills"),
    ("google-gemini",    "https://github.com/google-gemini/skills.git",          "skills"),
    ("composiohq",       "https://github.com/composiohq/skills.git",             "skills"),
    ("trycourier",       "https://github.com/trycourier/courier-skills.git",     "skills"),
    ("firecrawl",        "https://github.com/firecrawl/skills.git",              "skills"),
    ("neondatabase",     "https://github.com/neondatabase/skills.git",          "skills"),
    ("HashiCorp",        "https://github.com/hashicorp/skills.git",              "skills"),
    ("sanity-io",        "https://github.com/sanity-io/skills.git",             "skills"),
    ("ClickHouse",       "https://github.com/ClickHouse/skills.git",            "skills"),
    ("remotion-dev",     "https://github.com/remotion-dev/skills.git",          "skills"),
    ("replicate",        "https://github.com/replicate/skills.git",             "skills"),
    ("typefully",        "https://github.com/typefully/skills.git",             "skills"),
    ("Cloudflare",       "https://github.com/cloudflare/skills.git",            "skills"),
    ("netlify",          "https://github.com/netlify/skills.git",               "skills"),
    ("trailofbits",      "https://github.com/trailofbits/skills.git",           "skills"),
    ("getsentry",        "https://github.com/getsentry/skills.git",             "skills"),
    ("expo",             "https://github.com/expo/skills.git",                  "skills"),
    ("huggingface",      "https://github.com/huggingface/skills.git",           "skills"),
    ("Figma",            "https://github.com/figma/skills.git",                 "skills"),
    ("Microsoft",        "https://github.com/microsoft/skills.git",              "skills"),
    ("WordPress",        "https://github.com/WordPress/skills.git",             "skills"),
    ("OpenAI",           "https://github.com/openai/skills.git",               "skills"),
    ("fal-ai",           "https://github.com/fal-ai/skills.git",               "skills"),
    ("Resend",           "https://github.com/resend/skills.git",                "skills"),
    ("Notion",           "https://github.com/notion-skills/skills.git",         "skills"),
    ("ApolloGraphQL",    "https://github.com/apollographql/skills.git",         "skills"),
    ("auth0",            "https://github.com/auth0/skills.git",                 "skills"),
    ("Browserbase",      "https://github.com/browserbase/skills.git",           "skills"),
    ("CodeRabbitAI",      "https://github.com/CodeRabbitAI/skills.git",        "skills"),
    ("MongoDB",          "https://github.com/mongodb/skills.git",               "skills"),
    ("Firebase",         "https://github.com/firebase/skills.git",              "skills"),
    ("Flutter",          "https://github.com/flutter/skills.git",               "skills"),
    ("DuckDB",           "https://github.com/duckdb/skills.git",                "skills"),
    ("GSAP",             "https://github.com/GSAP/skills.git",                 "skills"),
]

# Priority repos（每日扫描，高频）
PRIORITY_REPOS = [
    ("anthropics",       "https://github.com/anthropics/skills.git",              "skills"),
    ("vercel-labs",      "https://github.com/vercel-labs/skills.git",             "skills"),
    ("wondelai",         "https://github.com/wondelai/skills.git",                ".claude/skills"),
    ("supabase",         "https://github.com/supabase/skills.git",               "skills"),
    ("stripe",           "https://github.com/stripe/stripe-skills.git",          "skills"),
    ("huggingface",      "https://github.com/huggingface/skills.git",           "skills"),
    ("composiohq",       "https://github.com/composiohq/skills.git",             "skills"),
    ("expo",             "https://github.com/expo/skills.git",                   "skills"),
    ("Google-gemini",    "https://github.com/google-gemini/skills.git",          "skills"),
    ("mongodb",          "https://github.com/mongodb/skills.git",                "skills"),
]

# Hermes 生态热点项目
HOT_PROJECTS = [
    ("gbrain",          "https://github.com/garrytan/gbrain",                  "memory",      "个性化记忆脑，11.4K★"),
    ("hermes-webui",    "https://github.com/nesquena/hermes-webui",             "workspace",   "Hermes网页GUI，4.2K★"),
    ("hermes-lcm",      "https://github.com/stephenschoettler/hermes-lcm",      "memory",      "DAG无损上下文，308★"),
    ("hindsight",       "https://github.com/vectorize-io/hindsight",            "memory",      "长期记忆服务，10.8K★"),
    ("mission-control", "https://github.com/builderz-labs/mission-control",     "multi-agent", "AI编排平台，3.9K★"),
    ("honeycomb",       "https://github.com/0xNyk/honeycomb",                   "analytics",   "Hermes遥测，462★"),
    ("skillclaw",       "https://github.com/AMAP-ML/SkillClaw",                "skill-dev",   "技能进化去重，705★"),
    ("autocontext",     "https://github.com/greyhaven-ai/autocontext",           "memory",      "递归上下文管理，960★"),
    ("honeycomb",       "https://github.com/0xNyk/honeycomb",                   "analytics",   "Hermes遥测"),
    ("hermes-atlas",    "https://github.com/nouveta-ai/hermes-atlas",           "registry",    "Hermes技能/工具目录"),
    ("openclaw",        "https://github.com/nouveta-ai/openclaw",               "framework",   "AI Agent框架，lookforge底座"),
]

SOURCES.mkdir(parents=True, exist_ok=True)

# ─── State management ────────────────────────────────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {"last_full_scan": None, "last_incremental_scan": None,
            "installed_skills": {}, "hot_stars": {}}

def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))

# ─── Logging ─────────────────────────────────────────────────────────────────
def log(msg: str):
    print(msg)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        ts = subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip()
    except:
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

# ─── Git operations ──────────────────────────────────────────────────────────
def git_clone_or_pull(url: str, dest: Path, name: str, depth: int = 1) -> bool:
    """Clone or fast-forward pull a git repo"""
    if dest.exists():
        try:
            subprocess.run(["git", "pull", "--ff", "origin", "main", "-q"],
                          cwd=dest, check=True, capture_output=True, timeout=30)
            log(f"  ↺ {name}: pulled")
            return True
        except subprocess.TimeoutExpired:
            log(f"  ⚠ {name}: pull timed out (using cached)")
            return False
        except subprocess.CalledProcessError:
            log(f"  ⚠ {name}: pull failed (using cached)")
            return False
    else:
        try:
            subprocess.run(["git", "clone", "--depth", str(depth), url, str(dest)],
                          check=True, capture_output=True, timeout=60)
            log(f"  ✓ {name}: cloned")
            return True
        except subprocess.TimeoutExpired:
            log(f"  ✗ {name}: clone timed out")
            return False
        except subprocess.CalledProcessError as e:
            log(f"  ✗ {name}: clone failed ({e})")
            return False

def get_installed() -> set:
    if not HERMES_SKILLS.exists():
        return set()
    return {d.name for d in HERMES_SKILLS.iterdir() if d.is_dir()}

def copy_skill(src_skill_dir: Path, dest_name: str) -> bool:
    dest = HERMES_SKILLS / dest_name
    try:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src_skill_dir, dest)
        return True
    except Exception as e:
        log(f"    ✗ copy failed: {dest_name}: {e}")
        return False

# ─── Skill discovery ────────────────────────────────────────────────────────
def find_skills_dir(repo_path: Path) -> Optional[Path]:
    """Find the skills directory in a cloned repo"""
    candidates = ["skills", ".claude/skills", ".cursor/skills",
                  "skill", ".claude/skill", ".cursor/skill", ""]
    for cand in candidates:
        p = repo_path / cand
        if p.exists() and p.is_dir():
            # Must contain subdirectories with SKILL.md
            if any((p / d / "SKILL.md").exists() for d in os.listdir(p) if (p / d).is_dir()):
                return p
    return None

def scan_and_install(repo_url: str, subdir: str, org: str, max_new: int = 10,
                     state: dict = None) -> int:
    """Clone/pull a skills repo, find new skills, install up to max_new"""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    dest = SOURCES / f"{org}-{repo_name}"
    name = f"{org}/{repo_name}"

    if not git_clone_or_pull(repo_url, dest, name):
        return 0

    skills_path = dest / subdir if subdir else dest
    skills_path = find_skills_dir(dest) or skills_path

    if not skills_path.exists():
        log(f"    skills dir not found in {name}")
        return 0

    installed = get_installed()
    new_skills = [d.name for d in skills_path.iterdir()
                  if d.is_dir() and d.name not in installed
                  and (d / "SKILL.md").exists()]
    if not new_skills:
        log(f"    {name}: 无新增")
        return 0

    log(f"    发现 {len(new_skills)} 个新技能: {', '.join(new_skills[:5])}{'...' if len(new_skills)>5 else ''}")
    count = 0
    for skill_name in sorted(new_skills):
        src = skills_path / skill_name
        if (src / "SKILL.md").exists():
            if copy_skill(src, skill_name):
                count += 1
                log(f"    ✓ installed: {skill_name}")
        if count >= max_new:
            log(f"    已安装 {count} 个，剩余 {len(new_skills) - count} 个待下次")
            break
    if count > 0:
        log(f"    ✓ {name}: 新增 {count} 个技能")
    return count

# ─── GitHub API with rate limit handling ────────────────────────────────────
def github_api(url: str, token: str = None) -> Optional[dict]:
    """Fetch GitHub API with token and rate limit handling"""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            log(f"  ⚠ GitHub API rate limit exceeded")
        else:
            log(f"  ⚠ HTTP {e.code}: {url}")
    except Exception as e:
        log(f"  ⚠ API error: {e}")
    return None

# ─── Hot projects stars monitoring ──────────────────────────────────────────
def monitor_hot_projects(state: dict):
    """Check stars growth for Hermes ecosystem projects"""
    log("--- Hermes 生态热点项目监控 ---")
    changes = []
    for name, url, category, desc in HOT_PROJECTS:
        repo = url.replace("https://github.com/", "")
        api_url = f"https://api.github.com/repos/{repo}"
        data = github_api(api_url)
        if data:
            stars = data.get("stargazers_count", 0)
            prev = state.get("hot_stars", {}).get(name)
            if prev:
                delta = stars - prev
                if delta > 0:
                    changes.append(f"  📈 {name}: {prev}→{stars} (+{delta})")
            state.setdefault("hot_stars", {})[name] = stars
            log(f"  · {name}: {stars}★ ({category})")
        else:
            log(f"  · {name}: (offline) {desc}")
    if changes:
        log("  Stars 变化:\n" + "\n".join(changes))

# ─── Topic discovery ────────────────────────────────────────────────────────
def discover_by_topic(state: dict):
    """Discover new repos by GitHub topic (启发式，不依赖API)"""
    # 启发式：根据已知的 skills 仓库模式主动探测
    # 不依赖搜索API（容易触发rate limit）
    known_patterns = [
        # (org, repo, skills_subdir)
        ("mattpocock", "skills", "skills"),
        ("nouveta-ai", "openclaw", "skills"),
        ("nouveta-ai", "hermes-atlas", "skills"),
        ("nesquena", "hermes-webui", "skills"),
        ("garrytan", "gbrain", "skills"),
        ("skills-you", "awesome-claude-skills", "skills"),
        ("modelcontextprotocol", "server-skills", "skills"),
    ]
    log("--- Topic 趋势发现 ---")
    for org, repo, subdir in known_patterns:
        url = f"https://github.com/{org}/{repo}.git"
        name = f"{org}/{repo}"
        dest = SOURCES / f"topic-{org}-{repo}"
        if git_clone_or_pull(url, dest, name, depth=1):
            skills_path = find_skills_dir(dest)
            if skills_path:
                installed = get_installed()
                new = [d.name for d in skills_path.iterdir()
                       if d.is_dir() and d.name not in installed
                       and (d / "SKILL.md").exists()]
                if new:
                    log(f"  发现 {name}: {', '.join(new[:5])}")
                    for s in new[:5]:
                        copy_skill(skills_path / s, s)
    log("  Topic 发现完成")

# ─── awesome-hermes-agent 列表跟踪 ──────────────────────────────────────────
def track_awesome_list(state: dict):
    """跟踪 awesome-hermes-agent 列表更新"""
    log("--- awesome-hermes-agent 跟踪 ---")
    awesome_repos = [
        ("nouveta-ai", "hermes-atlas"),
        ("nesquena", "hermes-webui"),
        ("garrytan", "gbrain"),
        ("stephenschoettler", "hermes-lcm"),
        ("vectorize-io", "hindsight"),
        ("builderz-labs", "mission-control"),
        ("AMAP-ML", "SkillClaw"),
        ("greyhaven-ai", "autocontext"),
        ("0xNyk", "honeycomb"),
        ("mattpocock", "skills"),
    ]
    found_new = False
    for org, repo in awesome_repos:
        url = f"https://github.com/{org}/{repo}.git"
        dest = SOURCES / f"awesome-{org}-{repo}"
        name = f"awesome/{org}/{repo}"
        if git_clone_or_pull(url, dest, name, depth=1):
            skills_path = find_skills_dir(dest)
            if skills_path:
                installed = get_installed()
                new = [d.name for d in skills_path.iterdir()
                       if d.is_dir() and d.name not in installed
                       and (d / "SKILL.md").exists()]
                for s in new[:3]:
                    copy_skill(skills_path / s, s)
                    log(f"  ✓ {s}")
                    found_new = True
    if not found_new:
        log("  无新增技能")

# ─── Main ───────────────────────────────────────────────────────────────────
def main():
    state = load_state()
    now = time.time()
    is_full_scan = len(sys.argv) > 1 and sys.argv[1] == "--full"

    log(f"=== Agent Skills 扫描开始 {'(全量)' if is_full_scan else '(增量)'} ===")
    installed_before = len(get_installed())

    # 1. Priority repos 扫描（每日）
    log("--- Priority Repos 扫描 ---")
    total_new = 0
    for org, url, subdir in PRIORITY_REPOS:
        total_new += scan_and_install(url, subdir, org, max_new=10, state=state)

    # 2. Hot projects 监控
    monitor_hot_projects(state)

    # 3. awesome-hermes-agent 跟踪（仅全量时）
    if is_full_scan:
        track_awesome_list(state)
        discover_by_topic(state)

        # 4. 全量 VoltAgent repos（仅全量时，每批限速）
        log("--- VoltAgent 全量仓库扫描 ---")
        # 分批处理，每批5个，避免git并发过多
        batch_size = 5
        for i in range(0, len(ALL_VOLT_REPOS), batch_size):
            batch = ALL_VOLT_REPOS[i:i+batch_size]
            for org, url, subdir in batch:
                scan_and_install(url, subdir, org, max_new=3, state=state)
            if i + batch_size < len(ALL_VOLT_REPOS):
                log(f"  ... 已处理 {i+batch_size}/{len(ALL_VOLT_REPOS)}")
                time.sleep(2)  # 避免触发 rate limit

    installed_after = len(get_installed())
    new_count = installed_after - installed_before
    log(f"=== 扫描完成: {installed_before} → {installed_after} (+{new_count}) ===")

    # 更新状态
    state["last_scan"] = now
    if is_full_scan:
        state["last_full_scan"] = now
    else:
        state["last_incremental_scan"] = now
    save_state(state)

if __name__ == "__main__":
    main()
