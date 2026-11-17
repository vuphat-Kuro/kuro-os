@echo off
REM Cai dien hoa cho Kuro: ComfyUI + RealVisXL + ControlNet Union SDXL. Can card NVIDIA tu 8 GB VRAM, tai khoang 11,5 GB.
REM Chay lai bao nhieu lan cung duoc: phan da co thi bo qua, dut mang thi tai tiep.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo [LOI] Chua cai Kuro. Bam dup setup.bat truoc. & pause & exit /b 1)
.venv\Scripts\python -X utf8 tools\cai_dien_hoa.py
echo.
pause
