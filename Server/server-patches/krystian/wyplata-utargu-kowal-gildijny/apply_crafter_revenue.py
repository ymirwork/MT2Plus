#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_crafter_revenue.py
Modyfikacja serwerowa Metin2: Wyplata utargu z ulepszen i przetopow u rzemieslnikow gildyjnych.
Umozliwia Liderowi gildii wyplate srodkow zebranych z ulepszen (pula startuje od 0 Yang)
zarowno u Straznika Wsi (11000, 11002, 11004) jak i bezposrednio u rzemieslnikow gildyjnych (20044, 20045, 20046).
Podatek cesarski (15%) stanowi permanentny gold sink.
Zapisuje stan do MySQL (tabela player.guild_crafter_revenue oraz flagi eventowe player.quest).
Autor: Krystian (MT2Plus)
"""

import os
import sys
import shutil
import argparse

def patch_file(file_path, old_text, new_text, description):
    if not os.path.isfile(file_path):
        print(f"[!] Nie znaleziono pliku: {file_path}")
        return False

    with open(file_path, "rb") as f:
        raw_bytes = f.read()

    is_crlf = b"\r\n" in raw_bytes
    content = raw_bytes.decode("latin1")

    content_normalized = content.replace("\r\n", "\n")
    old_normalized = old_text.replace("\r\n", "\n")
    new_normalized = new_text.replace("\r\n", "\n")

    if new_normalized in content_normalized:
        print(f"[OK] {description} - juz zaaplikowane.")
        return True

    if old_normalized in content_normalized:
        content_normalized = content_normalized.replace(old_normalized, new_normalized, 1)
        if is_crlf:
            result_bytes = content_normalized.replace("\n", "\r\n").encode("latin1")
        else:
            result_bytes = content_normalized.encode("latin1")

        with open(file_path, "wb") as f:
            f.write(result_bytes)
        print(f"[+] Zastosowano: {description}")
        return True

    print(f"[!] Nie znaleziono oryginalnego fragmentu dla: {description}")
    return False

def main():
    parser = argparse.ArgumentParser(description="Aplikuj system wyplaty utargu rzemieslnikow gildyjnych")
    parser.add_argument("--server-dir", default=".", help="Sciezka do glownego katalogu Server/ lub repozytorium")
    args = parser.parse_args()

    server_dir = os.path.abspath(args.server_dir)

    def find_file(rel_paths):
        for p in rel_paths:
            full = os.path.join(server_dir, p)
            if os.path.isfile(full):
                return full
            full_sub = os.path.join(server_dir, "Server", p)
            if os.path.isfile(full_sub):
                return full_sub
        return None

    guild_h_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "server", "game", "src", "guild.h"),
        os.path.join("game", "src", "guild.h")
    ])
    guild_cpp_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "server", "game", "src", "guild.cpp"),
        os.path.join("game", "src", "guild.cpp")
    ])
    char_cpp_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "server", "game", "src", "char.cpp"),
        os.path.join("game", "src", "char.cpp")
    ])
    input_login_cpp_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "server", "game", "src", "input_login.cpp"),
        os.path.join("game", "src", "input_login.cpp")
    ])
    questlua_guild_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "server", "game", "src", "questlua_guild.cpp"),
        os.path.join("game", "src", "questlua_guild.cpp")
    ])
    quest_functions_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "serverfiles", "share", "locale", "poland", "quest", "quest_functions"),
        os.path.join("quest", "quest_functions")
    ])
    questlib_lua_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "serverfiles", "share", "locale", "poland", "quest", "questlib.lua"),
        os.path.join("quest", "questlib.lua")
    ])
    dockerfile_file = find_file([
        os.path.join("linux-port", "docker", "game", "Dockerfile"),
        os.path.join("docker", "game", "Dockerfile")
    ])
    quest_dest_dir = find_file([
        os.path.join("linux-port", "docker", "game", "quest", "guild_building.quest"),
        os.path.join("quest", "guild_building.quest")
    ])
    if quest_dest_dir:
        quest_dest_dir = os.path.dirname(quest_dest_dir)

    print(f"[*] guild.h: {guild_h_file}")
    print(f"[*] guild.cpp: {guild_cpp_file}")
    print(f"[*] char.cpp: {char_cpp_file}")
    print(f"[*] input_login.cpp: {input_login_cpp_file}")
    print(f"[*] questlua_guild.cpp: {questlua_guild_file}")
    print(f"[*] quest_functions: {quest_functions_file}")
    print(f"[*] questlib.lua: {questlib_lua_file}")
    print(f"[*] Dockerfile: {dockerfile_file}")

    # 1. guild.h: deklaracja SendGuildPayout
    old_guild_h = """\t\tvoid\t\tChat(const char* c_pszText);
\t\tvoid\t\tP2PChat(const char* c_pszText);"""

    new_guild_h = """\t\tvoid\t\tChat(const char* c_pszText);
