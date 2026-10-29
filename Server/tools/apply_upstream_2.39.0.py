#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_upstream_2.39.0.py
Skrypt aktualizujący serwer i klienta MT2Plus do upstream 2.39.0 (mod-60, klient 2.0.70)
z pełnym zachowaniem autorskich modyfikacji MT2Plus (Krystian):
 - IsHumanTargetReachable w CPlayerBotManager (playerbot_manager.h / playerbot_manager.cpp)
 - Sklep 160 slotów z drewnianymi kluczami (ikarus_shop_manager.cpp, char_shop.cpp, offlineshopmanage.py, dualshop.py)
 - Seban Panel rozszerzona ekonomia (trasy /economy, doradca emerytur, M1/M2, bot prices, itemshop panel, filtry GM item_not_gm_scope_sql)
 - 30-dniowe amulety (limittype0=9), zwiekszone stacki do 200 i 92 flash oferty w mariadb/playerbot/apply.sh
 - Customowe questy w Dockerfile (recykling_bonusow, shop_unlock_slots)
 - Ukrywanie szarfy i uicostumehide w kliencie/serwerze
 - Ukrywanie HP mobów w uitarget.py
 - Narzędzia i interfejsy sesji farmienia, magazynu kolekcjonera, domu aukcyjnego
 - Usunięcie mikstur z metinów/bossów M2+ (brak-potek-m2-metiny-bossy)
