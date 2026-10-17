#!/bin/bash
# Codex CLI 状态同步到公司 GitHub 仓库
# 用途：cron 每日执行，记录版本、插件状态
# 位置：~/6-产品研发/22-出图智能体训练/sync_codex_repo.sh

set -e

REPO_DIR="$HOME/codex-workspace"
DATE=$(date +"%Y-%m-%d")

# 1. 创建工作目录
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

# 2. 克隆或拉取仓库（如果仓库不存在则初始化本地仓库用于记录）
if [ ! -d "yuxin-skills/.git" ]; then
    # 尝试克隆，失败则初始化本地 git 仓库
    git clone git@github.com:yuxin-tech/yuxin-skills.git yuxin-skills 2>/dev/null || {
        echo "Remote clone failed, creating local git repo..."
        mkdir -p yuxin-skills
        cd yuxin-skills
        git init
        echo "# yuxin-skills" > README.md
        git add README.md
        git commit -m "init: local codex status repo" 2>/dev/null || true
    }
fi

cd "$REPO_DIR/yuxin-skills"

# 3. 拉取最新代码（如果有远程仓库）
if git remote -v 2>/dev/null | grep -q "origin"; then
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
fi

# 4. 创建 codex 状态目录
mkdir -p codex/

# 5. 获取 Codex 版本信息
CODEX_VERSION=$(codex --version 2>/dev/null || echo "unknown")
NPM_VERSION=$(npm view @openai/codex version 2>/dev/null || echo "unknown")

# 6. 获取插件列表
PLUGIN_LIST=$(codex plugin list 2>/dev/null || echo "No plugins found (not logged in or no marketplace configured)")

# 7. 生成状态报告
cat > codex/status_${DATE}.md << EOF
# Codex CLI 状态报告 - ${DATE}

## 版本信息
- 当前版本: ${CODEX_VERSION}
- npm 最新版本: ${NPM_VERSION}

## 插件状态
\`\`\`
${PLUGIN_LIST}
\`\`\`

## 期望插件（核心10个）
- build-web-apps
- coderabbit
- figma
- github
- linear
- sentry
- superpowers
- browser
- chrome
- computer-use

## 备注
- AGENTS.md 记录应有 16 个插件（含文档类 6 个：documents, pdf, spreadsheets, presentations, template-creator, visualize）
EOF

# 8. 提交并推送（如果有远程仓库）
git add codex/
git commit -m "chore(codex): update status ${DATE}" 2>/dev/null || echo "no changes to commit"

if git remote -v 2>/dev/null | grep -q "origin"; then
    git push origin main 2>/dev/null || git push origin master 2>/dev/null || echo "push failed, saved locally"
else
    echo "no remote configured, saved locally"
fi

echo "✅ Codex status saved to codex/status_${DATE}.md"
