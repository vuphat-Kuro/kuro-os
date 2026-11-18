# Cai dat Kuro OS tu dong cho may Windows moi.
# Kiem tra tung thanh phan, thieu thi cai: Python 3.13, WebView2, Git, Node.js, Claude Code CLI, Antigravity CLI (agy).
# Roi tao .venv, cai thu vien, tao .env va bieu tuong Desktop.
#   -ChiKiemTra : chi bao thanh phan nao co/thieu, khong cai gi, khong dong toi may.
#   -Codex      : cai them Codex CLI (ChatGPT). Mac dinh khong cai.
# Can Windows 10 1809 tro len co winget (App Installer). Git va Node.js se hien hop xin quyen quan tri (UAC).
param([switch]$ChiKiemTra, [switch]$Codex)

$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dir = $PSScriptRoot
Set-Location $dir
$script:py = $null

function Lam-Moi-Path {
  # Trinh cai dat ghi PATH vao registry; tien trinh dang chay phai doc lai moi thay lenh vua cai.
  $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
  $npm = Join-Path $env:APPDATA 'npm'
  if ((Test-Path $npm) -and ($env:Path -notlike "*$npm*")) { $env:Path += ";$npm" }
}

function Co-Lenh($ten) { [bool](Get-Command $ten -ErrorAction SilentlyContinue) }

function Tim-Python {
  # Chi nhan 3.11-3.13: ban thu vien trong requirements-ky-thuat.txt da kiem tren 3.13.
  if (Co-Lenh 'py') {
    foreach ($v in '3.13', '3.12', '3.11') {
      $p = & py "-$v" -c "import sys;print(sys.executable)" 2>$null   # khong dung Select -First: cat ong som lam LASTEXITCODE sai
      if ($LASTEXITCODE -eq 0 -and $p -and (Test-Path "$p")) { return "$p" }
    }
  }
  $c = Get-Command python -ErrorAction SilentlyContinue
  if ($c -and $c.Source -notlike '*\WindowsApps\*') {   # WindowsApps\python.exe chi la lối tắt mở Store
    $v = & $c.Source -c "import sys;print('%d.%d' % sys.version_info[:2])" 2>$null
    if ($v -in '3.11', '3.12', '3.13') { return $c.Source }
  }
  return $null
}

function Co-WebView2 {
  $k = '{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}'
  foreach ($p in "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\$k", "HKLM:\SOFTWARE\Microsoft\EdgeUpdate\Clients\$k", "HKCU:\SOFTWARE\Microsoft\EdgeUpdate\Clients\$k") {
    if ((Get-ItemProperty $p -ErrorAction SilentlyContinue).pv) { return $true }
  }
  return $false
}

function Co-Agy { (Co-Lenh 'agy') -or (Test-Path (Join-Path $env:LOCALAPPDATA 'agy\bin\agy.exe')) }

function Winget($id, $them = @()) {
  if (-not (Co-Lenh 'winget')) {
    throw 'Máy chưa có winget. Mở Microsoft Store, cài "App Installer", rồi chạy lại setup.bat.'
  }
  & winget install -e --id $id --silent --accept-package-agreements --accept-source-agreements @them
}

function Npm-Cai($goi) {
  if (-not (Co-Lenh 'npm.cmd')) { throw 'Chưa có Node.js nên chưa cài được gói npm.' }
  & npm.cmd install -g $goi
}

# Moi thanh phan: Kiem (co chua?), Cai, BatBuoc (thieu la dung), Link (cai tay neu tu dong that bai)
$ThanhPhan = @(
  @{ Ten = 'Python 3.13'; BatBuoc = $true; Link = 'https://www.python.org/downloads/ (nhớ tích "Add python.exe to PATH")'
     Kiem = { $script:py = Tim-Python; [bool]$script:py }
     Cai  = { Winget 'Python.Python.3.13' @('--override', '/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1') } },
  @{ Ten = 'Edge WebView2 (khung cửa sổ ứng dụng)'; BatBuoc = $false; Link = 'https://developer.microsoft.com/microsoft-edge/webview2/'
     Kiem = { Co-WebView2 }
     Cai  = { Winget 'Microsoft.EdgeWebView2Runtime' } },
  @{ Ten = 'Git (để cập nhật Kuro)'; BatBuoc = $false; Link = 'https://git-scm.com/download/win'
     Kiem = { Co-Lenh 'git' }
     Cai  = { Winget 'Git.Git' } },
  @{ Ten = 'Node.js LTS'; BatBuoc = $true; Link = 'https://nodejs.org/'
     Kiem = { Co-Lenh 'node' }
     Cai  = { Winget 'OpenJS.NodeJS.LTS' } },
  @{ Ten = 'Claude Code CLI'; BatBuoc = $false; Link = 'mở PowerShell gõ: npm install -g @anthropic-ai/claude-code'
     Kiem = { Co-Lenh 'claude' }
     Cai  = { Npm-Cai '@anthropic-ai/claude-code' } },
  @{ Ten = 'Antigravity CLI (agy)'; BatBuoc = $false; Link = 'mở PowerShell gõ: irm https://antigravity.google/cli/install.ps1 | iex'
     Kiem = { Co-Agy }
     Cai  = { & powershell -NoProfile -ExecutionPolicy Bypass -Command 'irm https://antigravity.google/cli/install.ps1 | iex' } }
)
if ($Codex) {
  $ThanhPhan += @{ Ten = 'Codex CLI (ChatGPT)'; BatBuoc = $false; Link = 'mở PowerShell gõ: npm install -g @openai/codex'
                   Kiem = { Co-Lenh 'codex' }
                   Cai  = { Npm-Cai '@openai/codex' } }
}

