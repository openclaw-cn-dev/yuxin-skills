#!/bin/bash
# Re-implementation of sync_hermes_repo.sh export logic, worktree-based
set -u
HERMES_HOME="/Users/hua/.hermes"
export HOME="/Users/hua"
HERMES_DIR="/tmp/yuxin-sync-main/hermes"

redact_secrets() {
    sed -E \
        -e 's/(sk-[a-zA-Z0-9]{20,})/sk-***/g' \
        -e 's/(ark-[a-zA-Z0-9_-]{20,})/ark-***/g' \
        -e 's/([a-zA-Z0-9_-]{30,})/***SECRET***/g'
}

SKILLS_COUNT=$(ls "$HERMES_HOME/skills/" | grep -v '^\.' | wc -l | tr -d ' ')
PROFILES_COUNT=$(ls "$HERMES_HOME/profiles/" | wc -l | tr -d ' ')
SCRIPTS_COUNT=$(ls "$HERMES_HOME/scripts/"*.sh "$HERMES_HOME/scripts/"*.py 2>/dev/null | wc -l | tr -d ' ')
PLUGINS_COUNT=$(ls "$HERMES_HOME/plugins/" 2>/dev/null | wc -l | tr -d ' ')
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# STATUS.md
{
    echo "# Hermes Agent 状态快照"
    echo "> 导出时间: $TIMESTAMP"
    echo "> 主机: $(hostname)"
    echo ""
    echo "## 统计"
    echo "- Skills: $SKILLS_COUNT"
    echo "- Profiles: $PROFILES_COUNT"
    echo "- Scripts: $SCRIPTS_COUNT"
    echo "- Plugins: $PLUGINS_COUNT"
    echo ""
    echo "## 版本"
    hermes --version 2>/dev/null || echo "N/A"
    echo ""
    echo "## Profiles"
    ls "$HERMES_HOME/profiles/" | while read p; do echo "- $p"; done
    echo ""
    echo "## Skills 清单"
    ls "$HERMES_HOME/skills/" | grep -v '^\.' | while read s; do echo "- $s"; done
} > "$HERMES_DIR/STATUS.md"

# Skills
rm -rf "$HERMES_DIR/skills"
mkdir -p "$HERMES_DIR/skills"
for skill_dir in "$HERMES_HOME/skills/"*/; do
    name=$(basename "$skill_dir")
    [ "$name" = ".archive" ] && continue
    if [ -f "$skill_dir/SKILL.md" ]; then
        mkdir -p "$HERMES_DIR/skills/$name"
        redact_secrets < "$skill_dir/SKILL.md" > "$HERMES_DIR/skills/$name/SKILL.md"
        if [ -d "$skill_dir/scripts" ]; then
            cp -r "$skill_dir/scripts" "$HERMES_DIR/skills/$name/scripts" 2>/dev/null || true
            find "$HERMES_DIR/skills/$name/scripts" -type f \( -name '*.py' -o -name '*.sh' \) -print0 2>/dev/null \
                | while IFS= read -r -d '' f; do
                    redact_secrets < "$f" > "$f.tmp" && mv "$f.tmp" "$f"
                  done
        fi
    fi
done

# Profiles
rm -rf "$HERMES_DIR/profiles"
mkdir -p "$HERMES_DIR/profiles"
for profile_dir in "$HERMES_HOME/profiles/"*/; do
    pname=$(basename "$profile_dir")
    mkdir -p "$HERMES_DIR/profiles/$pname"
    if [ -d "$profile_dir/skills" ]; then
        ls "$profile_dir/skills/" | grep -v '^\.' > "$HERMES_DIR/profiles/$pname/skills_list.txt" 2>/dev/null || true
    fi
    if [ -d "$profile_dir/plugins" ]; then
        ls "$profile_dir/plugins/" | grep -v '^\.' > "$HERMES_DIR/profiles/$pname/plugins_list.txt" 2>/dev/null || true
    fi
    if [ -d "$profile_dir/cron" ]; then
        ls "$profile_dir/cron/" | grep -v '^\.' > "$HERMES_DIR/profiles/$pname/cron_list.txt" 2>/dev/null || true
    fi
done

# Scripts
rm -rf "$HERMES_DIR/scripts"
mkdir -p "$HERMES_DIR/scripts"
for script in "$HERMES_HOME/scripts/"*.sh "$HERMES_HOME/scripts/"*.py; do
    [ -f "$script" ] || continue
    name=$(basename "$script")
    redact_secrets < "$script" > "$HERMES_DIR/scripts/$name" 2>/dev/null || true
done

# Config strict redact
if [ -f "$HERMES_HOME/config.yaml" ]; then
    sed -E \
        -e 's/(api_key|token|secret|password|bearer|app_id|app_secret|lark_app_secret):\s*.*/\1: "***"/g' \
        -e 's/(api_key_env):\s*".*"/\1: "***"/g' \
        -e 's/[a-zA-Z0-9_-]{20,}//g' \
        "$HERMES_HOME/config.yaml" > "$HERMES_DIR/config.yaml"
fi

# MEMORY structure
if [ -f "$HERMES_HOME/memories/MEMORY.md" ]; then
    echo "# MEMORY.md 结构（内容已脱敏）" > "$HERMES_DIR/MEMORY_STRUCTURE.md"
    echo "" >> "$HERMES_DIR/MEMORY_STRUCTURE.md"
    echo "行数: $(wc -l < "$HERMES_HOME/memories/MEMORY.md" | tr -d ' ')" >> "$HERMES_DIR/MEMORY_STRUCTURE.md"
    echo "大小: $(ls -lh "$HERMES_HOME/memories/MEMORY.md" | awk '{print $5}')" >> "$HERMES_DIR/MEMORY_STRUCTURE.md"
fi

# .gitignore
echo "skills/*/references/" > "$HERMES_DIR/.gitignore"
echo "skills/*/assets/" >> "$HERMES_DIR/.gitignore"
echo "scripts/__pycache__/" >> "$HERMES_DIR/.gitignore"

# baseline JSON
python3 - "$HERMES_DIR/reports/hermes-sync-baseline.json" "$SKILLS_COUNT" "$PROFILES_COUNT" "$SCRIPTS_COUNT" << 'PYEOF'
import json, sys, datetime
path = sys.argv[1]
data = {
    "last_sync": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "skills": int(sys.argv[2]), "profiles": int(sys.argv[3]), "scripts": int(sys.argv[4]),
    "broken_known": "13 placeholder dirs (only DESCRIPTION.md) + 3 empty dirs (apple has README only; frontend/red-teaming/testing empty); leaf dirs w/o SKILL.md listed in weekly report"
}
with open(path, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
PYEOF

echo "EXPORT_DONE skills=$SKILLS_COUNT profiles=$PROFILES_COUNT scripts=$SCRIPTS_COUNT plugins=$PLUGINS_COUNT"
