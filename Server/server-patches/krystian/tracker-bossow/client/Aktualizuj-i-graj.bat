@echo off
setlocal
cd /d "%~dp0"
set "M2_HOST_BEFORE="
set "M2_CHANNELS_BEFORE="
if exist "coop.cfg" for /f "tokens=1,* delims==" %%A in (coop.cfg) do (
  if /i "%%A"=="host" set "M2_HOST_BEFORE=%%B"
  if /i "%%A"=="channels" set "M2_CHANNELS_BEFORE=%%B"
)
echo MT2009 Plus - aktualizacja i dodatki
echo Po zakonczeniu aktualizacji zamknij okno oficjalnego patchera bez klikania GRAJ.
echo.

if exist "MT2009-Dodatek.exe" (
  "MT2009-Dodatek.exe" --run-patcher --install
  if errorlevel 1 goto failed
) else (
  if not exist "MT2009-Patcher.exe" goto no_patcher
  start "" /wait "MT2009-Patcher.exe"
  if errorlevel 1 goto failed
)

if defined M2_HOST_BEFORE (
  powershell.exe -NoProfile -Command "$p=Join-Path (Get-Location) 'coop.cfg'; if(-not (Test-Path -LiteralPath $p)){exit 2}; $s=[IO.File]::ReadAllText($p); if($s -notmatch '(?m)^host='){exit 3}; $s=[regex]::Replace($s,'(?m)^host=.*$',('host='+$env:M2_HOST_BEFORE)); $old=0; [void][int]::TryParse($env:M2_CHANNELS_BEFORE,[ref]$old); $m=[regex]::Match($s,'(?m)^channels=([1-4])\s*$'); if($m.Success){$current=[int]$m.Groups[1].Value; if($old -gt $current -and $old -le 4){$s=[regex]::Replace($s,'(?m)^channels=.*$',('channels='+$old))}}; [IO.File]::WriteAllText($p,$s,[Text.Encoding]::ASCII)"
  if errorlevel 1 goto failed
)

if exist "Tracker-Serwer\sprawdz-lokalny-serwer.ps1" (
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "Tracker-Serwer\sprawdz-lokalny-serwer.ps1"
  if errorlevel 1 goto failed
)

if exist "MT2009-Dopalacze.exe" (
  "MT2009-Dopalacze.exe" --install
  if errorlevel 1 goto failed
)

if exist "MT2009-Tracker.exe" (
  "MT2009-Tracker.exe" --install
  if errorlevel 1 goto failed
)

if exist "MT2009-Sklep.exe" (
  "MT2009-Sklep.exe" --client "%CD%" --install
  if errorlevel 1 goto failed
)

if not exist "metin2client.exe" goto no_client
start "" "metin2client.exe"
exit /b 0

:no_patcher
echo Nie znaleziono MT2009-Patcher.exe.
goto failed
:no_client
echo Nie znaleziono metin2client.exe.
:failed
echo.
echo Instalacja przerwana. Gra nie zostala uruchomiona.
pause
exit /b 1
