# Thu bao cao font, doi chu, don style tren BAN SAO cua ban ve that (ban goc khong duoc mo/sua). PowerShell 5.1.
# Dung: powershell -File trial_copy.ps1 -Dwg "D:\...\ban_ve.dwg" [-Stores "thu_muc1;thu_muc2"]
# Ket qua trong %TEMP%\PKTTC\trial4\.
param(
    [Parameter(Mandatory = $true)][string]$Dwg,
    [string]$Stores = ''
)
$ErrorActionPreference = 'Stop'
$w   = $PSScriptRoot
$bin = (Get-Content "$w\bin\latest.txt" -Raw).Trim()
$tr  = Join-Path $env:TEMP 'PKTTC\trial4'
Remove-Item $tr -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $tr | Out-Null
$copy = Join-Path $tr 'copy.dwg'
Copy-Item -LiteralPath $Dwg $copy -Force
function L($p) { return $p -replace '\\', '/' }
if ($Stores) { $env:PKTTC_FONT_STORE = $Stores }

$lines = @(
    ('(command "_.NETLOAD" "' + (L "$bin\Pkttc.TextHub.dll") + '")'),
    'PKTEXTFONT', (L "$tr\fonts_before.json"), (L "$tr\cai_before.ps1"),
    'PKTEXTSCAN', (L "$tr\scan_before.json"),
    'PKTEXTFIX', 'YES',
    'PKTEXTFONT', (L "$tr\fonts_after.json"), (L "$tr\cai_after.ps1"),
    'PKTEXTPURGE', 'YES',
    'PKTEXTSCAN', (L "$tr\scan_after.json"),
    'QUIT', 'Y')
$scr = Join-Path $tr 'trial.scr'
[IO.File]::WriteAllLines($scr, $lines, (New-Object Text.UTF8Encoding($false)))
$p = Start-Process 'C:\Program Files\Autodesk\AutoCAD 2020\accoreconsole.exe' -ArgumentList @('/i', "`"$copy`"", '/s', "`"$scr`"", '/l', 'en-US') `
     -RedirectStandardOutput "$tr\trial.out.txt" -RedirectStandardError "$tr\trial.err.txt" -PassThru -WindowStyle Hidden
$deadline = (Get-Date).AddSeconds(420)
while ((Get-Date) -lt $deadline -and -not $p.HasExited) {
    if ((Test-Path "$tr\scan_after.json") -and ((Get-Item "$tr\scan_after.json").Length -gt 0)) { Start-Sleep -Seconds 3; break }
    Start-Sleep -Seconds 2
}
if (-not $p.HasExited) { $p.Kill() }
Remove-Item Env:\PKTTC_FONT_STORE -ErrorAction SilentlyContinue
Get-Content "$tr\trial.out.txt" -Encoding Unicode | Where-Object { $_ -match '\[PKTTC\]|^  - |^        ' } | ForEach-Object { $_ -replace [regex]::Escape($tr), '<trial>' }
"Thu muc ket qua: $tr"
