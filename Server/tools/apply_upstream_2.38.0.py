#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_upstream_2.38.0.py
Skrypt aktualizujący serwer i klienta MT2Plus do upstream 2.38.0 (mod-59, klient 2.0.69)
przy pełnym zachowaniu autorskich modyfikacji MT2Plus (Krystian):
 - IsHumanTargetReachable w CPlayerBotManager (playerbot_manager.h / playerbot_manager.cpp)
 - Sklep 160 slotów z drewnianymi kluczami (ikarus_shop_manager.cpp z fixem destPos, char_shop.cpp, char_item.cpp, offlineshopmanage.py)
 - Seban Panel rozszerzona ekonomia (trasy /economy, doradca emerytur, M1/M2 likwidacja, cache, optymalizacje collector.py, filtry item_not_gm_scope_sql)
 - 30-dniowe amulety (limittype0=9), zwiekszone stacki i flash oferty w mariadb/playerbot/apply.sh
 - Customowe questy w Dockerfile (recykling_bonusow, shop_unlock_slots)
 - Ukrywanie szarfy i uicostumehide w kliencie/serwerze
 - Ukrywanie HP mobów wyższych lv w uitarget.py
"""

import os
import sys
import subprocess
import shutil
import json

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
    res = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'upstream/main', prefix], stdout=subprocess.PIPE, text=True, encoding='utf-8')
    if res.returncode != 0:
        raise RuntimeError(f"Failed to ls-tree {prefix}")
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    server_root = os.path.join(repo_root, 'Server')
    klient_root = os.path.join(repo_root, 'Klient')

    print(f"[*] Rozpoczynam wdrazanie upstream 2.38.0 w {repo_root}...")

    # 1. Wersje i pliki glowne
    for fname in ['VERSION', 'MOD_VERSION', 'CLIENT_VERSION', 'CHANGELOG.md', 'client-files.json', 'update-manifest-mt2009.json']:
        content = get_upstream_file(fname)
        write_file(os.path.join(server_root, fname), content)
    write_file(os.path.join(klient_root, 'CLIENT_VERSION'), get_upstream_file('CLIENT_VERSION'))

    # 2. Narzędzia, skrypty, edycje
    general_files = [
        'files/admin_panel.py',
        'launcher/server-update-files.mod.txt',
        'tools/New-M2UpdatePackage.ps1',
        'server-patches/enginefixes/README.md',
        'server-patches/enginefixes/edits.json',
        'tools/maps_wz/gen_maps_wz.py',
        'tools/maps_wz/maps_wz_mobs.json',
    ]
    for gf in general_files:
        write_file(os.path.join(server_root, gf), get_upstream_file(gf))

    # Drzewa wzmaps i mapcheck w client-patches
    for pfx in ['client-patches/client-2.0.30/tools/wzmaps/', 'client-patches/client-2.0.30/tools/mapcheck/']:
        for f in get_tree_files(pfx):
            write_file(os.path.join(server_root, f), get_upstream_file(f))

    # 3. Docker & Server runtime
    # docker-compose.yml
    dc_content = get_upstream_file('linux-port/docker/docker-compose.yml')
    write_file(os.path.join(server_root, 'linux-port/docker/docker-compose.yml'), dc_content)

    # .env.example
    env_ex = get_upstream_file('linux-port/docker/.env.example')
    write_file(os.path.join(server_root, 'linux-port/docker/.env.example'), env_ex)

    # m2-render-config
    write_file(os.path.join(server_root, 'linux-port/docker/game/bin/m2-render-config'),
               get_upstream_file('linux-port/docker/game/bin/m2-render-config'))

    # maps_wz/ folder
    for f in get_tree_files('linux-port/docker/game/maps_wz/'):
        write_file(os.path.join(server_root, f), get_upstream_file(f))

    # mob_drop_item.seeds.append.txt
    write_file(os.path.join(server_root, 'linux-port/docker/game/mob_drop_item.seeds.append.txt'),
               get_upstream_file('linux-port/docker/game/mob_drop_item.seeds.append.txt'))

    # Questy
    quests = [
        'black_steel_crafting.quest',
        'labirynth.quest',
        # 'tp_bookmarks.quest' (custom devgameplay: scrolls 22000/22011/etc + dungeons)
    ]
    for q in quests:
        rel = f'linux-port/docker/game/quest/{q}'
        write_file(os.path.join(server_root, rel), get_upstream_file(rel))

    # game/Dockerfile (kompilacja questów z zachowaniem recykling_bonusow i shop_unlock_slots)
    df_path = os.path.join(server_root, 'linux-port/docker/game/Dockerfile')
    upstream_df = get_upstream_file('linux-port/docker/game/Dockerfile').decode('utf-8')
    upstream_loop = 'guild_war_join zaklety_las erebu labirynth black_steel_crafting; do'
    our_loop = 'recykling_bonusow shop_unlock_slots guild_war_join zaklety_las erebu labirynth black_steel_crafting; do'
    if upstream_loop in upstream_df:
        upstream_df = upstream_df.replace(upstream_loop, our_loop)
    write_file(df_path, upstream_df)
    print("[OK] Zaktualizowano game/Dockerfile z zachowaniem customowych questow")

    # MariaDB maps_wz.sql
    write_file(os.path.join(server_root, 'linux-port/docker/mariadb/playerbot/maps_wz.sql'),
               get_upstream_file('linux-port/docker/mariadb/playerbot/maps_wz.sql'))

    # mariadb apply.sh: zaktualizuj z upstream i wstrzyknij nasze customowe bloki
    apply_path = os.path.join(server_root, 'linux-port/docker/mariadb/playerbot/apply.sh')
    upstream_apply = get_upstream_file('linux-port/docker/mariadb/playerbot/apply.sh').decode('utf-8')

    amulet_block = """
