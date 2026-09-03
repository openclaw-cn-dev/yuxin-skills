# ============================================================
# 启动 Codex CLI TUI — 双击入口
# 委托给本脚本(因为 .ps1 在 Windows 默认双击进记事本)
# 自动:读 User env 里的 MINIMAX_API_KEY / 切到 Desktop / 启 TUI
# ============================================================

# 1) 读 User 级 env 里的 key
$sk = [System.Environment]::GetEnvironmentVariable('MINIMAX_API_KEY', 'User')
if ([string]::IsNullOrEmpty($sk) -or $sk -eq '__PUT_YOUR_MINIMAX_SK_HERE__') {
    Write-Host ''
    Write-Host '!! MINIMAX_API_KEY 没设或还是占位符' -ForegroundColor Red
    Write-Host '   请先在 PowerShell 跑:' -ForegroundColor Yellow
    Write-Host '   [System.Environment]::SetEnvironmentVariable(''MINIMAX_API_KEY'',''你的sk'',''User'')' -ForegroundColor Yellow
    Write-Host '   然后重新双击此脚本'
    Read-Host '按回车退出'
    exit 1
}

# 2) 注入本进程 env(因为 cmd / bat / TUI 启动是同进程子,继承不到 User 级)
$env:MINIMAX_API_KEY = $sk
Write-Host ("Key 前 8: {0}... 后 4: {1} | 长度: {2}" -f $sk.Substring(0,8), $sk.Substring($sk.Length-4), $sk.Length) -ForegroundColor Green

# 3) 切到 Desktop(codex 默认 workdir 影响文件读写权限)
Set-Location "C:\Users\Administrator\Desktop"
Write-Host '=== Codex CLI 启动中 (模型=MiniMax-Text-01, 中转=minimaxi.com) ===' -ForegroundColor Cyan

# 4) 启 TUI
codex
