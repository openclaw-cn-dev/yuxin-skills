# Chrome 用户数据迁移到 D 盘（robocopy + junction）
# 用法：修改 $userName，然后 powershell -ExecutionPolicy Bypass -File this.ps1

$userName = 'Administrator'
$source = "C:\Users\$userName\AppData\Local\Google"
$dest = 'D:\AppData\Google'

Write-Host "Source: $source"
Write-Host "Dest: $dest"

# 关 Chrome
taskkill /f /im chrome.exe 2>$null
Start-Sleep -Seconds 2

# 建目标目录
New-Item -ItemType Directory -Force -Path $dest -ErrorAction SilentlyContinue | Out-Null

# 复制（/NP /NFL /NDL = 静默，11 GB 约 13 分钟）
Write-Host "Copying..."
robocopy $source $dest /E /COPYALL /R:2 /W:3 /MT:4 /NP /NFL /NDL
$rc = $LASTEXITCODE
# robocopy exit 0-7 都算正常（1=复制成功无额外文件）
Write-Host "robocopy exit: $rc (0-7 = OK)"

# 验证
$srcSize = (Get-ChildItem -Path $source -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$dstSize = (Get-ChildItem -Path $dest -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
Write-Host "Source: $([math]::Round($srcSize/1GB,2)) GB"
Write-Host "Dest: $([math]::Round($dstSize/1GB,2)) GB"

if ($dstSize -gt 1GB -and $dstSize -ge ($srcSize * 0.9)) {
    Write-Host "OK - removing source..."
    Remove-Item -Path $source -Recurse -Force -ErrorAction Stop
    cmd /c "mklink /J `"$source`" `"$dest`""
    Write-Host "OK - junction created: $source -> $dest"
} else {
    Write-Host "FAIL - copy incomplete, source kept"
}
