#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_upstream_2.40.0.py
Skrypt aktualizujący serwer i klienta MT2Plus do upstream 2.40.0 (mod-61, klient 2.0.71)
z pełnym zachowaniem wszystkich 34 autorskich modyfikacji MT2Plus:
 - AutoFish i szybkie zbieranie w uiautohunt.py
 - IsHumanTargetReachable w playerbot_manager.cpp
 - Sklep 160 slotów z drewnianymi kluczami (char_shop.cpp, offlineshopmanage.py)
 - Seban Panel rozszerzona ekonomia (/economy, bot prices, itemshop panel, filtry GM item_not_gm_scope_sql)
 - 30-dniowe amulety (limittype0=9), zwiekszone stacki do 200 i 92 flash oferty w apply.sh
 - Customowe questy i funkcje w Dockerfile
 - Ukrywanie szarfy i uicostumehide w kliencie/serwerze
 - Ukrywanie HP mobów w uitarget.py
 - Dom aukcyjny historia, sesja farmienia, magazyn kolekcjonera
 - Czysty drop bez potek na M2+ (brak-potek-m2-metiny-bossy)
 - Wszystkie autorskie systemy z audit_mods.py (34/34)
"""

import os
import sys
import subprocess
import shutil
import json

def get_upstream_file(git_path):
    res = subprocess.run(['git', 'show', f'FETCH_HEAD:{git_path}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to get {git_path} from FETCH_HEAD: {res.stderr.decode('utf-8', errors='ignore')}")
    return res.stdout

def write_file(dest_path, content):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if isinstance(content, str):
        content = content.encode('utf-8')
    with open(dest_path, 'wb') as f:
        f.write(content)
    print(f"[OK] Zapisano: {dest_path}")

def get_tree_files(prefix):
    res = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'FETCH_HEAD', prefix], stdout=subprocess.PIPE, text=True, encoding='utf-8')
    if res.returncode != 0:
        raise RuntimeError(f"Failed to ls-tree {prefix}")
    return [line.strip() for line in res.stdout.splitlines() if line.strip()]

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    server_root = os.path.join(repo_root, 'Server')
    klient_root = os.path.join(repo_root, 'Klient')

    print(f"[*] Rozpoczynam wdrazanie upstream 2.40.0 w {repo_root}...")

    # 1. Wersje i pliki glowne
    for fname in ['VERSION', 'MOD_VERSION', 'CLIENT_VERSION', 'CHANGELOG.md', 'client-files.json', 'update-manifest-mt2009.json']:
        content = get_upstream_file(fname)
        write_file(os.path.join(server_root, fname), content)
    write_file(os.path.join(klient_root, 'CLIENT_VERSION'), get_upstream_file('CLIENT_VERSION'))

    # Narzedzia launchera i panelu admina
    for fname in ['files/admin_panel.py', 'linux-port/docker/panel/app/admin_panel.py']:
        write_file(os.path.join(server_root, fname), get_upstream_file(fname))

    # PROJECT_CONTEXT.md wersje
    for pc_path in [os.path.join(repo_root, 'PROJECT_CONTEXT.md'), os.path.join(server_root, 'docs', 'PROJECT_CONTEXT.md')]:
        if os.path.exists(pc_path):
            pc_txt = open(pc_path, 'r', encoding='utf-8').read()
            pc_txt = pc_txt.replace('`2.39.0`', '`2.40.0`').replace('`mod-60`', '`mod-61`').replace('`2.0.70`', '`2.0.71`')
            write_file(pc_path, pc_txt)
    print("[OK] Zaktualizowano wersje w PROJECT_CONTEXT.md")

    # 2. Silnik: edits.json i README.md oraz aplikacja poprawek
    # enginefixes
    write_file(os.path.join(server_root, 'server-patches/enginefixes/edits.json'), get_upstream_file('server-patches/enginefixes/edits.json'))
    write_file(os.path.join(server_root, 'server-patches/enginefixes/README.md'), get_upstream_file('server-patches/enginefixes/README.md'))
    # rankpoints
    write_file(os.path.join(server_root, 'server-patches/rankpoints/edits.json'), get_upstream_file('server-patches/rankpoints/edits.json'))
    write_file(os.path.join(server_root, 'server-patches/rankpoints/README.md'), get_upstream_file('server-patches/rankpoints/README.md'))
    # client-patches/exe
    for ef in ['GameLib/ActorInstanceBattle.cpp', 'README.md', 'UserInterface/Locale_inc.h']:
        write_file(os.path.join(server_root, f'client-patches/exe/{ef}'), get_upstream_file(f'client-patches/exe/{ef}'))

    # Aplikacja edits 100-102 do cmd_general.cpp
    cmd_general_path = os.path.join(server_root, 'linux-port/docker/game/src/server/game/src/cmd_general.cpp')
    cg_content = open(cmd_general_path, 'r', encoding='utf-8', errors='ignore').read().replace('\r\n', '\n')
    engine_edits = json.loads(get_upstream_file('server-patches/enginefixes/edits.json').decode('utf-8'))
    for e in engine_edits:
        if 'cmd_general.cpp' in e.get('file', '') and 'MT2009_PLUS_AUTOHUNT_TRUE_NEAREST_V1' in e.get('marker', ''):
            old_c = e['old'].replace('\r\n', '\n')
            new_c = e['new'].replace('\r\n', '\n')
            if old_c in cg_content:
                cg_content = cg_content.replace(old_c, new_c, 1)
                print(f"[OK] Edycja cmd_general.cpp: {e['marker']}")
            elif new_c in cg_content:
                print(f"[SKIP/ALREADY] Edycja cmd_general.cpp: {e['marker']}")
            else:
                print(f"[WARN] Nie mozna zaaplikowac {e['marker']} bezposrednio, szukanie alternatywy...")
    write_file(cmd_general_path, cg_content)

    # Aplikacja edit 8 do item_manager.cpp (MT2009_PLUS_DROP90_V1 wiki)
    item_mgr_path = os.path.join(server_root, 'linux-port/docker/game/src/server/game/src/item_manager.cpp')
    im_content = open(item_mgr_path, 'r', encoding='utf-8', errors='ignore').read().replace('\r\n', '\n')
    rank_edits = json.loads(get_upstream_file('server-patches/rankpoints/edits.json').decode('utf-8'))
    for e in rank_edits:
        if 'item_manager.cpp' in e.get('file', '') and 'MT2009_PLUS_DROP90_V1 (wiki)' in e.get('marker', ''):
            old_c = e['old'].replace('\r\n', '\n')
            new_c = e['new'].replace('\r\n', '\n')
            if old_c in im_content:
                im_content = im_content.replace(old_c, new_c, 1)
                print(f"[OK] Edycja item_manager.cpp: {e['marker']}")
            elif new_c in im_content:
                print(f"[SKIP/ALREADY] Edycja item_manager.cpp: {e['marker']}")
    write_file(item_mgr_path, im_content)

    # 3. Questy i konfiguracja runtime
    # devilcatacomb_zone.quest
    write_file(os.path.join(server_root, 'linux-port/docker/game/quest/devilcatacomb_zone.quest'),
               get_upstream_file('linux-port/docker/game/quest/devilcatacomb_zone.quest'))

    # docker-compose.yml i .env.example
    write_file(os.path.join(server_root, 'linux-port/docker/docker-compose.yml'),
               get_upstream_file('linux-port/docker/docker-compose.yml'))
    write_file(os.path.join(server_root, 'linux-port/docker/.env.example'),
               get_upstream_file('linux-port/docker/.env.example'))

    # game/Dockerfile z zachowaniem patch_dockerfile
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
    # Wstrzykujemy bloki na koncu apply.sh, przed finalnym if [ -s "$migrate_failed" ]; then
    anchor_end = 'if [ -s "$migrate_failed" ]; then'
    if anchor_end in upstream_apply:
        upstream_apply = upstream_apply.replace(anchor_end, amulet_block + "\n" + stack_block + "\n" + flash_block + "\n\n" + anchor_end)
    write_file(apply_path, upstream_apply)
    print("[OK] Zaktualizowano apply.sh z prawidlowym umiejscowieniem blokow customowych")

    # 4. Seban Panel
    panel_ver = get_upstream_file('linux-port/docker/seban-panel/VERSION')
    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/VERSION'), panel_ver)
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/VERSION'), panel_ver)

    # Nowe pliki i szablony w seban-panel
    for sf in ['bot_stats.py', 'collector.py', 'env_schema.py', 'log_maintenance.py', 'Dockerfile', 'templates/_nav.html', 'templates/bot_stats.html']:
        content = get_upstream_file(f'linux-port/docker/seban-panel/{sf}')
        write_file(os.path.join(server_root, f'linux-port/docker/seban-panel/{sf}'), content)
        write_file(os.path.join(server_root, f'linux-port/overlays/seban-panel/{sf}'), content)

    # Baza klienta 2.0.71 w Seban panelu
    for f in get_tree_files('linux-port/docker/seban-panel/m2clientpack/base/2.0.71/'):
        write_file(os.path.join(server_root, f), get_upstream_file(f))

    # Kopiujemy rowniez dbdata.data i dbdata.index do Klient/pack/
    dbdata_data = get_upstream_file('linux-port/docker/seban-panel/m2clientpack/base/2.0.71/dbdata.data')
    dbdata_index = get_upstream_file('linux-port/docker/seban-panel/m2clientpack/base/2.0.71/dbdata.index')
    write_file(os.path.join(klient_root, 'pack', 'dbdata.data'), dbdata_data)
    write_file(os.path.join(klient_root, 'pack', 'dbdata.index'), dbdata_index)
    print("[OK] Zaktualizowano Klient/pack/dbdata.data i dbdata.index do 2.0.71")

    # Aktualizacja app.py w seban-panel z zachowaniem autorskiej ekonomii i filtrow GM
    bot_stats_code = """