# MT2009_PLUS_AMULET_DURATION_30D: Pierścienie i amulety z ItemShopu (71135, 71136, 71143, 71145, 71148, 71149)
# zmiana czasu z 7 dni (domyślne 0) na 30 dni (2592000 s) oraz limittype0 = 9 (czas noszenia).
db -e "UPDATE world.item_proto SET limittype0 = 9, limitvalue0 = 2592000 WHERE vnum IN (71135, 71136, 71143, 71145, 71148, 71149);" \\
  || fail_step "could not update amulets and rings duration to 30 days" >&2
"""

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

    # 4. Panele
    write_file(os.path.join(server_root, 'linux-port/docker/panel/app/admin_panel.py'),
               get_upstream_file('linux-port/docker/panel/app/admin_panel.py'))

    panel_ver = get_upstream_file('linux-port/docker/seban-panel/VERSION')
    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/VERSION'), panel_ver)
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/VERSION'), panel_ver)

    seban_subfiles = [
        'linux-port/docker/seban-panel/dbeditor/mobs.py',
        'linux-port/docker/seban-panel/dbeditor/regen.py',
        'linux-port/docker/seban-panel/dbeditor/spawnfiles.py',
        'linux-port/docker/seban-panel/env_schema.py',
        'linux-port/docker/seban-panel/market_preview/sheet.py',
    ]
    for sf in seban_subfiles:
        write_file(os.path.join(server_root, sf), get_upstream_file(sf))

    # Aktualizacja MAP_NAMES i MAP_BOUNDS w app.py z zachowaniem filtrów GM
    for app_path in [
        os.path.join(server_root, 'linux-port/docker/seban-panel/app.py'),
        os.path.join(server_root, 'linux-port/overlays/seban-panel/app.py'),
        os.path.join(server_root, 'server-patches/krystian/seban-panel-ekonomia/app.py'),
    ]:
        if os.path.exists(app_path):
            txt = open(app_path, 'r', encoding='utf-8').read()
            if '70: "Kraina Gigantów", 80: "Wężowe Pole",' not in txt:
                target_mn = '366: "Starożytna Dżungla",'
                repl_mn = '366: "Starożytna Dżungla",\n    # MT2009_PLUS_MAPS_WZ_V1: the bots of 63-80 go there by the handover (game3).\n    70: "Kraina Gigantów", 80: "Wężowe Pole",'
                txt = txt.replace(target_mn, repl_mn)
            if '70: (819200, 716800, 51200, 51200), 80: (1049600, 716800, 102400, 102400),' not in txt:
                target_mb = '366: (768000, 537600, 76800, 76800),'
                repl_mb = '366: (768000, 537600, 76800, 76800),\n    # MT2009_PLUS_MAPS_WZ_V1: maps_wz/map/<folder>/Setting.txt (2x2 / 4x4).\n    70: (819200, 716800, 51200, 51200), 80: (1049600, 716800, 102400, 102400),'
                txt = txt.replace(target_mb, repl_mb)
            write_file(app_path, txt)
    print("[OK] Zaktualizowano seban-panel/app.py o Wężowe Pole i Krainę Gigantów z zachowaniem filtrów GM")

    # 5. Playerbot C++ nagłówki i źródła
    pb_files = [
        'playerbot_demon_tower.h',
        'playerbot_guild_war.h',
        'playerbot_navigation.h',
        'playerbot_price_tables.h',
        'playerbot_status.h',
        'playerbot_travel.h',
        'playerbot_types.h',
        'playerbot_wandering.h',
        'playerbot_yohara_bots.h',
    ]
    pb_overlay_dir = os.path.join(server_root, 'linux-port/overlays/playerbot/src/game/src')
    pb_staged_dir = os.path.join(server_root, 'linux-port/docker/game/src/server/game/src')

    for pbf in pb_files:
        rel = f'linux-port/overlays/playerbot/src/game/src/{pbf}'
        content = get_upstream_file(rel)
        write_file(os.path.join(pb_overlay_dir, pbf), content)
        write_file(os.path.join(pb_staged_dir, pbf), content)

    # 6. Aplikacja 18 nowych poprawek silnika z edits.json (building.h, building.cpp, cmd_gm.cpp)
    edits_raw = get_upstream_file('server-patches/enginefixes/edits.json').decode('utf-8')
    edits = json.loads(edits_raw)
    new_edits = edits[79:] # 18 poprawek 2.37.2/2.38.0
    print(f"[*] Aplikowanie {len(new_edits)} poprawek silnika dla budynków gildii...")
    
    files_cache = {}
    for fname in ('building.h', 'building.cpp', 'cmd_gm.cpp'):
        fp = os.path.join(pb_staged_dir, fname)
        files_cache[fname] = open(fp, 'r', encoding='utf-8', errors='ignore').read().replace('\r\n', '\n')

    for e in new_edits:
        fname = e['file']
        old_c = e['old'].replace('\r\n', '\n')
        new_c = e['new'].replace('\r\n', '\n')
        if old_c in files_cache[fname]:
            files_cache[fname] = files_cache[fname].replace(old_c, new_c, 1)
            print(f"[OK] Edycja {fname}: {e['marker']}")
        else:
            if new_c in files_cache[fname]:
                print(f"[SKIP/ALREADY] Edycja {fname}: {e['marker']}")
            else:
                raise RuntimeError(f"Failed to apply edit {e['marker']} to {fname}")

    for fname, fcontent in files_cache.items():
        fp = os.path.join(pb_staged_dir, fname)
        with open(fp, 'wb') as f:
            f.write(fcontent.encode('utf-8'))
        print(f"[OK] Zapisano spatchowany: {fp}")

    # 7. Pliki klienta 2.0.69
    client_patch_root = 'client-patches/client-2.0.30/root'
    client_files = [
        'localeinfo.py',
        'protoglobal.py',
        'uiaffectbar.py',
        'uidropwiki.py',
        'uigmpanel.py',
        'uiguild.py',
        'uitpbookmarks.py',
    ]
    for cf in client_files:
        rel = f'{client_patch_root}/{cf}'
        content = get_upstream_file(rel)
        write_file(os.path.join(server_root, rel), content)
        write_file(os.path.join(klient_root, 'pack/root', cf), content)

    # Przywrócenie customowych modyfikacji w Klient/pack/root:
    # 1. Ukrywanie szarfy (uicostumehide.py, uiinventory.py)
    sash_patch_dir = os.path.join(server_root, 'server-patches/krystian/ukryj-szarfe/klient_pliki/root')
    if os.path.exists(sash_patch_dir):
        for f in ['uicostumehide.py', 'uiinventory.py']:
            sp = os.path.join(sash_patch_dir, f)
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(klient_root, 'pack/root', f))
                print(f"[OK] Zachowano customowy {f} w Klient/pack/root")

    # 2. Ukrycie HP celu (uitarget.py)
    target_hp_patch = os.path.join(server_root, 'server-patches/krystian/ukrycie-hp-celu/klient_pliki/root/uitarget.py')
    if os.path.exists(target_hp_patch):
        shutil.copy2(target_hp_patch, os.path.join(klient_root, 'pack/root/uitarget.py'))
        print("[OK] Zachowano customowy uitarget.py w Klient/pack/root")

    # 3. Sklep 160 slotów (offlineshopmanage.py, offlineshopguest.py)
    shop_patch_dir = os.path.join(server_root, 'server-patches/krystian/sklep-160-slotow/klient_pliki/root')
    if os.path.exists(shop_patch_dir):
        for f in ['offlineshopmanage.py', 'offlineshopguest.py']:
            sp = os.path.join(shop_patch_dir, f)
            if os.path.exists(sp):
                shutil.copy2(sp, os.path.join(klient_root, 'pack/root', f))
                print(f"[OK] Zachowano customowy {f} w Klient/pack/root")

    print("\n[SUCCESS] Wdrozenie upstream 2.38.0 powiodlo sie pomyslnie!")

if __name__ == '__main__':
    main()
