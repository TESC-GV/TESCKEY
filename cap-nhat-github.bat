@echo off
chcp 65001 >nul
echo === Dua bo cong cu len https://github.com/TESC-GV/TESCKEY ===
where git >nul 2>&1
if errorlevel 1 (
  echo Dang cai Git, vui long cho...
  winget install --id Git.Git -e --silent --accept-package-agreements --accept-source-agreements
  echo Da cai Git. HAY DONG cua so nay va bam dup lai file nay.
  pause
  exit /b
)
echo.
echo Xoa dang nhap GitHub cu da luu tren may (neu co)...
cmdkey /delete:git:https://github.com >nul 2>&1
if exist .git rmdir /s /q .git
git init
git config user.name "TESC-GV"
git config user.email "TESC-GV@users.noreply.github.com"
git add -A
git commit -m "Bo go Viet"
git branch -M main
git remote add origin https://github.com/TESC-GV/TESCKEY.git
echo.
echo SAP HIEN CUA SO DANG NHAP GITHUB: hay dang nhap bang tai khoan TESC-GV.
git push -u origin main --force
echo.
echo BUOC CUOI (chi 1 lan): mo https://github.com/TESC-GV/TESCKEY/settings/pages
echo   chon Branch main, thu muc /docs, bam Save.
echo Roi vao https://github.com/TESC-GV/TESCKEY/actions cho "Build installer" co dau tich xanh.
echo Trang tai ve: https://tesc-gv.github.io/TESCKEY/tai-ve.html
pause
