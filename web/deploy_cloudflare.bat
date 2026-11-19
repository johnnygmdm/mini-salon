@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ========================================================
echo  Mini Salon Web - Cloudflare Pages 배포 마법사
echo ========================================================
echo.
echo 1. 최신 프로덕션 빌드 (Static Export)를 생성합니다...
call npm run build
if errorlevel 1 (
    echo 빌드 실패. 오류를 확인하세요.
    pause
    exit /b 1
)

echo.
echo 2. Cloudflare Pages로 직접 업로드 배포를 시작합니다...
echo (처음 실행 시 Cloudflare 계정 로그인 창이 뜹니다.)
echo.
call npx wrangler pages deploy out --project-name=mini-salon
if errorlevel 1 pause
