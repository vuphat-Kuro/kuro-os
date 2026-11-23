# Dung va chay kiem thu Core (S1). PowerShell 5.1. Chay: powershell -File build.ps1
# Dung csc.exe (.NET Framework, C# 5) co san tren may; khong can Visual Studio/NuGet.
$ErrorActionPreference = 'Stop'
$w   = $PSScriptRoot
$csc = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'

# 1. Sinh du lieu bang ma tu cac nguon doi chieu
python -X utf8 -I "$w\tools\build_charsets.py"
if ($LASTEXITCODE -ne 0) { throw 'build_charsets.py loi' }

New-Item -ItemType Directory -Force "$w\bin" | Out-Null
$core = Get-ChildItem "$w\src\Core\*.cs" | ForEach-Object { $_.FullName }

# 2. Thu vien Core
& $csc /nologo /target:library /platform:anycpu /optimize+ /warn:4 /codepage:65001 "/out:$w\bin\Pkttc.Text.Core.dll" $core
if ($LASTEXITCODE -ne 0) { throw "csc (Core) loi, ma $LASTEXITCODE" }

# 3. Bo kiem thu (bien dich cung ma Core de truy cap internal)
& $csc /nologo /target:exe /platform:anycpu /optimize+ /warn:4 /codepage:65001 "/out:$w\bin\Pkttc.Text.Core.Tests.exe" $core "$w\tests\CoreTests.cs"
if ($LASTEXITCODE -ne 0) { throw "csc (Tests) loi, ma $LASTEXITCODE" }

# 4. Chay
& "$w\bin\Pkttc.Text.Core.Tests.exe"
exit $LASTEXITCODE
