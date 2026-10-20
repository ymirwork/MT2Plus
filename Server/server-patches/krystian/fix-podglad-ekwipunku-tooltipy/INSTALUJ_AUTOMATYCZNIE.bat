@echo off
chcp 65001 >nul
title Fix Podglądu Ekwipunku - Panel Seban (MT2009 / MT2Plus)
cls
echo ======================================================================
echo    FIX PODGLĄDU EKWIPUNKU I DYMKÓW PRZEDMIOTÓW (SEBAN PANEL)
echo    Autor: Krystian | MT2Plus Community Fix
echo ======================================================================
echo.

set SCRIPT_DIR=%~dp0
set STATIC_SRC=%SCRIPT_DIR%pliki_panelu\static\player-profile.css
set TEMPLATE_SRC=%SCRIPT_DIR%pliki_panelu\templates\player.html

if not exist "%STATIC_SRC%" (
    echo [BLAD] Brak pliku: %STATIC_SRC%
    pause
    exit /b 1
)

echo [1/3] Sprawdzanie srodowiska Docker...
docker ps -q -f name=seban-panel >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Znaleziono kontener Docker Seban Panel.
    for /f "tokens=*" %%i in ('docker ps --filter "name=seban-panel" --format "{{.Names}}"') do set CONTAINER_NAME=%%i
    echo Kopiowanie plikow do kontenera: %CONTAINER_NAME%...
    docker cp "%STATIC_SRC%" %CONTAINER_NAME%:/app/static/player-profile.css
    docker cp "%TEMPLATE_SRC%" %CONTAINER_NAME%:/app/templates/player.html
    echo Restartowanie kontenera %CONTAINER_NAME%...
    docker restart %CONTAINER_NAME% >nul
    echo [OK] Kontener zaktualizowany i zrestartowany pomyslnie!
    goto DONE
)

echo [2/3] Nie wykryto dzialajacego kontenera Docker. Sprawdzam sciezke lokalna...
set LOCAL_PANEL_DIR=%SCRIPT_DIR%..\..\linux-port\docker\seban-panel
if exist "%LOCAL_PANEL_DIR%\static" (
    echo Kopiowanie do lokalnego folderu repozytorium...
    copy /Y "%STATIC_SRC%" "%LOCAL_PANEL_DIR%\static\player-profile.css" >nul
    copy /Y "%TEMPLATE_SRC%" "%LOCAL_PANEL_DIR%\templates\player.html" >nul
    echo [OK] Skopiowano do: %LOCAL_PANEL_DIR%
    goto DONE
)

echo [UWAGA] Nie wykryto automatycznej sciezki. Skopiuj recznie:
echo   - pliki_panelu\static\player-profile.css -> twoj_panel/static/
echo   - pliki_panelu\templates\player.html -> twoj_panel/templates/

:DONE
echo.
echo ======================================================================
echo    GOTOWE! W przegladarce odswiez strone z uzyciem [Ctrl + F5].
echo ======================================================================
pause
