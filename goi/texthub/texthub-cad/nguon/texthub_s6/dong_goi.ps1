# Dong goi PKTTC TextHub thanh bundle tu nap + goi cai dat. PowerShell 5.1.
# Dung: powershell -File dong_goi.ps1
# Dau ra: dist\PKTTC.TextHub.bundle\, dist\cai_dat.ps1, dist\HUONG_DAN_CAI_DAT.md, dist\PKTTC.TextHub-<phien ban>.zip
# Nguon: Core (texthub_s1) + Db (texthub_s5) + About.cs (thu muc nay). Phien ban lay tu tep VERSION.
$ErrorActionPreference = 'Stop'
$w   = $PSScriptRoot
$qt  = Split-Path $w -Parent
$s1  = Join-Path $qt 'texthub_s1'
$s5  = Join-Path $qt 'texthub_s5'
$ac  = 'C:\Program Files\Autodesk\AutoCAD 2020'
$csc = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$wpf = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF'

# Ma San pham co dinh qua cac phien ban (nang cap dung cung ProductCode/UpgradeCode)
$productCode = '{6CE93D44-325B-4673-A806-7A15E3D58F9C}'
$upgradeCode = '{8081FD1D-D9A3-4B77-8E82-68912EEBA901}'

$ver = (Get-Content "$w\VERSION" -Raw).Trim()
if ($ver -notmatch '^\d+\.\d+\.\d+$') { throw "VERSION khong hop le: $ver" }
$ver4 = "$ver.0"

# 0. Kiem thu Core (dung neu loi)
& "$s1\build.ps1" | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Kiem thu Core loi' }
python -X utf8 -I "$s1\tools\build_charsets.py" | Out-Null

# 1. Thong tin phien ban nhung vao DLL
$obj = Join-Path $w 'obj'
New-Item -ItemType Directory -Force $obj | Out-Null
$ai = @"
using System.Reflection;
[assembly: AssemblyTitle("PKTTC TextHub")]
[assembly: AssemblyCompany("Phong Ky thuat - Thi cong")]
[assembly: AssemblyProduct("PKTTC TextHub")]
[assembly: AssemblyVersion("$ver4")]
[assembly: AssemblyFileVersion("$ver4")]
[assembly: AssemblyInformationalVersion("$ver")]
"@
[IO.File]::WriteAllText("$obj\AssemblyInfo.g.cs", $ai, (New-Object Text.UTF8Encoding($false)))

# 2. Dung bundle
$dist   = Join-Path $w 'dist'
$bundle = Join-Path $dist 'PKTTC.TextHub.bundle'
if (Test-Path $dist) { Remove-Item $dist -Recurse -Force }
New-Item -ItemType Directory -Force "$bundle\Contents\Windows", "$bundle\Contents\Bridge", "$bundle\Contents\Docs", "$bundle\Contents\Fonts" | Out-Null

$core = Get-ChildItem "$s1\src\Core\*.cs" | ForEach-Object { $_.FullName }
$db   = Get-ChildItem "$s5\src\Db\*.cs"   | ForEach-Object { $_.FullName }
$more = @("$w\src\About.cs", "$obj\AssemblyInfo.g.cs")
$args1 = @('/nologo', '/target:library', '/platform:x64', '/optimize+', '/warn:4', '/codepage:65001', "/out:$bundle\Contents\Windows\Pkttc.TextHub.dll",
    "/reference:$ac\accoremgd.dll", "/reference:$ac\acdbmgd.dll", "/reference:$ac\acmgd.dll", '/reference:System.Drawing.dll',
    '/reference:System.Web.Extensions.dll', '/reference:System.Windows.Forms.dll', '/reference:Microsoft.CSharp.dll', "/reference:$wpf\PresentationCore.dll", "/reference:$wpf\WindowsBase.dll") + $core + $db + $more
$out = & $csc @args1 2>&1
$out | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0) { throw "csc loi, ma $LASTEXITCODE" }

