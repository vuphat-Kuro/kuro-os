# ============================================================
# KURO OS - phan KuroOS-Setup.exe chay sau khi chep vai tep nho cua no.
#
#   powershell -ExecutionPolicy Bypass -File bootstrap.ps1 [-Dir <thu muc>] [-LogFile <tep>] [-StatusFile <tep>]
#
# Cac buoc: 1 Git (winget, khong co thi bo cai Git for Windows chinh thuc) -> 2 git clone Kuro
# (hoac dung lai ban clone dang co) -> 3 va 4 giao cho cai-dat-tu-dong.ps1 (Python, Node, WebView2,
# CLI AI, .venv, thu vien, .env) -> 5 xong.
#
# Vi sao GIT CLONE chu khong chep tep vao .exe: nut Cap nhat trong app (server/updater.py) cap nhat
# bang git fetch + merge. Chep thang tep thi cai duoc nhung khong bao gio cap nhat; clone thi .exe
# khong bao gio loi thoi vi luon lay ban moi nhat.
#
# KHONG CO CUA SO RIENG: wizard chay tep nay an, doc -StatusFile moi 0,3 giay de hien buoc dang chay.
# Dong dau cua StatusFile: "<so buoc>|<dong chi tiet>", khi xong: "DONE|<ma thoat>|<thong bao>".
# Nen khong cho phep cho ban phim; moi chuong trinh ngoai chay qua Run-Capped (co gioi han thoi gian).
#
# Chi dung ASCII: Windows PowerShell 5.1 doc tep khong BOM bang ma ANSI.
# ============================================================
param(
  [string]$Dir = "C:\Kuro-os\Kuro",
  [string]$Repo = "https://github.com/vuphat-Kuro/kuro-os.git",
  [string]$Branch = "main",
  [string]$LogFile = "",
  [string]$StatusFile = "",
  [switch]$SkipCli,     # khong cai Claude Code CLI / Antigravity CLI
  [switch]$Codex,       # cai them Codex CLI (ChatGPT)
  [switch]$NoIcon,      # khong de cai-dat-tu-dong tao bieu tuong (Inno Setup da tao)
  [switch]$CheckOnly,   # chi kiem tra may, khong cai (thu bo cai)
  [switch]$NoPause
)

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"   # thanh tien do cua PS 5.1 lam tai file cham ~10 lan
try { [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false) } catch { }
$script:Step = 1

