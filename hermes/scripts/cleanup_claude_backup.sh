#!/bin/bash
# 3天后自动删除 Claude Code 迁移备份（华哥授权 2026-08-13）
# 安全设计：删除前二次验证迁移后的软链接/实体均正常，任一异常则跳过删除并告警

BACKUP="/Users/hua/.claude.bak.1786525931"
CLAUDE_LINK="/Users/hua/.claude"
CLAUDE_JSON_LINK="/Users/hua/.claude.json"
CLAUDE_REAL="/Users/hua/系统文件夹/Claude"
CLAUDE_JSON_REAL="/Users/hua/系统文件夹/Claude/.claude.json"

FAIL=0

# 1. 验证 ~/.claude 软链接 + 实体目录
if [ -L "$CLAUDE_LINK" ] && [ -d "$CLAUDE_REAL" ]; then
    echo "✅ ~/.claude 软链接正常"
else
    echo "❌ ~/.claude 软链接异常，跳过删除"
    FAIL=1
fi

# 2. 验证 ~/.claude.json 软链接 + 实体文件
if [ -L "$CLAUDE_JSON_LINK" ] && [ -f "$CLAUDE_JSON_REAL" ]; then
    echo "✅ ~/.claude.json 软链接正常"
else
    echo "❌ ~/.claude.json 软链接异常，跳过删除"
    FAIL=1
fi

# 3. 验证备份目录确实存在
if [ ! -d "$BACKUP" ]; then
    echo "ℹ️ 备份目录已不存在（可能已手动删除），无需处理"
    exit 0
fi

# 4. 验证通过才删除
if [ "$FAIL" -eq 0 ]; then
    SIZE=$(du -sh "$BACKUP" 2>/dev/null | awk '{print $1}')
    rm -rf "$BACKUP"
    if [ ! -e "$BACKUP" ]; then
        echo "✅ 迁移已稳定，备份已安全删除，释放 $SIZE：$BACKUP"
    else
        echo "⚠️ 备份删除失败，请手动检查：$BACKUP"
        exit 1
    fi
else
    echo "⚠️ 迁移验证未通过，已保留备份，请华哥检查后手动处理"
    exit 1
fi