"""

import os
import sys
import subprocess
import shutil
import json
import urllib.request

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
    print(f"[OK] Zapisano: {dest_path}")

def get_tree_files(prefix):
    res = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'upstream/main', prefix], stdout=subprocess.PIPE, text=True, encoding='utf-8')
    if res.returncode != 0:
        raise RuntimeError(f"Failed to ls-tree {prefix}")
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]

def download_file(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'MT2Plus-Updater'})
    with urllib.request.urlopen(req) as resp, open(dest_path, 'wb') as out:
        while chunk := resp.read(1024 * 1024):
            out.write(chunk)
    print(f"[OK] Pobrano z CDN: {dest_path}")

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    server_root = os.path.join(repo_root, 'Server')
    klient_root = os.path.join(repo_root, 'Klient')

    print(f"[*] Rozpoczynam wdrazanie upstream 2.39.0 w {repo_root}...")

    # 1. Wersje i pliki glowne
    for fname in ['VERSION', 'MOD_VERSION', 'CLIENT_VERSION', 'CHANGELOG.md', 'client-files.json', 'update-manifest-mt2009.json']:
        content = get_upstream_file(fname)
        write_file(os.path.join(server_root, fname), content)
    write_file(os.path.join(klient_root, 'CLIENT_VERSION'), get_upstream_file('CLIENT_VERSION'))

    # Narzedzia launchera i panelu admina
    for fname in ['files/admin_panel.py', 'launcher/server-update-files.mod.txt', 'linux-port/docker/panel/app/admin_panel.py']:
        write_file(os.path.join(server_root, fname), get_upstream_file(fname))

    # 2. Silnik: edits.json i README.md oraz aplikacja poprawek do char_item.cpp
    write_file(os.path.join(server_root, 'server-patches/enginefixes/README.md'),
               get_upstream_file('server-patches/enginefixes/README.md'))
    write_file(os.path.join(server_root, 'server-patches/enginefixes/edits.json'),
               get_upstream_file('server-patches/enginefixes/edits.json'))

    # Aplikacja edits 97, 98, 99 (MT2009_PLUS_SUMMON_STONE_V1) do char_item.cpp
    char_item_path = os.path.join(server_root, 'linux-port/docker/game/src/server/game/src/char_item.cpp')
    edits_raw = get_upstream_file('server-patches/enginefixes/edits.json').decode('utf-8')
    edits = json.loads(edits_raw)[97:] # nowe 3 poprawki 2.39.0
    
    ci_content = open(char_item_path, 'r', encoding='utf-8', errors='ignore').read().replace('\r\n', '\n')
    for e in edits:
        old_c = e['old'].replace('\r\n', '\n')
        new_c = e['new'].replace('\r\n', '\n')
        if old_c in ci_content:
            ci_content = ci_content.replace(old_c, new_c, 1)
            print(f"[OK] Edycja char_item.cpp: {e['marker']}")
        elif new_c in ci_content:
            print(f"[SKIP/ALREADY] Edycja char_item.cpp: {e['marker']}")
        else:
            raise RuntimeError(f"Failed to apply edit {e['marker']} to char_item.cpp")
    with open(char_item_path, 'wb') as f:
        f.write(ci_content.encode('utf-8'))
    print("[OK] Zapisano zaktualizowany char_item.cpp")

    # 3. Questy i konfiguracja runtime
    # event_halloween_hair.quest
    write_file(os.path.join(server_root, 'linux-port/docker/game/quest/event_halloween_hair.quest'),
               get_upstream_file('linux-port/docker/game/quest/event_halloween_hair.quest'))
    # special_item_group.halloween.txt
    write_file(os.path.join(server_root, 'linux-port/docker/game/special_item_group.halloween.txt'),
               get_upstream_file('linux-port/docker/game/special_item_group.halloween.txt'))

    # game/Dockerfile
    df_path = os.path.join(server_root, 'linux-port/docker/game/Dockerfile')
    upstream_df = get_upstream_file('linux-port/docker/game/Dockerfile').decode('utf-8')
    write_file(df_path, upstream_df)
    import patch_dockerfile
    patch_dockerfile.patch_dockerfile(server_root)
    print("[OK] Zaktualizowano game/Dockerfile i zabezpieczono customowe mody MT2Plus")

    # mariadb apply.sh
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

    # 4. Seban Panel
    panel_ver = get_upstream_file('linux-port/docker/seban-panel/VERSION')
    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/VERSION'), panel_ver)
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/VERSION'), panel_ver)

    # Baza klienta 2.0.70 w Seban panelu
    for f in get_tree_files('linux-port/docker/seban-panel/m2clientpack/base/2.0.70/'):
        write_file(os.path.join(server_root, f), get_upstream_file(f))

    # Aktualizacja event kinds w app.py z zachowaniem autorskich rozszerzen ekonomii i filtrow GM
    for app_path in [
        os.path.join(server_root, 'linux-port/docker/seban-panel/app.py'),
        os.path.join(server_root, 'linux-port/overlays/seban-panel/app.py'),
        os.path.join(server_root, 'server-patches/krystian/seban-panel-ekonomia/app.py'),
    ]:
        if os.path.exists(app_path):
            txt = open(app_path, 'r', encoding='utf-8').read()
            if '"halloween"' not in txt:
                txt = txt.replace('"chestdrop")', '"chestdrop",\n               # MT2009_PLUS_HALLOWEEN_V1: Halloween\n               "halloween")')
                txt = txt.replace('"flower", "easter")', '"flower", "easter", "halloween"')
                txt = txt.replace('"chestdrop": "Drop szkatułek",', '"chestdrop": "Drop szkatułek",\n    "halloween": "Halloween (dynie i Jack Pumpkin)",')
                txt = txt.replace('"chestdrop": "🧰"}', '"chestdrop": "🧰",\n               "halloween": "🎃"}')
                write_file(app_path, txt)
    print("[OK] Zaktualizowano app.py w seban-panel o event Halloween z pelnym zachowaniem ekonomii i filtrow GM")

    # 5. Playerbot C++ overlays
    pb_files_direct = [
        'playerbot_bpbots.h',
        'playerbot_chat_conversation.h',
        'playerbot_duel.h',
        'playerbot_event_rules.h',
        'playerbot_events.h',
        'playerbot_gear_upgrade.h',
        'playerbot_halloween.h',
        'playerbot_ingame_events.h',
        'playerbot_targeting.h',
        'playerbot_town.h',
        'playerbot_types.h',
        'playerbot_weapon_goal.h',
    ]
    pb_overlay_dir = os.path.join(server_root, 'linux-port/overlays/playerbot/src/game/src')
    pb_staged_dir = os.path.join(server_root, 'linux-port/docker/game/src/server/game/src')

    for pbf in pb_files_direct:
        rel = f'linux-port/overlays/playerbot/src/game/src/{pbf}'
        content = get_upstream_file(rel)
        write_file(os.path.join(pb_overlay_dir, pbf), content)
        write_file(os.path.join(pb_staged_dir, pbf), content)

    # playerbot_gear.h z zachowaniem IsPlayerBotHighValueLevel30
    gear_raw = get_upstream_file('linux-port/overlays/playerbot/src/game/src/playerbot_gear.h').decode('utf-8')
    anchor_gear = "bool IsPlayerBotL30WeaponSeller(LPCHARACTER ch)"
    high_value_block = """
	// MT2009_PLUS_HARDCORE_L30_RECYCLE_V1:
	// High value level-30 weapons on a hard server: average damage >= 25%,
	// skill damage >= 8%, or refined to +7..+9.
	// These are valuable assets: never vendored to NPC, always preserved for market or scrolls.
	bool IsPlayerBotHighValueLevel30(LPITEM item)
	{
		if (!item || !IsPlayerBotSpecialLevel30Weapon(item))
			return false;
		if (item->GetRefineLevel() >= 7)
			return true;
		const long avg = SumPlayerBotItemLines(item, APPLY_NORMAL_HIT_DAMAGE_BONUS);
		const long skill = SumPlayerBotItemLines(item, APPLY_SKILL_DAMAGE_BONUS);
		return (avg >= 25 || skill >= 8);
	}