\t\tvoid\t\tP2PChat(const char* c_pszText);
\t\tvoid\t\tSendGuildPayout(int amount);"""

    patch_file(guild_h_file, old_guild_h, new_guild_h, "guild.h: Deklaracja SendGuildPayout")

    # 2. guild.cpp: implementacja SendGuildPayout oraz wysylka przy SendGuildInfoPacket
    old_guild_info = """\td->BufferedPacket(pack);
\td->Packet(pack_sub);
}"""

    new_guild_info = """\td->BufferedPacket(pack);
\td->Packet(pack_sub);

\t// MT2009_PLUS_CRAFTER_REVENUE_V1: sync payout on guild info window open/refresh
\tchar szFlag[64];
\tsnprintf(szFlag, sizeof(szFlag), "guild_payout_%u", m_data.guild_id);
\tint payout = quest::CQuestManager::instance().GetEventFlag(szFlag);
\tch->ChatPacket(CHAT_TYPE_COMMAND, "GuildPayout %d", payout);
}"""

    patch_file(guild_cpp_file, old_guild_info, new_guild_info, "guild.cpp: SendGuildInfoPacket wysyla GuildPayout")

    old_guild_chat = """\tP2P_MANAGER::instance().Send(p1);
\tP2P_MANAGER::instance().Send(p2);
}"""

    new_guild_chat = """\tP2P_MANAGER::instance().Send(p1);
\tP2P_MANAGER::instance().Send(p2);
}

// MT2009_PLUS_CRAFTER_REVENUE_V1: wysylanie komendy GuildPayout do online czlonkow
void CGuild::SendGuildPayout(int amount)
{
\tchar szCmd[64];
\tsnprintf(szCmd, sizeof(szCmd), "GuildPayout %d", amount);
\tfor (TGuildMemberOnlineContainer::iterator it = m_memberOnline.begin(); it != m_memberOnline.end(); ++it)
\t{
\t\tLPCHARACTER ch = *it;
\t\tif (ch)
\t\t\tch->ChatPacket(CHAT_TYPE_COMMAND, szCmd);
\t}
}"""

    patch_file(guild_cpp_file, old_guild_chat, new_guild_chat, "guild.cpp: Implementacja SendGuildPayout")

    # 3. char.cpp: inkrementacja guild_payout_%u w PayRefineFee oraz zapis do player.guild_crafter_revenue
    old_char_refine = """\t\t\t// MT2009_PLUS_CRAFTER_REVENUE_V1: accumulate crafter payout
\t\t\tif (iFee > 0)
\t\t\t{
\t\t\t\tchar szFlag[64];
\t\t\t\tsnprintf(szFlag, sizeof(szFlag), "guild_payout_%u", pGuild->GetID());
\t\t\t\tint curPayout = quest::CQuestManager::instance().GetEventFlag(szFlag);
\t\t\t\tcurPayout += iFee;
\t\t\t\tquest::CQuestManager::instance().RequestSetEventFlag(szFlag, curPayout);
\t\t\t\tpGuild->SendGuildPayout(curPayout);
\t\t\t}"""

    new_char_refine = """\t\t\t// MT2009_PLUS_CRAFTER_REVENUE_V1: accumulate crafter payout
\t\t\tif (iFee > 0)
\t\t\t{
\t\t\t\tchar szFlag[64];
\t\t\t\tsnprintf(szFlag, sizeof(szFlag), "guild_payout_%u", pGuild->GetID());
\t\t\t\tint curPayout = quest::CQuestManager::instance().GetEventFlag(szFlag);
\t\t\t\tcurPayout += iFee;
\t\t\t\tquest::CQuestManager::instance().RequestSetEventFlag(szFlag, curPayout);
\t\t\t\tpGuild->SendGuildPayout(curPayout);

\t\t\t\tDBManager::instance().Query(
\t\t\t\t\t"INSERT INTO player.guild_crafter_revenue (guild_id, payout_available, total_earned) "
\t\t\t\t\t"VALUES (%u, %u, %u) "
\t\t\t\t\t"ON DUPLICATE KEY UPDATE payout_available = payout_available + %u, total_earned = total_earned + %u",
\t\t\t\t\tpGuild->GetID(), (DWORD)iFee, (DWORD)iFee, (DWORD)iFee, (DWORD)iFee
\t\t\t\t);
\t\t\t}"""

    patch_file(char_cpp_file, old_char_refine, new_char_refine, "char.cpp: Inkrementacja guild_payout_%u oraz INSERT/UPDATE w player.guild_crafter_revenue")

    # 4. input_login.cpp: wysylanie GuildPayout podczas logowania
    old_input_login = """\t\tCGuild* pGuild = ch->GetGuild();
