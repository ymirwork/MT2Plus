param([string]$ServerRoot)
$ErrorActionPreference = 'Stop'
if (-not $ServerRoot) { $ServerRoot = Read-Host 'Podaj glowny folder lokalnego serwera MT2009 Plus' }
$ServerRoot = $ServerRoot.Trim().Trim([char[]]@([char]34, [char]39))
$root = (Resolve-Path -LiteralPath $ServerRoot -ErrorAction Stop).Path
if (-not (Test-Path -LiteralPath (Join-Path $root 'VERSION')) -or
    -not (Test-Path -LiteralPath (Join-Path $root 'linux-port\docker'))) {
    Write-Error 'Wybrano zly folder. Wskaz folder z VERSION oraz linux-port\docker.'
    exit 1
}
$dir = Join-Path $env:APPDATA 'MT2009-Tracker'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
[IO.File]::WriteAllText((Join-Path $dir 'server-root.txt'), $root, [Text.Encoding]::UTF8)
Write-Host "Lokalny serwer ustawiony: $root"
Write-Host 'Od teraz Aktualizuj-i-graj.bat sprawdzi tracker przed startem gry.'
