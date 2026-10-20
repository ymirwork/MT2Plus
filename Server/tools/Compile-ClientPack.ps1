<#
.SYNOPSIS
    Kompilator / paker paczek klienta Metin2 EterPack (.data / .index).
.DESCRIPTION
    Skrypt pakuje, rozpakowuje, weryfikuje oraz synchronizuje paczki klienta
    wykorzystując silnik PackMakerLite-RS i konfigurację PackMakerLite.json.
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$PackName = 'root',

    [Parameter(Position = 1)]
    [ValidateSet('pack', 'unpack', 'watch', 'verify', 'info', 'pack-all', 'sync')]
    [string]$Action = 'pack',

    [string]$ClientDir = '',

    [switch]$NoBackup,
    [switch]$NoSync
)

$ErrorActionPreference = 'Stop'

# Wyznaczenie ścieżki do folderu Klient
if (-not $ClientDir) {
    if (Test-Path (Join-Path $PSScriptRoot 'pack')) {
        $ClientDir = $PSScriptRoot
    } elseif (Test-Path (Join-Path $PSScriptRoot 'Klient\pack')) {
        $ClientDir = Join-Path $PSScriptRoot 'Klient'
    } else {
        $ClientDir = 'd:\MT2\Metin2 Singleplayer Plus\Klient'
    }
}

$packDir = Join-Path $ClientDir 'pack'
if (-not (Test-Path $packDir)) {
    throw "Nie znaleziono folderu pack w: $ClientDir"
}

# Wyszukanie packmakerlite-cli.exe
$cliCandidates = @(
    "D:\MT2\Edycja\PackMakerLite-RS\packmakerlite-cli.exe",
    (Join-Path $packDir "packmakerlite-cli.exe"),
    (Join-Path $ClientDir "packmakerlite-cli.exe")
)
$pmlCmd = Get-Command "packmakerlite-cli.exe" -ErrorAction SilentlyContinue
if ($pmlCmd) { $cliCandidates += $pmlCmd.Source }

$cliPath = $null
foreach ($cand in $cliCandidates) {
    if ($cand -and (Test-Path -LiteralPath $cand -PathType Leaf)) {
        $cliPath = $cand
        break
    }
}

if (-not $cliPath) {
    throw "Nie znaleziono packmakerlite-cli.exe. Upewnij sie, ze narzedzie znajduje sie w D:\MT2\Edycja\PackMakerLite-RS lub w zmiennej PATH."
}

Write-Host "Uzywam silnika: $cliPath" -ForegroundColor DarkCyan
Write-Host "Folder pack: $packDir" -ForegroundColor DarkCyan

function Assert-CustomPatches([string]$Name, [string]$Folder) {
    if ($Name -eq 'root') {
        $huntPy = Join-Path $Folder "uiautohunt.py"
        if (Test-Path $huntPy) {
            $hasFish = Select-String -Path $huntPy -Pattern "AutoFishWindow" -Quiet
            if (-not $hasFish) {
                Write-Host ("[GUARD] Wykryto brak AutoFishWindow w " + $huntPy + "! Przywracam z server-patches...") -ForegroundColor Yellow
                $repoRoot = "d:\Github\MT2Plus"
                $patchFish = Join-Path $repoRoot "Server\server-patches\krystian\autofish\client\root\uiautohunt.py"
                if (Test-Path $patchFish) {
                    Copy-Item $patchFish $huntPy -Force
                    Write-Host "[GUARD] Pomyslnie przywrocono Auto-Wedkowanie do uiautohunt.py!" -ForegroundColor Green
                } else {
                    Write-Warning ("Nie znaleziono pliku wzorca: " + $patchFish)
                }
            }
        }

        $gamePy = Join-Path $Folder "game.py"
        if (Test-Path $gamePy) {
            $hasFish = Select-String -Path $gamePy -Pattern "AutoFishStatus" -Quiet
            if (-not $hasFish) {
                Write-Host ("[GUARD] Wykryto brak AutoFishStatus w " + $gamePy + "! Przywracam z server-patches...") -ForegroundColor Yellow
                $repoRoot = "d:\Github\MT2Plus"
                $patchGame = Join-Path $repoRoot "Server\server-patches\krystian\autofish\client\root\game.py"
                if (Test-Path $patchGame) {
                    Copy-Item $patchGame $gamePy -Force
                    Write-Host "[GUARD] Pomyslnie przywrocono game.py!" -ForegroundColor Green
                }
            }
        }
    }
}

function Backup-Pack([string]$Name) {
    $dataFile = Join-Path $packDir "$Name.data"
    $idxFile = Join-Path $packDir "$Name.index"
    if (Test-Path $dataFile) {
        Copy-Item $dataFile (Join-Path $packDir "$Name.data.bak") -Force
    }
    if (Test-Path $idxFile) {
        Copy-Item $idxFile (Join-Path $packDir "$Name.index.bak") -Force
    }
}

