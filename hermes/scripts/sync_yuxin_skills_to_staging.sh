#!/bin/bash
# yuxin-skills → RKR 中转站 同步脚本
# 完整 mirror GitHub 仓库到 ~/rkr_staging/文档中转站/yuxin-skills-YYYYMMDD/
#
# 用途：
#   - 把 openclaw-cn-dev/yuxin-skills 仓库所有 skills 镜像到 RKR 中转站
#   - 由 RKR Scanner 自动处理（向量化 + 知识图谱入库）
#
# ⚠️ 注意：RKR 中转站会被 Scanner 定期清理（每分钟扫描）。
#    如需永久保存，建议改用 RKR upload API 上传到独立 project。

set -euo pipefail

# 配置
GITHUB_REPO="openclaw-cn-dev/yuxin-skills"
GITHUB_URL="git@github.com:${GITHUB_REPO}.git"
STAGING_BASE="/Users/hua/rkr_staging/文档中转站"
CACHE_DIR="/tmp/yuxin-skills-sync-cache"
TIMESTAMP=$(date "+%Y%m%d")
BATCH_DIR="${STAGING_BASE}/yuxin-skills-${TIMESTAMP}"
LOG_FILE="/Users/hua/.hermes/logs/sync_yuxin_skills.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg" | tee -a "$LOG_FILE"
}

log "═══════════════════════════════════════════════════════════"
log "yuxin-skills → RKR 中转站 同步开始"

# ── Step 1: Clone 或 pull 缓存 ──
if [ -d "$CACHE_DIR/.git" ]; then
    log "1. 拉取最新: $CACHE_DIR"
    git -C "$CACHE_DIR" pull origin main 2>&1 | tail -3 | tee -a "$LOG_FILE"
else
    log "1. 克隆仓库到缓存: $CACHE_DIR"
    rm -rf "$CACHE_DIR"
    git clone --depth 50 "$GITHUB_URL" "$CACHE_DIR" 2>&1 | tail -3 | tee -a "$LOG_FILE"
fi

GH_COMMIT=$(git -C "$CACHE_DIR" log -1 --format='%h %ai %s')
log "   最新 commit: $GH_COMMIT"

# ── Step 2: 创建批次目录 ──
log "2. 创建批次目录: $BATCH_DIR"
mkdir -p "$BATCH_DIR"

# ── Step 3: rsync 镜像 ──
log "3. rsync 镜像 (剔除 .git)"
rsync -a --exclude='.git' "$CACHE_DIR/" "$BATCH_DIR/" 2>&1 | tail -5 | tee -a "$LOG_FILE"

# ── Step 4: 验证完整性 ──
log "4. 验证完整性"
TOTAL=$(find "$BATCH_DIR" -type f | wc -l | tr -d ' ')
CLAUDE=$(find "$BATCH_DIR/claude-code/skills" -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')
HERMES=$(find "$BATCH_DIR/hermes/skills" -name 'SKILL.md' 2>/dev/null | wc -l | tr -d ' ')
CODEX=$(find "$BATCH_DIR/codex/skills" -type f 2>/dev/null | wc -l | tr -d ' ')
DRAWING=$(find "$BATCH_DIR/drawing-skills" -type f 2>/dev/null | wc -l | tr -d ' ')
SIZE=$(du -sh "$BATCH_DIR" | awk '{print $1}')

log "   总文件: $TOTAL, 大小: $SIZE"
log "   claude-code: $CLAUDE SKILL.md"
log "   hermes: $HERMES SKILL.md"
log "   codex: $CODEX 文件"
log "   drawing-skills: $DRAWING 文件"

# ── Step 5: 健康检查（如果某些文件被 scanner 清了，重新补上）──
EXPECTED_MIN_TOTAL=600  # 期望最少文件数
if [ "$TOTAL" -lt "$EXPECTED_MIN_TOTAL" ]; then
    log "   ⚠️  文件数 ($TOTAL) 少于预期 ($EXPECTED_MIN_TOTAL)，重新 rsync"
    rsync -a --exclude='.git' "$CACHE_DIR/" "$BATCH_DIR/" 2>&1 | tail -3 | tee -a "$LOG_FILE"
    TOTAL=$(find "$BATCH_DIR" -type f | wc -l | tr -d ' ')
    log "   重新补充后: $TOTAL 文件"
fi

log "✅ 同步完成: $BATCH_DIR ($TOTAL 文件, $SIZE)"
log "═══════════════════════════════════════════════════════════"