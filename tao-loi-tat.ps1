# Tao bieu tuong Kuro App tren man hinh chinh (Desktop) va menu Start.
$dir = $PSScriptRoot
$sh = New-Object -ComObject WScript.Shell
$pythonw = Join-Path $dir ".venv\Scripts\pythonw.exe"
$appScript = Join-Path $dir "app_desktop.py"

foreach ($noi in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
  $s = $sh.CreateShortcut((Join-Path $noi 'Kuro OS.lnk'))
  $s.TargetPath = $pythonw
  $s.Arguments = '"' + $appScript + '"'
  $s.WorkingDirectory = $dir
  $s.IconLocation = (Join-Path $dir 'kuro.ico') + ',0'
  $s.Description = 'Kuro OS - Tro ly Ky su Ha tang (Windows App)'
  $s.Save()
}
Write-Host 'Da tao bieu tuong Kuro OS Desktop tren man hinh chinh (Desktop) va menu Start.'
