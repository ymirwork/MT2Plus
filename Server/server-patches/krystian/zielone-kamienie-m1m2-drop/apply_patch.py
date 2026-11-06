#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modyfikacja: Drop Zielonej Siły i Zielonego Czaru w M1/M2, priorytet botów i wymiana pozwoleń
Autor: Krystian / MT2Plus

Zakres:
1. item_manager.cpp:
   - Metiny M1: 5% szansy na Zielony Czar (71151) / Zieloną Siłę (71152) (losowanie 50/50).
   - Metiny M2: 8% szansy na Zielony Czar / Zieloną Siłę.
   - Bossy M1/M2: dokładnie 15% szansy na Zielony Czar / Zieloną Siłę (Lykos, Scrofa, Bera, Tigris, Mi-Jung, Eun-Jung, Se-Rang, Jin-Hee, Mahon, Bo, Goo-Pae, Chuong, Best. Kapitan).
   - Drop zarówno dla graczy, jak i dla botów (bot otrzymuje bezpośrednio do ekwipunku, brak śmiecenia ziemi).
   - Podgląd dropu (MobPreview) oraz Drop Wiki w grze pokazują drop 71151 i 71152.
2. playerbot_targeting.h:
   - Boty <= 40 lvl poszukujące bonusów traktują Metiny M1/M2 z wysokim priorytetem (+500 000 pkt celu).
   - Boty <= 40 lvl traktują Bossy M1/M2 z priorytetem +800 000 pkt celu (lvl 41-45: +500 000 pkt celu).
3. playerbot_bonus.h & playerbot_town.h:
   - ManagePlayerBotPermitExchange: automatyczna wymiana dropniętych Pozwoleń na Zaczarowanie (30370) na handlowalne Zaczarowanie (71284) oraz Pozwoleń na Wzmocnienie (30368, 30369) na Wzmocnienie (71285).
   - Boty natychmiast używają otrzymanych bonusów na ulepszenie własnego ekwipunku, a nadmiar wystawiają w sklepach offline (Ikarus).
4. playerbot_price_tables.h:
   - Wprowadzenie wyceny katalogowej dla Pozwoleń (30368, 30369, 30370) w gospodarce botów.
"""

import os
import sys

def find_repo_root():
    curr = os.path.abspath(os.path.dirname(__file__))
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, 'PROJECT_CONTEXT.md')):
            return curr
        curr = os.path.dirname(curr)
    return os.getcwd()

def apply():
    repo = find_repo_root()
    print(f"[*] Repozytorium: {repo}")

    # 1. item_manager.cpp
    im_path = os.path.join(repo, "Server/linux-port/docker/game/src/server/game/src/item_manager.cpp")
    if os.path.exists(im_path):
        with open(im_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")

        if "MT2009_PLUS_GREEN_STONES_M1M2_DROP_V1" not in content:
            target_drop = """\t\t\t\t\telse
\t\t\t\t\t\tvec_item.push_back(cor);
\t\t\t\t}
\t\t\t}
\t\t}
\t}