Write-Host '====================================================================='
Write-Host '         CÀI ĐẶT TỰ ĐỘNG TRỢ LÝ KỸ SƯ HẠ TẦNG - KURO OS'
Write-Host '====================================================================='
if ($ChiKiemTra) { Write-Host '(Chế độ chỉ kiểm tra: không cài gì)' }
Write-Host ''
Write-Host '[1/3] Kiểm tra và cài thành phần cần thiết...'

Lam-Moi-Path
$thieuBatBuoc = @()
$bang = @()
foreach ($c in $ThanhPhan) {
  if (& $c.Kiem) { $bang += [pscustomobject]@{ 'Thành phần' = $c.Ten; 'Trạng thái' = 'Đã có' }; continue }
  if ($ChiKiemTra) {
    $bang += [pscustomobject]@{ 'Thành phần' = $c.Ten; 'Trạng thái' = 'THIẾU' }
    if ($c.BatBuoc) { $thieuBatBuoc += $c.Ten }
    continue
  }
  Write-Host "-> Đang cài $($c.Ten)..."
  try { & $c.Cai } catch { Write-Host "   $($_.Exception.Message)" }
  Lam-Moi-Path
  if (& $c.Kiem) {
    $bang += [pscustomobject]@{ 'Thành phần' = $c.Ten; 'Trạng thái' = 'Vừa cài xong' }
  } else {
    $bang += [pscustomobject]@{ 'Thành phần' = $c.Ten; 'Trạng thái' = 'CÀI KHÔNG ĐƯỢC' }
    Write-Host "   [LỖI] Không cài được $($c.Ten). Cài tay: $($c.Link)"
    if ($c.BatBuoc) { $thieuBatBuoc += $c.Ten }
  }
}
Write-Host ''
$bang | Format-Table -AutoSize | Out-String | Write-Host

if ($thieuBatBuoc.Count) {
  Write-Host "[DỪNG] Còn thiếu thành phần bắt buộc: $($thieuBatBuoc -join ', '). Cài xong rồi chạy lại setup.bat."
  exit 1
}
if ($ChiKiemTra) { exit 0 }

Write-Host '[2/3] Tạo môi trường Python (.venv) và cài thư viện (2-5 phút, đừng tắt cửa sổ)...'
$venvPy = Join-Path $dir '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPy)) {
  if (Test-Path (Join-Path $dir '.venv')) { Remove-Item (Join-Path $dir '.venv') -Recurse -Force }
  & $script:py -m venv (Join-Path $dir '.venv')
  if (-not (Test-Path $venvPy)) { Write-Host '[LỖI] Không tạo được .venv. Kiểm tra quyền thư mục hoặc cài lại Python.'; exit 1 }
}
& $venvPy -m pip install --disable-pip-version-check --upgrade pip *> $null
& $venvPy -m pip install --disable-pip-version-check -r (Join-Path $dir 'requirements.txt')
if ($LASTEXITCODE -ne 0) {
  Write-Host '[Cảnh báo] Một số gói lỗi, thử lại các gói cốt lõi...'
  & $venvPy -m pip install pywebview pywin32 pythonnet psutil fastapi uvicorn httpx pyyaml claude-agent-sdk
}
if (Test-Path (Join-Path $dir 'requirements-ky-thuat.txt')) {
  & $venvPy -m pip install --disable-pip-version-check -r (Join-Path $dir 'requirements-ky-thuat.txt')
}
& $venvPy -c "import fastapi, uvicorn, claude_agent_sdk, webview" 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host '[LỖI] Thiếu thư viện lõi sau khi cài (fastapi, uvicorn, claude_agent_sdk, webview). Xem lỗi pip phía trên.'; exit 1 }

if (-not (Test-Path (Join-Path $dir '.env')) -and (Test-Path (Join-Path $dir 'env.example'))) {
  Copy-Item (Join-Path $dir 'env.example') (Join-Path $dir '.env')
  Write-Host '-> Đã tạo tệp cấu hình .env mặc định.'
}

Write-Host '[3/3] Tạo biểu tượng Kuro OS trên màn hình chính...'
& (Join-Path $dir 'tao-loi-tat.ps1')

Write-Host ''
Write-Host '====================================================================='
Write-Host 'CÀI ĐẶT HOÀN TẤT. Nhấp đúp biểu tượng KURO OS trên màn hình chính.'
Write-Host 'Còn một bước tay: đăng nhập AI (không tự làm được thay bạn).'
Write-Host ' - Claude: mở Kuro > Cài đặt > chọn Tài khoản Claude > bấm "Đăng nhập Claude CLI".'
Write-Host ' - Antigravity: mở PowerShell gõ "agy" một lần, đăng nhập Google.'
Write-Host '====================================================================='
