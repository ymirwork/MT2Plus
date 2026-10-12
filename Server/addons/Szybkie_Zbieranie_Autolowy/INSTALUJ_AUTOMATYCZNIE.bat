@echo off
chcp 65001 >nul
title [Community Mod] Szybkie Zbieranie Dropu w Autolowach + Fix - Instalator

echo ===============================================================================
echo     INSTALATOR MODYFIKACJI METIN2: SZYBKIE ZBIERANIE W AUTOLOWACH + FIX
echo ===============================================================================
echo.

:: 1. Detekcja Pythona
set "PYTHON_EXE="
if exist "..\..\tools\python-embed\python.exe" set "PYTHON_EXE=..\..\tools\python-embed\python.exe"
if not defined PYTHON_EXE if exist "..\tools\python-embed\python.exe" set "PYTHON_EXE=..\tools\python-embed\python.exe"
if not defined PYTHON_EXE (
    python --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_EXE=python"
)

if not defined PYTHON_EXE (
    echo [BLAD] Nie znaleziono srodowiska Python!
    echo Zainstaluj Python 3 i dodaj go do zmiennej PATH.
    pause
    exit /b 1
)

:: 2. Detekcja katalogu klienta
set "CLIENT_DIR="
if exist "..\..\Klient\pack\root.data" set "CLIENT_DIR=..\..\Klient"
if not defined CLIENT_DIR if exist "..\Klient\pack\root.data" set "CLIENT_DIR=..\Klient"
if not defined CLIENT_DIR if exist "Klient\pack\root.data" set "CLIENT_DIR=Klient"

if not defined CLIENT_DIR (
    echo [?] Podaj pelna sciezke do katalogu Klient (np. D:\MT2Plus\Klient):
    set /p "CLIENT_DIR=> "
)

echo [*] Wykryto katalog klienta: %CLIENT_DIR%
echo.

:: 3. Aplikacja modyfikacji klienta
echo [1/1] Aplikowanie zmian w skryptach Autołowów i rekompilacja paczki root...
"%PYTHON_EXE%" "klient_pliki\apply_autohunt_fastpickup_fix_client.py" --client-dir "%CLIENT_DIR%"
if errorlevel 1 (
    echo [BLAD] Wystapil blad podczas modyfikacji klienta!
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo [SUKCES] Modyfikacja zostala pomyslnie zaaplikowana!
echo Zrestartuj klienta gry, aby uruchomic zaktualizowane Autolowy.
echo ===============================================================================
pause
