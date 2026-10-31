@echo off
REM Cai Kuro OS mot lan: venv Python 3.13, thu vien, file .env
cd /d "%~dp0"
echo [1/5] Kiem tra Claude Code va Python...
REM Claude Code la phan chay nen mien phi, dung duoc voi moi AI (Claude, OpenRouter, DeepSeek, GLM, Kimi, Ollama)
where /q claude || (echo [LOI] Chua co Claude Code - phan chay nen MIEN PHI, khong can tai khoan Claude. Cai Node.js tu nodejs.org, roi mo PowerShell chay: npm install -g @anthropic-ai/claude-code & pause & exit /b 1)
where /q py || (echo [LOI] Chua co Python. Cai Python 3.13 tu python.org, nho tich "Add python.exe to PATH". & pause & exit /b 1)
REM Kiem tra python.exe chu khong chi thu muc: lan truoc tao do dang thi tao lai
if not exist ".venv\Scripts\python.exe" (
  echo [2/5] Tao moi truong Python...
  if exist ".venv" rmdir /s /q .venv
  py -3.13 -m venv .venv || py -3.12 -m venv .venv || (echo [LOI] Can Python 3.12 hoac 3.13 & pause & exit /b 1)
)
echo [3/5] Cai thu vien (lan dau mat 5-15 phut tuy mang, dung tat cua so)...
.venv\Scripts\python -m pip install --disable-pip-version-check -r requirements.txt -r requirements-ky-thuat.txt || (echo [LOI] pip install that bai. Kiem tra mang roi chay lai setup.bat & pause & exit /b 1)
echo [4/5] Tao file cau hinh...
if not exist ".env" copy env.example .env >nul
echo [5/5] Tao bieu tuong Kuro tren man hinh chinh va menu Start...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tao-loi-tat.ps1"
echo.
echo Xong. Bam dup bieu tuong KURO tren man hinh chinh - lan dau mo, Kuro hien man hinh CHON AI de ban chon.
echo Neu chon "Tai khoan Claude" thi mo PowerShell chay truoc: claude auth login
pause
