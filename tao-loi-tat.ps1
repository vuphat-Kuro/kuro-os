# Tao bieu tuong Kuro tren man hinh chinh (Desktop) va menu Start. Chay lai bao nhieu lan cung duoc.
$dir = $PSScriptRoot
$sh = New-Object -ComObject WScript.Shell
foreach ($noi in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
  $s = $sh.CreateShortcut((Join-Path $noi 'Kuro.lnk'))
  $s.TargetPath = Join-Path $env:WINDIR 'System32\wscript.exe'
  $s.Arguments = '"' + (Join-Path $dir 'kuro.vbs') + '"'
  $s.WorkingDirectory = $dir
  $s.IconLocation = (Join-Path $dir 'kuro.ico') + ',0'
  $s.Description = 'Kuro - tro ly ky su ha tang'
  $s.Save()
}
Write-Host 'Da tao bieu tuong Kuro tren man hinh chinh va menu Start.'
