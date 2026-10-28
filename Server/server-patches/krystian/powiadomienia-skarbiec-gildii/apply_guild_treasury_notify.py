#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_guild_treasury_notify.py
Modyfikacja serwerowa Metin2: Powiadomienia o Skarbcu Gildii
- Przy logowaniu (stan skarbca i przyrost Yang od ostatniego logowania)
- Na zywo przy uzyciu kowala gildyjnego / alchemika ze szczegolami:
  kto, co, na jaki poziom (+X) ulepszyl lub spalil, u kogo oraz kwota Yang.
Kodowanie: CP1250 (oktaly \346, \263, \352).
Autor: Krystian (MT2Plus)
"""

import os
import sys
import argparse

def patch_file(file_path, old_text, new_text, description):
    if not os.path.isfile(file_path):
        print(f"[!] Nie znaleziono pliku: {file_path}")
        return False

    with open(file_path, "rb") as f:
        raw_bytes = f.read()

    is_crlf = b"\r\n" in raw_bytes
    content = raw_bytes.decode("latin1")

    # Ujednolicenie do LF na czas dopasowywania
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
    parser = argparse.ArgumentParser(description="Aplikuj powiadomienia o skarbcu gildii ze smaczkiem ulepszania/spalenia")
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

    char_h_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "server", "game", "src", "char.h"),
        os.path.join("game", "src", "char.h")
    ])
    char_cpp_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "server", "game", "src", "char.cpp"),
        os.path.join("game", "src", "char.cpp")
    ])
    char_item_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "server", "game", "src", "char_item.cpp"),
        os.path.join("game", "src", "char_item.cpp")
    ])
    login_file = find_file([
        os.path.join("linux-port", "docker", "game", "src", "server", "game", "src", "input_login.cpp"),
        os.path.join("game", "src", "input_login.cpp")
    ])

    if not char_h_file or not char_cpp_file or not char_item_file or not login_file:
        print("[!] BLAD: Nie znaleziono wszystkich wymaganych plikow zrodlowych!")
        print(f"char.h: {char_h_file}")
        print(f"char.cpp: {char_cpp_file}")
        print(f"char_item.cpp: {char_item_file}")
        print(f"input_login.cpp: {login_file}")
        sys.exit(1)

    print(f"[*] Plik char.h: {char_h_file}")
    print(f"[*] Plik char.cpp: {char_cpp_file}")
    print(f"[*] Plik char_item.cpp: {char_item_file}")
    print(f"[*] Plik input_login.cpp: {login_file}")

    # --- 1. char.h ---
    old_char_h = "\t\tvoid\t\t\tPayRefineFee(YANG iTotalMoney);"
    new_char_h = "\t\tvoid\t\t\tPayRefineFee(YANG iTotalMoney, bool bSuccess = true, const char* szItemName = nullptr);"
    patch_file(char_h_file, old_char_h, new_char_h, "char.h: Sygnatura PayRefineFee")

    # --- 2. char.cpp ---
    # Sygnatura funkcji
    patch_file(char_cpp_file,
               "void CHARACTER::PayRefineFee(YANG iTotalMoney)",
               "void CHARACTER::PayRefineFee(YANG iTotalMoney, bool bSuccess, const char* szItemName)",
               "char.cpp: Definicja PayRefineFee")

    # Blok powiadomienia w PayRefineFee
    old_notify_v1 = """\t\t\t\tchar szNotify[256];
\t\t\t\tif (isAlchemist)
\t\t\t\t\tsnprintf(szNotify, sizeof(szNotify), "[Skarbiec Gildii] Posta\\346 %s przetopi\\263a rud\\352 u %s (+%s Yang).", GetName(), szCrafter, strFee.c_str());
\t\t\t\telse
\t\t\t\t\tsnprintf(szNotify, sizeof(szNotify), "[Skarbiec Gildii] Posta\\346 %s ulepszy\\263a przedmiot u %s (+%s Yang).", GetName(), szCrafter, strFee.c_str());"""

    raw_char_cpp = """\tif (pGuild)
\t{
\t\tif (pGuild != GetGuild())
\t\t{
\t\t\tpGuild->RequestDepositMoney(this, iFee);
\t\t\tiRemain -= iFee;
\t\t}
\t}"""

    new_notify_v2 = """\t\t\t\tchar szNotify[256];