function Sync-PacksToPeer([string]$Name) {
    $devPack = "d:\Github\MT2Plus\Klient\pack"
    $prodPack = "d:\MT2\Metin2 Singleplayer Plus\Klient\pack"
    
    $isDev = $packDir.StartsWith("d:\Github\MT2Plus", [StringComparison]::OrdinalIgnoreCase)
    $source = if ($isDev) { $devPack } else { $prodPack }
    $target = if ($isDev) { $prodPack } else { $devPack }

    if (-not (Test-Path $target)) { return }

    if ($Name -eq 'all') {
        Get-ChildItem -Path $source -Filter "*.data" | ForEach-Object {
            $base = [IO.Path]::GetFileNameWithoutExtension($_.Name)
            Copy-Item $_.FullName (Join-Path $target "$base.data") -Force
            $idx = Join-Path $source "$base.index"
            if (Test-Path $idx) { Copy-Item $idx (Join-Path $target "$base.index") -Force }
        }
        Write-Host "Zsynchronizowano wszystkie paczki miedzy Dev a Oficjalnym klientem." -ForegroundColor Green
    } else {
        $srcData = Join-Path $source "$Name.data"
        $srcIdx = Join-Path $source "$Name.index"
        if (Test-Path $srcData) {
            Copy-Item $srcData (Join-Path $target "$Name.data") -Force
            Copy-Item $srcIdx (Join-Path $target "$Name.index") -Force
            Write-Host "Zsynchronizowano paczke $Name do drugiego srodowiska." -ForegroundColor Green
        }
    }
}

switch ($Action.ToLower()) {
    'pack' {
        $targetFolder = Join-Path $packDir $PackName
        if (-not (Test-Path $targetFolder -PathType Container)) {
            throw "Folder do spakowania nie istnieje: $targetFolder"
        }
        Assert-CustomPatches $PackName $targetFolder
        if (-not $NoBackup) {
            Backup-Pack $PackName
        }
        Write-Host "Pakowanie folderu '$PackName'..." -ForegroundColor Yellow
        Push-Location $packDir
        try {
            & $cliPath --pack $PackName
            if ($LASTEXITCODE -ne 0) { throw "Blad pakowania (kod $LASTEXITCODE)" }
            Write-Host "Paczka '$PackName' zostala pomyslnie skompilowana!" -ForegroundColor Green
            & $cliPath --verify $PackName
            if (-not $NoSync) { Sync-PacksToPeer $PackName }
        }
        finally { Pop-Location }
    }

    'unpack' {
        Write-Host "Rozpakowywanie '$PackName'..." -ForegroundColor Yellow
        Push-Location $packDir
        try {
            & $cliPath --unpack $PackName
            if ($LASTEXITCODE -ne 0) { throw "Blad rozpakowywania (kod $LASTEXITCODE)" }
            Write-Host "Rozpakowano '$PackName' do folderu!" -ForegroundColor Green
        }
        finally { Pop-Location }
    }

    'watch' {
        Write-Host "Tryb Watch aktywny dla '$PackName'. Zmiany w plikach beda automatycznie kompilowane." -ForegroundColor Cyan
        Write-Host "Wcisnij Ctrl+C, aby przerwac." -ForegroundColor DarkGray
        Push-Location $packDir
        try {
            & $cliPath --watch $PackName
        }
        finally { Pop-Location }
    }

    'verify' {
        Push-Location $packDir
        try {
            & $cliPath --verify $PackName
        }
        finally { Pop-Location }
    }

    'info' {
        Push-Location $packDir
        try {
            & $cliPath --info $PackName
        }
        finally { Pop-Location }
    }

    'pack-all' {
        $dirs = Get-ChildItem -Path $packDir -Directory | Where-Object {
            Test-Path (Join-Path $packDir "$($_.Name).data")
        }
        if ($dirs.Count -eq 0) {
            Write-Host "Brak rozpakowanych folderow z istniejacymi paczkami." -ForegroundColor Yellow
            return
        }
        Push-Location $packDir
        try {
            foreach ($d in $dirs) {
                Assert-CustomPatches $d.Name $d.FullName
                Write-Host "`nPakowanie '$($d.Name)'..." -ForegroundColor Yellow
                if (-not $NoBackup) { Backup-Pack $d.Name }
                & $cliPath --pack $d.Name
                & $cliPath --verify $d.Name
                if (-not $NoSync) { Sync-PacksToPeer $d.Name }
            }
            Write-Host "`nWszystkie paczki skompilowane pomyslnie!" -ForegroundColor Green
        }
        finally { Pop-Location }
    }

    'sync' {
        Sync-PacksToPeer $PackName
    }
}
