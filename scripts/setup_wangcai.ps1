<#
.SYNOPSIS
    旺财 Hermes Agent Windows 一键部署脚本
.DESCRIPTION
    在 Windows 上安装、配置和启动旺财 Hermes Agent + Codex CLI
.NOTES
    版本: 1.0.0
    作者: 渔芯科技
#>

$ErrorActionPreference = "Stop"
$WangcaiRoot = "$env:USERPROFILE\.hermes\profiles\wangcai"
$SkillsRoot = "$env:USERPROFILE\.hermes\skills"
$WorkspaceRoot = "$env:USERPROFILE\wangcai-workspace"

Write-Host "=== 旺财 Hermes Agent Windows 部署脚本 ===" -ForegroundColor Cyan
Write-Host ""

# ===== Step 1: 检查依赖 =====
Write-Host "[1/6] 检查依赖..." -ForegroundColor Yellow

# Python
try {
    $pyVer = python --version 2>&1
    Write-Host "  ✅ Python: $pyVer"
} catch {
    Write-Host "  ❌ Python 未安装！请先安装 Python 3.11+"
    Write-Host "     下载: https://www.python.org/downloads/"
    exit 1
}

# pip
try {
    $pipVer = pip --version 2>&1
    Write-Host "  ✅ pip: $($pipVer.Split()[1])"
} catch {
    python -m ensurepip
}

# Git
try {
    $gitVer = git --version 2>&1
    Write-Host "  ✅ Git: $($gitVer.Split()[2])"
} catch {
    Write-Host "  ❌ Git 未安装！请先安装 Git for Windows"
    Write-Host "     下载: https://git-scm.com/download/win"
    exit 1
}

# ===== Step 2: 安装 Hermes Agent =====
Write-Host "[2/6] 安装 Hermes Agent..." -ForegroundColor Yellow

# 检查是否已安装
try {
    $hermesVer = hermes --version 2>&1
    Write-Host "  ✅ Hermes Agent 已安装: $hermesVer"
} catch {
    Write-Host "  ⏳ 安装 Hermes Agent..."
    pip install hermes-agent
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ pip 安装失败！尝试 scoop..."
        # 检查 scoop
        try {
            scoop install hermes-agent
        } catch {
            Write-Host "  ❌ scoop 也失败。请手动安装: pip install hermes-agent"
            exit 1
        }
    }
}

# ===== Step 3: 拉取技能仓库 =====
Write-Host "[3/6] 拉取技能仓库..." -ForegroundColor Yellow

if (Test-Path "$env:USERPROFILE\.hermes\skills-repo") {
    Write-Host "  ⏳ 更新现有仓库..."
    Push-Location "$env:USERPROFILE\.hermes\skills-repo"
    git pull
    Pop-Location
} else {
    Write-Host "  ⏳ 克隆 yuxin-skills 仓库..."
    git clone git@github.com:openclaw-cn-dev/yuxin-skills.git "$env:USERPROFILE\.hermes\skills-repo"
}

# ===== Step 4: 创建旺财 Profile =====
Write-Host "[4/6] 创建旺财 Profile..." -ForegroundColor Yellow

# 创建 profile 目录
New-Item -ItemType Directory -Force -Path $WangcaiRoot | Out-Null
New-Item -ItemType Directory -Force -Path "$WangcaiRoot\memories" | Out-Null
New-Item -ItemType Directory -Force -Path "$WangcaiRoot\config" | Out-Null

# 复制配置
Copy-Item "$env:USERPROFILE\.hermes\skills-repo\profiles\wangcai\*" $WangcaiRoot -Recurse -Force
Write-Host "  ✅ Profile 配置已复制"

# 软链技能目录 (Windows 用 junction)
if (-not (Test-Path $SkillsRoot)) {
    New-Item -ItemType Junction -Path $SkillsRoot -Target "$env:USERPROFILE\.hermes\skills-repo\skills" | Out-Null
    Write-Host "  ✅ 技能目录已链接"
} else {
    Write-Host "  ℹ️ 技能目录已存在"
}

# 替换 Secret 占位符（部署时手动填写）
Write-Host "  ⚠️ 请在 config.yaml 中替换飞书 Secret！"
Write-Host "     位置: $WangcaiRoot\config.yaml"
Write-Host "     字段: app_secret: '__REPLACE_WITH_REAL_SECRET_ON_WINDOWS__'"

# ===== Step 5: 安装 Codex CLI =====
Write-Host "[5/6] 安装 Codex CLI..." -ForegroundColor Yellow

try {
    $codexVer = codex --version 2>&1
    Write-Host "  ✅ Codex CLI 已安装: $codexVer"
} catch {
    Write-Host "  ⏳ 安装 Codex CLI..."
    try {
        npm install -g @openai/codex
    } catch {
        Write-Host "  ⏳ npm 不可用，尝试 scoop..."
        try {
            scoop install codex
        } catch {
            Write-Host "  ⚠️ Codex CLI 安装跳过。可稍后手动安装: npm install -g @openai/codex"
        }
    }
}

# 配置 Codex AGENTS.md
$CodexConfigDir = "$env:USERPROFILE\.codex"
New-Item -ItemType Directory -Force -Path $CodexConfigDir | Out-Null
Copy-Item "$env:USERPROFILE\.hermes\skills-repo\windows\AGENTS.md" "$CodexConfigDir\AGENTS.md" -Force -ErrorAction SilentlyContinue
Write-Host "  ✅ Codex AGENTS.md 已配置"

# ===== Step 6: 创建 Workspace 并启动 Gateway =====
Write-Host "[6/6] 创建 Workspace 并启动 Gateway..." -ForegroundColor Yellow

# 创建工作目录
New-Item -ItemType Directory -Force -Path $WorkspaceRoot\cad_outputs | Out-Null
New-Item -ItemType Directory -Force -Path $WorkspaceRoot\social_media | Out-Null
New-Item -ItemType Directory -Force -Path $WorkspaceRoot\evolution | Out-Null
Write-Host "  ✅ Workspace 已创建: $WorkspaceRoot"

# 测试飞书连接
Write-Host "  ⏳ 测试飞书连接..."
hermes gateway test --profile wangcai 2>&1

# 启动 Gateway
Write-Host "  ⏳ 启动 Gateway..."
Start-Process -WindowStyle Hidden -FilePath "hermes" -ArgumentList "gateway run --profile wangcai"
Write-Host "  ✅ Gateway 已启动（后台运行）"

Write-Host ""
Write-Host "=== 部署完成！ ===" -ForegroundColor Green
Write-Host ""
Write-Host "旺财已就绪："
Write-Host "  📁 Profile: $WangcaiRoot"
Write-Host "  📁 Skills:  $SkillsRoot"
Write-Host "  📁 Workspace: $WorkspaceRoot"
Write-Host ""
Write-Host "下一步："
Write-Host "  1. 飞书私聊旺财，发送 /start 激活"
Write-Host "  2. 测试 CAD 出图：'画一个 600x400x300 的箱体'"
Write-Host "  3. 测试自媒体：'发一篇抖音水产养殖科普'"
Write-Host ""
Write-Host "常用命令："
Write-Host "  hermes gateway status --profile wangcai    # 查看 Gateway 状态"
Write-Host "  hermes gateway stop --profile wangcai       # 停止 Gateway"
Write-Host "  hermes gateway run --profile wangcai         # 启动 Gateway"
