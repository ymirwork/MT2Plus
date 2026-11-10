#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_patch.py - Reaplikacja poprawek wartości, opisów i tooltipów dla Zielonych i Fioletowych Mikstur.
Modyfikacja: balans-mikstury-szybkosci
Autor: Krystian / MT2Plus
"""

import os
import sys
import struct
import subprocess

def find_repo_root():
    curr = os.path.abspath(os.path.dirname(__file__))
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, 'PROJECT_CONTEXT.md')):
            return curr
        curr = os.path.dirname(curr)
    return r'd:\Github\MT2Plus'

REPO = find_repo_root()

def patch_itemdesc():
    itemdesc_path = os.path.join(REPO, 'Klient', 'pack', 'dbdata', 'locale', 'pl', 'itemdesc.txt')
    if not os.path.isfile(itemdesc_path):
        print(f"[-] Nie znaleziono {itemdesc_path}")
        return

    with open(itemdesc_path, 'r', encoding='cp1250', errors='ignore') as f:
        lines = f.readlines()

    pot_map = {
        '27100': "Zwiększa Twoją Szybkość Ataku o +10% na okres 10 minut.",
        '27101': "Zwiększa Twoją Szybkość Ataku o +20% na okres 10 minut.",
        '27102': "Zwiększa Twoją Szybkość Ataku o +30% na okres 10 minut.",
        '27110': "Zwiększa Twoją Szybkość Ataku o +10% na okres 10 minut.",
        '27111': "Zwiększa Twoją Szybkość Ataku o +20% na okres 10 minut.",
        '27112': "Zwiększa Twoją Szybkość Ataku o +30% na okres 10 minut.",
        '27053': "Zwiększa Twoją Szybkość Ataku o +10% na okres 10 minut. Niezdatna do handlu.",
        '27123': "Zwiększa Twoją Szybkość Ataku o +10% na okres 10 minut. Niezdatna do handlu.",
        '27103': "Zwiększa Szybkość Ruchu o +10% na okres 10 minut.",
        '27104': "Zwiększa Szybkość Ruchu o +20% na okres 10 minut.",
        '27105': "Zwiększa Szybkość Ruchu o +30% na okres 10 minut.",
        '27113': "Zwiększa Szybkość Ruchu o +10% na okres 10 minut.",
        '27114': "Zwiększa Szybkość Ruchu o +20% na okres 10 minut.",
        '27115': "Zwiększa Szybkość Ruchu o +30% na okres 10 minut.",
        '27054': "Zwiększa Szybkość Ruchu o +10% na okres 10 minut. Niezdatna do handlu.",
    }

    new_lines = []
    for line in lines:
        parts = line.split('\t')
        if len(parts) >= 3 and parts[0] in pot_map:
            parts[2] = pot_map[parts[0]] + '\n'
            new_lines.append('\t'.join(parts))
        else:
            new_lines.append(line)

    with open(itemdesc_path, 'w', encoding='cp1250', newline='\r\n') as f:
        f.writelines(new_lines)
    print("[+] itemdesc.txt: zaktualizowano opisy mikstur")

def patch_uitooltip():
    paths = [
        os.path.join(REPO, 'Klient', 'pack', 'root', 'uitooltip.py'),
        os.path.join(REPO, 'Server', 'server-patches', 'krystian', 'zdalne-npc', 'client', 'root', 'uitooltip.py')
    ]
    for p in paths:
        if not os.path.isfile(p):
            continue
        with open(p, 'r', encoding='latin-1') as f:
            c = f.read()
        if '27053: "Zwi\\xeaksza Twoj\\xb1' in c or '27053: "Zwi' in c:
            continue
        target = '\t\t\t72161: "Umo\\xbfliwia zdalny dost\\xeap do Domu Aukcyjnego w M1.",\n'
        replacement = target + (
            '\t\t\t27053: "Zwi\\xeaksza Twoj\\xb1 Szybko\\x9c\\xe6 Ataku o +10% na okres 10 minut. Niezdatna do handlu.",\n'
            '\t\t\t27054: "Zwi\\xeaksza Szybko\\x9c\\xe6 Ruchu o +10% na okres 10 minut. Niezdatna do handlu.",\n'
            '\t\t\t27123: "Zwi\\xeaksza Twoj\\xb1 Szybko\\x9c\\xe6 Ataku o +10% na okres 10 minut. Niezdatna do handlu.",\n'
            '\t\t\t27100: "Zwi\\xeaksza Twoj\\xb1 Szybko\\x9c\\xe6 Ataku o +10% na okres 10 minut.",\n'
            '\t\t\t27101: "Zwi\\xeaksza Twoj\\xb1 Szybko\\x9c\\xe6 Ataku o +20% na okres 10 minut.",\n'
            '\t\t\t27102: "Zwi\\xeaksza Twoj\\xb1 Szybko\\x9c\\xe6 Ataku o +30% na okres 10 minut.",\n'
            '\t\t\t27110: "Zwi\\xeaksza Twoj\\xb1 Szybko\\x9c\\xe6 Ataku o +10% na okres 10 minut.",\n'
            '\t\t\t27111: "Zwi\\xeaksza Twoj\\xb1 Szybko\\x9c\\xe6 Ataku o +20% na okres 10 minut.",\n'
            '\t\t\t27112: "Zwi\\xeaksza Twoj\\xb1 Szybko\\x9c\\xe6 Ataku o +30% na okres 10 minut.",\n'
            '\t\t\t27103: "Zwi\\xeaksza Szybko\\x9c\\xe6 Ruchu o +10% na okres 10 minut.",\n'
            '\t\t\t27104: "Zwi\\xeaksza Szybko\\x9c\\xe6 Ruchu o +20% na okres 10 minut.",\n'
            '\t\t\t27105: "Zwi\\xeaksza Szybko\\x9c\\xe6 Ruchu o +30% na okres 10 minut.",\n'
            '\t\t\t27113: "Zwi\\xeaksza Szybko\\x9c\\xe6 Ruchu o +10% na okres 10 minut.",\n'
            '\t\t\t27114: "Zwi\\xeaksza Szybko\\x9c\\xe6 Ruchu o +20% na okres 10 minut.",\n'
            '\t\t\t27115: "Zwi\\xeaksza Szybko\\x9c\\xe6 Ruchu o +30% na okres 10 minut.",\n'
        )
        if target in c:
            c = c.replace(target, replacement, 1)
            with open(p, 'w', encoding='latin-1') as f:
                f.write(c)
            print(f"[+] {os.path.basename(p)}: zaktualizowano opisy w uitooltip.py")

def main():
    print("=== Aplikacja patcha: Balans i Opisy Mikstur Szybkosci ===")
    patch_itemdesc()
    patch_uitooltip()
    print("=== Gotowe! ===")

if __name__ == '__main__':
    main()
