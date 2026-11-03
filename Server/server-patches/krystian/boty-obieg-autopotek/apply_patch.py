#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patch: boty-obieg-autopotek
Autor: Krystian
Opis: Autonomiczny obieg eliksirów (auto-potek) dla botów:
      - Limit w ekwipunku (max 2-3 sztuki)
      - Depozyt u Dozorcy (max 2-3 sztuki)
      - Wystawianie nadmiaru na sklep offline (max 3-4 sztuki, cena: koszt napełnienia + 25%)
      - Napełnianie / utylizacja pustych flakonów u Alchemika
      - Zdejmowanie niesprzedanych z tobołka po upływie terminu (TTL ~24h)
      - AI kupca: boty bez potek skupują je z rynku
"""

import os
import shutil
import sys

FILES = [
    'playerbot_consumables.h',
    'playerbot_town.h',
    'playerbot_economy.h',
    'playerbot_offline_shop.h',
    'playerbot_market.h',
    'playerbot_offline_market.h'
]

def apply_patch(repo_root=None):
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

    overlay_dir = os.path.join(repo_root, 'Server', 'linux-port', 'overlays', 'playerbot', 'src', 'game', 'src')
    docker_dir = os.path.join(repo_root, 'Server', 'linux-port', 'docker', 'game', 'src', 'server', 'game', 'src')

    if not os.path.isdir(overlay_dir) or not os.path.isdir(docker_dir):
        print(f"Błąd: Nie znaleziono katalogów źródłowych: {overlay_dir} lub {docker_dir}")
        return False

    print("Synchronizacja plików systemu autopotek:")
    for f in FILES:
        src = os.path.join(overlay_dir, f)
        dst = os.path.join(docker_dir, f)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            print(f"  [OK] Zsynchronizowano {f}")
        else:
            print(f"  [!] Brak pliku źródłowego: {src}")

    print("Pomyślnie zaaplikowano patch boty-obieg-autopotek.")
    return True

if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else None
    success = apply_patch(root)
    sys.exit(0 if success else 1)
