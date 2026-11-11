@echo off
cd /d "%~dp0"
MT2009-Tracker.exe --install
if errorlevel 1 pause
