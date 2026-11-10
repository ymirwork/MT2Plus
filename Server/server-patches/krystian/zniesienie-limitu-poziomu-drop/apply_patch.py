#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_patch.py - Reaplikacja zniesienia limitu delty poziomu dla dropu i Yang.
Modyfikacja: zniesienie-limitu-poziomu-drop
Autor: Krystian / MT2Plus
"""

import os
import sys

def find_repo_root():
    curr = os.path.abspath(os.path.dirname(__file__))
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, 'PROJECT_CONTEXT.md')):
            return curr
        curr = os.path.dirname(curr)
    return r'd:\Github\MT2Plus'

REPO = find_repo_root()

def patch_item_manager():
    path = os.path.join(REPO, 'Server', 'linux-port', 'docker', 'game', 'src', 'server', 'game', 'src', 'item_manager.cpp')
    if not os.path.isfile(path):
        print(f"[-] Nie znaleziono {path}")
        return
    with open(path, 'r', encoding='latin-1') as f:
        content = f.read()

    modified = False

    # 1. GetDropPct - wymuszenie iDeltaPercent = 100
    if "MT2009_PLUS_NO_LEVEL_DELTA_DROP: brak kary za roznice poziomow" not in content:
        target = "int iDeltaPercent = PERCENT_LVDELTA(pkKiller->GetLevel(), pkChr->GetLevel());"
        replacement = """// MT2009_PLUS_NO_LEVEL_DELTA_DROP: brak kary za roznice poziomow (100% szansy na drop)
	// int iDeltaPercent = PERCENT_LVDELTA(pkKiller->GetLevel(), pkChr->GetLevel());
	int iDeltaPercent = 100;"""
        if target in content:
            content = content.replace(target, replacement, 1)
            print("[+] item_manager.cpp: zniesiono kare levelDiff w GetDropPct")
            modified = True

    # 2. Sash / cloth drop check
    if "pkKiller->GetLevel() <= pkChr->GetLevel() + 30" in content:
        content = content.replace(
            "pkKiller->GetLevel() <= pkChr->GetLevel() + 30",
            "true /* MT2009_PLUS_NO_LEVEL_DELTA_DROP: bez limitu lvl na sukno */"
        )
        print("[+] item_manager.cpp: zniesiono limit poziomu na drop sukna na szarfy")
        modified = True

    if modified:
        with open(path, 'w', encoding='latin-1') as f:
            f.write(content)

def patch_char_battle():
    path = os.path.join(REPO, 'Server', 'linux-port', 'docker', 'game', 'src', 'server', 'game', 'src', 'char_battle.cpp')
    if not os.path.isfile(path):
        print(f"[-] Nie znaleziono {path}")
        return
    with open(path, 'r', encoding='latin-1') as f:
        content = f.read()

    if "MT2009_PLUS_NO_LEVEL_DELTA_DROP: brak kary za roznice poziomow dla yang" not in content:
        target = "iPercent = ((iGoldPercent * PERCENT_LVDELTA(pkAttacker->GetLevel(), GetLevel())) / 100);"
        replacement = """// MT2009_PLUS_NO_LEVEL_DELTA_DROP: brak kary za roznice poziomow dla yang (100% bazowego gold drop)
	// iPercent = ((iGoldPercent * PERCENT_LVDELTA(pkAttacker->GetLevel(), GetLevel())) / 100);
	iPercent = iGoldPercent;"""
        if target in content:
            content = content.replace(target, replacement, 1)
            with open(path, 'w', encoding='latin-1') as f:
                f.write(content)
            print("[+] char_battle.cpp: zniesiono kare levelDiff dla dropu Yang")

def patch_dragon_soul_quest():
    path = os.path.join(REPO, 'Server', 'linux-port', 'docker', 'game', 'quest', 'dragon_soul.quest')
    if not os.path.isfile(path):
        return
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    old_target = """\t\t\t-- Roznica dropu do 30 poziomow
\t\t\tif npc.get_level0() < pc.get_level() - 30 then
\t\t\t\treturn
\t\t\tend"""
    replacement = """\t\t\t-- MT2009_PLUS_NO_LEVEL_DELTA_DROP: bez limitu poziomu
\t\t\t-- if npc.get_level0() < pc.get_level() - 30 then
\t\t\t-- \treturn
\t\t\t-- end"""
    if old_target in content:
        content = content.replace(old_target, replacement)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("[+] dragon_soul.quest: wylaczono limit 30 poziomow na odlamki")

def patch_playerbot_files():
    # playerbot_alchemy.h
    for p in [
        os.path.join(REPO, 'Server', 'linux-port', 'overlays', 'playerbot', 'src', 'game', 'src', 'playerbot_alchemy.h'),
        os.path.join(REPO, 'Server', 'linux-port', 'docker', 'game', 'src', 'server', 'game', 'src', 'playerbot_alchemy.h')
    ]:
        if os.path.isfile(p):
            with open(p, 'r', encoding='latin-1') as f:
                c = f.read()
            if "if (!victim || (int)victim->GetLevel() < (int)ch->GetLevel() - 15)" in c:
                c = c.replace(
                    "if (!victim || (int)victim->GetLevel() < (int)ch->GetLevel() - 15)",
                    "// MT2009_PLUS_NO_LEVEL_DELTA_DROP: odlamki smoczego kamienia bez limitu poziomu\n\t\tif (!victim)"
                )
                with open(p, 'w', encoding='latin-1') as f:
                    f.write(c)
                print(f"[+] {os.path.basename(p)}: usunieto limit delty poziomu")

    # playerbot_events.h
    for p in [
        os.path.join(REPO, 'Server', 'linux-port', 'overlays', 'playerbot', 'src', 'game', 'src', 'playerbot_events.h'),
        os.path.join(REPO, 'Server', 'linux-port', 'docker', 'game', 'src', 'server', 'game', 'src', 'playerbot_events.h')
    ]:
        if os.path.isfile(p):
            with open(p, 'r', encoding='latin-1') as f:
                c = f.read()
            if "if (killer->GetLevel() > victim->GetLevel() + 30)" in c:
                c = c.replace(
                    "if (killer->GetLevel() > victim->GetLevel() + 30)\n\t\treturn;",
                    "// MT2009_PLUS_NO_LEVEL_DELTA_DROP: skrzynie eventowe bez ograniczenia poziomu zabojcy\n\t// if (killer->GetLevel() > victim->GetLevel() + 30) return;"
                )
                with open(p, 'w', encoding='latin-1') as f:
                    f.write(c)
                print(f"[+] {os.path.basename(p)}: usunieto limit 30 poziomow dla skrzynek eventowych")

def main():
    print("=== Aplikacja patcha: Zniesienie Limitu Poziomu Dropu & Yang ===")
    patch_item_manager()
    patch_char_battle()
    patch_dragon_soul_quest()
    patch_playerbot_files()
    print("=== Gotowe! ===")

if __name__ == '__main__':
    main()
