# S5: kiem thu che do KHONG CHAN tren MOT PHIEN AUTOCAD GIAO DIEN RIENG (acad.exe thu hai, ban sao mau). PowerShell 5.1.
# Khong dung vao phien AutoCAD dang lam viec cua nguoi dung; phien thu bi dong o cuoi.
$ErrorActionPreference = 'Stop'
$w   = $PSScriptRoot
$t   = Join-Path $w 'test'
$bin = (Get-Content "$w\bin\latest.txt" -Raw).Trim()
function Lisp($path) { return $path -replace '\\', '/' }

if (-not (Test-Path "$t\fixture_20.dwg")) { throw 'Chay run_tests_bridge.ps1 truoc de tao fixture_20.dwg' }
Copy-Item "$t\fixture_20.dwg" "$t\idle_work.dwg" -Force
$h0 = (Get-FileHash "$t\idle_work.dwg").Hash
$scanJson = "$t\idle_scan_by_script.json"
Remove-Item $scanJson -ErrorAction SilentlyContinue
Remove-Item "$t\_backup" -Recurse -Force -ErrorAction SilentlyContinue

$scr = "$t\idle.scr"
$lines = @(
    ('(command "_.NETLOAD" "' + (Lisp "$bin\Pkttc.TextHub.dll") + '")'),
    'PKTEXTBRIDGE', 'YES',
    'PKTEXTSCAN', (Lisp $scanJson))
[IO.File]::WriteAllLines($scr, $lines, (New-Object Text.UTF8Encoding($false)))

$before = @(Get-Process acad -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
'AutoCAD dang chay truoc khi thu (khong dong): ' + ($before -join ', ')
$p = Start-Process 'C:\Program Files\Autodesk\AutoCAD 2020\acad.exe' -ArgumentList @("`"$t\idle_work.dwg`"", '/nologo', '/b', "`"$scr`"") -PassThru -WindowStyle Minimized
"Phien thu: PID $($p.Id)"
if ($before -contains $p.Id) { throw 'PID trung phien dang co' }

$rc = 1
try {
    $ErrorActionPreference = 'Continue'
    python -X utf8 -I "$w\tests\bridge_idle_test.py" $w $p.Id $scanJson 2>&1 | ForEach-Object { "$_" }
    $rc = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
}
finally {
    if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force }   # chi dong phien thu cua minh
    $p.WaitForExit(30000) | Out-Null
    $after = @(Get-Process acad -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
    'AutoCAD con lai sau khi thu: ' + ($after -join ', ')
}
if ($h0 -ne (Get-FileHash "$t\idle_work.dwg").Hash) { 'LOI: idle_work.dwg tren dia bi thay doi (khong duoc luu)!'; $rc = 1 } else { 'Tep tren dia khong doi (SHA-256).' }
Get-ChildItem $t -Filter 'idle_work*' | ForEach-Object { '  ' + $_.Name + ' ' + $_.Length + ' ' + $_.LastWriteTime }
exit $rc
