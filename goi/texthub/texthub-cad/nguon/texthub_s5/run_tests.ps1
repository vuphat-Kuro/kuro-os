# S4: kiem thu font ngoai tuyen va don Style, headless tren ban sao mau. PowerShell 5.1.
# Kho font thu: 05-ThuVien\04-Fonts-SHX (bien moi truong PKTTC_FONT_STORE chi cho tien trinh con).
$ErrorActionPreference = 'Stop'
$w   = $PSScriptRoot
$ac  = 'C:\Program Files\Autodesk\AutoCAD 2020'
$t   = Join-Path $w 'test'
$bin = (Get-Content "$w\bin\latest.txt" -Raw).Trim()
$store = (Resolve-Path (Join-Path $w '..\..\05-ThuVien\04-Fonts-SHX')).Path
New-Item -ItemType Directory -Force $t | Out-Null
function Lisp($path) { return $path -replace '\\', '/' }

function Invoke-Core($dwg, $lines, $tag) {
    $scr = Join-Path $t "$tag.scr"
    [IO.File]::WriteAllLines($scr, $lines, (New-Object Text.UTF8Encoding($false)))
    $out = Join-Path $t "$tag.out.txt"
    $p = Start-Process "$ac\accoreconsole.exe" -ArgumentList @('/i', "`"$dwg`"", '/s', "`"$scr`"", '/l', 'en-US') `
         -RedirectStandardOutput $out -RedirectStandardError (Join-Path $t "$tag.err.txt") -PassThru -WindowStyle Hidden
    if (-not $p.WaitForExit(240000)) { $p.Kill(); throw "accoreconsole qua han ($tag)" }
    Get-Content $out -Encoding Unicode | Where-Object { $_ -match '\[PKTTC\]|\[FIXTURE\]|rror|Unknown command|^  - ' }
}
$load = '(command "_.NETLOAD" "' + (Lisp "$bin\Pkttc.TextHub.dll") + '")'

Remove-Item "$t\_backup" -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem $t -Include *.json, *.ps1 -Recurse | Remove-Item -Force
Copy-Item "$env:LOCALAPPDATA\Autodesk\AutoCAD 2020\R23.1\enu\Template\acad.dwt" "$t\blank_copy.dwg" -Force
Remove-Item "$t\fixture_font.dwg" -ErrorAction SilentlyContinue
'--- Tao ban ve mau (font)'
Invoke-Core "$t\blank_copy.dwg" @(('(command "_.NETLOAD" "' + (Lisp "$bin\Pkttc.TextHub.FixtureMaker.dll") + '")'), 'PKTMAKEFONTFIXTURE', 'QUIT', 'Y') 'make' | Out-Null
if (-not (Test-Path "$t\fixture_font.dwg")) { throw 'Khong tao duoc fixture_font.dwg' }
$h0 = (Get-FileHash "$t\fixture_font.dwg").Hash
$dwg = "$t\fixture_font.dwg"

# Kho thu = thu muc gia lap (co pkttdemo.shx, font chac chan khong co tren may) + kho that cua phong
New-Item -ItemType Directory -Force "$t\store" | Out-Null
Copy-Item "$store\Alumni.shx" "$t\store\pkttdemo.shx" -Force
$env:PKTTC_FONT_STORE = "$t\store;$store"

'--- A: bao cao, thay font, don style'
Invoke-Core $dwg @($load,
    'PKTEXTFONT', (Lisp "$t\fonts_before.json"), (Lisp "$t\cai_before.ps1"),
    'PKTEXTSCAN', (Lisp "$t\scan_before.json"),
    'PKTEXTFONTSUB', 'YES',
    'PKTEXTFONT', (Lisp "$t\fonts_after_sub.json"), (Lisp "$t\cai_after.ps1"),
    'PKTEXTPURGE', 'YES',
    'PKTEXTSCAN', (Lisp "$t\scan_after.json"),
    'QUIT', 'Y') 'A'

'--- B: thay font + don style roi UNDO 2 lan'
Invoke-Core $dwg @($load,
    'PKTEXTFONTSUB', 'YES',
    'PKTEXTPURGE', 'YES',
    '_.U', '_.U',
    'PKTEXTSCAN', (Lisp "$t\scan_undo.json"),
    'QUIT', 'Y') 'B'

'--- C: tu choi xac nhan'
Invoke-Core $dwg @($load,
    'PKTEXTFONTSUB', 'no',
    'PKTEXTPURGE', 'no',
    'PKTEXTSCAN', (Lisp "$t\scan_cancel.json"),
    'QUIT', 'Y') 'C'

'--- D: khong cau hinh kho font'
$env:PKTTC_FONT_STORE = 'NONE'
Invoke-Core $dwg @($load,
    'PKTEXTFONT', (Lisp "$t\fonts_nostore.json"), (Lisp "$t\cai_nostore.ps1"),
    'QUIT', 'Y') 'D'
Remove-Item Env:\PKTTC_FONT_STORE -ErrorAction SilentlyContinue

if ($h0 -ne (Get-FileHash $dwg).Hash) { throw 'Tep fixture_font.dwg tren dia bi thay doi (khong duoc luu)!' } else { 'Tep tren dia khong doi (SHA-256).' }

python -X utf8 -I "$w\tests\verify_s4.py" $t "$w\src\Db"
exit $LASTEXITCODE
