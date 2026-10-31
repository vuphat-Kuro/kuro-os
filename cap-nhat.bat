@echo off
REM Cap nhat Kuro len ban moi nhat tren GitHub. Khong dong toi .env, state\, brains\ (key, lich su, ky uc).
REM Ca than script nam trong MOT khoi ngoac: cmd doc het khoi truoc khi chay, nen git pull thay chinh file
REM nay giua chung cung khong lam cmd doc nham dong.
cd /d "%~dp0"
(
  echo [1/4] Tat Kuro dang chay...
  call "%~dp0tat-kuro.bat"
  echo [2/4] Tai ban moi...
  git pull --ff-only || (echo [LOI] Khong cap nhat duoc. Neu ban da tu sua file ma nguon, hay hoi nguoi quan ly Kuro. & pause & exit /b 1)
  echo [3/4] Cap nhat thu vien...
  .venv\Scripts\python -m pip install --disable-pip-version-check -r requirements.txt -r requirements-ky-thuat.txt || (echo [LOI] pip install that bai & pause & exit /b 1)
  echo [4/4] Lam moi bieu tuong tren man hinh chinh...
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tao-loi-tat.ps1"
  echo.
  echo Xong. Dang mo lai Kuro...
  start "" wscript "%~dp0kuro.vbs"
  timeout /t 3 >nul
  exit /b 0
)
