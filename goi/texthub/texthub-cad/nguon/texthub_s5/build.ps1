# S5: dung Pkttc.TextHub.dll (Core + Db) va FixtureMaker. PowerShell 5.1.
# Dung csc.exe .NET Framework (C# 5). Core lay thang tu texthub_s1 (khong sao chep).
# Moi lan dung ra thu muc bin\b<thoi gian>\ (AutoCAD khoa DLL da NETLOAD nen khong ghi de duoc); bin\latest.txt tro toi thu muc moi nhat.
$ErrorActionPreference = 'Stop'
$w   = $PSScriptRoot
$s1  = Join-Path (Split-Path $w -Parent) 'texthub_s1'
$ac  = 'C:\Program Files\Autodesk\AutoCAD 2020'
$csc = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'

# Sinh lai du lieu bang ma (S1) de Core luon khop CSV
python -X utf8 -I "$s1\tools\build_charsets.py"
if ($LASTEXITCODE -ne 0) { throw 'build_charsets.py loi' }

$dir = Join-Path $w ('bin\b' + (Get-Date -Format 'yyyyMMddHHmmss'))
New-Item -ItemType Directory -Force $dir, "$w\test" | Out-Null
$core = Get-ChildItem "$s1\src\Core\*.cs" | ForEach-Object { $_.FullName }
$db   = Get-ChildItem "$w\src\Db\*.cs"    | ForEach-Object { $_.FullName }

function Invoke-Csc($argsList, $name) {
    $out = & $csc @argsList 2>&1
    $out | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) { throw "csc ($name) loi, ma $LASTEXITCODE" }
}

Invoke-Csc (@('/nologo', '/target:library', '/platform:x64', '/optimize+', '/warn:4', '/codepage:65001',
              "/out:$dir\Pkttc.TextHub.dll", "/reference:$ac\accoremgd.dll", "/reference:$ac\acdbmgd.dll", '/reference:System.Drawing.dll', '/reference:System.Web.Extensions.dll', '/reference:System.Windows.Forms.dll', '/reference:Microsoft.CSharp.dll', '/reference:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\PresentationCore.dll', '/reference:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\WindowsBase.dll', "/reference:$ac\acmgd.dll") + $core + $db) 'TextHub'

Invoke-Csc @('/nologo', '/target:library', '/platform:x64', '/optimize+', '/warn:4', '/codepage:65001',
             "/out:$dir\Pkttc.TextHub.FixtureMaker.dll", "/reference:$ac\accoremgd.dll", "/reference:$ac\acdbmgd.dll", "$w\tests\FixtureMaker.cs") 'FixtureMaker'

# Kiem thu dat ten style dich (khong can AutoCAD)
Invoke-Csc @('/nologo', '/target:exe', '/platform:anycpu', '/optimize+', '/warn:4', '/codepage:65001', "/out:$dir\PlanTests.exe",
             '/reference:System.Web.Extensions.dll', "$w\src\Db\Model.cs", "$w\src\Db\Plan.cs", "$w\tests\PlanTests.cs") 'PlanTests'
& "$dir\PlanTests.exe" | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0) { throw 'PlanTests loi' }

Set-Content -Path "$w\bin\latest.txt" -Value $dir -Encoding ASCII
# Giu 4 ban dung gan nhat
Get-ChildItem "$w\bin" -Directory | Sort-Object Name -Descending | Select-Object -Skip 4 | ForEach-Object {
    try { Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop } catch { }
}
"Dung xong: $dir"