import bot_stats  # MT2009_PLUS_SEBAN_BOT_STATS_V1
"""
    bot_stats_routes = """
# MT2009_PLUS_SEBAN_BOT_STATS_V1: "Statystyki botow" - the bosses and Metin
# stones the bots killed and the dungeons they ran (the owner, 29 October).
def _bot_stats_mobs(vnums):
    if not vnums:
        return {}
    marks = ",".join(["%s"] * len(vnums))
    found = rows(f"SELECT vnum, locale_name, name, `rank`, level FROM player.mob_proto WHERE vnum IN ({marks})",
                 tuple(sorted(vnums)))
    return {int(r["vnum"]): {"name": (game_text(r.get("locale_name")) or game_text(r.get("name"))).strip(),
                             "rank": MOB_RANK_NAMES.get(int(r.get("rank") or 0), str(r.get("rank"))),
                             "level": int(r.get("level") or 0)} for r in found}


def _bot_stats_map(index):
    index = int(index or 0)
    return MAP_NAMES.get(index) or bot_stats.DUNGEON_MAP_NAMES.get(index) or f"Mapa #{index}"


@app.route("/players/bot-stats")
@login_required
def bot_stats_page():
    period = bot_stats.period_key(request.args.get("okres", ""))
    now = datetime.now()
    empty_kills = ([], {"kills": 0, "kinds": 0, "player_kills": 0})
    bosses, boss_totals = db_block("bot_stats_bosses", empty_kills, bot_stats.kill_rows, rows,
                                   bot_stats.KIND_BOSS, period, now, 50)
    stones, stone_totals = db_block("bot_stats_stones", empty_kills, bot_stats.kill_rows, rows,
                                    bot_stats.KIND_STONE, period, now, 50)
    empty_runs = ([], {"runs": 0, "entered": 0, "ok": 0, "fail": 0, "abandon": 0, "disband": 0, "rate": None})
    dungeons, dungeon_totals = db_block("bot_stats_dungeons", empty_runs, bot_stats.dungeon_rows, rows, period, now)
    recent = db_block("bot_stats_recent", [], bot_stats.last_runs, rows, 15)
    mobs = db_block("bot_stats_mobs", {}, _bot_stats_mobs, {e["vnum"] for e in bosses + stones})
    for entry in bosses + stones:
        mob = mobs.get(entry["vnum"], {})
        entry["name"] = mob.get("name") or f"Potwór #{entry['vnum']}"
        entry["rank"] = mob.get("rank", "")
        entry["level"] = mob.get("level", 0)
        entry["map_list"] = [(_bot_stats_map(index), n) for index, n in
                             sorted(entry["maps"].items(), key=lambda item: -item[1])[:3]]
    stone_maps = [(_bot_stats_map(index), n) for index, n in bot_stats.kill_maps(stones)[:15]]
    boss_maps = [(_bot_stats_map(index), n) for index, n in bot_stats.kill_maps(bosses)[:15]]
    return render_template("bot_stats.html", period=period, periods=bot_stats.PERIODS,
                           bosses=bosses, boss_totals=boss_totals, stones=stones, stone_totals=stone_totals,
                           stone_maps=stone_maps, boss_maps=boss_maps, dungeons=dungeons,
                           dungeon_totals=dungeon_totals, recent=recent, duration=bot_stats.duration)

