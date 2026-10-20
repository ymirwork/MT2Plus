@echo off
title Instalator Recyklingu Bonusow Dozorcy
chcp 65001 >nul
echo ========================================================
echo   Instalacja modyfikacji: Recykling Bonusow u Dozorcy
echo ========================================================
echo.

set "TARGET_DIR=%~dp0"
if not exist "%TARGET_DIR%Klient" (
    if exist "%TARGET_DIR%..\Klient" (
        set "TARGET_DIR=%~dp0..\"
    )
)

if not exist "%TARGET_DIR%Klient" (
    echo [BLAD] Nie znaleziono folderu Klient!
    echo Umiesc ten instalator bezposrednio w folderze gry z katalogami Klient i Server.
    pause
    exit /b 1
)

echo [1/3] Kopiowanie plikow klienta...
copy /y "%~dp0Klient\pack\root.data" "%TARGET_DIR%Klient\pack\root.data" >nul
copy /y "%~dp0Klient\pack\root.index" "%TARGET_DIR%Klient\pack\root.index" >nul

echo [2/3] Kopiowanie plikow serwera...
xcopy /y /e /i "%~dp0Server" "%TARGET_DIR%Server" >nul

echo [3/3] Aktualizacja kontenera gry (jesli Docker jest uruchomiony)...
set "CONTAINER_ID="
for /f "tokens=*" %%i in ('docker ps -q -f "name=-game" 2^>nul') do set CONTAINER_ID=%%i

if defined CONTAINER_ID (
    echo Wykryto uruchomiony kontener gry: %CONTAINER_ID%
    docker cp "%TARGET_DIR%Server\linux-port\docker\game\src\serverfiles\share\locale\poland\quest\libs\crafting\item_exchange.lua" %CONTAINER_ID%:/opt/metin2/share/locale/poland/quest/libs/crafting/item_exchange.lua >nul 2>&1
    docker cp "%TARGET_DIR%Server\linux-port\docker\game\src\serverfiles\share\locale\poland\quest\object\9005\chat\." %CONTAINER_ID%:/opt/metin2/share/locale/poland/quest/object/9005/chat/ >nul 2>&1
    docker cp "%TARGET_DIR%Server\linux-port\docker\game\src\serverfiles\share\locale\poland\quest\object\state\recykling_bonusow" %CONTAINER_ID%:/opt/metin2/share/locale/poland/quest/object/state/recykling_bonusow >nul 2>&1
    echo Restartowanie procesow serwera...
    docker restart %CONTAINER_ID% >nul 2>&1
    echo Serwer zostal zaktualizowany i zrestartowany!
) else (
    echo Docker nie jest uruchomiony lub serwer jest zatrzymany.
    echo Pliki zostaly skopiowane. Uruchom serwer normalnie przez start.bat.
)

echo.
echo ========================================================
echo   Instalacja zakonczona sukcesem!
echo ========================================================
pause
