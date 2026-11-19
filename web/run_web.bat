@echo off
cd /d "%~dp0"
echo Starting Mini Salon Web (http://localhost:3000)...
npm run dev
if errorlevel 1 pause