"""
    if anchor_gear in gear_raw and 'IsPlayerBotHighValueLevel30' not in gear_raw:
        # Znajdź koniec funkcji IsPlayerBotL30WeaponSeller
        idx = gear_raw.find(anchor_gear)
        brace = gear_raw.find('}', idx)
        gear_raw = gear_raw[:brace+1] + "\n" + high_value_block + gear_raw[brace+1:]
    write_file(os.path.join(pb_overlay_dir, 'playerbot_gear.h'), gear_raw)
    write_file(os.path.join(pb_staged_dir, 'playerbot_gear.h'), gear_raw)
    print("[OK] Zaktualizowano playerbot_gear.h z zachowaniem IsPlayerBotHighValueLevel30")

    # playerbot_economy.h z zachowaniem IsPlayerBotHighValueLevel30 i wdrozeniem IsPlayerBotArcherFightingDagger
    econ_path = os.path.join(pb_overlay_dir, 'playerbot_economy.h')
    econ_txt = open(econ_path, 'r', encoding='utf-8', errors='ignore').read()
    target_econ = "FindPlayerBotStoneWeapon(ch, false) == item)"
    repl_econ = "(FindPlayerBotStoneWeapon(ch, false) == item || IsPlayerBotArcherFightingDagger(ch, item)))"
    if target_econ in econ_txt and repl_econ not in econ_txt:
        econ_txt = econ_txt.replace(target_econ, repl_econ)
        write_file(econ_path, econ_txt)
        write_file(os.path.join(pb_staged_dir, 'playerbot_economy.h'), econ_txt)
        print("[OK] Zaktualizowano playerbot_economy.h o IsPlayerBotArcherFightingDagger")

    # playerbot_manager.cpp: dodanie #include "playerbot_halloween.h"
    for mgr_path in [os.path.join(pb_overlay_dir, 'playerbot_manager.cpp'), os.path.join(pb_staged_dir, 'playerbot_manager.cpp')]:
        if os.path.exists(mgr_path):
            mgr_txt = open(mgr_path, 'r', encoding='utf-8', errors='ignore').read()
            if 'playerbot_halloween.h' not in mgr_txt:
                mgr_txt = mgr_txt.replace('#include "playerbot_yutnori.h"', '#include "playerbot_yutnori.h"\n#include "playerbot_halloween.h"')
                write_file(mgr_path, mgr_txt)
    print("[OK] Zaktualizowano playerbot_manager.cpp o include playerbot_halloween.h")

    # 6. Klient & Narzedzia Halloween
    for f in get_tree_files('client-patches/client-2.0.30/tools/halloween/'):
        write_file(os.path.join(server_root, f), get_upstream_file(f))

    # uiingameevent.py w patchu i w kliecie
    write_file(os.path.join(server_root, 'client-patches/client-2.0.30/root/uiingameevent.py'),
               get_upstream_file('client-patches/client-2.0.30/root/uiingameevent.py'))
    
    klient_ui_event = os.path.join(klient_root, 'pack/root/uiingameevent.py')
    if os.path.exists(klient_ui_event):
        evt_txt = open(klient_ui_event, 'r', encoding='utf-8', errors='ignore').read()
        if "'halloween'" not in evt_txt:
            h_def = """\t# MT2009_PLUS_HALLOWEEN_V1 (Autor: Owsap): Jack Pumpkin, the pumpkins and the wands
