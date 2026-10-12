@echo off
chcp 65001 >nul
title [Community Mod] Wstawanie ze 100%% HP po smierci - Instalator

echo ===============================================================================
echo     INSTALATOR MODYFIKACJI METIN2: WSTAWANIE ZE 100%% HP PO SMIERCI
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

:: 2. Detekcja sciezki serwera
set "SERVER_DIR="
if exist "..\..\linux-port" set "SERVER_DIR=..\.."
if not defined SERVER_DIR if exist "..\linux-port" set "SERVER_DIR=.."
if not defined SERVER_DIR if exist "Server\linux-port" set "SERVER_DIR=Server"

if not defined SERVER_DIR (
    echo [?] Podaj pelna sciezke do katalogu Server/ (np. D:\MT2Plus\Server):
    set /p "SERVER_DIR=> "
)

echo [*] Wykryto katalog serwera: %SERVER_DIR%
echo.

:: 3. Aplikacja patcha C++
echo [1/2] Aplikowanie zmian w kodzie C++ serwera (cmd_general.cpp, char.cpp)...
"%PYTHON_EXE%" "serwer_cpp\apply_revive_100_hp_server.py" --server-dir "%SERVER_DIR%"
if errorlevel 1 (
    echo [BLAD] Nie udalo sie zaaplikowac zmian w kodzie C++!
    pause
    exit /b 1
)

echo.
echo [2/2] Rekompilacja kontenera Docker 'game'...
set /p "DOCKER_BUILD=Czy chcesz przebudowac kontener gry w Dockerze teraz? (T/N): "
if /i "%DOCKER_BUILD%"=="T" (
    docker compose --project-directory "%SERVER_DIR%\linux-port\docker" build game
    echo.
    echo [*] Zrestartuj usluge poleceniem:
    echo     docker compose --project-directory "%SERVER_DIR%\linux-port\docker" restart game
)

echo.
echo ===============================================================================
echo [SUKCES] Modyfikacja zostala pomyslnie zainstalowana!
echo ===============================================================================
pause
