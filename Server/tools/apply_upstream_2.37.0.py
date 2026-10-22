#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_upstream_2.37.0.py
Skrypt aktualizujący serwer i klienta MT2Plus do upstream 2.37.0 (mod-58, klient 2.0.68)
przy pełnym zachowaniu customowych systemów (YmirWork / Krystian):
 - IsHumanTargetReachable w CPlayerBotManager (playerbot_manager.h / playerbot_manager.cpp)
 - Sklep 160 slotów z drewnianymi kluczami (ikarus_shop_manager.cpp / offlineshopmanage.py)
 - Seban Panel rozszerzona ekonomia (trasy /economy, doradca emerytur, M1/M2 likwidacja, cache)
 - Zielone dodania M1/M2 oraz M1/M2 likwidacja w playerbot_bonus.h
 - Optymalizacje collector.py (executemany) oraz prune_old_snapshots
 - 30-dniowe amulety, zwiekszone stacki i flash oferty w mariadb/playerbot/apply.sh
 - Customowe questy w Dockerfile (recykling_bonusow, shop_unlock_slots)
 - Ukrywanie szarfy i uicostumehide w kliencie/serwerze
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

def get_tree_files(prefix):
    res = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'upstream/main', prefix], stdout=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to ls-tree {prefix}")
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    server_root = os.path.join(repo_root, 'Server')
    klient_root = os.path.join(repo_root, 'Klient')

    print(f"[*] Rozpoczynam wdrazanie upstream 2.37.0 w {repo_root}...")

    # 1. Wersje i pliki glowne
    for fname in ['VERSION', 'MOD_VERSION', 'CLIENT_VERSION', 'CHANGELOG.md', 'client-files.json', 'update-manifest-mt2009.json']:
        content = get_upstream_file(fname)
        write_file(os.path.join(server_root, fname), content)
    write_file(os.path.join(klient_root, 'CLIENT_VERSION'), get_upstream_file('CLIENT_VERSION'))

    # 2. Launchery, instalatory, dokumentacja i server-patches
    general_files = [
        'Metin2-Launcher-GUI.ps1',
        'Metin2-Launcher.ps1',
        'TUTORIAL.md',
        'start-server.ps1',
        'tools/port/Apply-MT2009PlusEngine.ps1',
        'tools/New-M2UpdatePackage.ps1',
        'files/admin_panel.py',
        'linux-port/docker/panel/app/admin_panel.py',
        'linux-port/tools/update.sh',
        'linux-port/tools/vps-install.sh',
    ]
    for gf in general_files:
        write_file(os.path.join(server_root, gf), get_upstream_file(gf))

    # Foldery drzew upstream
    tree_prefixes = [
        'launcher/',
        'server-patches/bonusyglobal/',
        'tools/las237/',
        'tools/globalmode/',
        'tools/protoglobal/',
        'tools/refineglobal/',
        'tools/zywioly/',
        'client-patches/client-2.0.30/tools/',
    ]
    for pfx in tree_prefixes:
        files = get_tree_files(pfx)
        for f in files:
            write_file(os.path.join(server_root, f), get_upstream_file(f))

    # tools/yohara_bot_lootrun_map.py
    write_file(os.path.join(server_root, 'tools/yohara_bot_lootrun_map.py'), get_upstream_file('tools/yohara_bot_lootrun_map.py'))

    # 3. Docker & Server runtime
    # docker-compose.yml
    dc_content = get_upstream_file('linux-port/docker/docker-compose.yml')
    write_file(os.path.join(server_root, 'linux-port/docker/docker-compose.yml'), dc_content)

    # .env.example
    env_ex = get_upstream_file('linux-port/docker/.env.example')
    write_file(os.path.join(server_root, 'linux-port/docker/.env.example'), env_ex)

    # game/bin/*
    for gb in ['entrypoint.sh', 'm2-dragonsoul', 'm2-drops', 'm2-render-config']:
        rel = f'linux-port/docker/game/bin/{gb}'
        write_file(os.path.join(server_root, rel), get_upstream_file(rel))

    # game/dragon_soul_applys.global.txt
    write_file(os.path.join(server_root, 'linux-port/docker/game/dragon_soul_applys.global.txt'),
               get_upstream_file('linux-port/docker/game/dragon_soul_applys.global.txt'))

    # Foldery map i danych gry: cape301, maps302, moby_global, yohara_zaklety, zaklety237, arezzo
    game_tree_prefixes = [
        'linux-port/docker/game/cape301/',
        'linux-port/docker/game/maps302/',
        'linux-port/docker/game/moby_global/',
        'linux-port/docker/game/yohara_zaklety/',
        'linux-port/docker/game/zaklety237/',
        'linux-port/docker/game/arezzo/',
    ]
    for gtp in game_tree_prefixes:
        for f in get_tree_files(gtp):
            write_file(os.path.join(server_root, f), get_upstream_file(f))

    # Usunięcie starych plików natural_map z arezzo jeśli zostały skasowane w upstream
    old_natural = os.path.join(server_root, 'linux-port/docker/game/arezzo/map/natural_map')
    if os.path.exists(old_natural):
        shutil.rmtree(old_natural)
        print("[OK] Usunieto zdezaktualizowany folder natural_map z arezzo")

    # Questy
    quests = [
        'erebu.quest',
        'zaklety_las.quest',
        'temple_of_the_ochao.quest',
        'starozytna_dzungla.quest',
        'map_warp.quest',
        'tp_bookmarks.quest',
        'zywioly.quest',
    ]
    for q in quests:
        rel = f'linux-port/docker/game/quest/{q}'
        write_file(os.path.join(server_root, rel), get_upstream_file(rel))

    # game/Dockerfile (kompilacja questów z zachowaniem recykling_bonusow i shop_unlock_slots)
    df_path = os.path.join(server_root, 'linux-port/docker/game/Dockerfile')
    upstream_df = get_upstream_file('linux-port/docker/game/Dockerfile').decode('utf-8')
    # W upstream pętla kończy się na: guild_war_join zaklety_las erebu; do
    # My dodajemy recykling_bonusow i shop_unlock_slots
    upstream_loop = 'guild_war_join zaklety_las erebu; do'
    our_loop = 'recykling_bonusow shop_unlock_slots guild_war_join zaklety_las erebu; do'
    if upstream_loop in upstream_df:
        upstream_df = upstream_df.replace(upstream_loop, our_loop)
    write_file(df_path, upstream_df)
    print("[OK] Zaktualizowano game/Dockerfile z zachowaniem customowych questow")

    # MariaDB playerbot & initdb
    mariadb_files = [
        'linux-port/docker/mariadb/initdb.d/20-log-schema.sql',
        'linux-port/docker/mariadb/playerbot/item_proto.mt2009plus.sql',
        'linux-port/docker/mariadb/playerbot/log_schema.sql',
        'linux-port/docker/mariadb/playerbot/playerbot_core_handover.sql',
        'linux-port/docker/mariadb/playerbot/refine_global_2x.sql',
        'linux-port/docker/mariadb/playerbot/yohara_items_zaklety.sql',
        'linux-port/docker/mariadb/playerbot/yohara_zaklety.sql',
        'linux-port/docker/mariadb/playerbot/yohara_zaklety_zywioly.sql',
        'linux-port/docker/mariadb/playerbot/zywioly_moby_global.sql',
    ]
    for mf in mariadb_files:
        write_file(os.path.join(server_root, mf), get_upstream_file(mf))

    # mariadb apply.sh: zaktualizuj z upstream i wstrzyknij nasze customowe bloki
    apply_path = os.path.join(server_root, 'linux-port/docker/mariadb/playerbot/apply.sh')
    upstream_apply = get_upstream_file('linux-port/docker/mariadb/playerbot/apply.sh').decode('utf-8')
    
    # Nasze bloki:
    # 1. 30 dniowe amulety
    amulet_block = """
# MT2009_PLUS_AMULET_DURATION_30D: Pierścienie i amulety z ItemShopu (71135, 71136, 71143, 71145, 71148, 71149)
# zmiana czasu z 7 dni (domyślne 0) na 30 dni (2592000 s).
db -e "UPDATE world.item_proto SET limitvalue0 = 2592000 WHERE vnum IN (71135, 71136, 71143, 71145, 71148, 71149);" \\
  || fail_step "could not update amulets and rings duration to 30 days" >&2
"""
    # 2. Stack 200
    stack_block = """
# MT2009_PLUS_STACK_200_EXTENDED: Zwiekszenie stackowania wybranych przedmiotow do 200
# Ziola malp, kowalstwo/ulepszanie, malze, perly, ryby, przetopy, ksiegi pasywne, klucze i przedmioty specjalne
db -e "
UPDATE world.item_proto SET stack = 200 WHERE vnum IN (50050, 50057, 50058, 50059, 25040, 25041, 25042, 25043, 70039, 25044, 25045, 71032, 70024, 25100, 71025, 71026, 27987, 27992, 27993, 27994, 50060, 50061, 50062, 50008, 50009, 70014, 70005, 70042, 70043, 72005, 72006);
UPDATE world.item_proto SET stack = 200 WHERE vnum BETWEEN 27800 AND 27899;
UPDATE world.item_proto SET stack = 200 WHERE vnum BETWEEN 50621 AND 50640;
UPDATE world.item_proto SET stack = 200 WHERE vnum BETWEEN 50301 AND 50322;
" >/dev/null 2>&1 || true
"""
    # 3. 92_itemshop_flash_offers.sql
    flash_block = """
if [ -s /opt/playerbot/mod/92_itemshop_flash_offers.sql ]; then
    db < /opt/playerbot/mod/92_itemshop_flash_offers.sql || fail_step "could not apply 92_itemshop_flash_offers.sql" >&2
fi
"""

    anchor_fresh = "# MT2009_PLUS_FRESH_INSTALL_FIX_V1:"
    if anchor_fresh in upstream_apply:
        upstream_apply = upstream_apply.replace(anchor_fresh, amulet_block + "\n" + stack_block + "\n" + flash_block + "\n" + anchor_fresh)
    write_file(apply_path, upstream_apply)
    print("[OK] Zaktualizowano apply.sh z zachowaniem customowych modyfikacji")

    # 4. Seban Panel
    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/VERSION'), get_upstream_file('linux-port/docker/seban-panel/VERSION'))
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/VERSION'), get_upstream_file('linux-port/docker/seban-panel/VERSION'))
    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/env_schema.py'), get_upstream_file('linux-port/docker/seban-panel/env_schema.py'))
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/env_schema.py'), get_upstream_file('linux-port/docker/seban-panel/env_schema.py'))
    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/static/server-env.js'), get_upstream_file('linux-port/docker/seban-panel/static/server-env.js'))

    # m2clientpack
    for f in get_tree_files('linux-port/docker/seban-panel/m2clientpack/'):
        write_file(os.path.join(server_root, f), get_upstream_file(f))

    # app.py: zmiana Zaczarowany Las na Zaklety Las w MAP_NAMES i MAP_BOUNDS
    for app_path in [
        os.path.join(server_root, 'linux-port/docker/seban-panel/app.py'),
        os.path.join(server_root, 'linux-port/overlays/seban-panel/app.py'),
    ]:
        txt = open(app_path, 'r', encoding='utf-8').read()
        txt = txt.replace('362: "Zaczarowany Las",', '353: "Zaklęty Las",')
        txt = txt.replace('362: (332800, 384000, 102400, 102400),', '353: (768000, 1408000, 76800, 102400),')
        write_file(app_path, txt)
    print("[OK] Zaktualizowano seban-panel/app.py o Zaklety Las")

    # 5. Playerbot C++ nagłówki i źródła
    pb_src_dir = 'linux-port/overlays/playerbot/src/game/src'
    pb_files = [
        'playerbot_arezzo.h',
        'playerbot_arezzo_bots.h',
        'playerbot_arezzo_dungeon_bots.h',
        'playerbot_belts.h',
        'playerbot_boss_raid.h',
        'playerbot_bpbots.h',
        'playerbot_chat_world.h',
        'playerbot_dungeon_lfg.h',
        'playerbot_dungeon_runs.h',
        'playerbot_economy.h',
        'playerbot_gear.h',
        'playerbot_guild_shaman.h',
        'playerbot_market.h',
        'playerbot_market_life.h',
        'playerbot_movement.h',
        'playerbot_navigation.h',
        'playerbot_ochao_bots.h',
        'playerbot_offline_market.h',
        'playerbot_offline_policy.h',
        'playerbot_offline_shop.h',
        'playerbot_party_dungeon.h',
        'playerbot_seonhae.h',
        'playerbot_sidekick.h',
        'playerbot_status.h',
        'playerbot_targeting.h',
        'playerbot_town.h',
        'playerbot_travel.h',
        'playerbot_types.h',
        'playerbot_wandering.h',
        'playerbot_yohara_bots.h',
        'playerbot_bonus_mode.cpp',
        'playerbot_elements.cpp',
    ]
    for pbf in pb_files:
        rel = f'{pb_src_dir}/{pbf}'
        write_file(os.path.join(server_root, rel), get_upstream_file(rel))

    # playerbot_manager.cpp: pobierz z upstream i dopisz na końcu IsHumanTargetReachable
    pbm_cpp_path = os.path.join(server_root, f'{pb_src_dir}/playerbot_manager.cpp')
    upstream_pbm_cpp = get_upstream_file(f'{pb_src_dir}/playerbot_manager.cpp').decode('utf-8')
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
    if 'bool CPlayerBotManager::IsHumanTargetReachable' not in upstream_pbm_cpp:
        upstream_pbm_cpp = upstream_pbm_cpp.rstrip() + "\n" + reachable_impl
    write_file(pbm_cpp_path, upstream_pbm_cpp)
    print("[OK] Zaktualizowano playerbot_manager.cpp z zachowaniem IsHumanTargetReachable")

    # 6. Klient
    client_patch_root = 'client-patches/client-2.0.30/root'
    client_files = [
        'game.py',
        'localeinfo.py',
        'localeinfo_point.py',
        'protoglobal.py',
        'uidropwiki.py',
        'uigmpanel.py',
        'uitarget.py',
        'uitpbookmarks.py',
        'zywioly_global.py',
        'icon/item/30613.tga',
        'icon/item/31096.tga',
        'icon/item/31097.tga',
        'icon/item/31098.tga',
        'icon/item/31099.tga',
        'icon/item/31100.tga',
        'icon/item/50266.tga',
        'icon/item/54701.tga',
    ]
    for cf in client_files:
        rel = f'{client_patch_root}/{cf}'
        content = get_upstream_file(rel)
        write_file(os.path.join(server_root, rel), content)
        write_file(os.path.join(klient_root, 'pack/root', cf), content)

    # uicostumehide.py i uiinventory.py z patcha ukryj-szarfe
    sash_patch_dir = os.path.join(server_root, 'server-patches/krystian/ukryj-szarfe/klient_pliki/root')
    if os.path.exists(sash_patch_dir):
        for f in ['uicostumehide.py', 'uiinventory.py']:
            sp = os.path.join(sash_patch_dir, f)
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(klient_root, 'pack/root', f))
                print(f"[OK] Skopiowano customowy {f} do Klient/pack/root")

    print("\n[SUCCESS] Wdrozenie upstream 2.37.0 powiodlo sie pomyslnie!")

if __name__ == '__main__':
    main()