# 3. Danh sach lenh lay tu ma nguon (khong go tay)
$cmds = @()
foreach ($f in ($db + $more)) {
    $cmds += [regex]::Matches((Get-Content $f -Raw -Encoding UTF8), 'CommandMethod\("([A-Za-z0-9_]+)"') | ForEach-Object { $_.Groups[1].Value }
}
$cmds = $cmds | Sort-Object -Unique
if ($cmds.Count -lt 10) { throw "Danh sach lenh bat thuong: $($cmds.Count)" }
$cmdXml = ($cmds | ForEach-Object { "        <Command Local=`"$_`" Global=`"$_`" />" }) -join "`r`n"

# 4. PackageContents.xml (AutoCAD 2020 = R23.1)
$xml = @"
<?xml version="1.0" encoding="utf-8"?>
<ApplicationPackage SchemaVersion="1.0" ProductType="Application" Name="PKTTC TextHub" AppVersion="$ver" Description="Quan ly chu tieng Viet trong ban ve: doi bang ma TCVN3/VNI sang Unicode, quan ly font va style, cong cho tro ly" Author="Phong Ky thuat - Thi cong" FriendlyVersion="$ver" ProductCode="$productCode" UpgradeCode="$upgradeCode" AutodeskProduct="AutoCAD" SupportedLocales="Enu">
  <CompanyDetails Name="Phong Ky thuat - Thi cong" />
  <Components Description="AutoCAD 2020 (.NET Framework 4.7/4.8, API 23.1)">
    <RuntimeRequirements OS="Win64" Platform="AutoCAD" SeriesMin="R23.1" SeriesMax="R23.1" SupportPath="./Contents/Fonts" />
    <ComponentEntry AppName="PKTTC.TextHub" Version="$ver" ModuleName="./Contents/Windows/Pkttc.TextHub.dll" AppDescription="PKTTC TextHub" LoadOnAutoCADStartup="true">
      <Commands GroupName="PKTTC_TEXTHUB">
$cmdXml
      </Commands>
    </ComponentEntry>
  </Components>
</ApplicationPackage>
"@
[IO.File]::WriteAllText("$bundle\PackageContents.xml", $xml, (New-Object Text.UTF8Encoding($false)))

# 4b. SHX Unicode (header "AutoCAD-86 unifont") tu kho font vao Contents\Fonts: AutoCAD them thu muc nay vao Support File Search Path
#     (RuntimeRequirements SupportPath), nen may moi khong thieu uv-abc.shx, 3T-Unicode.shx, VN_UNI.shx... khi chu da doi sang SHX Unicode.
$kho = Join-Path (Split-Path $qt -Parent) '05-ThuVien\06-Kho-Font'
$nShx = 0
if (Test-Path $kho) {
    foreach ($f in (Get-ChildItem $kho -Recurse -File -Filter *.shx | Sort-Object Name)) {
        $fs = [IO.File]::OpenRead($f.FullName); $buf = New-Object byte[] 32; $n = $fs.Read($buf, 0, 32); $fs.Close()
        if ([Text.Encoding]::ASCII.GetString($buf, 0, $n).StartsWith('AutoCAD-86 unifont') -and -not (Test-Path "$bundle\Contents\Fonts\$($f.Name)")) {
            Copy-Item $f.FullName "$bundle\Contents\Fonts\" ; $nShx++
        }
    }
}
if ($nShx -lt 1) { throw "Khong co SHX Unicode nao trong kho font ($kho): bundle se thieu font." }

# 5. Tro ly, tai lieu
Copy-Item "$s5\bridge\pkttc_client.py", "$s5\bridge\pkttc_mcp.py" "$bundle\Contents\Bridge\"
Copy-Item "$w\package\HUONG_DAN_SU_DUNG.md" "$bundle\Contents\Docs\"
Copy-Item "$s5\HUONG_DAN_KURO.md" "$bundle\Contents\Docs\"
Copy-Item "$w\package\cai_dat.ps1" "$dist\"
Copy-Item "$w\package\HUONG_DAN_CAI_DAT.md" "$dist\"

# 6. MANIFEST (SHA-256 moi tep trong bundle, tru chinh MANIFEST)
$lines = @("PKTTC TextHub $ver", "Dong goi: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')", '')
foreach ($f in (Get-ChildItem $bundle -Recurse -File | Where-Object { $_.Name -ne 'MANIFEST.txt' } | Sort-Object FullName)) {
    $rel = $f.FullName.Substring($bundle.Length + 1)
    $lines += ('{0}  {1}' -f (Get-FileHash $f.FullName -Algorithm SHA256).Hash, $rel)
}
[IO.File]::WriteAllLines("$bundle\MANIFEST.txt", $lines, (New-Object Text.UTF8Encoding($false)))

# 7. Zip
$zip = Join-Path $dist "PKTTC.TextHub-$ver.zip"
Compress-Archive -Path $bundle, "$dist\cai_dat.ps1", "$dist\HUONG_DAN_CAI_DAT.md" -DestinationPath $zip -Force
"Da dong goi ${ver}: $zip"
"Lenh trong bundle ($($cmds.Count)): " + ($cmds -join ', ')
