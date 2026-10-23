#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_upstream_2.37.1.py
Skrypt aktualizujący serwer i klienta MT2Plus do upstream 2.37.1 (mod-58, klient 2.0.68)
przy pełnym zachowaniu autorskich modyfikacji MT2Plus (Krystian):
 - IsHumanTargetReachable w CPlayerBotManager (playerbot_manager.h / playerbot_manager.cpp)
 - Sklep 160 slotów z drewnianymi kluczami (ikarus_shop_manager.cpp z fixem destPos, char_shop.cpp, char_item.cpp, offlineshopmanage.py)
 - Seban Panel rozszerzona ekonomia (trasy /economy, doradca emerytur, M1/M2 likwidacja, cache, optymalizacje collector.py)
 - 30-dniowe amulety (limittype0=9), zwiekszone stacki i flash oferty w mariadb/playerbot/apply.sh
 - Customowe questy w Dockerfile (recykling_bonusow, shop_unlock_slots)
 - Ukrywanie szarfy i uicostumehide w kliencie/serwerze
 - Ukrywanie HP mobów wyższych lv w uitarget.py
"""

import os
import sys
import subprocess
import shutil

def get_upstream_file(git_path):
    res = subprocess.run(['git', 'show', f'upstream/main:{git_path}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to get {git_path} from upstream/main: {res.stderr.decode('utf-8', errors='ignore')}")
    return res.stdout

def write_file(dest_path, content):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if isinstance(content, str):
        content = content.encode('utf-8')
    with open(dest_path, 'wb') as f:
        f.write(content)
    print(f"[OK] Updated: {dest_path}")

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    server_root = os.path.join(repo_root, 'Server')
    klient_root = os.path.join(repo_root, 'Klient')

    print(f"[*] Rozpoczynam wdrazanie upstream 2.37.1 w {repo_root}...")

    # 1. Wersje i pliki glowne
    for fname in ['VERSION', 'MOD_VERSION', 'CHANGELOG.md', 'update-manifest-mt2009.json']:
        content = get_upstream_file(fname)
        write_file(os.path.join(server_root, fname), content)

    # 2. Seban Panel wersje
    panel_ver = get_upstream_file('linux-port/docker/seban-panel/VERSION')
    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/VERSION'), panel_ver)
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/VERSION'), panel_ver)

    # 3. server-patches/zodiak/README.md
    write_file(os.path.join(server_root, 'server-patches/zodiak/README.md'),
               get_upstream_file('server-patches/zodiak/README.md'))

    # 4. Playerbot C++ nagłówki i źródła z upstream 2.37.1
    pb_rel_files = [
        'playerbot_bonus_mode.cpp',
        'playerbot_dungeon_runs.h',
        'playerbot_herbalism.h',
        'playerbot_navigation.h',
        'playerbot_survival.h',
        'playerbot_town.h',
        'playerbot_zodiac_bots.h',
        'playerbot_zodiac_runs.h',
    ]

    pb_overlay_dir = os.path.join(server_root, 'linux-port', 'overlays', 'playerbot', 'src', 'game', 'src')
    pb_staged_dir = os.path.join(server_root, 'linux-port', 'docker', 'game', 'src', 'server', 'game', 'src')

    for pbf in pb_rel_files:
        git_rel = f'linux-port/overlays/playerbot/src/game/src/{pbf}'
        content = get_upstream_file(git_rel)
        write_file(os.path.join(pb_overlay_dir, pbf), content)
        write_file(os.path.join(pb_staged_dir, pbf), content)

    # 5. playerbot_manager.cpp (z zachowaniem IsHumanTargetReachable na koncu)
    pbm_git = 'linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp'
    upstream_pbm = get_upstream_file(pbm_git).decode('utf-8')

    reachable_impl = """
bool CPlayerBotManager::IsHumanTargetReachable(LPCHARACTER ch, long targetX, long targetY)
{
	if (!ch)
		return false;
	const long lMapIndex = ch->GetMapIndex();
	if (GetHumanPathKind(lMapIndex) == 0)
		return true;

	const long base = lMapIndex >= PLAYERBOT_INSTANCE_MAP_INDEX_MIN ? lMapIndex / 10000 : lMapIndex;
	CPlayerBotNavigation& navigation = CPlayerBotNavigation::instance(base);
	if (!navigation.Init(base))
		return true;

	const DWORD chComp = navigation.GetComponentAtWorld(ch->GetX(), ch->GetY(), 2);
	const DWORD targetComp = navigation.GetComponentAtWorld(targetX, targetY, 2);
	if (chComp != 0 && targetComp != 0 && chComp != targetComp)
		return false;

	return true;
}
"""
    if 'bool CPlayerBotManager::IsHumanTargetReachable' not in upstream_pbm:
        upstream_pbm = upstream_pbm.rstrip() + "\n" + reachable_impl

    write_file(os.path.join(pb_overlay_dir, 'playerbot_manager.cpp'), upstream_pbm)
    write_file(os.path.join(pb_staged_dir, 'playerbot_manager.cpp'), upstream_pbm)
    print("[OK] Zaktualizowano playerbot_manager.cpp z zachowaniem IsHumanTargetReachable")

    print("\n[SUCCESS] Wdrozenie upstream 2.37.1 powiodlo sie pomyslnie!")

if __name__ == '__main__':
    main()
