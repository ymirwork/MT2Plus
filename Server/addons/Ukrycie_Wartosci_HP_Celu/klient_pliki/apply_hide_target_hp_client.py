#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_hide_target_hp_client.py
Modyfikacja klienta Metin2: Ukrycie wartosci liczbowej HP celu (np. 100/100)
"""

import os
import sys
import argparse
import subprocess
import shutil

def patch_uitarget(file_path):
    if not os.path.isfile(file_path):
        print(f"[!] Nie znaleziono pliku: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Zastąpienia komentujące pokazywanie tekstu HP
    targets = [
        ("self.hpText.Show()", "# self.hpText.Show() - usuniete biale napisy z iloscia HP"),
        ('self.hpText.SetText("%d / %d" % (hp, maxHp))', '# self.hpText.SetText("%d / %d" % (hp, maxHp))'),
        ('self.hpText.SetText("%d/%d" % (hp, maxHp))', '# self.hpText.SetText("%d/%d" % (hp, maxHp))'),
        ('self.hpText.SetText(localeInfo.FormatHP(hp, maxHp))', '# self.hpText.SetText(localeInfo.FormatHP(hp, maxHp))')
    ]

    modified = False
    for old, new in targets:
        if old in content:
            content = content.replace(old, new)
            modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Zmodyfikowano {file_path}")
        return True
    else:
        print(f"[*] Plik {file_path} ma juz ukryty tekst HP lub uzyto gotowego pliku.")
        return True

def pack_client_root(client_dir):
    script_ps1 = os.path.join(client_dir, "Compile-ClientPack.ps1")
    if os.path.isfile(script_ps1):
        print("[*] Wykryto Compile-ClientPack.ps1, kompilowanie paczki root...")
        res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_ps1, "root", "pack"], cwd=client_dir)
        return res.returncode == 0
    return False

def main():
    parser = argparse.ArgumentParser(description="Ukryj wartosc HP celu w kliencie")
    parser.add_argument("--client-dir", default=".", help="Sciezka do katalogu Klient/")
    args = parser.parse_args()

    client_dir = os.path.abspath(args.client_dir)
    print(f"[*] Katalog klienta: {client_dir}")

    # Sciezka do rozpakowanego root/uitarget.py
    root_uitarget = os.path.join(client_dir, "pack", "root", "uitarget.py")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    addon_uitarget = os.path.join(script_dir, "root", "uitarget.py")

    if os.path.isdir(os.path.join(client_dir, "pack", "root")):
        if os.path.isfile(addon_uitarget):
            print(f"[*] Kopiowanie gotowego uitarget.py do {root_uitarget}...")
            shutil.copy2(addon_uitarget, root_uitarget)
        else:
            patch_uitarget(root_uitarget)

        pack_client_root(client_dir)
        print("[SUCCESS] Paczka root zostala zaktualizowana i skompilowana!")
    else:
        print("[!] Uwaga: Folder pack/root nie jest rozpakowany!")
        print("    Rozpakuj paczke root, zamien plik uitarget.py i skompiluj ponownie.")

if __name__ == "__main__":
    main()
