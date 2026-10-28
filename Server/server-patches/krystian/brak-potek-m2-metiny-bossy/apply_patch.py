#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modyfikacja: Usunięcie dropu Czerwonych i Niebieskich Mikstur z Kamieni Metin i Bossów od M2 w górę.
Autor: Krystian / MT2Plus
"""

import os
import re
import sys

# Moby / Metiny z M1, w których zostawiamy drop potek dla początkujących graczy:
M1_MOBS_TO_KEEP = {
    191, 192, 193, 194,     # Bossy M1: Lykos, Scrofa, Bera, Tigris
    8001, 8002, 8003, 8004  # Metiny M1: Cierpienia, Walki, Bitwy, Chciwości
}

# VNUMy Czerwonych i Niebieskich Mikstur do usunięcia:
POTION_VNUMS_TO_REMOVE = {
    '27001', '27002', '27003', '27007', '27051',  # Czerwone (M, Ś, D, XL, starter)
    '27004', '27005', '27006', '27008', '27052',  # Niebieskie (M, Ś, D, XL, starter)
}

TARGET_FILES = [
    'Server/linux-port/docker/game/src/serverfiles/share/locale/poland/mob_drop_item.txt',
    'Server/linux-port/docker/game/mob_drop_item.dropedit.append.txt',
    'Server/linux-port/docker/game/ochao/mob_drop_item.ochao.txt',
    'Server/linux-port/docker/game/arezzo/mob_drop_item.arezzo.txt',
    'Server/linux-port/docker/game/arezzo/mob_drop_item.arezzo2.txt',
    'Server/linux-port/docker/game/yohara_zaklety/mob_drop_item.yohara_zaklety.txt'
]

def find_repo_root():
    curr = os.path.abspath(os.path.dirname(__file__))
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, 'PROJECT_CONTEXT.md')):
            return curr
        curr = os.path.dirname(curr)
    return os.getcwd()

def process_file(abs_path):
    if not os.path.exists(abs_path):
        print(f"[OSTRZEŻENIE] Plik nie istnieje: {abs_path}")
        return 0, 0

    with open(abs_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified_groups = 0
    removed_pots = 0

    def process_group(glines):
        nonlocal modified_groups, removed_pots
        mob = None
        for l in glines:
            m = re.match(r'^\s*mob\s+(\d+)', l, re.IGNORECASE)
            if m:
                mob = int(m.group(1))
                break

        # Zachowaj M1 bez zmian
        if mob is not None and mob in M1_MOBS_TO_KEEP:
            return glines

        has_pot = any(
            re.match(r'^\s*(\d+)\s+(\d+)\s+', l) and
            re.match(r'^\s*(\d+)\s+(\d+)\s+', l).group(2) in POTION_VNUMS_TO_REMOVE
            for l in glines
        )
        if not has_pot:
            return glines

        modified_groups += 1
        new_glines = []
        item_idx = 1

        for l in glines:
            ending = '\r\n' if l.endswith('\r\n') else '\n'
            clean_l = l.rstrip('\r\n')
            m = re.match(r'^(\s*)(\d+)(\s+)(\S+)(.*)$', clean_l)
            if m and m.group(2).isdigit() and not re.match(r'^\s*(mob|type|kill_drop|level_limit)', clean_l, re.IGNORECASE):
                leading_ws = m.group(1)
                ws_after_idx = m.group(3)
                vnum_token = m.group(4)
                rest = m.group(5)

                if vnum_token in POTION_VNUMS_TO_REMOVE:
                    removed_pots += 1
                    continue

                new_glines.append(f'{leading_ws}{item_idx}{ws_after_idx}{vnum_token}{rest}{ending}')
                item_idx += 1
            else:
                new_glines.append(l)

        return new_glines

    cur_group = []
    output_lines = []

    for line in lines:
        if re.match(r'^\s*Group\b', line, re.IGNORECASE):
            if cur_group:
                output_lines.extend(process_group(cur_group))
                cur_group = []
            cur_group.append(line)
        elif cur_group:
            cur_group.append(line)
            if re.match(r'^\s*\}', line):
                output_lines.extend(process_group(cur_group))
                cur_group = []
        else:
            output_lines.append(line)

    if cur_group:
        output_lines.extend(process_group(cur_group))

    with open(abs_path, 'w', encoding='utf-8', newline='') as f:
        f.writelines(output_lines)

    return modified_groups, removed_pots

def main():
    root = find_repo_root()
    print(f"MT2Plus: Usuwanie Czerwonych i Niebieskich Mikstur z Metinów i Bossów od M2 w górę...")
    print(f"Katalog główny: {root}\n")

    total_groups = 0
    total_pots = 0

    for rel_path in TARGET_FILES:
        abs_path = os.path.join(root, rel_path.replace('/', os.sep))
        mod_groups, rem_pots = process_file(abs_path)
        total_groups += mod_groups
        total_pots += rem_pots
        print(f" - {rel_path}: zmodyfikowano grup: {mod_groups}, usunięto linii potek: {rem_pots}")

    print(f"\n[SUKCES] Łącznie zmodyfikowano grup: {total_groups}, usunięto linii mikstur: {total_pots}")

if __name__ == '__main__':
    main()