\t'halloween': {'name': 'Halloween', 'icon': CAL + 'halloween_event.tga', 'open': 'info',
\t\t\t'desc': 'Potwory dropi\\xb9 Upiorne Dynie, a Metiny Czarodziejskie R\\xf3\\xbfd\\xbfki - u\\xbfyj r\\xf3\\xbfd\\xbfki, a dynia zamieni si\\xea w Upiorn\\xb9 Skrzyni\\xea. Kart\\xea Maski Dyni wymienisz u Jacka Pumpkina w mie\\x9ccie.',
\t\t\t'rewards': ((30321, 1), (30322, 1), (30323, 1))},
"""
            evt_txt = evt_txt.replace("'easter':", h_def + "\t'easter':")
            evt_txt = evt_txt.replace("'easter', 'goblin',", "'easter', 'halloween', 'goblin',")
            write_file(klient_ui_event, evt_txt)
    print("[OK] Zaktualizowano uiingameevent.py o event Halloween")

    # uitooltip.py: dodanie wykluczenia 30321 (Halloween Pumpkin) przy pelnym zachowaniu szarf
    klient_tooltip = os.path.join(klient_root, 'pack/root/uitooltip.py')
    if os.path.exists(klient_tooltip):
        tt_txt = open(klient_tooltip, 'r', encoding='utf-8', errors='ignore').read()
        target_tt = "if item.USE_POTION == itemSubType or item.USE_POTION_NODELAY == itemSubType:"
        repl_tt = "if (item.USE_POTION == itemSubType or item.USE_POTION_NODELAY == itemSubType) and itemVnum != 30321:"
        if target_tt in tt_txt:
            tt_txt = tt_txt.replace(target_tt, repl_tt)
            write_file(klient_tooltip, tt_txt)
            print("[OK] Zaktualizowano uitooltip.py o weryfikacje dyni 30321")

    # Pobranie paczek halloween z oficjalnego serwera patchera
    halloween_data = os.path.join(klient_root, 'pack/halloween.data')
    halloween_index = os.path.join(klient_root, 'pack/halloween.index')
    download_file('http://141.94.100.53/patcher/files/1728150914e58f8f428211098c6ec401', halloween_data)
    download_file('http://141.94.100.53/patcher/files/07f8f2cbeba5a9ada57308e9b02c0457', halloween_index)

    # Rejestracja halloween w pack/Index
    index_path = os.path.join(klient_root, 'pack/Index')
    if os.path.exists(index_path):
        ix_bytes = open(index_path, 'rb').read()
        if b'halloween' not in ix_bytes:
            ix_bytes = ix_bytes.rstrip(b'\r\n') + b'\r\n*\r\nhalloween\r\n'
            open(index_path, 'wb').write(ix_bytes)
            print("[OK] Zarejestrowano pack/halloween w pack/Index")

    # 7. Ponowne zaaplikowanie patcha usuwającego mikstury z metinów i bossów od M2 wzwyż
    pot_patch = os.path.join(server_root, 'server-patches/krystian/brak-potek-m2-metiny-bossy/apply_patch.py')
    if os.path.exists(pot_patch):
        print("[*] Ponowna weryfikacja czystego dropu mikstur z metinow/bossow M2+...")
        subprocess.run([sys.executable, pot_patch], check=True)

    print("\n[SUCCESS] Wdrozenie upstream 2.39.0 powiodlo sie pomyslnie!")

if __name__ == '__main__':
    main()
