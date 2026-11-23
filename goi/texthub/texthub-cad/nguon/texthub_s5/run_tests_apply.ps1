# S4: kiem thu GHI (ten style theo ten font) headless tren ban sao mau. PowerShell 5.1.
# Kich ban A: quet truoc -> lap ke hoach -> ap dung (YES) -> quet sau -> lap ke hoach lan 2 (phai rong).
# Kich ban B: ap dung roi UNDO mot buoc -> quet: phai bang quet truoc.
# Kich ban C: ap dung voi xac nhan sai (khong phai YES) -> ban ve khong doi, khong sao luu.
$ErrorActionPreference = 'Stop'
$w   = $PSScriptRoot
$ac  = 'C:\Program Files\Autodesk\AutoCAD 2020'
$t   = Join-Path $w 'test'
$bin = (Get-Content "$w\bin\latest.txt" -Raw).Trim()
New-Item -ItemType Directory -Force $t | Out-Null
function Lisp($path) { return $path -replace '\\', '/' }

function Invoke-Core($dwg, $lines, $tag) {
    $scr = Join-Path $t "$tag.scr"
    [IO.File]::WriteAllLines($scr, $lines, (New-Object Text.UTF8Encoding($false)))
    $out = Join-Path $t "$tag.out.txt"
    $p = Start-Process "$ac\accoreconsole.exe" -ArgumentList @('/i', "`"$dwg`"", '/s', "`"$scr`"", '/l', 'en-US') `
         -RedirectStandardOutput $out -RedirectStandardError (Join-Path $t "$tag.err.txt") -PassThru -WindowStyle Hidden
    if (-not $p.WaitForExit(240000)) { $p.Kill(); throw "accoreconsole qua han ($tag)" }
    Get-Content $out -Encoding Unicode | Where-Object { $_ -match '\[PKTTC\]|\[FIXTURE\]|rror|Unknown command' }
}
$load = '(command "_.NETLOAD" "' + (Lisp "$bin\Pkttc.TextHub.dll") + '")'

# --- Ban sao mau ---
Remove-Item "$t\_backup" -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem $t -Include *.json -Recurse | Remove-Item -Force
Copy-Item "$env:LOCALAPPDATA\Autodesk\AutoCAD 2020\R23.1\enu\Template\acad.dwt" "$t\blank_copy.dwg" -Force
Remove-Item "$t\fixture_20.dwg" -ErrorAction SilentlyContinue
'--- Tao ban ve mau'
Invoke-Core "$t\blank_copy.dwg" @(('(command "_.NETLOAD" "' + (Lisp "$bin\Pkttc.TextHub.FixtureMaker.dll") + '")'), 'PKTMAKEFIXTURE', 'QUIT', 'Y') 'make' | Out-Null
if (-not (Test-Path "$t\fixture_20.dwg")) { throw 'Khong tao duoc fixture_20.dwg' }
$h0 = (Get-FileHash "$t\fixture_20.dwg").Hash

# --- A ---
'--- Kich ban A: ap dung'
Invoke-Core "$t\fixture_20.dwg" @($load,
    'PKTEXTSCAN', (Lisp "$t\before.json"),
    'PKTEXTPLAN', (Lisp "$t\plan.json"), '',
    'PKTEXTAPPLY', (Lisp "$t\plan.json"), 'YES',
    'PKTEXTSCAN', (Lisp "$t\after.json"),
    'PKTEXTPLAN', (Lisp "$t\plan2.json"), '',
    'QUIT', 'Y') 'A'

# --- B ---
'--- Kich ban B: ap dung roi UNDO'
Invoke-Core "$t\fixture_20.dwg" @($load,
    'PKTEXTAPPLY', (Lisp "$t\plan.json"), 'YES',
    '_.U',
    'PKTEXTSCAN', (Lisp "$t\after_undo.json"),
    'QUIT', 'Y') 'B'

# --- C ---
'--- Kich ban C: tu choi xac nhan'
Invoke-Core "$t\fixture_20.dwg" @($load,
    'PKTEXTAPPLY', (Lisp "$t\plan.json"), 'no',
    'PKTEXTSCAN', (Lisp "$t\after_cancel.json"),
    'QUIT', 'Y') 'C'

# --- D: ke hoach bi sua tay phai bi tu choi ---
'--- Kich ban D: ke hoach bi sua'
$planText = [IO.File]::ReadAllText("$t\plan.json", [Text.Encoding]::UTF8)
$tampered = $planText.Replace('"newStyle":"Arial Unicode MS_2"', '"newStyle":"HACK"')
if ($tampered -eq $planText) { throw 'Khong tao duoc ban ke hoach bi sua' }
[IO.File]::WriteAllText("$t\plan_tamper.json", $tampered, (New-Object Text.UTF8Encoding($false)))
Invoke-Core "$t\fixture_20.dwg" @($load,
    'PKTEXTAPPLY', (Lisp "$t\plan_tamper.json"),   # bi tu choi truoc khi hoi YES, nen khong gui YES
    'PKTEXTSCAN', (Lisp "$t\after_tamper.json"),
    'QUIT', 'Y') 'D'

$h1 = (Get-FileHash "$t\fixture_20.dwg").Hash
if ($h0 -ne $h1) { throw 'Tep fixture_20.dwg tren dia bi thay doi (khong duoc luu, khong mong doi)!' } else { 'Tep tren dia khong doi (SHA-256 truoc = sau).' }

python -X utf8 -I "$w\tests\verify_apply.py" $t
exit $LASTEXITCODE