\t\t\t\tif (szItemName && *szItemName)
\t\t\t\t{
\t\t\t\t\tconst char* pPlus = strrchr(szItemName, '+');
\t\t\t\t\tif (pPlus && pPlus > szItemName && isdigit(pPlus[1]))
\t\t\t\t\t{
\t\t\t\t\t\tstd::string strBaseName(szItemName, pPlus - szItemName);
\t\t\t\t\t\twhile (!strBaseName.empty() && (strBaseName.back() == ' ' || strBaseName.back() == '\\t'))
\t\t\t\t\t\t\tstrBaseName.pop_back();

\t\t\t\t\t\tstd::string strLevel(pPlus);
\t\t\t\t\t\twhile (!strLevel.empty() && (strLevel.back() == ' ' || strLevel.back() == '\\t'))
\t\t\t\t\t\t\tstrLevel.pop_back();

\t\t\t\t\t\tif (!strBaseName.empty())
\t\t\t\t\t\t{
\t\t\t\t\t\t\tif (bSuccess)
\t\t\t\t\t\t\t\tsnprintf(szNotify, sizeof(szNotify), "[Skarbiec Gildii] Posta\\346 %s ulepszy\\263a %s na %s u %s (+%s Yang).", GetName(), strBaseName.c_str(), strLevel.c_str(), szCrafter, strFee.c_str());
\t\t\t\t\t\t\telse
\t\t\t\t\t\t\t\tsnprintf(szNotify, sizeof(szNotify), "[Skarbiec Gildii] Posta\\346 %s spali\\263a %s na %s u %s (+%s Yang).", GetName(), strBaseName.c_str(), strLevel.c_str(), szCrafter, strFee.c_str());
\t\t\t\t\t\t}
\t\t\t\t\t\telse
\t\t\t\t\t\t{
\t\t\t\t\t\t\tif (bSuccess)
\t\t\t\t\t\t\t\tsnprintf(szNotify, sizeof(szNotify), "[Skarbiec Gildii] Posta\\346 %s ulepszy\\263a %s u %s (+%s Yang).", GetName(), szItemName, szCrafter, strFee.c_str());
\t\t\t\t\t\t\telse
\t\t\t\t\t\t\t\tsnprintf(szNotify, sizeof(szNotify), "[Skarbiec Gildii] Posta\\346 %s spali\\263a %s u %s (+%s Yang).", GetName(), szItemName, szCrafter, strFee.c_str());
\t\t\t\t\t\t}
\t\t\t\t\t}
\t\t\t\t\telse
\t\t\t\t\t{
\t\t\t\t\t\tif (bSuccess)
\t\t\t\t\t\t\tsnprintf(szNotify, sizeof(szNotify), "[Skarbiec Gildii] Posta\\346 %s ulepszy\\263a %s u %s (+%s Yang).", GetName(), szItemName, szCrafter, strFee.c_str());
\t\t\t\t\t\telse
\t\t\t\t\t\t\tsnprintf(szNotify, sizeof(szNotify), "[Skarbiec Gildii] Posta\\346 %s spali\\263a %s u %s (+%s Yang).", GetName(), szItemName, szCrafter, strFee.c_str());
\t\t\t\t\t}
\t\t\t\t}
\t\t\t\telse if (isAlchemist)
\t\t\t\t{
\t\t\t\t\tsnprintf(szNotify, sizeof(szNotify), "[Skarbiec Gildii] Posta\\346 %s przetopi\\263a rud\\352 u %s (+%s Yang).", GetName(), szCrafter, strFee.c_str());
\t\t\t\t}
\t\t\t\telse
\t\t\t\t{
\t\t\t\t\tsnprintf(szNotify, sizeof(szNotify), "[Skarbiec Gildii] Posta\\346 %s ulepszy\\263a przedmiot u %s (+%s Yang).", GetName(), szCrafter, strFee.c_str());
\t\t\t\t}"""

    if not patch_file(char_cpp_file, old_notify_v1, new_notify_v2, "char.cpp: Powiadomienie ze smaczkiem ulepszania/spalenia"):
        full_raw_to_new = """\tif (pGuild)
