@echo off
REM Tat Kuro dang chay an (mo bang bieu tuong tren man hinh chinh). Lich su, ky uc, key van giu nguyen.
set "TAT="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r /c:"127.0.0.1:7788 .*LISTENING"') do (
  taskkill /PID %%p /F >nul 2>&1
  set "TAT=1"
)
if defined TAT (echo Da tat Kuro.) else (echo Kuro khong chay.)
