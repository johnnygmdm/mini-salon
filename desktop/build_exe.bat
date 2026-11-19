@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ========================================================
echo  Mini Salon Desktop - PyInstaller .exe 단일 파일 빌드
echo ========================================================
echo.
echo 빌드를 시작합니다. 잠시만 기다려주세요...
pyinstaller --noconsole --onefile --clean --name="MiniSalon" main.py
if errorlevel 1 (
    echo 빌드 중 오류가 발생했습니다.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo  [빌드 성공!] dist\MiniSalon.exe 파일이 생성되었습니다.
echo ========================================================
pause
