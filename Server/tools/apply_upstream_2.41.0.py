#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_upstream_2.41.0.py
Skrypt aktualizujacy serwer MT2Plus do upstream 2.41.0 (mod-62, klient 2.0.71)
z zachowaniem wszystkich autorskich modyfikacji MT2Plus (34/34 w deep_audit.py):
 - Grota Wygnancow V2 monster spawns & commanders (boss.grota2.txt, regen.grota2.txt, gen_grota2.py)
 - MariaDB 1GB buffer pool i indeksy zapytań
 - Seban Panel snapshot retention policy i optymalizacja live_bots
 - Playerbot census (playerbot_f_census.h) i tuning ekonomii
 - Wszystkie 34 autorskie systemy MT2Plus: AutoFish, 160 slotów, wstawanie 100 HP,
   ceny botów, emerytura, lottery30, ulepszanie, ukrywanie szarfy/hp, brak potek.
"""

import os
import sys
import subprocess
import shutil
import json

UPSTREAM_TAG = "v2.41.0"

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

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    server_root = os.path.join(repo_root, 'Server')
    klient_root = os.path.join(repo_root, 'Klient')

    print(f"[*] Rozpoczynam wdrazanie upstream {UPSTREAM_TAG} w {repo_root}...")

    # 1. Metadane i wersje
    for fname in ['VERSION', 'MOD_VERSION', 'CHANGELOG.md', 'update-manifest-mt2009.json']:
        content = get_upstream_file(fname)
        write_file(os.path.join(server_root, fname), content)
    print("[OK] Zaktualizowano metadane serwera do 2.41.0 (mod-62)")

    # 2. Grota 2 pliki respów i generator
    for grota_f in ['boss.grota2.txt', 'gen_report.txt', 'regen.grota2.txt']:
        content = get_upstream_file(f'linux-port/docker/game/grota2/{grota_f}')
        write_file(os.path.join(server_root, 'linux-port/docker/game/grota2', grota_f), content)
    write_file(os.path.join(server_root, 'tools/grota2/gen_grota2.py'), get_upstream_file('tools/grota2/gen_grota2.py'))
    print("[OK] Zapisano pliki Groty Wygnancow V2")

    # 3. Docker Compose i .env.example
    write_file(os.path.join(server_root, 'linux-port/docker/docker-compose.yml'),
               get_upstream_file('linux-port/docker/docker-compose.yml'))
    write_file(os.path.join(server_root, 'linux-port/docker/.env.example'),
               get_upstream_file('linux-port/docker/.env.example'))

    # 4. game/Dockerfile z zachowaniem patch_dockerfile
    df_path = os.path.join(server_root, 'linux-port/docker/game/Dockerfile')
    upstream_df = get_upstream_file('linux-port/docker/game/Dockerfile').decode('utf-8')
    write_file(df_path, upstream_df)
    
    # Zaaplikuj autorskie mody do Dockerfile
    sys.path.insert(0, os.path.join(server_root, 'tools'))
    import patch_dockerfile
    patch_dockerfile.patch_dockerfile(server_root)
    print("[OK] Zaktualizowano game/Dockerfile i zabezpieczono customowe mody MT2Plus")

    # 5. MariaDB
    write_file(os.path.join(server_root, 'linux-port/docker/mariadb/conf.d/99-metin2.cnf'),
               get_upstream_file('linux-port/docker/mariadb/conf.d/99-metin2.cnf'))
    write_file(os.path.join(server_root, 'linux-port/docker/mariadb/initdb.d/20-log-schema.sql'),
               get_upstream_file('linux-port/docker/mariadb/initdb.d/20-log-schema.sql'))
    write_file(os.path.join(server_root, 'linux-port/docker/mariadb/playerbot/log_schema.sql'),
               get_upstream_file('linux-port/docker/mariadb/playerbot/log_schema.sql'))
    print("[OK] Zaktualizowano konfiguracje MariaDB (1GB buffer pool, log schema)")

    # 6. Seban Panel
    panel_files = [
        'Dockerfile', 'VERSION', 'collector.py', 'env_schema.py',
        'log_maintenance.py', 'snapshot_retention.py', 'test_snapshot_retention.py'
    ]
    for pf in panel_files:
        content = get_upstream_file(f'linux-port/docker/seban-panel/{pf}')
        write_file(os.path.join(server_root, f'linux-port/docker/seban-panel/{pf}'), content)
        write_file(os.path.join(server_root, f'linux-port/overlays/seban-panel/{pf}'), content)

    # Optymalizacja live_bots w app.py
    old_query = """        prior = rows(\"\"\"SELECT s.pid,s.map_index,s.x,s.y FROM player.web_seban_bot_position_snapshot s
          JOIN (SELECT pid, MAX(captured_at) captured_at FROM player.web_seban_bot_position_snapshot
                WHERE captured_at <= NOW() - INTERVAL %s MINUTE GROUP BY pid) old
          ON old.pid=s.pid AND old.captured_at=s.captured_at WHERE s.pid IN (\"\"\" + placeholders + \")\", (threshold, *ids))"""
    
    new_query = """        # MT2009_PLUS_SEBAN_SNAPSHOT_RETENTION_V1: only the last hour before
        # the threshold - the GROUP BY used to read every position ever kept
        # (17M rows on the Yohara test server, 3 November); a position older
        # than that is no "stuck since" evidence anyway.
        prior = rows(\"\"\"SELECT s.pid,s.map_index,s.x,s.y FROM player.web_seban_bot_position_snapshot s
          JOIN (SELECT pid, MAX(captured_at) captured_at FROM player.web_seban_bot_position_snapshot
                WHERE captured_at <= NOW() - INTERVAL %s MINUTE AND captured_at > NOW() - INTERVAL %s MINUTE
                  AND pid IN (\"\"\" + placeholders + \"\"\") GROUP BY pid) old
          ON old.pid=s.pid AND old.captured_at=s.captured_at\"\"\", (threshold, threshold + 60, *ids))"""

    for app_path in [
        os.path.join(server_root, 'linux-port/docker/seban-panel/app.py'),
        os.path.join(server_root, 'linux-port/overlays/seban-panel/app.py'),
        os.path.join(server_root, 'server-patches/krystian/seban-panel-ekonomia/app.py'),
    ]:
        if os.path.exists(app_path):
            with open(app_path, 'r', encoding='utf-8') as f:
                app_txt = f.read()
            if old_query in app_txt:
                app_txt = app_txt.replace(old_query, new_query, 1)
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write(app_txt)
                print(f"[OK] Zaktualizowano live_bots() w: {app_path}")
            elif 'MT2009_PLUS_SEBAN_SNAPSHOT_RETENTION_V1' in app_txt:
                print(f"[SKIP/ALREADY] live_bots() juz zaktualizowane w: {app_path}")
            else:
                print(f"[WARN] Nie znaleziono starego bloku live_bots() w {app_path}")

    # 7. Playerbot overlays C++
    pb_files = [
        'playerbot_alchemy.h',
        'playerbot_bonus.h',
        'playerbot_bonus_rules.h',
        'playerbot_economy.h',
        'playerbot_explain.h',
        'playerbot_f_census.h',
        'playerbot_gambler.h',
        'playerbot_gear.h',
        'playerbot_itemshop.h',
        'playerbot_manager.cpp',
        'playerbot_market.h',
        'playerbot_offline_shop.h',
        'playerbot_party_dungeon.h',
        'playerbot_town.h',
        'playerbot_travel.h',
        'playerbot_types.h',
        'playerbot_upstream_botlogic.h',
        'playerbot_wandering.h',
    ]

    pb_overlay_dir = os.path.join(server_root, 'linux-port/overlays/playerbot/src/game/src')
    pb_staged_dir = os.path.join(server_root, 'linux-port/docker/game/src/server/game/src')

    for pbf in pb_files:
        rel = f'linux-port/overlays/playerbot/src/game/src/{pbf}'
        content = get_upstream_file(rel)
        write_file(os.path.join(pb_overlay_dir, pbf), content)
        write_file(os.path.join(pb_staged_dir, pbf), content)

    # Wstrzyknięcie nagłówka playerbot_custom_prices.h w playerbot_town.h
    town_path = os.path.join(pb_overlay_dir, 'playerbot_town.h')
    with open(town_path, 'r', encoding='utf-8') as f:
        town_txt = f.read()
    if '#include "playerbot_custom_prices.h"' not in town_txt:
        town_txt = '#include "playerbot_custom_prices.h"\n' + town_txt
        with open(town_path, 'w', encoding='utf-8') as f:
            f.write(town_txt)
        with open(os.path.join(pb_staged_dir, 'playerbot_town.h'), 'w', encoding='utf-8') as f:
            f.write(town_txt)
        print("[OK] Dodano #include 'playerbot_custom_prices.h' do playerbot_town.h")

    # Wstrzyknięcie deklaracji IsPlayerBotRetiring w playerbot_manager.cpp przed #include "playerbot_offline_shop.h"
    mgr_path = os.path.join(pb_overlay_dir, 'playerbot_manager.cpp')
    with open(mgr_path, 'r', encoding='utf-8') as f:
        mgr_txt = f.read()
    fwd_decl = "namespace { bool IsPlayerBotRetiring(DWORD dwPlayerID); }\n#include \"playerbot_offline_shop.h\""
    if '#include "playerbot_offline_shop.h"' in mgr_txt and 'namespace { bool IsPlayerBotRetiring(DWORD dwPlayerID); }' not in mgr_txt:
        mgr_txt = mgr_txt.replace('#include "playerbot_offline_shop.h"', fwd_decl, 1)
        with open(mgr_path, 'w', encoding='utf-8') as f:
            f.write(mgr_txt)
        with open(os.path.join(pb_staged_dir, 'playerbot_manager.cpp'), 'w', encoding='utf-8') as f:
            f.write(mgr_txt)
        print("[OK] Dodano forward declaration IsPlayerBotRetiring w playerbot_manager.cpp")

    # 8. Zaaplikuj wszystkie autorskie modyfikacje do plików playerbot
    print("\n[*] Aplikowanie customowych modyfikacji (apply_custom_restorations.py)...")
    import apply_custom_restorations
    apply_custom_restorations.main()

    # 9. Aktualizacja PROJECT_CONTEXT.md
    for pc_path in [os.path.join(repo_root, 'PROJECT_CONTEXT.md'), os.path.join(server_root, 'docs', 'PROJECT_CONTEXT.md')]:
        if os.path.exists(pc_path):
            with open(pc_path, 'r', encoding='utf-8') as f:
                pc_txt = f.read()
            pc_txt = pc_txt.replace('`2.40.0`', '`2.41.0`').replace('`mod-61`', '`mod-62`')
            with open(pc_path, 'w', encoding='utf-8') as f:
                f.write(pc_txt)
            print(f"[OK] Zaktualizowano wersje w: {pc_path}")

    print("\n=== Wdrozenie upstream 2.41.0 zakonczone sukcesem! ===")

if __name__ == '__main__':
    main()
