#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_dockerfile.py - Automatyczne zabezpieczenie i rejestracja autorskich funkcji oraz questow w Dockerfile
Chroni autorskie systemy MT2Plus (wyplata utargu, recykling, sloty sklepu) przed nadpisaniem podczas aktualizacji z upstream.
Autor: Krystian (MT2Plus)
"""

import os
import sys

CUSTOM_QUEST_FUNCTIONS = [
    "guild.treasury_withdraw",
    "open_guild_payout_dialog",
    "guild.payout_get",
    "guild.payout_withdraw",
    "guild.payout_add",
]

CUSTOM_QUESTS = [
    "recykling_bonusow",
    "shop_unlock_slots",
    "guild_crafter_revenue",
    "guild_building_npc",
]

def patch_dockerfile(repo_dir=None):
    if not repo_dir:
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    df_path = os.path.join(repo_dir, "Server", "linux-port", "docker", "game", "Dockerfile")
    if not os.path.isfile(df_path):
        # Fallback jesli repo_dir to juz Server
        df_path = os.path.join(repo_dir, "linux-port", "docker", "game", "Dockerfile")
        if not os.path.isfile(df_path):
            print(f"[!] Nie znaleziono Dockerfile w: {df_path}")
            return False

    with open(df_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    modified = False

    # 1. Zabezpieczenie funkcji w petli for fn in ...
    for fn in CUSTOM_QUEST_FUNCTIONS:
        if fn not in content:
            # Wstrzyknij przed guild.leave_war lub zodiac_temple.starttemple
            target = "guild.treasury_spend"
            if target in content:
                content = content.replace(target, f"{target} {fn}")
                print(f"[+] Dockerfile: dodano brakujaca funkcje Lua '{fn}'")
                modified = True
            else:
                target2 = "guild.leave_war"
                if target2 in content:
                    content = content.replace(target2, f"{fn} {target2}")
                    print(f"[+] Dockerfile: dodano brakujaca funkcje Lua '{fn}' (obok {target2})")
                    modified = True

    # 2. Zabezpieczenie questow w petli for q in ...
    for q in CUSTOM_QUESTS:
        if f" {q} " not in content and not content.endswith(f" {q}; do") and f" {q}; do" not in content:
            target = "labirynth black_steel_crafting"
            if target in content:
                content = content.replace(target, f"{q} {target}")
                print(f"[+] Dockerfile: dodano brakujacy quest '{q}' do petli kompilacji qc")
                modified = True
            else:
                target2 = "event_halloween_hair;"
                if target2 in content:
                    content = content.replace(target2, f"{q} {target2}")
                    print(f"[+] Dockerfile: dodano brakujacy quest '{q}' (obok {target2})")
                    modified = True

    if modified:
        with open(df_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print(f"[OK] Pomyslnie zaktualizowano Dockerfile ({df_path})")
    else:
        print(f"[OK] Dockerfile juz zawiera wszystkie autorskie funkcje i questy ({df_path})")

    return True

if __name__ == "__main__":
    repo_root = sys.argv[1] if len(sys.argv) > 1 else None
    success = patch_dockerfile(repo_root)
    sys.exit(0 if success else 1)
