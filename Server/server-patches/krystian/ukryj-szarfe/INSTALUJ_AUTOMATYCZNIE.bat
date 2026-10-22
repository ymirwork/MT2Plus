@echo off
title Instalator Modyfikacji: Ukryj Szarfe (MT2Plus)
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo     Instalator Modyfikacji: Ukryj Szarfe
echo     (Ukrywanie szarfy w oknie Kostiumow)
echo ========================================================
echo.

echo [1/3] Aplikowanie zmian w zrodlach serwera C++...
python serwer_cpp\apply_hide_sash_server.py
if errorlevel 1 (
    echo [BLAD] Nie udalo sie zaaplikowac zmian w kodzie serwera.
    pause
    exit /b 1
)

echo.
echo [2/3] Kopiowanie zaktualizowanych plikow klienta...
copy /y "klient_pliki\root\uicostumehide.py" "..\..\..\..\Klient\pack\root\uicostumehide.py" >nul
copy /y "klient_pliki\root\uiinventory.py" "..\..\..\..\Klient\pack\root\uiinventory.py" >nul
if exist "..\..\..\..\Klient\client-patches\client-2.0.30\root\" (
    copy /y "klient_pliki\root\uicostumehide.py" "..\..\..\..\Klient\client-patches\client-2.0.30\root\uicostumehide.py" >nul
    copy /y "klient_pliki\root\uiinventory.py" "..\..\..\..\Klient\client-patches\client-2.0.30\root\uiinventory.py" >nul
)

echo.
echo [3/3] Pakowanie paczki 'root' klienta...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "..\..\..\..\Klient\Compile-ClientPack.ps1" -PackName "root" -Action "pack"

echo.
echo ========================================================
echo   Instalacja zakonczona sukcesem!
echo   Pamietaj o przebudowaniu kontenera game (docker compose build game)
echo   lub restarcie serwera.
echo ========================================================
pause
