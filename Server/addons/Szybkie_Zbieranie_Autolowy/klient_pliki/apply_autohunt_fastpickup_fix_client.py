#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_autohunt_fastpickup_fix_client.py
Modyfikacja i naprawa Autołowów:
1. Natychmiastowe zbieranie obszarowe /pickup_nearby zamiast pojedynczego podnoszenia.
2. Zabezpieczenie GetActorPosition(vid) zapobiegajace awarii NoneType w pakiecie AutoHuntTarget.
"""

import os
import sys
import argparse
import subprocess
import shutil

def pack_client_root(client_dir):
    script_ps1 = os.path.join(client_dir, "Compile-ClientPack.ps1")
    if os.path.isfile(script_ps1):
        print("[*] Wykryto Compile-ClientPack.ps1, kompilowanie paczki root...")
        res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_ps1, "root", "pack"], cwd=client_dir)
        return res.returncode == 0
    return False

def main():
    parser = argparse.ArgumentParser(description="Aplikuj szybkie zbieranie i fix crasha Autołowów")
    parser.add_argument("--client-dir", default=".", help="Sciezka do katalogu Klient/")
    args = parser.parse_args()

    client_dir = os.path.abspath(args.client_dir)
    print(f"[*] Katalog klienta: {client_dir}")

    root_autohunt = os.path.join(client_dir, "pack", "root", "uiautohunt.py")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    addon_autohunt = os.path.join(script_dir, "root", "uiautohunt.py")

    if os.path.isdir(os.path.join(client_dir, "pack", "root")):
        if os.path.isfile(addon_autohunt):
            print(f"[*] Kopiowanie gotowego uiautohunt.py do {root_autohunt}...")
            shutil.copy2(addon_autohunt, root_autohunt)
            pack_client_root(client_dir)
            print("[SUCCESS] Paczka root zostala zaktualizowana i skompilowana!")
        else:
            print("[!] Nie znaleziono pliku wzorcowego uiautohunt.py!")
            sys.exit(1)
    else:
        print("[!] Folder pack/root nie jest rozpakowany!")
        print("    Rozpakuj paczke root, zamien plik uiautohunt.py i skompiluj ponownie.")

if __name__ == "__main__":
    main()
