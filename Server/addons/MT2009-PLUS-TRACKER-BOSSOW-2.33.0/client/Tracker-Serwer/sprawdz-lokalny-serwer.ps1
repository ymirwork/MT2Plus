$ErrorActionPreference = 'Stop'
$config = Join-Path $env:APPDATA 'MT2009-Tracker\server-root.txt'
if (-not (Test-Path -LiteralPath $config)) { exit 0 }

$serverRoot = (Get-Content -LiteralPath $config -Raw -Encoding UTF8).Trim()
$script = Join-Path $PSScriptRoot 'tracker_maintenance.py'
if (-not (Test-Path -LiteralPath (Join-Path $serverRoot 'VERSION'))) {
    Write-Error "Nie znaleziono lokalnego serwera: $serverRoot. Uruchom ponownie Ustaw-serwer-PC.bat."
    exit 1
}
if (-not (Test-Path -LiteralPath $script)) {
    Write-Error 'Brakuje plikow Tracker-Serwer obok Aktualizuj-i-graj.bat.'
    exit 1
}

$launcher = Get-Command py -ErrorAction SilentlyContinue
if ($launcher) {
    & $launcher.Source -3 $script --server-root $serverRoot --repair
} else {
    $launcher = Get-Command python -ErrorAction SilentlyContinue
    if (-not $launcher) {
        Write-Error 'Brakuje Python 3. Zainstaluj go jednorazowo i ponow probe.'
        exit 1
    }
    & $launcher.Source $script --server-root $serverRoot --repair
}
exit $LASTEXITCODE
