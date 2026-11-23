# Cai dat, nang cap, go PKTTC TextHub (bundle tu nap khi AutoCAD khoi dong). PowerShell 5.1.
#   powershell -File cai_dat.ps1                   cai hoac nang cap
#   powershell -File cai_dat.ps1 -WhatIf           chi xem se lam gi, khong thay doi gi
#   powershell -File cai_dat.ps1 -Uninstall        go cai dat
#   powershell -File cai_dat.ps1 -FontStore "D:\Kho-Font"   cai dat va (neu chua co) tao cau hinh kho font
# Chi chep tep vao thu muc ApplicationPlugins cua nguoi dung. KHONG ghi registry, KHONG doi thiet lap AutoCAD.
param(
    [string]$Target = (Join-Path $env:APPDATA 'Autodesk\ApplicationPlugins'),
    [switch]$Uninstall,
    [switch]$WhatIf,
    [string]$FontStore = ''
)
$ErrorActionPreference = 'Stop'
$bundleName = 'PKTTC.TextHub.bundle'
$src  = Join-Path $PSScriptRoot $bundleName
$dst  = Join-Path $Target $bundleName
$old  = Join-Path $Target 'PKTTC.TextHub.old'
$dll  = 'Contents\Windows\Pkttc.TextHub.dll'

function Say($m) { Write-Host $m }
function Is-Locked($path) {
    if (-not (Test-Path -LiteralPath $path)) { return $false }
    try { $f = [IO.File]::Open($path, 'Open', 'ReadWrite', 'None'); $f.Close(); return $false } catch { return $true }
}
function Bundle-Version($dir) {
    $x = Join-Path $dir 'PackageContents.xml'
    if (-not (Test-Path -LiteralPath $x)) { return $null }
    try { return ([xml](Get-Content -LiteralPath $x -Raw -Encoding UTF8)).ApplicationPackage.AppVersion } catch { return $null }
}

# ------------------------------------------------------------------ go
if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $dst)) { Say 'Chua cai dat: khong co gi de go.'; exit 0 }
    if (Is-Locked (Join-Path $dst $dll)) { Say 'LOI: AutoCAD dang dung TextHub. Dong AutoCAD roi chay lai.'; exit 2 }
    if ($WhatIf) { Say "[XEM] se xoa $dst"; exit 0 }
    Remove-Item -LiteralPath $dst -Recurse -Force
    if (Test-Path -LiteralPath $old) { Remove-Item -LiteralPath $old -Recurse -Force }
    # Tep cau hinh mau cho tro ly do chinh trinh cai tao (chi khi cai vao thu muc mac dinh): go cung de khong tro vao duong dan da xoa
    $kc = Join-Path $env:LOCALAPPDATA 'PKTTC\kuro_mcp_config.json'
    if (($Target -eq (Join-Path $env:APPDATA 'Autodesk\ApplicationPlugins')) -and (Test-Path -LiteralPath $kc)) { Remove-Item -LiteralPath $kc -Force }
    Say "Da go: $dst"
    Say 'Giu lai: kho font (%LOCALAPPDATA%\PKTTC\fontstore.txt), nhat ky cong (%LOCALAPPDATA%\PKTTC\bridge\audit.log), ban sao luu ban ve (_backup).'
    exit 0
}

# ------------------------------------------------------------------ cai
if (-not (Test-Path -LiteralPath $src)) { Say "LOI: khong thay thu muc $bundleName canh tep cai_dat.ps1."; exit 1 }
$newVer = Bundle-Version $src
if (-not $newVer) { Say 'LOI: PackageContents.xml trong goi bi hong.'; exit 1 }

