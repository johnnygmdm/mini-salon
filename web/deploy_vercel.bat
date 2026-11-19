@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ========================================================
echo  Mini Salon Web - Vercel Cloud Free Deploy Wizard
echo ========================================================
echo.
echo Vercel 클라우드로 배포를 시작합니다...
echo (처음 실행 시 브라우저에서 로그인 확인 창이 나타납니다.)
echo.
npx vercel
if errorlevel 1 pause
