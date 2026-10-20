#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_revive_100_hp_server.py
Modyfikacja serwerowa Metin2: Wstawanie po smierci ze 100% HP (do_restart & Disconnect)
"""

import os
import sys
import argparse

def patch_file(file_path, old_text, new_text, description):
    if not os.path.isfile(file_path):
        print(f"[!] Nie znaleziono pliku: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    if new_text in content:
        print(f"[OK] {description} - juz zaaplikowane.")
        return True

    if old_text not in content:
        print(f"[!] Nie znaleziono oryginalnego fragmentu w: {file_path}")
        return False

    content = content.replace(old_text, new_text, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] Zastosowano: {description}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Aplikuj wstawanie z 100% HP")
    parser.add_argument("--server-dir", default=".", help="Sciezka do glownego katalogu Server/")
    args = parser.parse_args()

    server_dir = os.path.abspath(args.server_dir)

    # Szukamy cmd_general.cpp oraz char.cpp w typowych lokacjach
    cmd_candidates = [
        os.path.join(server_dir, "linux-port", "docker", "game", "src", "server", "game", "src", "cmd_general.cpp"),
        os.path.join(server_dir, "game", "src", "cmd_general.cpp"),
        os.path.join(server_dir, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "cmd_general.cpp")
    ]
    char_candidates = [
        os.path.join(server_dir, "linux-port", "docker", "game", "src", "server", "game", "src", "char.cpp"),
        os.path.join(server_dir, "game", "src", "char.cpp"),
        os.path.join(server_dir, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "char.cpp")
    ]

    cmd_file = next((p for p in cmd_candidates if os.path.isfile(p)), None)
    char_file = next((p for p in char_candidates if os.path.isfile(p)), None)

    if not cmd_file:
        print("[!] BŁĄD: Nie znaleziono pliku cmd_general.cpp w podanej sciezce!")
        sys.exit(1)

    print(f"[*] Patchowanie cmd_general.cpp: {cmd_file}")

    # Patch do_restart SCMD_RESTART_TOWN
    old_town = "ch->PointChange(POINT_HP, 50 - ch->GetHP());\n\t\t\tch->DeathPenalty(1);"
    new_town = "ch->PointChange(POINT_HP, ch->GetMaxHP() - ch->GetHP());\n\t\t\tch->DeathPenalty(1);"
    patch_file(cmd_file, old_town, new_town, "SCMD_RESTART_TOWN (100% HP)")

    # Patch do_restart SCMD_RESTART_HERE
    old_here = "ch->PointChange(POINT_HP, 50 - ch->GetHP());\n\t\t\tch->DeathPenalty(0);"
    new_here = "ch->PointChange(POINT_HP, ch->GetMaxHP() - ch->GetHP());\n\t\t\tch->DeathPenalty(0);"
    patch_file(cmd_file, old_here, new_here, "SCMD_RESTART_HERE (100% HP)")

    if char_file:
        print(f"[*] Patchowanie char.cpp: {char_file}")
        old_char = "DeathPenalty(0);\n\t\tPointChange(POINT_HP, 50 - GetHP());"
        new_char = "DeathPenalty(0);\n\t\tPointChange(POINT_HP, GetMaxHP() - GetHP());"
        patch_file(char_file, old_char, new_char, "CHARACTER::Disconnect (100% HP)")

    print("[SUCCESS] Pomyslnie zmodyfikowano kod serwera pod 100% HP po smierci.")

if __name__ == "__main__":
    main()
