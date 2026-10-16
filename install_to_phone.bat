@echo off
chcp 65001 >nul
echo ============================================================
echo   CAI DAT UNG DUNG VINUNI AI THUC CHIEN VAO DIEN THOAI
echo ============================================================
echo.
set ADB="C:\Users\thanh\AppData\Local\Android\Sdk\platform-tools\adb.exe"

echo [1/3] Kiem tra ket noi thiet bi ADB...
%ADB% devices

echo.
echo [2/3] Dang cai dat VinUniAIThucChien.apk vao dien thoai...
%ADB% install -r "D:\proj\VinUniAIThucChien.apk"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] CHU Y: Neu thong bao "device unauthorized", hay mo khoa dien thoai
    echo     va bam vao hop thoai "Cho phep go loi USB" (Allow USB debugging),
    echo     sau do chay lai file nay.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Dang khoi chay ung dung tren man hinh dien thoai...
%ADB% shell am start -n edu.vinuni.aithucchien/.MainActivity

echo.
echo [V] THIET LAP REVERSE PORT CHO PWA (http://localhost:8000)...
%ADB% reverse tcp:8000 tcp:8000

echo.
echo ============================================================
echo   THANH CONG! UNG DUNG DA DUOC MO TREN DIEN THOAI CUA BAN.
echo ============================================================
pause
