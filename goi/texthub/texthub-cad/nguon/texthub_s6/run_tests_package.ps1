# S6: dong goi roi kiem thu goi (tinh, trinh cai, tu nap that tren phien AutoCAD rieng). PowerShell 5.1.
$ErrorActionPreference = 'Stop'
$w = $PSScriptRoot
$fixture = Join-Path (Split-Path $w -Parent) 'texthub_s5\test\fixture_20.dwg'
if (-not (Test-Path $fixture)) { throw "Thieu $fixture (chay texthub_s5\run_tests_bridge.ps1 de tao)" }
& "$w\dong_goi.ps1" | ForEach-Object { Write-Host $_ }
$ErrorActionPreference = 'Continue'
python -X utf8 -I "$w\tests\package_test.py" $w $fixture 2>&1 | ForEach-Object { "$_" }
exit $LASTEXITCODE