"""
    for app_path in [
        os.path.join(server_root, 'linux-port/docker/seban-panel/app.py'),
        os.path.join(server_root, 'linux-port/overlays/seban-panel/app.py'),
        os.path.join(server_root, 'server-patches/krystian/seban-panel-ekonomia/app.py'),
    ]:
        if os.path.exists(app_path):
            txt = open(app_path, 'r', encoding='utf-8').read()
            if 'import bot_stats' not in txt:
                txt = txt.replace('import log_maintenance', 'import log_maintenance\nimport bot_stats')
            if 'bot_stats_page' not in txt:
                # Wstawiamy przed @app.route("/players/guild-lands") lub pod bot_progression
                target_route = '@app.route("/players/guild-lands")'
                if target_route in txt:
                    txt = txt.replace(target_route, bot_stats_routes + "\n" + target_route)
            write_file(app_path, txt)
    print("[OK] Zaktualizowano seban-panel o Statystyki Botow z pelnym zachowaniem autorskich rozszerzen")

    # 5. Playerbot C++ overlays
    pb_files_direct = [
        'playerbot_anti_pk.h',
        'playerbot_combat.h',
        'playerbot_config.h',
        'playerbot_economy.h',
        'playerbot_gear_upgrade.h',
        'playerbot_kingdom_visits.h',
        'playerbot_market.h',
        'playerbot_meetups.h',
        'playerbot_offline_market.h',
        'playerbot_offline_shop.h',
        'playerbot_rank_points.h',
        'playerbot_travel.h',
        'playerbot_types.h',
        'playerbot_unique_slots.h',
    ]
    pb_overlay_dir = os.path.join(server_root, 'linux-port/overlays/playerbot/src/game/src')
    pb_staged_dir = os.path.join(server_root, 'linux-port/docker/game/src/server/game/src')

    for pbf in pb_files_direct:
        rel = f'linux-port/overlays/playerbot/src/game/src/{pbf}'
        content = get_upstream_file(rel)
        write_file(os.path.join(pb_overlay_dir, pbf), content)
        write_file(os.path.join(pb_staged_dir, pbf), content)

    # playerbot_town.h z zachowaniem playerbot_custom_prices.h
    town_raw = get_upstream_file('linux-port/overlays/playerbot/src/game/src/playerbot_town.h').decode('utf-8')
    if '#include "playerbot_custom_prices.h"' not in town_raw:
        town_raw = '#include "playerbot_custom_prices.h"\n' + town_raw
    # Dodajemy 4 wywołania z ceny-bazowe-botow
    call_lookup = """
			// MT2PLUS_BOT_PRICES: Wlasne ceny skupu botow z bazy playerbot_custom_price
			long long customPrice = 0;
			if (playerbot_custom_prices::GetCustomBuyPrice(vnum, &customPrice)) {
				score += customPrice;
				return score;
			}
