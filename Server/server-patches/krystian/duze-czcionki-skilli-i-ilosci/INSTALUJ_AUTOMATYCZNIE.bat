@echo off
chcp 65001 >nul
echo ========================================================
echo   Instalacja Duzych Czcionek Skilli i Ilosci Przedmiotow
echo ========================================================

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%..\..\..\"

echo [1/2] Kopiowanie plikow do Klient\pack\etc...
xcopy /E /Y /I "%SCRIPT_DIR%klient_pliki\etc\*" "%ROOT_DIR%Klient\pack\etc\" >nul
if errorlevel 1 (
    echo Blad podczas kopiowania plikow!
    pause
    exit /b 1
)

echo [2/2] Pakowanie paczki etc...
powershell -ExecutionPolicy Bypass -File "%ROOT_DIR%Klient\Compile-ClientPack.ps1" etc pack
if errorlevel 1 (
    echo Blad podczas pakowania paczki etc!
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   Gotowe! Duze czcionki zostaly pomyslnie zainstalowane.
echo ========================================================
pause