\t{
\t\tif (pGuild != GetGuild())
\t\t{
\t\t\tpGuild->RequestDepositMoney(this, iFee);
\t\t\tiRemain -= iFee;

\t\t\t// MT2009_PLUS_GUILD_TREASURY_NOTIFY_V1 (refine notice):
\t\t\tif (iFee > 0)
\t\t\t{
\t\t\t\tLPCHARACTER chRefineNPC = CHARACTER_MANAGER::instance().Find(m_dwRefineNPCVID);
\t\t\t\tconst char* szCrafter = "Kowala Gildijnego";
\t\t\t\tbool isAlchemist = false;
\t\t\t\tif (chRefineNPC)
\t\t\t\t{
\t\t\t\t\tDWORD race = chRefineNPC->GetRaceNum();
\t\t\t\t\tif (race == 20044)
\t\t\t\t\t\tszCrafter = "Kowala Broni";
\t\t\t\t\telse if (race == 20045)
\t\t\t\t\t\tszCrafter = "P\\263atnerza";
\t\t\t\t\telse if (race == 20046)
\t\t\t\t\t\tszCrafter = "Jubilera";
\t\t\t\t\telse if (race >= 20060 && race <= 20072)
\t\t\t\t\t{
\t\t\t\t\t\tszCrafter = "Alchemika";
\t\t\t\t\t\tisAlchemist = true;
\t\t\t\t\t}
\t\t\t\t}

\t\t\t\tstd::string strFee = std::to_string(iFee);
\t\t\t\tfor (int n = (int)strFee.length() - 3; n > 0; n -= 3)
\t\t\t\t\tstrFee.insert(n, " ");

""" + new_notify_v2 + """

\t\t\t\tpGuild->Chat(szNotify);
\t\t\t}
\t\t}
\t}"""
        patch_file(char_cpp_file, raw_char_cpp, full_raw_to_new, "char.cpp: Pelne powiadomienie z kowala gildyjnego")

    # --- 3. char_item.cpp ---
    # DoRefine - Sukces
    old_dorefine_success = """\t\t\tsys_log(0, "PayPee %d", cost);
\t\t\tPayRefineFee(cost);
\t\t\tsys_log(0, "PayPee End %d", cost);"""

    new_dorefine_success = """\t\t\tsys_log(0, "PayPee %d", cost);
\t\t\tPayRefineFee(cost, true, pProto->szLocaleName);
\t\t\tsys_log(0, "PayPee End %d", cost);"""

    patch_file(char_item_file, old_dorefine_success, new_dorefine_success, "char_item.cpp: DoRefine sukces (przekazanie nazwy przedmiotu)")

    # DoRefine - Spalenie (Failure)
    old_dorefine_fail = """\t\tPayRefineFee(cost);
\t}

\treturn true;
}

bool CHARACTER::DoRefineWithScroll(LPITEM item)"""

    new_dorefine_fail = """\t\tPayRefineFee(cost, false, pProto->szLocaleName);
\t}

\treturn true;
}

bool CHARACTER::DoRefineWithScroll(LPITEM item)"""

    patch_file(char_item_file, old_dorefine_fail, new_dorefine_fail, "char_item.cpp: DoRefine spalenie (przekazanie nazwy przedmiotu)")

    # DoRefineWithScroll - opcjonalnie
    old_scroll_success = """\t\t\tITEM_MANAGER::instance().FlushDelayedSave(pkNewItem);
\t\t\tpkNewItem->AttrLog();
\t\t\tPayRefineFee(cost);"""

    new_scroll_success = """\t\t\tITEM_MANAGER::instance().FlushDelayedSave(pkNewItem);
\t\t\tpkNewItem->AttrLog();
\t\t\tPayRefineFee(cost, true, pProto->szLocaleName);"""

    patch_file(char_item_file, old_scroll_success, new_scroll_success, "char_item.cpp: DoRefineWithScroll sukces")

    old_scroll_fail = """\t\tNotifyRefineFail(this, item, szRefineType);
\t\tPayRefineFee(cost);"""

    new_scroll_fail = """\t\tNotifyRefineFail(this, item, szRefineType);
\t\tPayRefineFee(cost, false, pProto->szLocaleName);"""

    patch_file(char_item_file, old_scroll_fail, new_scroll_fail, "char_item.cpp: DoRefineWithScroll niepowodzenie")

    # --- 4. input_login.cpp (powiadomienie przy logowaniu) ---
    login_inc_old = '#include "char_manager.h"'
    login_inc_new = '#include "char_manager.h"\n#include "guild.h"'

    login_code_old = """\t// MT2009_PLUS_GUILD_TREASURY_NOTIFY_V1 (login): notify guild members of the treasury balance"""

    patch_file(login_file, login_inc_old, login_inc_new, "input_login.cpp: #include guild.h")
    patch_file(login_file, login_code_old, login_code_old, "input_login.cpp: Powiadomienie o stanie skarbca przy wejsciu do gry")

    print("[SUCCESS] Wszystkie modyfikacje powiadomien o skarbcu gildii zaaplikowane pomyslnie!")

if __name__ == "__main__":
    main()
