$targets = @(
    @{Path='C:\Program Files'; Label='Program Files'},
    @{Path='C:\Program Files (x86)'; Label='Program Files (x86)'},
    @{Path="$env:USERPROFILE\AppData\Local"; Label='AppData\Local'},
    @{Path="$env:USERPROFILE\AppData\Roaming"; Label='AppData\Roaming'}
)

foreach ($t in $targets) {
    Write-Host "`n=== $($t.Label) ===" -ForegroundColor Yellow
    $subdirs = Get-ChildItem -Path $t.Path -Directory -ErrorAction SilentlyContinue
    $results = @()
    foreach ($d in $subdirs) {
        $size = (Get-ChildItem -Path $d.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        if ($size -gt 10MB) {
            $results += [PSCustomObject]@{
                Name = $d.Name
                SizeGB = [math]::Round($size / 1GB, 2)
                SizeMB = [math]::Round($size / 1MB, 0)
            }
        }
    }
    $results | Sort-Object SizeGB -Descending | Select-Object -First 15 | Format-Table Name, SizeGB, SizeMB -AutoSize
}

# C:\ root dirs (>100MB)
Write-Host "`n=== C:\ root (>100MB) ===" -ForegroundColor Yellow
Get-ChildItem -Path 'C:\' -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $sum = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($sum -gt 100MB) {
        Write-Host "  $([math]::Round($sum/1GB,1)) GB  $($_.Name)"
    }
}
