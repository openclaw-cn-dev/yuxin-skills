<# force-free-port.ps1 — Kill whatever is listening on a given TCP port on Windows
# Usage: powershell -ExecutionPolicy Bypass -File force-free-port.ps1 -Port 8021
# Why: netstat -ano sometimes misses listeners; Get-NetTCPConnection -State Listen is authoritative.

param(
    [Parameter(Mandatory=$true)]
    [int]$Port
)

Write-Host "=== Searching for listeners on port $Port ==="
$conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if (-not $conns) {
    Write-Host "✅ Port $Port has no LISTEN entries. Already free."
    exit 0
}

foreach ($c in $conns) {
    $pid = $c.OwningProcess
    Write-Host "  Killing PID $pid on port $Port..."
    try {
        Stop-Process -Id $pid -Force -ErrorAction Stop
    } catch {
        Write-Host "    ❌ Failed to kill PID ${pid}: $_" -ForegroundColor Red
    }
}

Start-Sleep -Seconds 2

$remain = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($remain) {
    Write-Host "❌ Port $Port still has listeners:" -ForegroundColor Red
    $remain | Format-Table -AutoSize
    exit 1
} else {
    Write-Host "✅ Port $Port is now free." -ForegroundColor Green
    exit 0
}
