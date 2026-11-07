#!/bin/bash
# scan-agent-skills.sh - 定期扫描 wondelai/skills 和 VoltAgent/awesome-agent-skills
# 发现新技能后记录到 ~/.hermes/logs/skill-scan.log

set -e

LOG="$HOME/.hermes/logs/skill-scan.log"
mkdir -p "$(dirname "$LOG")"
SOURCES="$HOME/.cache/hermes-skill-sources"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M')] $*" >> "$LOG"
}

log "=== 开始扫描 ==="

# 1. wondelai/skills - 直接 git pull
if [ -d "$SOURCES/wondelai-skills" ]; then
    cd "$SOURCES/wondelai-skills"
    git pull --ff origin main -q 2>/dev/null && log "wondelai/skills updated" || log "wondelai/skills pull failed"
else
    git clone --depth 1 https://github.com/wondelai/skills.git "$SOURCES/wondelai-skills" 2>/dev/null
    log "wondelai/skills cloned fresh"
fi

# 列出 wondelai 新技能
SKILLS_DIR="$HOME/.hermes/skills/productivity"
cd "$SOURCES/wondelai-skills/.claude/skills"
for skill_dir in */; do
    skill_name="${skill_dir%/}"
    if [ ! -d "$SKILLS_DIR/$skill_name" ]; then
        log "NEW wondelai: $skill_name"
    fi
done

# 2. VoltAgent/awesome-agent-skills - 通过 officialskills.sh API 扫描新增
# 获取最新技能列表
SKILLS_JSON=$(curl -s "https://officialskills.sh/api/skills?limit=1000" 2>/dev/null || echo "{}")
echo "$SKILLS_JSON" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    skills = data.get('skills', data.get('data', []))
    for s in skills:
        name = s.get('name', s.get('id', 'unknown'))
        print(f\"VOLT: {name}\")
except:
    pass
" 2>/dev/null | while read line; do
    log "VOLT $line"
done

# 3. 检查 anthropics/skills 更新
if [ -d "$SOURCES/anthropics-skills" ]; then
    cd "$SOURCES/anthropics-skills"
    git pull --ff origin main -q 2>/dev/null && log "anthropics/skills updated" || log "anthropics/skills pull failed"
else
    git clone --depth 1 https://github.com/anthropics/skills.git "$SOURCES/anthropics-skills" 2>/dev/null
    log "anthropics/skills cloned fresh"
fi

log "=== 扫描完成 ==="
