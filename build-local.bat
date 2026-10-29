@echo off
chcp 65001 >nul
echo === Tu dung BoGoViet.exe tren may (khong can GitHub) ===
where python >nul 2>&1
if errorlevel 1 (
  echo Chua co Python. Dang cai Python...
  winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements
  echo Da cai Python. HAY DONG cua so nay va bam dup lai file nay.
  pause
  exit /b
)
python -m pip install --upgrade pip pyinstaller pystray pillow
python -m PyInstaller --onefile --noconsole --name BoGoViet --hidden-import pystray._win32 --paths bogo-viet bogo-viet/bogo.py
echo.
echo XONG. File chay: dist\BoGoViet.exe  (chep di dau cung duoc, bam dup la chay)
pause
