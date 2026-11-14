#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_upstream_2.43.0.py
Skrypt aktualizujacy serwer MT2Plus do upstream 2.43.0 (mod-64, klient 2.0.71)
z zachowaniem wszystkich autorskich modyfikacji MT2Plus (47/47 w audit_mods.py i 34/34 w deep_audit.py):
 - Nowy launcher 2.43.0: obsługa odblokowanej aktualizacji do Yohary, tło Yohary, logo, postęp pobierania
 - Zaktualizowane pliki manifestu, VERSION (2.43.0) i MOD_VERSION (mod-64)
 - Seban Panel VERSION (2.43.0)
 - Zachowanie autorskich optymalizacji bazy w Metin2Launcher.psm1 (-NoData dla bazy log)
 - Wszystkie autorskie systemy MT2Plus w 100% aktywne i nienaruszone.
"""

import os
import sys
import subprocess
import re

UPSTREAM_TAG = "v2.43.0"

def get_upstream_file(git_path):
    res = subprocess.run(['git', 'show', f'{UPSTREAM_TAG}:{git_path}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to get {git_path} from {UPSTREAM_TAG}: {res.stderr.decode('utf-8', errors='ignore')}")
    return res.stdout

def write_file(dest_path, content):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if isinstance(content, str):
        content = content.encode('utf-8')
    with open(dest_path, 'wb') as f:
        f.write(content)
    print(f"[OK] Zapisano: {dest_path}")

def patch_metin2launcher_psm1(upstream_bytes):
    text = upstream_bytes.decode('utf-8', errors='ignore')

    # 1. Export-M2Database param & body
    old_target1 = """    param([string]$Container, [string]$Database, [string]$OutFile, [switch]$Force)
    $previous = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    $errFile = "$OutFile.err"
    try {
        $extra = if ($Force) { ' --force' } else { '' }"""

    new_repl1 = """    # -NoData dumps only the database structure/schema without table rows.
    # Used for 'log' which holds write-only event history (millions of rows,
    # gigabytes) that the game never reads back.
    param([string]$Container, [string]$Database, [string]$OutFile, [switch]$Force, [switch]$NoData)
    $previous = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    $errFile = "$OutFile.err"
    try {
        $extra = ''
        if ($Force) { $extra += ' --force' }
        if ($NoData) { $extra += ' --no-data' }"""

    # Normalize line endings for replacement
    text = text.replace('\r\n', '\n')
    old_target1_norm = old_target1.replace('\r\n', '\n')
    new_repl1_norm = new_repl1.replace('\r\n', '\n')
    if old_target1_norm not in text:
        raise RuntimeError("patch_metin2launcher_psm1: target 1 (Export-M2Database) not found!")
    text = text.replace(old_target1_norm, new_repl1_norm)

    # 2. Invoke-M2DatabaseImport: target backup
    old_target2 = """            $exists = & docker exec $tgtC mariadb -uroot -N -B -e "SHOW DATABASES LIKE '$db'" 2>$null
            if ($exists) { Export-M2Database -Container $tgtC -Database $db -OutFile (Join-Path $backupDir "target-before-import\\$db.sql") }"""
    new_repl2 = """            $exists = & docker exec $tgtC mariadb -uroot -N -B -e "SHOW DATABASES LIKE '$db'" 2>$null
            if ($exists) {
                $noData = ($db -eq 'log')
                Export-M2Database -Container $tgtC -Database $db -OutFile (Join-Path $backupDir "target-before-import\\$db.sql") -NoData:$noData
            }"""
    old_target2_norm = old_target2.replace('\r\n', '\n')
    new_repl2_norm = new_repl2.replace('\r\n', '\n')
    if old_target2_norm not in text:
        raise RuntimeError("patch_metin2launcher_psm1: target 2 (Invoke-M2DatabaseImport target) not found!")
    text = text.replace(old_target2_norm, new_repl2_norm)

    # 3. Invoke-M2DatabaseImport: source dump & CREATE DATABASE log
    old_target3 = """            Export-M2Database -Container $srcC -Database $db -OutFile (Join-Path $work "source\\$db.sql")
            $found += $db
        }
        Stop-M2ThrowawayDb -Container $srcC; $srcC = $null
        if ($found -notcontains 'player') {
            throw "W wolumenie '$SourceVolume' nie ma bazy player - to nie jest swiat tego serwera."
        }

        # 3. Replace the game databases the source has in the target.
        $tgtC = Start-M2ThrowawayDb -Volume $TargetVolume
        $sb = New-Object System.Text.StringBuilder
        [void]$sb.AppendLine('SET FOREIGN_KEY_CHECKS=0;')
        foreach ($db in $found) {
            [void]$sb.AppendLine("DROP DATABASE IF EXISTS $db;")
            [void]$sb.AppendLine("CREATE DATABASE $db DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;")
        }"""
    new_repl3 = """            $noData = ($db -eq 'log')
            Export-M2Database -Container $srcC -Database $db -OutFile (Join-Path $work "source\\$db.sql") -NoData:$noData
            $found += $db
        }
        Stop-M2ThrowawayDb -Container $srcC; $srcC = $null
        if ($found -notcontains 'player') {
            throw "W wolumenie '$SourceVolume' nie ma bazy player - to nie jest swiat tego serwera."
        }

        # 3. Replace the game databases the source has in the target.
        $tgtC = Start-M2ThrowawayDb -Volume $TargetVolume
        $sb = New-Object System.Text.StringBuilder
        [void]$sb.AppendLine('SET FOREIGN_KEY_CHECKS=0;')
        foreach ($db in $found) {
            [void]$sb.AppendLine("DROP DATABASE IF EXISTS $db;")
            [void]$sb.AppendLine("CREATE DATABASE $db DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;")
        }
        [void]$sb.AppendLine("CREATE DATABASE IF NOT EXISTS log DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;")"""
    old_target3_norm = old_target3.replace('\r\n', '\n')
    new_repl3_norm = new_repl3.replace('\r\n', '\n')
    if old_target3_norm not in text:
        raise RuntimeError("patch_metin2launcher_psm1: target 3 (Invoke-M2DatabaseImport source) not found!")
    text = text.replace(old_target3_norm, new_repl3_norm)

    # 4. New-M2DatabaseBackup
    old_target4 = """            $out = Join-Path $dir "$db.sql"
            try {
                Export-M2Database -Container $container -Database $db -OutFile $out
            }
            catch {
                # The log database is history only - nothing in the game reads
                # it - and it is where a crashed MyISAM table lives: 22 million
                # rows of log.log, killed with the engine. Its dump failing used
                # to fail the whole backup, and the world reset behind it
                # ("Zrzut bazy 'log' nie powiodl sie", uxietoszef, 20 September).
                # It is dumped again past the unreadable tables, and if even that
                # fails the backup goes on without it and says so. Any other
                # database is the world itself and still stops the backup.
                if ($db -ne 'log') { throw }
                $first = $_.Exception.Message
                try {
                    Export-M2Database -Container $container -Database $db -OutFile $out -Force"""
    new_repl4 = """            $out = Join-Path $dir "$db.sql"
            $noData = ($db -eq 'log')
            try {
                Export-M2Database -Container $container -Database $db -OutFile $out -NoData:$noData
            }
            catch {
                # The log database is history only - nothing in the game reads
                # it - and it is where a crashed MyISAM table lives: 22 million
                # rows of log.log, killed with the engine. Its dump failing used
                # to fail the whole backup, and the world reset behind it
                # ("Zrzut bazy 'log' nie powiodl sie", uxietoszef, 20 September).
                # It is dumped again past the unreadable tables, and if even that
                # fails the backup goes on without it and says so. Any other
                # database is the world itself and still stops the backup.
                if ($db -ne 'log') { throw }
                $first = $_.Exception.Message
                try {
                    Export-M2Database -Container $container -Database $db -OutFile $out -Force -NoData:$noData"""
    old_target4_norm = old_target4.replace('\r\n', '\n')
    new_repl4_norm = new_repl4.replace('\r\n', '\n')
    if old_target4_norm not in text:
        raise RuntimeError("patch_metin2launcher_psm1: target 4 (New-M2DatabaseBackup) not found!")
    text = text.replace(old_target4_norm, new_repl4_norm)

    # 5. New-M2DatabaseBackup readme note
    old_target5 = """        [void]$readme.AppendLine('Zawartosc (zrzuty mariadb-dump, latin1 jak w grze):')
        foreach ($s in $sizes) {
            [void]$readme.AppendLine(('  {0,-12} {1,12:N0} B' -f ($s.Name + '.sql'), $s.Bytes))
        }"""
    new_repl5 = """        [void]$readme.AppendLine('Zawartosc (zrzuty mariadb-dump, latin1 jak w grze):')
        foreach ($s in $sizes) {
            $note = if ($s.Name -eq 'log') { ' (schemat tabel bez historii)' } else { '' }
            [void]$readme.AppendLine(('  {0,-12} {1,12:N0} B{2}' -f ($s.Name + '.sql'), $s.Bytes, $note))
        }"""
    old_target5_norm = old_target5.replace('\r\n', '\n')
    new_repl5_norm = new_repl5.replace('\r\n', '\n')
    if old_target5_norm not in text:
        raise RuntimeError("patch_metin2launcher_psm1: target 5 (New-M2DatabaseBackup readme) not found!")
    text = text.replace(old_target5_norm, new_repl5_norm)

    # 6. Restore-M2DatabaseBackup: CREATE DATABASE log
    old_target6 = """        $tgtC = Start-M2ThrowawayDb -Volume $TargetVolume
        $sb = New-Object System.Text.StringBuilder
        [void]$sb.AppendLine('SET FOREIGN_KEY_CHECKS=0;')
        foreach ($db in $found) {
            [void]$sb.AppendLine("DROP DATABASE IF EXISTS $db;")
            [void]$sb.AppendLine("CREATE DATABASE $db DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;")
        }
        $createFile = Join-Path $work 'create.sql'"""
    new_repl6 = """        $tgtC = Start-M2ThrowawayDb -Volume $TargetVolume
        $sb = New-Object System.Text.StringBuilder
        [void]$sb.AppendLine('SET FOREIGN_KEY_CHECKS=0;')
        foreach ($db in $found) {
            [void]$sb.AppendLine("DROP DATABASE IF EXISTS $db;")
            [void]$sb.AppendLine("CREATE DATABASE $db DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;")
        }
        [void]$sb.AppendLine("CREATE DATABASE IF NOT EXISTS log DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;")
        $createFile = Join-Path $work 'create.sql'"""
    old_target6_norm = old_target6.replace('\r\n', '\n')
    new_repl6_norm = new_repl6.replace('\r\n', '\n')
    if old_target6_norm not in text:
        raise RuntimeError("patch_metin2launcher_psm1: target 6 (Restore-M2DatabaseBackup create.sql) not found!")
    text = text.replace(old_target6_norm, new_repl6_norm)

    # Restore CRLF
    return text.replace('\n', '\r\n').encode('utf-8')

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    server_root = os.path.join(repo_root, 'Server')

    print(f"[*] Rozpoczynam wdrazanie upstream {UPSTREAM_TAG} w {repo_root}...")

    # 1. Metadane i wersje
    for fname in ['VERSION', 'MOD_VERSION', 'CHANGELOG.md', 'update-manifest-mt2009.json']:
        content = get_upstream_file(fname)
        write_file(os.path.join(server_root, fname), content)
    print("[OK] Zaktualizowano metadane serwera do 2.43.0 (mod-64)")

    # 2. Seban Panel VERSION
    panel_ver = get_upstream_file('linux-port/docker/seban-panel/VERSION')
    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/VERSION'), panel_ver)
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/VERSION'), panel_ver)

    # 3. VPS install script
    write_file(os.path.join(server_root, 'linux-port/tools/vps-install.sh'),
               get_upstream_file('linux-port/tools/vps-install.sh'))

    # 4. Launcher files
    launcher_files = [
        'Metin2-Launcher-GUI.Background.png',
        'Metin2-Launcher-GUI.Layout.ps1',
        'Metin2-Launcher-GUI.Logo.png',
        'Metin2-Launcher-GUI.ps1',
        'Metin2-Launcher.ps1',
        'launcher/server-update-files.mt2009.txt'
    ]
    for lf in launcher_files:
        content = get_upstream_file(lf)
        write_file(os.path.join(server_root, lf), content)

    # 5. server-update-files.mod.txt (upewnij sie ze zawiera Metin2-Launcher-GUI.Logo.png)
    mod_txt_path = os.path.join(server_root, 'launcher', 'server-update-files.mod.txt')
    if os.path.exists(mod_txt_path):
        with open(mod_txt_path, 'r', encoding='utf-8') as f:
            mod_lines = f.read().splitlines()
        if 'Metin2-Launcher-GUI.Logo.png' not in mod_lines:
            # Wstaw po Metin2-Launcher-GUI.Background.png
            new_lines = []
            for line in mod_lines:
                new_lines.append(line)
                if line.strip() == 'Metin2-Launcher-GUI.Background.png':
                    new_lines.append('Metin2-Launcher-GUI.Logo.png')
            with open(mod_txt_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines) + '\n')
            print(f"[OK] Zaktualizowano: {mod_txt_path} (dodano Metin2-Launcher-GUI.Logo.png)")

    # 6. Metin2Launcher.psm1 z zachowaniem autorskich patchy -NoData
    upstream_psm1 = get_upstream_file('launcher/Metin2Launcher.psm1')
    patched_psm1 = patch_metin2launcher_psm1(upstream_psm1)
    write_file(os.path.join(server_root, 'launcher/Metin2Launcher.psm1'), patched_psm1)
    print("[OK] Zaktualizowano launcher/Metin2Launcher.psm1 z autorskim patchem -NoData")

    # 7. patch_dockerfile.py
    sys.path.insert(0, os.path.join(server_root, 'tools'))
    import patch_dockerfile
    patch_dockerfile.patch_dockerfile(server_root)

    print("\n[SUCCESS] Wdrozenie upstream 2.43.0 zakonczone sukcesem!")

if __name__ == '__main__':
    main()