\t\tif (pGuild)
\t\t{
\t\t\tint now = get_global_time();"""

    new_input_login = """\t\tCGuild* pGuild = ch->GetGuild();
\t\tif (pGuild)
\t\t{
\t\t\t// MT2009_PLUS_CRAFTER_REVENUE_V1: sync payout to logging-in member
\t\t\tchar szFlag[64];
\t\t\tsnprintf(szFlag, sizeof(szFlag), "guild_payout_%u", pGuild->GetID());
\t\t\tint payout = quest::CQuestManager::instance().GetEventFlag(szFlag);
\t\t\tch->ChatPacket(CHAT_TYPE_COMMAND, "GuildPayout %d", payout);

\t\t\tint now = get_global_time();"""

    patch_file(input_login_cpp_file, old_input_login, new_input_login, "input_login.cpp: Wysylka GuildPayout przy logowaniu")

    # 5. questlua_guild.cpp: include db.h oraz poprawka wyplaty (ch->ChangeGold zamiast PointChange) i aktualizacja bazy
    old_ql_inc = """#include "guild.h"
#include "guild_manager.h" """
    new_ql_inc = """#include "guild.h"
#include "guild_manager.h"
#include "db.h" """

    patch_file(questlua_guild_file, "#include \"guild_manager.h\"", "#include \"guild_manager.h\"\n#include \"db.h\"", "questlua_guild.cpp: Dodanie include db.h")

    # Wymiana PointChange na ChangeGold w obu funkcjach wyplaty:
    old_tw_pointchange = """\t\tif (!pGuild->SpendGuildMoney(ch, gold, "WITHDRAW_TO_MASTER"))
\t\t{
\t\t\tch->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("Nie udalo sie pobrac Yang ze skarbca."));
\t\t\tlua_pushnumber(L, 0);
\t\t\treturn 1;
\t\t}

\t\tch->PointChange(POINT_GOLD, net_gold);"""

    new_tw_pointchange = """\t\tif (!pGuild->SpendGuildMoney(ch, gold, "WITHDRAW_TO_MASTER"))
\t\t{
\t\t\tch->ChatPacket(CHAT_TYPE_INFO, LC_TEXT("Nie udalo sie pobrac Yang ze skarbca."));
\t\t\tlua_pushnumber(L, 0);
\t\t\treturn 1;
\t\t}

\t\tDBManager::instance().SendMoneyLog(MONEY_LOG_GUILD, ch->GetPlayerID(), net_gold);
\t\tch->ChangeGold(net_gold);"""

    patch_file(questlua_guild_file, old_tw_pointchange, new_tw_pointchange, "questlua_guild.cpp: guild_treasury_withdraw ch->ChangeGold")

    old_pw_pointchange = """\t\tpGuild->SendGuildPayout(curPayout);

\t\tch->PointChange(POINT_GOLD, net_gold);"""

    new_pw_pointchange = """\t\tpGuild->SendGuildPayout(curPayout);

\t\tDBManager::instance().SendMoneyLog(MONEY_LOG_GUILD, ch->GetPlayerID(), net_gold);
\t\tch->ChangeGold(net_gold);

\t\tDBManager::instance().Query(
\t\t\t"INSERT INTO player.guild_crafter_revenue (guild_id, payout_available, total_withdrawn, last_withdrawal_time) "
\t\t\t"VALUES (%u, 0, %u, NOW()) "
\t\t\t"ON DUPLICATE KEY UPDATE payout_available = GREATEST(0, CAST(payout_available AS SIGNED) - %u), "
\t\t\t"total_withdrawn = total_withdrawn + %u, last_withdrawal_time = NOW()",
\t\t\tpGuild->GetID(), (DWORD)gold, (DWORD)gold, (DWORD)gold
\t\t);"""

    patch_file(questlua_guild_file, old_pw_pointchange, new_pw_pointchange, "questlua_guild.cpp: guild_payout_withdraw ch->ChangeGold + DBManager UPDATE")

    old_padd = """\t\tpGuild->RequestDepositMoney(ch, add);
\t\tpGuild->SendGuildPayout(curPayout);
\t\tlua_pushboolean(L, true);"""

    new_padd = """\t\tpGuild->RequestDepositMoney(ch, add);
\t\tpGuild->SendGuildPayout(curPayout);

\t\tDBManager::instance().Query(
\t\t\t"INSERT INTO player.guild_crafter_revenue (guild_id, payout_available, total_earned) "
\t\t\t"VALUES (%u, %u, %u) "
\t\t\t"ON DUPLICATE KEY UPDATE payout_available = payout_available + %u, total_earned = total_earned + %u",
\t\t\tpGuild->GetID(), (DWORD)add, (DWORD)add, (DWORD)add, (DWORD)add
\t\t);

\t\tlua_pushboolean(L, true);"""

    patch_file(questlua_guild_file, old_padd, new_padd, "questlua_guild.cpp: guild_payout_add INSERT/UPDATE w player.guild_crafter_revenue")

    print("[SUCCESS] Zaktualizowano wszystkie modyfikacje serwera pod wzgledem ChangeGold i MySQL!")

if __name__ == "__main__":
    main()
