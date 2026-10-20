#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_upstream_2.36.0.py
Skrypt aktualizujący serwer i klienta MT2Plus do upstream 2.36.0 (mod-57, klient 2.0.67)
przy pełnym zachowaniu customowych systemów (YmirWork / Krystian):
 - IsHumanTargetReachable w CPlayerBotManager (playerbot_manager.h / playerbot_manager.cpp)
 - Sklep 160 slotów z drewnianymi kluczami (ikarus_shop_manager.cpp / offlineshopmanage.py)
 - Seban Panel rozszerzona ekonomia (trasy /economy, doradca emerytur, M1/M2 likwidacja, cache)
 - Optymalizacje collector.py (executemany) oraz prune_old_snapshots
 - 30-dniowe amulety i zwiekszone stacki w mariadb/playerbot/apply.sh
 - Customowe questy w Dockerfile (recykling_bonusow, shop_unlock_slots)
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

    print(f"[*] Rozpoczynam wdrazanie upstream 2.36.0 w {repo_root}...")

    # 1. Wersje i pliki glowne
    for fname in ['VERSION', 'MOD_VERSION', 'CLIENT_VERSION', 'CHANGELOG.md', 'client-files.json', 'update-manifest-mt2009.json']:
        content = get_upstream_file(fname)
        write_file(os.path.join(server_root, fname), content)
    write_file(os.path.join(klient_root, 'CLIENT_VERSION'), get_upstream_file('CLIENT_VERSION'))

    # 2. Narzedzia, konfiguracja i server-patches
    for tf in [
        'linux-port/docker/mariadb/conf.d/99-metin2.cnf',
        'linux-port/docker/.env.example',
        'linux-port/tools/update.sh',
        'start-server.ps1',
        'tools/port/Apply-MT2009PlusEngine.ps1',
        'files/admin_panel.py',
        'linux-port/docker/panel/app/admin_panel.py',
        'server-patches/enginefixes/README.md',
        'server-patches/enginefixes/edits.json',
        'server-patches/autohuntnorevenge/Apply-AutoHuntNoRevengePatch.ps1',
        'server-patches/autohuntnorevenge/apply_autohuntnorevenge.py',
        'server-patches/autohuntnorevenge/edits.json',
    ]:
        write_file(os.path.join(server_root, tf), get_upstream_file(tf))

    # docker-compose.yml (dodanie DB_LOG_RETENTION_DAYS)
    dc_path = os.path.join(server_root, 'linux-port/docker/docker-compose.yml')
    dc_text = open(dc_path, 'r', encoding='utf-8').read()
    if 'DB_LOG_RETENTION_DAYS' not in dc_text:
        marker = 'SEBAN_COLLECTOR_INTERVAL: "${M2_SEBAN_COLLECTOR_INTERVAL:-300}"\n'
        addition = ('      # MT2009_PLUS_DB_LOG_RETENTION_V1: days of the log database the collector\n'
                    '      # keeps (0 = all). Absent from an .env made before 2.36: 0, nothing is\n'
                    '      # deleted until the owner chooses; .env.example ships 14 for a new one.\n'
                    '      DB_LOG_RETENTION_DAYS: "${M2_DB_LOG_RETENTION_DAYS:-0}"\n')
        if marker in dc_text:
            dc_text = dc_text.replace(marker, marker + addition)
            write_file(dc_path, dc_text)
            print("[OK] Dodano DB_LOG_RETENTION_DAYS do docker-compose.yml")

    # 3. Questy
    quests = [
        'linux-port/docker/game/quest/biblioteka_wiedzy.quest',
        'linux-port/docker/game/quest/collect_quest_lv70.quest',
        'linux-port/docker/game/quest/devilcatacomb_zone.quest',
        'linux-port/docker/game/quest/deviltower_zone.quest',
        'linux-port/docker/game/quest/nemere_dungeon.quest',
        'linux-port/docker/game/quest/razador_dungeon.quest',
        'linux-port/docker/game/quest/ruiny_atlantydy.quest',
        'linux-port/docker/game/quest/ruiny_skorpiona.quest',
        'linux-port/docker/game/quest/starozytna_dzungla.quest',
        'linux-port/docker/game/quest/wzgorze_wukonga.quest',
    ]
    for q in quests:
        write_file(os.path.join(server_root, q), get_upstream_file(q))

    # game/Dockerfile (dodanie collect_quest_lv70 przy zachowaniu customowych questow)
    df_path = os.path.join(server_root, 'linux-port/docker/game/Dockerfile')
    df_text = open(df_path, 'r', encoding='utf-8').read()
    if 'collect_quest_lv70' not in df_text:
        df_text = df_text.replace('collect_quest_lv85 towarzysz', 'collect_quest_lv85 collect_quest_lv70 towarzysz')
        # Dodanie takze komentarza
        com_marker = '# collect_quest_lv85 is the Biologist\'s red-branch row with its hand-in'
        com_add = ('    # collect_quest_lv70 drops its Konar Zelkova (30165) whatever the bag\n'
                   '    # already holds - the branch stacks (MT2009_PLUS_UPSTREAM_BOTLOGIC_ZELKOVA_V1).\n')
        idx = df_text.find(com_marker)
        if idx != -1:
            df_text = df_text[:idx] + com_add + df_text[idx:]
        write_file(df_path, df_text)
        print("[OK] Dodano collect_quest_lv70 do game/Dockerfile")

    # mariadb apply.sh (Konar Zelkova stack 200 przy zachowaniu custom amuletow i stackow)
    apply_path = os.path.join(server_root, 'linux-port/docker/mariadb/playerbot/apply.sh')
    apply_text = open(apply_path, 'r', encoding='utf-8').read()
    if 'Konar Zelkova (30165)' not in apply_text:
        marker = 'db -e "UPDATE world.item_proto SET flag = flag | 4 WHERE vnum = 30202 AND (flag & 4) = 0;" || fail_step "could not make Tanaka\'s ear stack" >&2\n'
        addition = ('# MT2009_PLUS_UPSTREAM_BOTLOGIC_ZELKOVA_V1: Konar Zelkova (30165), the\n'
                    '# Biologist\'s level-70 branch, stacks to 200: collect_quest_lv70.quest now\n'
                    '# drops one whatever the bag holds. Idempotent; never lowers a stack.\n'
                    'db -e "UPDATE world.item_proto SET flag = flag | 4, stack = GREATEST(stack, 200) WHERE vnum = 30165 AND ((flag & 4) = 0 OR stack < 200);" || fail_step "could not make Konar Zelkova stack" >&2\n')
        if marker in apply_text:
            apply_text = apply_text.replace(marker, marker + addition)
            write_file(apply_path, apply_text)
            print("[OK] Dodano Zelkova stack do apply.sh")

    # 4. Seban Panel
    # Kopiowanie nowych/zaktualizowanych plikow panelu
    seban_copies = [
        'linux-port/docker/seban-panel/VERSION',
        'linux-port/docker/seban-panel/Dockerfile',
        'linux-port/docker/seban-panel/log_maintenance.py',
        'linux-port/docker/seban-panel/templates/db_logs.html',
        'linux-port/docker/seban-panel/templates/_nav.html',
        'linux-port/docker/seban-panel/test_panel_db_guard.py',
        'linux-port/docker/seban-panel/env_schema.py',
    ]
    for sc in seban_copies:
        content = get_upstream_file(sc)
        write_file(os.path.join(server_root, sc), content)
        # Mirror to overlays/seban-panel
        overlay_rel = sc.replace('linux-port/docker/seban-panel/', '')
        if overlay_rel != 'Dockerfile':
            write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel', overlay_rel), content)

    # collector.py: zachowaj nasze executemany i prune_old_snapshots, dodaj log_maintenance
    col_path = os.path.join(server_root, 'linux-port/docker/seban-panel/collector.py')
    col_text = open(col_path, 'r', encoding='utf-8').read()
    if 'import log_maintenance' not in col_text:
        col_text = col_text.replace('import pymysql\n', 'import pymysql\n\nimport log_maintenance\n')
    if 'log_maintenance.run_cycle' not in col_text:
        m_marker = 'print("[seban-collector] snapshot complete", flush=True)\n'
        m_addition = ('            # MT2009_PLUS_DB_LOG_RETENTION_V1: the log summaries and the daily\n'
                      '            # prune, on a connection of their own without the panel\'s\n'
                      '            # statement limit; a failure there never stops the snapshots.\n'
                      '            try:\n'
                      '                maintenance = log_maintenance.connect()\n'
                      '                try:\n'
                      '                    log_maintenance.run_cycle(maintenance)\n'
                      '                finally:\n'
                      '                    maintenance.close()\n'
                      '            except Exception as exc:\n'
                      '                print(f"[seban-collector] log maintenance: {exc}", flush=True)\n')
        col_text = col_text.replace(m_marker, m_marker + m_addition)
    write_file(col_path, col_text)
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/collector.py'), col_text)
    print("[OK] Zaktualizowano collector.py")

    # templates/manage.html
    upstream_manage = get_upstream_file('linux-port/docker/seban-panel/templates/manage.html').decode('utf-8')
    # Przywrocenie czerwonego ostrzezenia o Drop Yang
    yang_warning = '<p style="color:#e53935;font-weight:700">⚠️ Drop Yang: CENY I BOTY SĄ ZOPTYMALIZOWANE POD DROP 100%, ustawiając więcej, psujesz sobie rozgrywkę, a na serwerze będzie wielka inflacja, a ceny będą przesadzone.</p>'
    if yang_warning not in upstream_manage:
        sub_marker = '<div class="manage-form restart-settings">{% for key,label in [(\'exp\',\'Doświadczenie\'),(\'drop\',\'Drop przedmiotów\'),(\'yang\',\'Drop Yang\')] %}<label>{{label}} <input required type="number" min="1" max="{{ 1000 if key == \'yang\' else 10000 }}" name="{{key}}" value="{{rates[key]}}"><small>%</small></label>{% endfor %}</div>'
        if sub_marker in upstream_manage:
            upstream_manage = upstream_manage.replace(sub_marker, sub_marker + '\n' + yang_warning)
    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/templates/manage.html'), upstream_manage)
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/templates/manage.html'), upstream_manage)

    # templates/player.html (dodanie guardu gear_history is none)
    player_path = os.path.join(server_root, 'linux-port/docker/seban-panel/templates/player.html')
    player_text = open(player_path, 'r', encoding='utf-8').read()
    if '{% if gear_history is none %}' not in player_text:
        old_part = '<div class="log-lines" id="gear-history-lines">{% for line in gear_history %}'
        new_part = '<div class="log-lines" id="gear-history-lines">{% if gear_history is none %}<p class="muted">Historia chwilowo niedostępna — baza nie odpowiedziała na czas. Reszta profilu działa; odśwież stronę za chwilę.</p>{% else %}{% for line in gear_history %}'
        end_old = '{% else %}<p class="muted">Brak zapisanych zdarzeń ekwipunku.</p>{% endfor %}</div>'
        end_new = '{% else %}<p class="muted">Brak zapisanych zdarzeń ekwipunku.</p>{% endfor %}{% endif %}</div>'
        player_text = player_text.replace(old_part, new_part).replace(end_old, end_new)
        write_file(player_path, player_text)
        write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/templates/player.html'), player_text)
        print("[OK] Zaktualizowano player.html")

    # app.py 3-way merge
    base_app = get_upstream_file('linux-port/docker/seban-panel/app.py') # z v2.35.0
    res_base = subprocess.run(['git', 'show', 'v2.35.0:linux-port/docker/seban-panel/app.py'], stdout=subprocess.PIPE)
    base_app = res_base.stdout
    theirs_app = get_upstream_file('linux-port/docker/seban-panel/app.py') # z upstream/main
    ours_app = open(os.path.join(server_root, 'linux-port/docker/seban-panel/app.py'), 'rb').read().replace(b'\r\n', b'\n')

    t_base = os.path.join(server_root, 'temp_base.py')
    t_theirs = os.path.join(server_root, 'temp_theirs.py')
    t_ours = os.path.join(server_root, 'temp_ours.py')
    open(t_base, 'wb').write(base_app)
    open(t_theirs, 'wb').write(theirs_app)
    open(t_ours, 'wb').write(ours_app)

    merge_res = subprocess.run(['git', 'merge-file', '-p', t_ours, t_base, t_theirs], stdout=subprocess.PIPE)
    lines = merge_res.stdout.decode('utf-8', errors='replace').splitlines()
    for f in [t_base, t_theirs, t_ours]:
        if os.path.exists(f): os.remove(f)

    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('<<<<<<<'):
            conflict_ours = []
            conflict_theirs = []
            is_theirs = False
            i += 1
            while i < len(lines) and not lines[i].startswith('>>>>>>>'):
                if lines[i].startswith('======='):
                    is_theirs = True
                elif not is_theirs:
                    conflict_ours.append(lines[i])
                else:
                    conflict_theirs.append(lines[i])
                i += 1
            i += 1  # skip >>>>>>>

            theirs_str = '\n'.join(conflict_theirs)
            if 'stall_sales_total' in theirs_str:
                out.extend(conflict_theirs)
            elif 'transactions_total' in theirs_str:
                out.append('        "transactions_total": db_block("economy_shops.total", 0, stall_sales_total),')
                out.append('        "transactions_period": tx_period,')
            elif 'all_sales_velocity' in theirs_str:
                out.append('    all_sales_velocity = db_block("economy_shops.velocity", [], shop_sales_velocity, hours=hours, limit=None)')
            elif 'render_template("economy_shops.html"' in theirs_str:
                out.append('    rendered = render_template("economy_shops.html", latest=latest, by_map=by_map, query=query, hours=hours,')
                out.append('                               empire_totals=empire_totals, kpi=kpi, value_trend=value_trend,')
                out.append('                               market_items=market_items, fastest_items_limit=fastest_items_limit,')
                out.append('                               sales_velocity=all_sales_velocity[:fastest_items_limit],')
                out.append('                               skillbook_velocity=db_block("economy_shops.skillbooks", [], shop_sales_velocity,')
                out.append('                                                           hours=hours, limit=5, only_skillbooks=True),')
                out.append('                               recent_sales=db_block("economy_shops.recent", [], recent_shop_sales, 10))')
                out.append('    _ECONOMY_SHOPS_CACHE[cache_key] = {"ts": now_ts, "html": rendered}')
                out.append('    return rendered')
            else:
                raise RuntimeError(f"Unknown conflict:\nOurs: {conflict_ours}\nTheirs: {conflict_theirs}")
        else:
            out.append(line)
            i += 1

    merged_text = '\n'.join(out)
    if '<<<<<<<' in merged_text:
        raise RuntimeError("Pozostaly nierozwiazane konflikty w app.py!")

    write_file(os.path.join(server_root, 'linux-port/docker/seban-panel/app.py'), merged_text)
    write_file(os.path.join(server_root, 'linux-port/overlays/seban-panel/app.py'), merged_text)
    print("[OK] Zmerge'owano seban-panel/app.py bez konfliktow!")

    # 5. Nagłówki Playerbot C++ (20 nagłówków)
    pb_headers = [
        'playerbot_anti_pk.h',
        'playerbot_config.h',
        'playerbot_economy.h',
        'playerbot_explain_rules.h',
        'playerbot_gear.h',
        'playerbot_lpp.h',
        'playerbot_market.h',
        'playerbot_market_life.h',
        'playerbot_offline_market.h',
        'playerbot_offline_policy.h',
        'playerbot_offline_shop.h',
        'playerbot_persona.h',
        'playerbot_persona_rules.h',
        'playerbot_progression_needs.h',
        'playerbot_stone4.h',
        'playerbot_town.h',
        'playerbot_travel.h',
        'playerbot_types.h',
        'playerbot_upstream_botlogic.h',
        'playerbot_world_memory.h',
    ]
    for pbh in pb_headers:
        rel = f'linux-port/overlays/playerbot/src/game/src/{pbh}'
        write_file(os.path.join(server_root, rel), get_upstream_file(rel))

    # playerbot_manager.h (zachowanie IsHumanTargetReachable i dodanie OnAutoHunt)
    pbm_h_path = os.path.join(server_root, 'linux-port/overlays/playerbot/src/game/src/playerbot_manager.h')
    pbm_h_text = get_upstream_file('linux-port/overlays/playerbot/src/game/src/playerbot_manager.h').decode('utf-8')
    if 'IsHumanTargetReachable' not in pbm_h_text:
        target_marker = 'int\t\tPlanHumanPath(LPCHARACTER ch, long targetX, long targetY, std::vector<std::pair<long, long> >& out);\n'
        addition = '\t\tbool\tIsHumanTargetReachable(LPCHARACTER ch, long targetX, long targetY);\n'
        pbm_h_text = pbm_h_text.replace(target_marker, target_marker + addition)
    write_file(pbm_h_path, pbm_h_text)
    print("[OK] Zaktualizowano playerbot_manager.h z zachowaniem IsHumanTargetReachable")

    # playerbot_manager.cpp (aktualizacja upstream + dopisanie IsHumanTargetReachable na koncu)
    pbm_cpp_path = os.path.join(server_root, 'linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp')
    pbm_cpp_text = get_upstream_file('linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp').decode('utf-8')
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
    if 'bool CPlayerBotManager::IsHumanTargetReachable' not in pbm_cpp_text:
        pbm_cpp_text = pbm_cpp_text.rstrip() + "\n" + reachable_impl
    write_file(pbm_cpp_path, pbm_cpp_text)
    print("[OK] Zaktualizowano playerbot_manager.cpp z zachowaniem IsHumanTargetReachable")

    # ikarus_shop_manager.cpp (aktualizacja z upstream zmianami DS + 4 strony botow + 160 slotow gracza na klucze)
    ika_path = os.path.join(server_root, 'linux-port/overlays/playerbot/src/game/src/ikarus_shop_manager.cpp')
    ika_text = open(ika_path, 'r', encoding='utf-8').read()
    # 1. IkashopHasRoomFor helper
    if 'IkashopHasRoomFor' not in ika_text:
        helper_code = """// MT2009_PLUS_IKASHOP_DS_V1 (helper) (server-patches/enginefixes): a Dragon Soul stone from an offline
// shop goes to the Dragon Soul inventory (CanTakeInventoryItem), so the room asked for before a buy
// or a take-back is there - HasSlotForItem only looks at the bag. A stone for someone without the
// Dragon Soul inventory open (DragonSoul_IsQualified) finds no room.
template <typename TShopLine>
static bool IkashopHasRoomFor(LPCHARACTER ch, const TShopLine& line)
{
	const TItemTable* proto = ITEM_MANAGER::instance().GetTable(line->GetVnum());
	if (!proto || proto->bType != ITEM_DS)
		return ch->HasSlotForItem(line->GetVnum());
	if (!ch->DragonSoul_IsQualified())
	{
		ch->ChatPacket(CHAT_TYPE_INFO, "Najpierw odblokuj Smocza Alchemie - kamien trafia do jej okna.");
		return false;
	}
	LPITEM probe = line->CreateItem();
	if (!probe)
		return false;
	TItemPos pos;
	const bool room = ch->CanTakeInventoryItem(probe, &pos);
	probe->SetSkipSave(true);
	M2_DESTROY_ITEM(probe);
	return room;
}

void MoveAndDestroyInstance(LPITEM item, BYTE window, WORD pos)"""
        ika_text = ika_text.replace('void MoveAndDestroyInstance(LPITEM item, BYTE window, WORD pos)', helper_code)

    # 2. buy & take back: zamiana HasSlotForItem na IkashopHasRoomFor
    ika_text = ika_text.replace(
        'if (!ch->HasSlotForItem(pitem->GetVnum()))',
        'if (!IkashopHasRoomFor(ch, pitem)) // MT2009_PLUS_IKASHOP_DS_V1 (buy): a stone\'s room is in the DS inventory'
    )
    ika_text = ika_text.replace(
        'if (!ch->HasSlotForItem(shopItem->GetVnum()))',
        'if (!IkashopHasRoomFor(ch, shopItem)) // MT2009_PLUS_IKASHOP_DS_V1 (take back)'
    )

    # 3. 4-page bot shop check and destPos bounds
    old_dest_check = """		if (destPos < 0 || destPos >= SHOP_PLAYER_WIDTH * SHOP_PLAYER_HEIGHT * 2 ||
            !ch->CanAddItemToShop(item, destPos))
			return false;"""
    new_dest_check = """		if (destPos < 0 || destPos >= SHOP_PLAYER_WIDTH * SHOP_PLAYER_HEIGHT * playerbot_offline::BOT_SHOP_PAGES)
			return false;

		// MT2009_PLUS_BOT_SHOP_PAGES4_V1 (slot): the premium and locked cells are the first page's; a cell past it
		// is asked as the first cell past it - CanAddItemToShop takes a BYTE, and a bot's fourth page (240-319) wrapped
		if (!ch->CanAddItemToShop(item, destPos < SHOP_PLAYER_WIDTH * SHOP_PLAYER_HEIGHT ? destPos : SHOP_PLAYER_WIDTH * SHOP_PLAYER_HEIGHT))
			return false;"""
    if old_dest_check in ika_text:
        ika_text = ika_text.replace(old_dest_check, new_dest_check)

    old_person_check = """		if (secondPage && !(ch->GetDesc() && ch->GetDesc()->IsBot()) && !ikashop_qol::BigShopsOn() && !ch->CanAddItemToShop(item, destPos))
		{
			ch->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("SHOP_ITEM_WRONG_POS"));
			return false;
		}"""
    new_person_check = """		// MT2009_PLUS_BOT_SHOP_PAGES4_V1 (person): a bot's stand has playerbot_offline::BOT_SHOP_PAGES pages (four,
		// 320 cells); a person's never more than the two of the bigger shops switch or wood key unlock
		if (destPos >= SHOP_PLAYER_WIDTH * SHOP_PLAYER_HEIGHT * 2 && !(ch->GetDesc() && ch->GetDesc()->IsBot()))
		{
			ch->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("SHOP_ITEM_WRONG_POS"));
			return false;
		}
		if (secondPage && !(ch->GetDesc() && ch->GetDesc()->IsBot()) && !ikashop_qol::BigShopsOn() && !ch->CanAddItemToShop(item, destPos))
		{
			ch->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("SHOP_ITEM_WRONG_POS"));
			return false;
		}"""
    if old_person_check in ika_text and 'MT2009_PLUS_BOT_SHOP_PAGES4_V1 (person)' not in ika_text:
        ika_text = ika_text.replace(old_person_check, new_person_check)

    write_file(ika_path, ika_text)
    print("[OK] Zaktualizowano ikarus_shop_manager.cpp")

    # 6. Klient (offlineshopguest, uiautohunt, offlineshopmanage)
    # offlineshopguest.py
    guest_content = get_upstream_file('client-patches/client-2.0.30/root/offlineshopguest.py')
    write_file(os.path.join(server_root, 'client-patches/client-2.0.30/root/offlineshopguest.py'), guest_content)
    write_file(os.path.join(klient_root, 'pack/root/offlineshopguest.py'), guest_content)

    # uiautohunt.py
    autohunt_content = get_upstream_file('client-patches/client-2.0.30/root/uiautohunt.py')
    write_file(os.path.join(server_root, 'client-patches/client-2.0.30/root/uiautohunt.py'), autohunt_content)
    write_file(os.path.join(klient_root, 'pack/root/uiautohunt.py'), autohunt_content)

    # Re-apply custom autofish patch
    autofish_patch = os.path.join(server_root, 'server-patches/krystian/autofish/client/root/uiautohunt.py')
    if os.path.exists(autofish_patch):
        shutil.copy2(autofish_patch, os.path.join(klient_root, 'pack/root/uiautohunt.py'))
        shutil.copy2(autofish_patch, os.path.join(server_root, 'client-patches/client-2.0.30/root/uiautohunt.py'))
        print("[OK] Przywrocono AutoFishWindow do Klient/pack/root/uiautohunt.py i client-patches")
    game_patch = os.path.join(server_root, 'server-patches/krystian/autofish/client/root/game.py')
    if os.path.exists(game_patch):
        shutil.copy2(game_patch, os.path.join(klient_root, 'pack/root/game.py'))
        shutil.copy2(game_patch, os.path.join(server_root, 'client-patches/client-2.0.30/root/game.py'))
        print("[OK] Przywrocono AutoFishStatus do Klient/pack/root/game.py i client-patches")

    # offlineshopmanage.py
    manage_py_path = os.path.join(klient_root, 'pack/root/offlineshopmanage.py')
    manage_py_text = open(manage_py_path, 'r', encoding='utf-8').read()
    if 'SLOT_TYPE_DRAGON_SOUL_INVENTORY' not in manage_py_text:
        target = "	def OnSelectEmptySlot(self, inventorySlotIndex, shopSlotIndex, inventoryWindowType, itemVnum, itemCount):\n		self.visualState.OnSelectEmptySlot(self, inventorySlotIndex, shopSlotIndex, inventoryWindowType, itemVnum, itemCount)"
        replacement = """	def OnSelectEmptySlot(self, inventorySlotIndex, shopSlotIndex, inventoryWindowType, itemVnum, itemCount):
		# MT2009_PLUS_IKASHOP_DS_V1: the shop grids hand over the mouse's slot
		# type, not the window - the same number for the bag (1), another for
		# the Dragon Soul inventory (11 against window 5), so a Dragon Soul
		# stone was looked up and sent from a window that does not exist.
		if inventoryWindowType == player.SLOT_TYPE_DRAGON_SOUL_INVENTORY:
			inventoryWindowType = player.SlotTypeToInvenType(inventoryWindowType)
		self.visualState.OnSelectEmptySlot(self, inventorySlotIndex, shopSlotIndex, inventoryWindowType, itemVnum, itemCount)"""
        if target in manage_py_text:
            manage_py_text = manage_py_text.replace(target, replacement)
            write_file(manage_py_path, manage_py_text)
            write_file(os.path.join(server_root, 'client-patches/client-2.0.30/root/offlineshopmanage.py'), manage_py_text)
            print("[OK] Zaktualizowano offlineshopmanage.py o obsluge Smoczej Alchemii")

    print("\n[SUCCESS] Wdrozenie upstream 2.36.0 powiodlo sie pomyslnie!")

if __name__ == '__main__':
    main()
