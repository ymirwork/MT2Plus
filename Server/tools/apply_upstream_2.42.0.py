#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_upstream_2.42.0.py
Skrypt aktualizujacy serwer MT2Plus do upstream 2.42.0 (mod-63, klient 2.0.71)
z zachowaniem wszystkich autorskich modyfikacji MT2Plus (34/34 w deep_audit.py):
 - Playerbot AI rozwój i odblokowania expa (timeout 3h, no-better slot rule, Zodiac strength gate)
 - Playerbot przeżywalność i ucieczka po śmierci (playerbot_deathloop.h, playerbot_survive.h)
 - Baza wiedzy o dropie i przepływ materiałów (playerbot_dropknow.h, playerbot_mats_flow.h)
 - Czyszczenie rynku i ceny wyprzedażowe (playerbot_market_clearing.h, PLAYERBOT_MARKET_CLEAR_*)
 - Optymalizacja logów botów (mniej spamu o 80-90%)
 - Bezpieczeństwo MariaDB ulimits core: 0
 - Wszystkie 34 autorskie systemy MT2Plus w 100% aktywne i nienaruszone.
"""

import os
import sys
import subprocess
import shutil

UPSTREAM_TAG = "v2.42.0"

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
    overlays_pb_dir = os.path.join(server_root, 'linux-port', 'overlays', 'playerbot', 'src', 'game', 'src')
    docker_pb_dir = os.path.join(server_root, 'linux-port', 'docker', 'game', 'src', 'server', 'game', 'src')

    print(f"[*] Rozpoczynam wdrazanie upstream {UPSTREAM_TAG} w {repo_root}...")

    # 1. Metadane i wersje
    for fname in ['VERSION', 'MOD_VERSION', 'CHANGELOG.md', 'update-manifest-mt2009.json']:
        content = get_upstream_file(fname)
        write_file(os.path.join(server_root, fname), content)
    print("[OK] Zaktualizowano metadane serwera do 2.42.0 (mod-63)")

    # 2. Docker Compose i .env.example
    write_file(os.path.join(server_root, 'linux-port/docker/docker-compose.yml'),
               get_upstream_file('linux-port/docker/docker-compose.yml'))
    write_file(os.path.join(server_root, 'linux-port/docker/.env.example'),
               get_upstream_file('linux-port/docker/.env.example'))
    
    # Seban Panel VERSION
    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/VERSION'),
               get_upstream_file('linux-port/docker/seban-panel/VERSION'))
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/VERSION'),
               get_upstream_file('linux-port/docker/seban-panel/VERSION'))

    # 3. Pliki Playerbot z v2.42.0
    pb_files = [
        'playerbot_alchemy.h',
        'playerbot_boss_raid.h',
        'playerbot_channel_rules.h',
        'playerbot_combat.h',
        'playerbot_deathloop.h',
        'playerbot_dropknow.h',
        'playerbot_dungeon_lfg.h',
        'playerbot_economy.h',
        'playerbot_gear.h',
        'playerbot_gear_upgrade.h',
        'playerbot_log.h',
        'playerbot_manager.cpp',
        'playerbot_market.h',
        'playerbot_market_clearing.h',
        'playerbot_mats_flow.h',
        'playerbot_mood.h',
        'playerbot_movement.h',
        'playerbot_offline_market.h',
        'playerbot_offline_policy.h',
        'playerbot_offline_shop.h',
        'playerbot_party_dungeon.h',
        'playerbot_persona.h',
        'playerbot_persona_rules.h',
        'playerbot_progression.h',
        'playerbot_refine_rules.h',
        'playerbot_saddlebag.h',
        'playerbot_survival.h',
        'playerbot_survive.h',
        'playerbot_targeting.h',
        'playerbot_town.h',
        'playerbot_travel.h',
        'playerbot_types.h',
        'playerbot_zodiac_runs.h'
    ]

    print(f"[*] Aktualizacja {len(pb_files)} plikow playerbot w nakladkach...")
    for pf in pb_files:
        upstream_path = f"linux-port/overlays/playerbot/src/game/src/{pf}"
        content = get_upstream_file(upstream_path)
        dest_overlay = os.path.join(overlays_pb_dir, pf)
        write_file(dest_overlay, content)
        dest_docker = os.path.join(docker_pb_dir, pf)
        write_file(dest_docker, content)

    # 4. Zaaplikuj autorskie mody MT2Plus do playerbotów
    print("\n[*] Reaplikacja autorskich modyfikacji MT2Plus...")
    sys.path.insert(0, os.path.join(server_root, 'tools'))
    import apply_custom_restorations
    apply_custom_restorations.main()

    # 5. Sprawdź i zaaplikuj ewentualne modyfikacje do Dockerfile
    import patch_dockerfile
    patch_dockerfile.patch_dockerfile(server_root)

    print("\n[SUCCESS] Wdrozenie upstream 2.42.0 zakonczone sukcesem!")

if __name__ == '__main__':
    main()
