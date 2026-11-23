# S5: kiem thu cong Kuro headless tren ban sao mau. PowerShell 5.1.
$ErrorActionPreference = 'Stop'
$w   = $PSScriptRoot
$ac  = 'C:\Program Files\Autodesk\AutoCAD 2020'
$t   = Join-Path $w 'test'
$bin = (Get-Content "$w\bin\latest.txt" -Raw).Trim()
New-Item -ItemType Directory -Force $t | Out-Null
function Lisp($path) { return $path -replace '\\', '/' }

Get-Process accoreconsole -ErrorAction SilentlyContinue | Stop-Process -Force
Copy-Item "$env:LOCALAPPDATA\Autodesk\AutoCAD 2020\R23.1\enu\Template\acad.dwt" "$t\blank_copy.dwg" -Force
Remove-Item "$t\fixture_20.dwg" -ErrorAction SilentlyContinue
$scr = "$t\make.scr"
[IO.File]::WriteAllLines($scr, @(('(command "_.NETLOAD" "' + (Lisp "$bin\Pkttc.TextHub.FixtureMaker.dll") + '")'), 'PKTMAKEFIXTURE', 'QUIT', 'Y'), (New-Object Text.UTF8Encoding($false)))
$p = Start-Process "$ac\accoreconsole.exe" -ArgumentList @('/i', "`"$t\blank_copy.dwg`"", '/s', "`"$scr`"", '/l', 'en-US') -RedirectStandardOutput "$t\make.out.txt" -PassThru -WindowStyle Hidden
if (-not $p.WaitForExit(180000)) { $p.Kill(); throw 'tao fixture qua han' }
if (-not (Test-Path "$t\fixture_20.dwg")) { throw 'Khong tao duoc fixture_20.dwg' }
$h0 = (Get-FileHash "$t\fixture_20.dwg").Hash

python -X utf8 -I "$w\tests\bridge_test.py" $w $bin "$t\fixture_20.dwg"
$rc = $LASTEXITCODE
if ($h0 -ne (Get-FileHash "$t\fixture_20.dwg").Hash) { throw 'fixture_20.dwg tren dia bi thay doi (khong duoc luu)!' } else { 'Tep tren dia khong doi (SHA-256).' }
exit $rc
