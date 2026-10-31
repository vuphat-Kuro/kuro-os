@echo off
REM Cai Kuro OS mot lan: venv Python 3.13, thu vien, file .env
cd /d "%~dp0"
echo [1/4] Kiem tra Claude Code va Python...
where /q claude || (echo [LOI] Chua co Claude Code. Mo PowerShell, chay: npm install -g @anthropic-ai/claude-code & pause & exit /b 1)
where /q py || (echo [LOI] Chua co Python. Cai Python 3.13 tu python.org, nho tich "Add python.exe to PATH". & pause & exit /b 1)
REM Kiem tra python.exe chu khong chi thu muc: lan truoc tao do dang thi tao lai
if not exist ".venv\Scripts\python.exe" (
  echo [2/4] Tao moi truong Python...
  if exist ".venv" rmdir /s /q .venv
  py -3.13 -m venv .venv || py -3.12 -m venv .venv || (echo [LOI] Can Python 3.12 hoac 3.13 & pause & exit /b 1)
)
echo [3/4] Cai thu vien (lan dau mat 5-15 phut tuy mang, dung tat cua so)...
.venv\Scripts\python -m pip install --disable-pip-version-check -r requirements.txt -r requirements-ky-thuat.txt || (echo [LOI] pip install that bai. Kiem tra mang roi chay lai setup.bat & pause & exit /b 1)
echo [4/4] Tao file cau hinh...
if not exist ".env" copy env.example .env >nul
echo.
echo Xong. Neu chua dang nhap Claude thi mo PowerShell chay: claude auth login
echo Chay Kuro: bam dup run.bat
pause
