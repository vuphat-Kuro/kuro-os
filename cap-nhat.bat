@echo off
REM Cap nhat Kuro len ban moi nhat tren GitHub. Khong dong toi .env, state\, brains\ (key, lich su, ky uc).
cd /d "%~dp0"
git pull --ff-only || (echo [LOI] Khong cap nhat duoc. Neu ban da tu sua file ma nguon, hay hoi nguoi quan ly Kuro. & pause & exit /b 1)
.venv\Scripts\python -m pip install --disable-pip-version-check -r requirements.txt -r requirements-ky-thuat.txt || (echo [LOI] pip install that bai & pause & exit /b 1)
echo.
echo Xong. Tat cua so Kuro dang chay roi bam dup run.bat. Skill moi tu vao brain khi Kuro khoi dong.
pause
