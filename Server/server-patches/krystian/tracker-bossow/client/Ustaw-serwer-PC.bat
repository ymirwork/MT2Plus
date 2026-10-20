@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Tracker-Serwer\Ustaw-serwer-PC.ps1"
echo.
pause
