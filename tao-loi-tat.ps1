# Tao bieu tuong Kuro App tren man hinh chinh (Desktop) va menu Start.
$dir = $PSScriptRoot
$sh = New-Object -ComObject WScript.Shell
$pythonw = Join-Path $dir ".venv\Scripts\pythonw.exe"
$appScript = Join-Path $dir "app_desktop.py"
$iconFile = Join-Path $dir "kuro_logo.ico"

# Danh sach cac noi dat shortcut
$locations = @(
  [Environment]::GetFolderPath('Desktop'),
  [Environment]::GetFolderPath('Programs')
)

# Kiem tra them cac thu muc Desktop OneDrive neu co
$oneDriveDesktop = Join-Path $env:USERPROFILE "OneDrive\Desktop"
if (Test-Path $oneDriveDesktop) { $locations += $oneDriveDesktop }

foreach ($noi in $locations) {
  if (Test-Path $noi) {
    $oldLnk = Join-Path $noi 'Kuro.lnk'
    if (Test-Path $oldLnk) { Remove-Item $oldLnk -Force -ErrorAction SilentlyContinue }
    
    $lnkPath = Join-Path $noi 'Kuro OS.lnk'
    $s = $sh.CreateShortcut($lnkPath)
    $s.TargetPath = $pythonw
    $s.Arguments = '"' + $appScript + '"'
    $s.WorkingDirectory = $dir
    $s.IconLocation = $iconFile + ',0'
    $s.Description = 'Kuro OS - Tro ly Ky su Ha tang (Windows App)'
    $s.Save()
  }
}

# Thong bao cho Windows Explorer lam moi lai toan bo Icon tren man hinh
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public class ShellNotification {
    [DllImport("shell32.dll")]
    public static extern void SHChangeNotify(int wEventId, int uFlags, IntPtr dwItem1, IntPtr dwItem2);
}
'@ -ErrorAction SilentlyContinue

try {
    [ShellNotification]::SHChangeNotify(0x08000000, 0x0000, [IntPtr]::Zero, [IntPtr]::Zero)
} catch {}

Write-Host 'Da tao va lam moi bieu tuong Kuro OS voi logo moi thanh cong!'