\t// Szarfa (COSTUME_ACCE) drops -- operator's explicit request"""

            replacement_drop = """\t\t\t\t\telse
\t\t\t\t\t\tvec_item.push_back(cor);
\t\t\t\t}
\t\t\t}
\t\t}
\t}

\t// MT2009_PLUS_GREEN_STONES_M1M2_DROP_V1 (Task 2):
\t// - Metiny M1: 5% szansy na Zielony Czar (71151) / Zielona Sile (71152).
\t// - Metiny M2: 8% szansy na Zielony Czar / Zielona Sile.
\t// - Bossy M1/M2: dokladnie 15% szansy na Zielony Czar / Zielona Sile.
\t// - Losowanie 50/50 pomiedzy Zielona Sila a Zielonym Czarem.
\t// - Drop dla graczy i botow (bot otrzymuje bezposrednio do ekwipunku).
\tif (pkKiller &&
\t\tpkKiller->IsPC() &&
\t\tpkKiller->GetDesc() &&
\t\tquest::CQuestManager::instance().GetEventFlag("m2_green_drop_off") == 0)
\t{
\t\tint greenChance = 0;
\t\tconst char* greenKind = "none";
\t\tconst DWORD dwRace = pkChr->GetRaceNum();
\t\tconst long lMap = pkChr->GetMapIndex();

\t\tif (pkChr->IsStone())
\t\t{
\t\t\t// Metiny M1 (Shinsoo 1, Chunjo 21, Jinno 41 lub vnum 8001-8004)
\t\t\tif ((dwRace >= 8001 && dwRace <= 8004) || lMap == 1 || lMap == 21 || lMap == 41)
\t\t\t{
\t\t\t\tgreenChance = 5;
\t\t\t\tgreenKind = "stone_m1";
\t\t\t}
\t\t\t// Metiny M2 (Shinsoo 3, Chunjo 23, Jinno 43 lub vnum 8005-8007)
\t\t\telse if ((dwRace >= 8005 && dwRace <= 8007) || lMap == 3 || lMap == 23 || lMap == 43)
\t\t\t{
\t\t\t\tgreenChance = 8;
\t\t\t\tgreenKind = "stone_m2";
\t\t\t}
\t\t}
\t\telse if (pkChr->GetMobRank() >= MOB_RANK_BOSS)
\t\t{
\t\t\t// Bossy M1/M2: Lykos/Scrofa/Bera/Tigris (191-194), Biala Przysiega (391-394),
\t\t\t// Dzicy Ludzie (491-494), Best. Kapitan (591) lub kazdy boss na mapach M1/M2
\t\t\tconst bool isM1M2Boss = (dwRace >= 191 && dwRace <= 194) ||
\t\t\t\t\t\t\t\t\t(dwRace >= 391 && dwRace <= 394) ||
\t\t\t\t\t\t\t\t\t(dwRace >= 491 && dwRace <= 494) ||
\t\t\t\t\t\t\t\t\t(dwRace == 591) ||
\t\t\t\t\t\t\t\t\t((lMap == 1 || lMap == 21 || lMap == 41 || lMap == 3 || lMap == 23 || lMap == 43) && pkChr->GetLevel() <= 45);

\t\t\tif (isM1M2Boss)
\t\t\t{
\t\t\t\tgreenChance = 15;
\t\t\t\tgreenKind = "boss_m1m2";
\t\t\t}
\t\t}

\t\tif (greenChance > 0)
\t\t{
\t\t\tint roll = number(1, 100);
\t\t\tbool bWin = roll <= greenChance;

\t\t\tsys_log(0, "[GREEN_BONUS_DROP] mob_vnum=%u kind=%s map=%ld killer=%s killer_pid=%u is_bot=%d chance=%d roll=%d win=%d",
\t\t\t\tpkChr->GetRaceNum(), greenKind, lMap, pkKiller->GetName(), pkKiller->GetPlayerID(),
\t\t\t\tpkKiller->GetDesc() && pkKiller->GetDesc()->IsBot() ? 1 : 0, greenChance, roll, bWin ? 1 : 0);

\t\t\tif (bWin)
\t\t\t{
\t\t\t\tconst DWORD greenVnum = (number(1, 100) <= 50) ? 71151 : 71152;
\t\t\t\tLPITEM greenItem = CreateItem(greenVnum, 1);

\t\t\t\tsys_log(0, "[GREEN_BONUS_DROP] mob_vnum=%u kind=%s vnum=%u created=%d",
\t\t\t\t\tpkChr->GetRaceNum(), greenKind, greenVnum, greenItem ? 1 : 0);

\t\t\t\tif (greenItem)
\t\t\t\t{
\t\t\t\t\tLPCHARACTER Mt2009PlusSidekickLootReceiver(LPCHARACTER ch, long lMapIndex, long x, long y);
\t\t\t\t\tif (pkKiller->GetDesc()->IsBot() &&
\t\t\t\t\t\tMt2009PlusSidekickLootReceiver(pkKiller, pkChr->GetMapIndex(), pkChr->GetX(), pkChr->GetY()) == pkKiller)
\t\t\t\t\t{
\t\t\t\t\t\tif (pkKiller->GetEmptyInventoryEx(greenItem) != -1)
\t\t\t\t\t\t\tpkKiller->AutoGiveItem(greenItem);
\t\t\t\t\t\telse
\t\t\t\t\t\t\tM2_DESTROY_ITEM(greenItem);
\t\t\t\t\t}
\t\t\t\t\telse
\t\t\t\t\t\tvec_item.push_back(greenItem);
\t\t\t\t}
\t\t\t}
\t\t}
\t}

\t// Szarfa (COSTUME_ACCE) drops -- operator's explicit request"""

            content = content.replace(target_drop.replace('\r\n', '\n').replace('\n', '\r\n'),
                                      replacement_drop.replace('\r\n', '\n').replace('\n', '\r\n'))

            # Preview
            target_preview = """\t\t\t\tif (!clothRule || clothRule->sashChance > 0)
\t\t\t\t\tAddMobPreviewItem(lines, MT2009_PLUS_SASH_CLOTH_VNUM, Mt2009PlusSashClothCount(viewer->GetLevel()));
\t\t\t}
\t\t}
\t\t}"""

            replacement_preview = """\t\t\t\tif (!clothRule || clothRule->sashChance > 0)
\t\t\t\t\tAddMobPreviewItem(lines, MT2009_PLUS_SASH_CLOTH_VNUM, Mt2009PlusSashClothCount(viewer->GetLevel()));
\t\t\t}
\t\t}
\t\t}

\t\t// MT2009_PLUS_GREEN_STONES_M1M2_DROP_V1 (preview green):
\t\tif (quest::CQuestManager::instance().GetEventFlag("m2_green_drop_off") == 0)
\t\t{
\t\t\tconst DWORD dwR = mob->GetRaceNum();
\t\t\tconst bool isM1M2Stone = mob->IsStone() && (dwR >= 8001 && dwR <= 8007);
\t\t\tconst bool isM1M2Boss = (dwR >= 191 && dwR <= 194) || (dwR >= 391 && dwR <= 394) ||
\t\t\t\t\t\t\t\t\t(dwR >= 491 && dwR <= 494) || (dwR == 591);
\t\t\tif (isM1M2Stone || isM1M2Boss)
\t\t\t{
\t\t\t\tAddMobPreviewItem(lines, 71151, 1);
\t\t\t\tAddMobPreviewItem(lines, 71152, 1);
\t\t\t}
\t\t}"""

            content = content.replace(target_preview.replace('\r\n', '\n').replace('\n', '\r\n'),
                                      replacement_preview.replace('\r\n', '\n').replace('\n', '\r\n'))

            # Wiki
            target_wiki = """\t\t\tif (sashChance > 0)
\t\t\t\tDropWikiAdd(rows, MT2009_PLUS_SASH_CLOTH_VNUM, Mt2009PlusSashClothCount(level), sashChance / 100.0);
\t\t}

\t\t// The tables' own Moonlight chests drop only while a chest window is open."""

            replacement_wiki = """\t\t\tif (sashChance > 0)
\t\t\t\tDropWikiAdd(rows, MT2009_PLUS_SASH_CLOTH_VNUM, Mt2009PlusSashClothCount(level), sashChance / 100.0);
\t\t}

\t\t// MT2009_PLUS_GREEN_STONES_M1M2_DROP_V1 (wiki green):
\t\tif (quest::CQuestManager::instance().GetEventFlag("m2_green_drop_off") == 0)
\t\t{
\t\t\tint gChance = 0;
\t\t\tif (stone && (race >= 8001 && race <= 8004))
\t\t\t\tgChance = 5;
\t\t\telse if (stone && (race >= 8005 && race <= 8007))
\t\t\t\tgChance = 8;
\t\t\telse if (table.bRank >= MOB_RANK_BOSS && ((race >= 191 && race <= 194) || (race >= 391 && race <= 394) || (race >= 491 && race <= 494) || race == 591))
\t\t\t\tgChance = 15;

\t\t\tif (gChance > 0)
\t\t\t{
\t\t\t\tDropWikiAdd(rows, 71151, 1, (gChance / 2.0) / 100.0);
\t\t\t\tDropWikiAdd(rows, 71152, 1, (gChance / 2.0) / 100.0);
\t\t\t}
\t\t}

\t\t// The tables' own Moonlight chests drop only while a chest window is open."""

            content = content.replace(target_wiki.replace('\r\n', '\n').replace('\n', '\r\n'),
                                      replacement_wiki.replace('\r\n', '\n').replace('\n', '\r\n'))

            with open(im_path, "wb") as f:
                f.write(content.encode("utf-8"))
            print("[+] item_manager.cpp zaktualizowany!")
        else:
            print("[ ] item_manager.cpp zawiera juz nowy drop zielonych kamieni.")

    # 2. playerbot_targeting.h
    pt_path = os.path.join(repo, "Server/linux-port/overlays/playerbot/src/game/src/playerbot_targeting.h")
    if os.path.exists(pt_path):
        with open(pt_path, "rb") as f:
            pt_content = f.read().decode("utf-8", errors="ignore")

        if "MT2009_PLUS_GREEN_STONES_M1M2_DROP_V1" not in pt_content:
            target_pt_stone = """\t\t\t\t\tbaseScore = isMetinHunter ? 1500000 : PLAYERBOT_STONE_BASE_SCORE;
\t\t\t\t\tif (IsPlayerBotStoneUnderJoinableAttack(m_owner, candidate))
\t\t\t\t\t\tbaseScore += PLAYERBOT_STONE_JOIN_BONUS;"""

            replacement_pt_stone = """\t\t\t\t\tbaseScore = isMetinHunter ? 1500000 : PLAYERBOT_STONE_BASE_SCORE;
\t\t\t\t\tif (IsPlayerBotStoneUnderJoinableAttack(m_owner, candidate))
\t\t\t\t\t\tbaseScore += PLAYERBOT_STONE_JOIN_BONUS;
\t\t\t\t\t// MT2009_PLUS_GREEN_STONES_M1M2_DROP_V1 (bot metin priority):
\t\t\t\t\tif (botLevel <= 40 && candidate->GetRaceNum() >= 8001 && candidate->GetRaceNum() <= 8007)
\t\t\t\t\t\tbaseScore += 500000;"""

            target_pt_boss = """\t\t\t\t\tif (candidate->GetMobRank() >= MOB_RANK_BOSS &&
\t\t\t\t\t\t\tCountPlayerBotRaiders(candidate->GetRaceNum(), m_dwNow) >=
\t\t\t\t\t\t\t\tPLAYERBOT_RAID_SWARM_MIN)
\t\t\t\t\t\tbaseScore += PLAYERBOT_RAID_SWARM_TARGET_BONUS;"""

            replacement_pt_boss = """\t\t\t\t\tif (candidate->GetMobRank() >= MOB_RANK_BOSS &&
\t\t\t\t\t\t\tCountPlayerBotRaiders(candidate->GetRaceNum(), m_dwNow) >=
\t\t\t\t\t\t\t\tPLAYERBOT_RAID_SWARM_MIN)
\t\t\t\t\t\tbaseScore += PLAYERBOT_RAID_SWARM_TARGET_BONUS;

\t\t\t\t\t// MT2009_PLUS_GREEN_STONES_M1M2_DROP_V1 (bot boss priority):
\t\t\t\t\tif (candidate->GetMobRank() >= MOB_RANK_BOSS)
\t\t\t\t\t{
\t\t\t\t\t\tconst DWORD raceVnum = candidate->GetRaceNum();
\t\t\t\t\t\tconst long lMap = candidate->GetMapIndex();
\t\t\t\t\t\tconst bool isM1M2Boss = (raceVnum >= 191 && raceVnum <= 194) ||
\t\t\t\t\t\t\t\t\t\t\t\t(raceVnum >= 391 && raceVnum <= 394) ||
\t\t\t\t\t\t\t\t\t\t\t\t(raceVnum >= 491 && raceVnum <= 494) ||
\t\t\t\t\t\t\t\t\t\t\t\t(raceVnum == 591) ||
\t\t\t\t\t\t\t\t\t\t\t\t((lMap == 1 || lMap == 21 || lMap == 41 || lMap == 3 || lMap == 23 || lMap == 43) && candidate->GetLevel() <= 45);

\t\t\t\t\t\tif (isM1M2Boss && botLevel <= 45)
\t\t\t\t\t\t{
\t\t\t\t\t\t\tbaseScore += (botLevel <= 40) ? 800000 : 500000;
\t\t\t\t\t\t}
\t\t\t\t\t}"""

            pt_content = pt_content.replace(target_pt_stone, replacement_pt_stone)
            pt_content = pt_content.replace(target_pt_boss, replacement_pt_boss)

            with open(pt_path, "wb") as f:
                f.write(pt_content.encode("utf-8"))
            print("[+] playerbot_targeting.h zaktualizowany!")
        else:
            print("[ ] playerbot_targeting.h zawiera juz priorytety M1/M2.")

    # 3. playerbot_bonus.h
    pb_path = os.path.join(repo, "Server/linux-port/overlays/playerbot/src/game/src/playerbot_bonus.h")
    if os.path.exists(pb_path):
        with open(pb_path, "rb") as f:
            pb_content = f.read().decode("utf-8", errors="ignore")

        if "MT2009_PLUS_PERMIT_EXCHANGE_V1" not in pb_content:
            target_pb_func = """\tbool ManagePlayerBotBonusReroll(LPCHARACTER ch, TPlayerBotAIState& state, DWORD dwNow)"""

            replacement_pb_func = """\t// MT2009_PLUS_PERMIT_EXCHANGE_V1 (Task 2):
\t// Boty wymieniaja Pozwolenia na Zaczarowania/Wzmocnienia (30370, 30368, 30369)
\t// na handlowalne Zaczarowania (71284) i Wzmocnienia (71285).
\t// Nastepnie bot uzywa ich na wlasny ekwipunek, a nadmiar wystawia na sklep offline.
\tbool ManagePlayerBotPermitExchange(LPCHARACTER ch)
\t{
\t\tif (!ch || !ch->IsItemLoaded())
\t\t\treturn false;

\t\tbool convertedAny = false;
\t\tfor (WORD cell = 0; cell < PLAYERBOT_BAG_CELLS; ++cell)
\t\t{
\t\t\tLPITEM item = ch->GetInventoryItem(cell);
\t\t\tif (!item || item->isLocked())
\t\t\t\tcontinue;

\t\t\tconst DWORD vnum = item->GetVnum();
\t\t\tif (vnum == 30370) // Pozwolenie na Zaczar. Przedmiotu
\t\t\t{
\t\t\t\tDWORD count = item->GetCount();
\t\t\t\tch->RemoveSpecifyItem(30370, count);
\t\t\t\tLPITEM reward = ch->AutoGiveItem(71284, count, -1, false);
\t\t\t\tif (reward)
\t\t\t\t{
\t\t\t\t\tLogManager::instance().ItemLog(ch, reward, "PLAYERBOT_PERMIT_EXCHANGE", reward->GetName());
\t\t\t\t\tsys_log(0, "PLAYERBOT_PERMIT_EXCHANGE: pid=%u name=%s exchanged permit=30370 count=%u -> reward=71284",
\t\t\t\t\t\tch->GetPlayerID(), ch->GetName(), count);
\t\t\t\t\tconvertedAny = true;
\t\t\t\t}
\t\t\t}
\t\t\telse if (vnum == 30368 || vnum == 30369) // Pozwolenie na Wzmocn. Przedmiotu
\t\t\t{
\t\t\t\tDWORD count = item->GetCount();
\t\t\t\tch->RemoveSpecifyItem(vnum, count);
\t\t\t\tLPITEM reward = ch->AutoGiveItem(71285, count, -1, false);
\t\t\t\tif (reward)
\t\t\t\t{
\t\t\t\t\tLogManager::instance().ItemLog(ch, reward, "PLAYERBOT_PERMIT_EXCHANGE", reward->GetName());
\t\t\t\t\tsys_log(0, "PLAYERBOT_PERMIT_EXCHANGE: pid=%u name=%s exchanged permit=%u count=%u -> reward=71285",
\t\t\t\t\t\tch->GetPlayerID(), ch->GetName(), vnum, count);
\t\t\t\t\tconvertedAny = true;
\t\t\t\t}
\t\t\t}
\t\t}
\t\treturn convertedAny;
\t}

\tbool ManagePlayerBotBonusReroll(LPCHARACTER ch, TPlayerBotAIState& state, DWORD dwNow)"""

            target_pb_call = """\t\tManagePlayerBotRefinerExchange(ch);
\t\tManagePlayerBotLiquidationM1M2(ch);"""

            replacement_pb_call = """\t\tManagePlayerBotRefinerExchange(ch);
\t\tManagePlayerBotLiquidationM1M2(ch);
\t\tManagePlayerBotPermitExchange(ch);"""

            pb_content = pb_content.replace(target_pb_func.replace('\r\n', '\n').replace('\n', '\r\n'),
                                            replacement_pb_func.replace('\r\n', '\n').replace('\n', '\r\n'))
            pb_content = pb_content.replace(target_pb_call.replace('\r\n', '\n').replace('\n', '\r\n'),
                                            replacement_pb_call.replace('\r\n', '\n').replace('\n', '\r\n'))

            with open(pb_path, "wb") as f:
                f.write(pb_content.encode("utf-8"))
            print("[+] playerbot_bonus.h zaktualizowany!")
        else:
            print("[ ] playerbot_bonus.h zawiera juz wymiane pozwolen.")

    # 4. playerbot_town.h
    ptw_path = os.path.join(repo, "Server/linux-port/overlays/playerbot/src/game/src/playerbot_town.h")
    if os.path.exists(ptw_path):
        with open(ptw_path, "rb") as f:
            ptw_content = f.read().decode("utf-8", errors="ignore")

        if "ManagePlayerBotPermitExchange(ch);" not in ptw_content:
            target_ptw = """\tvoid CollectPlayerBotShopItems(LPCHARACTER ch,
\t\t\tstd::vector<std::pair<int, WORD> >& outScored, bool merchant,
\t\t\tint lowGearOnCounter = 0, bool keepOverflow = false)
\t{
\t\toutScored.clear();
\t\tif (!ch || !ch->IsItemLoaded())
\t\t\treturn;"""

            replacement_ptw = """\tvoid CollectPlayerBotShopItems(LPCHARACTER ch,
\t\t\tstd::vector<std::pair<int, WORD> >& outScored, bool merchant,
\t\t\tint lowGearOnCounter = 0, bool keepOverflow = false)
\t{
\t\toutScored.clear();
\t\tif (!ch || !ch->IsItemLoaded())
\t\t\treturn;
\t\tManagePlayerBotPermitExchange(ch);"""

            ptw_content = ptw_content.replace(target_ptw.replace('\r\n', '\n').replace('\n', '\r\n'),
                                              replacement_ptw.replace('\r\n', '\n').replace('\n', '\r\n'))

            with open(ptw_path, "wb") as f:
                f.write(ptw_content.encode("utf-8"))
            print("[+] playerbot_town.h zaktualizowany!")
        else:
            print("[ ] playerbot_town.h zawiera juz wywolanie ManagePlayerBotPermitExchange.")

    # 5. playerbot_price_tables.h
    pp_path = os.path.join(repo, "Server/linux-port/overlays/playerbot/src/game/src/playerbot_price_tables.h")
    if os.path.exists(pp_path):
        with open(pp_path, "rb") as f:
            pp_content = f.read().decode("utf-8", errors="ignore")

        if "30370" not in pp_content:
            target_pp = """\t\t{ 71151,   100000 },\t// Zielony Czar (scaled like the sheet)
\t\t{ 71152,   250000 },\t// Zielona Sila (scaled like the sheet)"""

            replacement_pp = """\t\t{ 30368,  4500000 },\t// Pozwolenie na Wzmocnienie Przedmiotu
\t\t{ 30369,  4500000 },\t// Pozwolenie na Wzmocnienie Przedmiotu (alt)
\t\t{ 30370,  1200000 },\t// Pozwolenie na Zaczarowanie Przedmiotu
\t\t{ 71151,   100000 },\t// Zielony Czar (scaled like the sheet)
\t\t{ 71152,   250000 },\t// Zielona Sila (scaled like the sheet)"""

            pp_content = pp_content.replace(target_pp.replace('\r\n', '\n').replace('\n', '\r\n'),
                                            replacement_pp.replace('\r\n', '\n').replace('\n', '\r\n'))

            with open(pp_path, "wb") as f:
                f.write(pp_content.encode("utf-8"))
            print("[+] playerbot_price_tables.h zaktualizowany!")
        else:
            print("[ ] playerbot_price_tables.h zawiera juz ceny pozwolen.")

    print("[*] Gotowe! Wszystkie pliki modyfikacji Zielone Kamienie M1/M2 i Pozwolenia zaktualizowane.")

if __name__ == '__main__':
    apply()