# Kiem tra toan ven theo MANIFEST truoc khi chep
$man = Join-Path $src 'MANIFEST.txt'
if (Test-Path -LiteralPath $man) {
    $bad = @()
    foreach ($line in (Get-Content -LiteralPath $man -Encoding UTF8)) {
        if ($line -match '^([0-9A-F]{64})\s+(.+)$') {
            $f = Join-Path $src $Matches[2]
            if (-not (Test-Path -LiteralPath $f) -or (Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash -ne $Matches[1]) { $bad += $Matches[2] }
        }
    }
    if ($bad.Count) { Say ('LOI: goi bi hong, tep khong khop MANIFEST: ' + ($bad -join ', ')); exit 1 }
}

$curVer = Bundle-Version $dst
Say ("Cai dat PKTTC TextHub $newVer vao $Target" + $(if ($curVer) { " (dang co ban $curVer)" } else { '' }))
if ($curVer -and (Is-Locked (Join-Path $dst $dll))) { Say 'LOI: AutoCAD dang dung TextHub. Dong AutoCAD roi chay lai.'; exit 2 }
if ($WhatIf) {
    Say "[XEM] se chep $src -> $dst"
    if ($curVer) { Say "[XEM] ban cu giu o $old" }
    if ($FontStore) { Say "[XEM] se tao cau hinh kho font neu chua co: $FontStore" }
    exit 0
}

New-Item -ItemType Directory -Force $Target | Out-Null
$moved = $false
try {
    if (Test-Path -LiteralPath $old) { Remove-Item -LiteralPath $old -Recurse -Force }
    if (Test-Path -LiteralPath $dst) { Move-Item -LiteralPath $dst -Destination $old; $moved = $true }
    Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
    if ((Get-FileHash -LiteralPath (Join-Path $dst $dll)).Hash -ne (Get-FileHash -LiteralPath (Join-Path $src $dll)).Hash) { throw 'Tep DLL sau khi chep khong khop.' }
}
catch {
    Say ('LOI khi cai: ' + $_.Exception.Message)
    if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Recurse -Force -ErrorAction SilentlyContinue }
    if ($moved -and (Test-Path -LiteralPath $old)) { Move-Item -LiteralPath $old -Destination $dst; Say 'Da khoi phuc ban cu.' }
    exit 1
}
Say "Da cai: $dst"

# Cau hinh kho font: chi tao khi chua co, khong ghi de
if ($FontStore) {
    $cfgDir = Join-Path $env:LOCALAPPDATA 'PKTTC'
    $cfg = Join-Path $cfgDir 'fontstore.txt'
    if (-not (Test-Path -LiteralPath $FontStore)) { Say "Canh bao: thu muc kho font khong ton tai: $FontStore (bo qua)" }
    elseif (Test-Path -LiteralPath $cfg) { Say "Giu cau hinh kho font san co: $cfg" }
    else {
        New-Item -ItemType Directory -Force $cfgDir | Out-Null
        [IO.File]::WriteAllLines($cfg, @('# Kho font cua phong (PKTTC TextHub). Moi dong mot thu muc.', $FontStore), (New-Object Text.UTF8Encoding($false)))
        Say "Da tao cau hinh kho font: $cfg"
    }
}

# Cau hinh mau cho tro ly (Kuro) voi duong dan that. Chi tao khi cai vao thu muc mac dinh cua AutoCAD (de cai thu khong ghi de).
$mcp = Join-Path $dst 'Contents\Bridge\pkttc_mcp.py'
$kcfg = Join-Path (Join-Path $env:LOCALAPPDATA 'PKTTC') 'kuro_mcp_config.json'
if ($Target -eq (Join-Path $env:APPDATA 'Autodesk\ApplicationPlugins')) {
    New-Item -ItemType Directory -Force (Split-Path $kcfg) | Out-Null
    $cfgObj = [ordered]@{ mcpServers = [ordered]@{ 'pkttc-text' = [ordered]@{ command = 'python'; args = @('-X', 'utf8', $mcp); env = [ordered]@{ PKTTC_CLIENT_NAME = 'Kuro' } } } }
    [IO.File]::WriteAllText($kcfg, ($cfgObj | ConvertTo-Json -Depth 6), (New-Object Text.UTF8Encoding($false)))
}

Say ''
Say 'Xong. Khoi dong lai AutoCAD: TextHub tu nap, go PKTEXTABOUT de kiem tra.'
if ($Target -eq (Join-Path $env:APPDATA 'Autodesk\ApplicationPlugins')) { Say "Cau hinh mau cho tro ly (Kuro): $kcfg" }
exit 0
