# -*- coding: utf-8 -*-
"""
apply_patch.py - Wykluczenie przedmiotow bonusowych z Market Clearing oraz poprawa floor zielonych bonusow
MT2Plus
"""

import os
import sys

def apply_to_clearing(file_path):
    if not os.path.isfile(file_path):
        print(f"[!] Nie znaleziono: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Normalize CRLF for matching
    newline = "\r\n" if "\r\n" in content else "\n"

    target_old = (
        f"\tbool IsPlayerBotClearingGoods(DWORD vnum){newline}"
        f"\t{{{newline}"
        f"\t\tif (vnum == 0 || IsPlayerBotCorVnum(vnum) || vnum == PLAYERBOT_CRAFT_MATERIAL_VNUM_PRICED ||{newline}"
        f"\t\t\t\tvnum == PLAYERBOT_MOONLIGHT_CHEST_VNUM || IsPlayerBotGuildBuildMaterial(vnum) ||{newline}"
        f"\t\t\t\tIsPlayerBotFixedPriceTalismanVnum(vnum) ||{newline}"
        f"\t\t\t\tIsPlayerBotBeltVnum(vnum) || IsPlayerBotSashVnum(vnum)){newline}"
        f"\t\t\treturn false;{newline}"
        f"\t\tconst TItemTable* proto = ITEM_MANAGER::instance().GetTable(vnum);{newline}"
        f"\t\tif (!proto){newline}"
        f"\t\t\treturn false;{newline}"
        f"\t\tif (proto->bType == ITEM_WEAPON || proto->bType == ITEM_ARMOR || proto->bType == ITEM_COSTUME ||{newline}"
        f"\t\t\t\tproto->bType == ITEM_SKILLBOOK || proto->bType == ITEM_DS || proto->bType == ITEM_BELT){newline}"
        f"\t\t\treturn false;{newline}"
        f"\t\treturn IS_SET(proto->dwFlags, ITEM_FLAG_STACKABLE) || GetPlayerBotRefineMaterialVnums().count(vnum) != 0;{newline}"
        f"\t}}"
    )

    replacement_new = (
        f"\tbool IsPlayerBotClearingGoods(DWORD vnum){newline}"
        f"\t{{{newline}"
        f"\t\tif (vnum == 0 || IsPlayerBotCorVnum(vnum) || vnum == PLAYERBOT_CRAFT_MATERIAL_VNUM_PRICED ||{newline}"
        f"\t\t\t\tvnum == PLAYERBOT_MOONLIGHT_CHEST_VNUM || IsPlayerBotGuildBuildMaterial(vnum) ||{newline}"
        f"\t\t\t\tIsPlayerBotFixedPriceTalismanVnum(vnum) ||{newline}"
        f"\t\t\t\tIsPlayerBotBeltVnum(vnum) || IsPlayerBotSashVnum(vnum) ||{newline}"
        f"\t\t\t\tIsPlayerBotGreenBonusStone(vnum) ||{newline}"
        f"\t\t\t\tvnum == 30368 || vnum == 30369 || vnum == 30370){newline}"
        f"\t\t\treturn false;{newline}"
        f"\t\tconst TItemTable* proto = ITEM_MANAGER::instance().GetTable(vnum);{newline}"
        f"\t\tif (!proto){newline}"
        f"\t\t\treturn false;{newline}"
        f"\t\tif (proto->bType == ITEM_WEAPON || proto->bType == ITEM_ARMOR || proto->bType == ITEM_COSTUME ||{newline}"
        f"\t\t\t\tproto->bType == ITEM_SKILLBOOK || proto->bType == ITEM_DS || proto->bType == ITEM_BELT){newline}"
        f"\t\t\treturn false;{newline}"
        f"\t\t// MT2PLUS_EXCLUDE_BONUS_FROM_CLEARING: Wykluczenie przedmiotow dodawania, zmiany i 5. bonusu (Wzmocnienie, Zaczarowanie, Zielona Sila, Zielony Czar, Marmur){newline}"
        f"\t\tif (proto->bType == ITEM_USE && (proto->bSubType == USE_CHANGE_ATTRIBUTE ||{newline}"
        f"\t\t\t\tproto->bSubType == USE_ADD_ATTRIBUTE || proto->bSubType == USE_ADD_ATTRIBUTE2)){newline}"
        f"\t\t\treturn false;{newline}"
        f"\t\treturn IS_SET(proto->dwFlags, ITEM_FLAG_STACKABLE) || GetPlayerBotRefineMaterialVnums().count(vnum) != 0;{newline}"
        f"\t}}"
    )

    if "MT2PLUS_EXCLUDE_BONUS_FROM_CLEARING" in content:
        print(f"[-] Juz zaaplikowano w: {file_path}")
        return True

    if target_old in content:
        content = content.replace(target_old, replacement_new)
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        print(f"[+] Zaaplikowano zmiane w: {file_path}")
        return True
    else:
        print(f"[!] Nie znaleziono bloku docelowego w: {file_path}")
        return False

def apply_to_town(file_path):
    if not os.path.isfile(file_path):
        print(f"[!] Nie znaleziono: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    newline = "\r\n" if "\r\n" in content else "\n"

    target_old = (
        f"\tDWORD GetPlayerBotBonusGoodsFloorUnit(LPITEM item){newline}"
        f"\t{{{newline}"
        f"\t\tif (!item){newline}"
        f"\t\t\treturn 0;{newline}"
        f"\t\tlong long unit = 0;{newline}"
        f"\t\tif (item->GetVnum() == PLAYERBOT_MOONLIGHT_CHEST_VNUM){newline}"
        f"\t\t\tunit = playerbot_moonlight_rules::ChestFloor(GetPlayerBotMoonlightChestWorth(),{newline}"
        f"\t\t\t\t\tPLAYERBOT_MOONLIGHT_CHEST_FLOOR_PERCENT);{newline}"
        f"\t\telse if (IsPlayerBotBonusStoneItem(item))"
    )

    replacement_new = (
        f"\tDWORD GetPlayerBotBonusGoodsFloorUnit(LPITEM item){newline}"
        f"\t{{{newline}"
        f"\t\tif (!item){newline}"
        f"\t\t\treturn 0;{newline}"
        f"\t\tlong long unit = 0;{newline}"
        f"\t\tif (item->GetVnum() == PLAYERBOT_MOONLIGHT_CHEST_VNUM){newline}"
        f"\t\t\tunit = playerbot_moonlight_rules::ChestFloor(GetPlayerBotMoonlightChestWorth(),{newline}"
        f"\t\t\t\t\tPLAYERBOT_MOONLIGHT_CHEST_FLOOR_PERCENT);{newline}"
        f"\t\t// MT2PLUS_GREEN_BONUS_FLOOR: Zielony Czar i Zielona Sila maja wlasny floor ze swoich cen bazowych{newline}"
        f"\t\telse if (IsPlayerBotGreenBonusStone(item->GetVnum())){newline}"
        f"\t\t{{{newline}"
        f"\t\t\tunit = GetPlayerBotMaterialAskingBase(item->GetVnum());{newline}"
        f"\t\t}}{newline}"
        f"\t\telse if (IsPlayerBotBonusStoneItem(item))"
    )

    if "MT2PLUS_GREEN_BONUS_FLOOR" in content:
        print(f"[-] Juz zaaplikowano w: {file_path}")
        return True

    if target_old in content:
        content = content.replace(target_old, replacement_new)
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        print(f"[+] Zaaplikowano zmiane w: {file_path}")
        return True
    else:
        print(f"[!] Nie znaleziono bloku docelowego w: {file_path}")
        return False

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

    targets_clearing = [
        os.path.join(repo_root, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "playerbot_market_clearing.h"),
        os.path.join(repo_root, "Server", "linux-port", "overlays", "playerbot", "src", "game", "src", "playerbot_market_clearing.h")
    ]

    targets_town = [
        os.path.join(repo_root, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "playerbot_town.h"),
        os.path.join(repo_root, "Server", "linux-port", "overlays", "playerbot", "src", "game", "src", "playerbot_town.h")
    ]

    ok = True
    for p in targets_clearing:
        if not apply_to_clearing(p):
            ok = False

    for p in targets_town:
        if not apply_to_town(p):
            ok = False

    if ok:
        print("[SUKCES] Pomyslnie zmodyfikowano wszystkie pliki!")
    else:
        print("[BLAD] Wystapily bledy podczas aplikacji patcha!")
        sys.exit(1)

if __name__ == "__main__":
    main()