function Log($t) {
  Write-Host $t
  if ($LogFile) { try { Add-Content -Path $LogFile -Value ("{0} {1}" -f (Get-Date -Format "HH:mm:ss"), $t) -Encoding UTF8 } catch { } }
}
function Status($detail) {
  if (-not $StatusFile) { return }
  # UTF-8 co BOM de Inno Setup doc dung tieng Viet trong dong chi tiet
  try { [IO.File]::WriteAllText($StatusFile, "$($script:Step)|$detail", (New-Object Text.UTF8Encoding($true))) } catch { }
}
function Step($n, $t) { $script:Step = $n; Status $t; Log "[$n/5] $t" }
function Have($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

function Refresh-Path {
  $m = [Environment]::GetEnvironmentVariable("Path", "Machine")
  $u = [Environment]::GetEnvironmentVariable("Path", "User")
  $env:PATH = (@($m, $u) | Where-Object { $_ }) -join ";"
  foreach ($g in @((Join-Path $env:ProgramFiles "Git\cmd"), (Join-Path $env:LOCALAPPDATA "Programs\Git\cmd"))) {
    if ((Test-Path $g) -and ($env:PATH -notlike "*$g*")) { $env:PATH = "$env:PATH;$g" }
  }
}

# Chay 1 chuong trinh ngoai an, doi DUNG tien trinh do (khong doi tien trinh con de lai), toi da $Minutes.
# Dau ra (stdout + stderr) duoc chuyen vao nhat ky NGAY KHI co (wizard hien o khung log), $OnTick chay moi 2 giay
# voi duong dan tep stdout (de lay dong moi nhat). Tra ve ma thoat; -1 khong chay duoc; -2 het gio.
$script:Pos = @{}
function Flush-Out($f) {
  # doc phan moi them vao ke tu lan truoc, giai ma UTF-8, noi vao nhat ky
  try {
    $fs = New-Object IO.FileStream($f, "Open", "Read", "ReadWrite")
    $from = 0; if ($script:Pos.ContainsKey($f)) { $from = $script:Pos[$f] }
    if ($fs.Length -gt $from) {
      $null = $fs.Seek($from, "Begin")
      $buf = New-Object byte[] ($fs.Length - $from)
      $n = $fs.Read($buf, 0, $buf.Length)
      $script:Pos[$f] = $from + $n
      $txt = [Text.Encoding]::UTF8.GetString($buf, 0, $n)
      # tien do kieu "Updating files: 12%" ghi de nhau bang ky tu CR: chi giu ban cuoi cua moi dong
      $lines = foreach ($l in ($txt -split "`n")) { $l = ($l.TrimEnd("`r") -split "`r")[-1]; if ($l.Trim()) { $l.TrimEnd() } }
      if ($LogFile -and $lines) { Add-Content -Path $LogFile -Value $lines -Encoding UTF8 }
    }
    $fs.Close()
  } catch { }
}
function Run-Capped {
  param([string]$File, [string]$Arguments, [int]$Minutes = 20, [scriptblock]$OnTick = $null)
  $out = [IO.Path]::GetTempFileName(); $err = [IO.Path]::GetTempFileName()
  $code = -1
  try {
    $p = Start-Process -FilePath $File -ArgumentList $Arguments -WindowStyle Hidden -PassThru `
         -RedirectStandardOutput $out -RedirectStandardError $err
    $null = $p.Handle   # PS 5.1 mat ExitCode neu khong doc Handle truoc khi tien trinh thoat
    $limit = (Get-Date).AddMinutes($Minutes)
    while (-not $p.WaitForExit(2000)) {
      Flush-Out $out; Flush-Out $err
      if ($OnTick) { & $OnTick $out }
      if ((Get-Date) -gt $limit) {
        & taskkill.exe /PID $p.Id /T /F 2>&1 | Out-Null
        Log "    [!] Qua $Minutes phut chua xong, da dung: $File"
        $code = -2; break
      }
    }
    if ($code -ne -2) { $code = $p.ExitCode }
  } catch {
    Log "    [!] Khong chay duoc $File ($($_.Exception.Message))"
  }
  Flush-Out $out; Flush-Out $err
  foreach ($f in @($out, $err)) { $script:Pos.Remove($f); Remove-Item $f -Force -ErrorAction SilentlyContinue }
  return $code
}

function Finish($code, $msg) {
  if ($code -eq 0) { Log "Xong." } else { Log "[LOI] $msg" }
  if ($StatusFile) { try { [IO.File]::WriteAllText($StatusFile, "DONE|$code|$msg", (New-Object Text.UTF8Encoding($true))) } catch { } }
  exit $code
}

Log "KURO OS - kiem tra va cai nhung gi may con thieu. Thu muc: $Dir"

# ------------------------------------------------------------ 1. Git
Step 1 "Git"
Refresh-Path
if (-not (Have "git") -and (Have "winget")) {
  Log "    Chua co Git, cai bang winget (1-3 phut). Neu Windows hoi quyen thi bam Yes."
  Run-Capped -File (Get-Command winget).Source -Arguments "install -e --id Git.Git --source winget --silent --accept-source-agreements --accept-package-agreements" | Out-Null
  Refresh-Path
}
if (-not (Have "git")) {
  # May khong co winget: bo cai Git for Windows 64-bit moi nhat, im lang, cai cho rieng nguoi dung (khong can quyen admin)
  try {
    Log "    Tai Git for Windows (khoang 65 MB)..."
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $rel = Invoke-RestMethod -Uri "https://api.github.com/repos/git-for-windows/git/releases/latest" -UseBasicParsing -TimeoutSec 60
    $asset = $rel.assets | Where-Object { $_.name -match "^Git-[0-9.]+-64-bit\.exe$" } | Select-Object -First 1
    if ($asset) {
      $tmp = Join-Path $env:TEMP $asset.name
      Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $tmp -UseBasicParsing
      Run-Capped -File $tmp -Arguments "/VERYSILENT /NORESTART /NOCANCEL /SP- /SUPPRESSMSGBOXES /CURRENTUSER" | Out-Null
      Remove-Item $tmp -Force -ErrorAction SilentlyContinue
      Refresh-Path
    }
  } catch { Log "    [!] Khong tai duoc Git: $($_.Exception.Message)" }
}
if (-not (Have "git")) { Finish 1 "Chua co Git. Cai Git tai https://git-scm.com/download/win roi chay lai KuroOS-Setup.exe." }
Log "    OK $((git --version) 2>&1)"

# ------------------------------------------------------------ 2. ma nguon
Step 2 "Tai Kuro ve may"
if (Test-Path (Join-Path $Dir ".git")) {
  # Chay lai (sua loi, hoac sau buoc hong) khong duoc dong vao ban clone: trong do co ky uc, lich su, .env cua nguoi dung
  Log "    Da co ban Kuro o $Dir, giu nguyen (cap nhat bang nut Cap nhat trong app)"
} else {
  if ((Test-Path $Dir) -and (Get-ChildItem -Force $Dir | Select-Object -First 1)) {
    Finish 1 "Thu muc $Dir da co tep nhung khong phai ban Kuro tai bang git. Doi ten hoac chuyen thu muc do di roi chay lai."
  }
  $parent = Split-Path $Dir -Parent
  try { if ($parent -and -not (Test-Path $parent)) { New-Item -ItemType Directory -Force $parent | Out-Null } }
  catch { Finish 1 "Khong tao duoc thu muc $parent ($($_.Exception.Message)). Chon thu muc khac." }
  # blob:none = du lich su, tai noi dung tep khi can: updater gop va hoan tac tren lich su nay, ban --depth co the tu choi
  $c = Run-Capped -File (Get-Command git).Source -Minutes 30 -Arguments "clone --filter=blob:none --branch $Branch `"$Repo`" `"$Dir`""
  if ($c -ne 0 -or -not (Test-Path (Join-Path $Dir "cai-dat-tu-dong.ps1"))) {
    Log "    Clone nhe that bai (ma $c), thu lai clone day du..."
    if (Test-Path $Dir) { Remove-Item $Dir -Recurse -Force -ErrorAction SilentlyContinue }
    $c = Run-Capped -File (Get-Command git).Source -Minutes 30 -Arguments "clone --branch $Branch `"$Repo`" `"$Dir`""
  }
  if ($c -ne 0 -or -not (Test-Path (Join-Path $Dir "cai-dat-tu-dong.ps1"))) {
    Finish 1 "Khong tai duoc Kuro tu $Repo (kiem tra mang Internet)."
  }
  Log "    Da tai ve $Dir"
}

# ------------------------------------------------------------ 3-4. Python, Node, CLI, .venv, thu vien
Step 3 "Python, Node.js va cac bo nao AI"
$inst = Join-Path $Dir "cai-dat-tu-dong.ps1"
$a = "-NoProfile -ExecutionPolicy Bypass -File `"$inst`""
# Ban Kuro cu (chua co cac co nay) se bao loi tham so, nen chi truyen khi tep co khai bao
$txt = Get-Content $inst -Raw -Encoding UTF8
if ($CheckOnly) { $a += " -ChiKiemTra" }
if ($SkipCli) { if ($txt -match "BoQuaCli") { $a += " -BoQuaCli" } else { Log "    [!] Ban Kuro nay chua ho tro bo qua CLI, se cai nhu binh thuong." } }
if ($Codex) { $a += " -Codex" }
if ($NoIcon -and $txt -match "KhongTaoIcon") { $a += " -KhongTaoIcon" }

# Dong "[2/3] ..." cua cai-dat-tu-dong.ps1 la buoc 4 (thu vien), dong "[3/3] ..." la buoc 5 (bieu tuong)
$tick = {
  param($f)
  try {
    $fs = New-Object IO.FileStream($f, "Open", "Read", "ReadWrite")
    $sr = New-Object IO.StreamReader($fs, [Text.Encoding]::UTF8)
    $lines = $sr.ReadToEnd() -split "`r?`n" | Where-Object { $_.Trim() }
    $sr.Close(); $fs.Close()
    foreach ($l in $lines) { if ($l -match "^\[(\d)/3\]") { $script:Step = [Math]::Min(2 + [int]$Matches[1], 5) } }
    if ($lines) { Status ($lines[-1].Trim()) }
  } catch { }
}
$code = Run-Capped -File (Join-Path $PSHOME "powershell.exe") -Arguments $a -Minutes 120 -OnTick $tick
if ($code -ne 0) { Finish 1 "Buoc cai Python/Node/thu vien bao loi (ma $code). Xem nhat ky de biet thieu gi." }

Step 5 "Hoan tat"
# Giai phong cong 7788 neu chinh ban Kuro nay dang chay (khong dong vao ung dung khac dung cung cong)
if (-not $CheckOnly) {
  try {
    $port = 7788
    $own = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($id in $own) {
      $cl = (Get-CimInstance Win32_Process -Filter "ProcessId=$id" -ErrorAction SilentlyContinue).CommandLine
      if ($cl -and $cl -like "*$Dir*") { Log "    Tat Kuro dang chay (PID $id) de dung cong $port"; Stop-Process -Id $id -Force -ErrorAction SilentlyContinue }
      else { Log "    Cong $port dang do chuong trinh khac dung (PID $id), khong dong vao." }
    }
  } catch { }
}
Finish 0 "OK"