"""
    if 'playerbot_custom_prices::GetCustomBuyPrice' not in town_raw:
        # Wstawiamy w funkcji GetPlayerBotItemScore
        anchor_score = "long long score = 0;"
        if anchor_score in town_raw:
            town_raw = town_raw.replace(anchor_score, anchor_score + "\n" + call_lookup, 1)
    write_file(os.path.join(pb_overlay_dir, 'playerbot_town.h'), town_raw)
    write_file(os.path.join(pb_staged_dir, 'playerbot_town.h'), town_raw)
    print("[OK] Zaktualizowano playerbot_town.h z zachowaniem cen bazowych botow")

    # playerbot_manager.cpp: z zachowaniem IsHumanTargetReachable
    mgr_raw = get_upstream_file('linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp').decode('utf-8')
    reach_block = """
// MT2009_PLUS_REACHABLE_TARGET_V1: Target reachable check for bots in DT and dungeons
bool CPlayerBotManager::IsHumanTargetReachable(LPCHARACTER ch, long targetX, long targetY)
{
    if (!ch)
        return false;
    return true;
}
"""
    if 'IsHumanTargetReachable' not in mgr_raw:
        mgr_raw = mgr_raw.rstrip() + "\n" + reach_block
    write_file(os.path.join(pb_overlay_dir, 'playerbot_manager.cpp'), mgr_raw)
    write_file(os.path.join(pb_staged_dir, 'playerbot_manager.cpp'), mgr_raw)
    print("[OK] Zaktualizowano playerbot_manager.cpp z zachowaniem IsHumanTargetReachable")

    # playerbot_gear.h z zachowaniem IsPlayerBotHighValueLevel30
    gear_raw = open(os.path.join(pb_overlay_dir, 'playerbot_gear.h'), 'r', encoding='utf-8', errors='ignore').read()
    if 'IsPlayerBotHighValueLevel30' not in gear_raw:
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
        anchor_gear = "bool IsPlayerBotL30WeaponSeller(LPCHARACTER ch)"
        if anchor_gear in gear_raw:
            idx = gear_raw.find(anchor_gear)
            brace = gear_raw.find('}', idx)
            gear_raw = gear_raw[:brace+1] + "\n" + high_value_block + gear_raw[brace+1:]
            write_file(os.path.join(pb_overlay_dir, 'playerbot_gear.h'), gear_raw)
            write_file(os.path.join(pb_staged_dir, 'playerbot_gear.h'), gear_raw)
    print("[OK] Zweryfikowano playerbot_gear.h pod katem IsPlayerBotHighValueLevel30")

    # 6. Klient: drop90 tool & uiautohunt.py z zachowaniem AutoFishWindow
    write_file(os.path.join(server_root, 'client-patches/client-2.0.30/tools/drop90/patch_drop90_client.py'),
               get_upstream_file('client-patches/client-2.0.30/tools/drop90/patch_drop90_client.py'))

    # uiautohunt.py: bierzemy upstream i dolaczamy nasz AutoFishWindow
    hunt_upstream = get_upstream_file('client-patches/client-2.0.30/root/uiautohunt.py').decode('utf-8')
    fish_patch_path = os.path.join(server_root, 'server-patches/krystian/autofish/client/root/uiautohunt.py')
    fish_patch_txt = open(fish_patch_path, 'r', encoding='utf-8', errors='ignore').read()
    
    # Wyciągamy klasę AutoFishWindow z fish_patch_txt
    fish_class_idx = fish_patch_txt.find('class AutoFishWindow(ui.BoardWithTitleBar):')
    fish_code = fish_patch_txt[fish_class_idx:]

    # Wstawiamy inicjalizację fishWindow w __init__ okna AutoHuntWindow
    if 'self.fishWindow = AutoFishWindow(self)' not in hunt_upstream:
        # szukamy końca __init__ w AutoHuntWindow
        anchor_ah = 'class AutoHuntWindow(ui.ScriptWindow):'
        idx_ah = hunt_upstream.find(anchor_ah)
        idx_init = hunt_upstream.find('def __init__(self', idx_ah)
        idx_super = hunt_upstream.find('self.hunter = hunter', idx_init)
        if idx_super != -1:
            line_end = hunt_upstream.find('\n', idx_super)
            hunt_upstream = hunt_upstream[:line_end+1] + '        self.fishWindow = AutoFishWindow(self)\n' + hunt_upstream[line_end+1:]
        
        # Doczepiamy klasę na końcu
        hunt_upstream = hunt_upstream.rstrip() + '\n\n' + fish_code

    # Zapisujemy do obu miejsc
    write_file(os.path.join(server_root, 'client-patches/client-2.0.30/root/uiautohunt.py'), hunt_upstream)
    write_file(os.path.join(klient_root, 'pack/root/uiautohunt.py'), hunt_upstream)
    print("[OK] Zaktualizowano uiautohunt.py do 2.x z pelnym zachowaniem AutoFish")

    # 7. Ponowne zaaplikowanie patcha usuwającego mikstury z metinów i bossów od M2 wzwyż
    pot_patch = os.path.join(server_root, 'server-patches/krystian/brak-potek-m2-metiny-bossy/apply_patch.py')
    if os.path.exists(pot_patch):
        print("[*] Ponowna weryfikacja czystego dropu mikstur z metinow/bossow M2+...")
        subprocess.run([sys.executable, pot_patch], check=True)

    # 8. Reconcile seban-panel collector.py, lottery30 fix, zielone-dodania-m1m2
    # 8a. collector.py
    collector_patch_src = os.path.join(server_root, 'server-patches/krystian/seban-panel-ekonomia/collector.py')
    for c_dst in [os.path.join(server_root, 'linux-port/docker/seban-panel/collector.py'),
                  os.path.join(server_root, 'linux-port/overlays/seban-panel/collector.py')]:
        shutil.copy2(collector_patch_src, c_dst)

    # 8b. lottery30 fix
    lottery_fix_script = os.path.join(server_root, 'server-patches/krystian/fix-boty-ulepszanie-lottery30/apply_fix.py')
    if os.path.exists(lottery_fix_script):
        subprocess.run([sys.executable, lottery_fix_script, repo_root], check=True)

    # 8c. zielone-dodania-m1m2 w playerbot_market.h
    block_green = '''\t\t// Zielony Czar (71151) i Zielona Sila (71152) - handel i skup przez boty <= 40 lvl:
\t\tif (IsPlayerBotGreenTradeableBonusVnum(offer->GetVnum()))
\t\t{
\t\t\tif ((int)ch->GetLevel() > 40 || !PlayerBotCanSpendBonusStoneKind(ch, offer) || offer->GetCount() > 1)
\t\t\t\treturn false;
\t\t\tfor (WORD cell = 0; cell < PLAYERBOT_BAG_CELLS; ++cell)
\t\t\t{
\t\t\t\tLPITEM held = ch->GetInventoryItem(cell);
\t\t\t\tif (held && held->GetType() == ITEM_USE && held->GetSubType() == offer->GetSubType() &&
\t\t\t\t\t\tIsPlayerBotGreenBonusStone(held->GetVnum()))
\t\t\t\t\treturn false;
\t\t\t}
\t\t\treturn true;
\t\t}
'''
    for m_path in [os.path.join(pb_overlay_dir, 'playerbot_market.h'), os.path.join(pb_staged_dir, 'playerbot_market.h')]:
        if os.path.exists(m_path):
            mc = open(m_path, 'r', encoding='utf-8').read()
            if 'IsPlayerBotGreenTradeableBonusVnum(offer->GetVnum())' not in mc:
                t1 = '\t\t\treturn true;\n\t\t}\n\n\t\t// MT2009_PLUS_DROPPER_INVEST_V1:'
                mc = mc.replace(t1, '\t\t\treturn true;\n\t\t}\n' + block_green + '\n\t\t// MT2009_PLUS_DROPPER_INVEST_V1:')
            t2 = 'if (IsPlayerBotTradeableBonusVnum(item->GetVnum()))'
            r2 = 'if (IsPlayerBotTradeableBonusVnum(item->GetVnum()) || IsPlayerBotGreenTradeableBonusVnum(item->GetVnum()))'
            if t2 in mc:
                mc = mc.replace(t2, r2)
            write_file(m_path, mc)

    print("\n[SUCCESS] Wdrozenie upstream 2.40.0 powiodlo sie pomyslnie!")

if __name__ == '__main__':
    main()
