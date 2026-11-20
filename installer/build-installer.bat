@echo off
REM Build bo cai KuroOS-Setup.exe bang Inno Setup 6 (cai: winget install JRSoftware.InnoSetup).
REM Ket qua: installer\Output\KuroOS-Setup.exe. So phien ban lay tu tep VERSION.
cd /d "%~dp0"
set "ISCC="
for %%P in ("%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" "%ProgramFiles%\Inno Setup 6\ISCC.exe" "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe") do if exist %%P set "ISCC=%%~P"
if not defined ISCC (
  echo [LOI] Chua co Inno Setup 6. Cai: winget install -e --id JRSoftware.InnoSetup
  exit /b 1
)
set /p VER=<"%~dp0..\VERSION"
"%ISCC%" /Qp /DAppVer=%VER% KuroOS-Setup.iss
if errorlevel 1 (echo [LOI] Build that bai & exit /b 1)
echo.
echo Xong: %~dp0Output\KuroOS-Setup.exe  (phien ban %VER%)
