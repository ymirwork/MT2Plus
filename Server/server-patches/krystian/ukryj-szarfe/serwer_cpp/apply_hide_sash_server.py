#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_hide_sash_server.py
Modyfikacja serwera C++ dodajaca obsluge ukrywania szarfy (bit 8 w masce kostiumow).
Dotyczy plikow: item.cpp oraz cmd_general.cpp
"""
import os
import sys

def patch_file(path, old_bytes, new_bytes):
    if not os.path.exists(path):
        print(f"Brak pliku: {path}")
        return False
    with open(path, 'rb') as f:
        content = f.read()
    if new_bytes in content:
        print(f"Plik {path} juz zawiera modyfikacje.")
        return True
    if old_bytes not in content:
        print(f"Nie znaleziono wzorca w {path}!")
        return False
    content = content.replace(old_bytes, new_bytes, 1)
    with open(path, 'wb') as f:
        f.write(content)
    print(f"Pomyslnie zmodyfikowano: {path}")
    return True

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    game_src = os.path.join(base_dir, 'Server', 'linux-port', 'docker', 'game', 'src', 'server', 'game', 'src')
    
    item_cpp = os.path.join(game_src, 'item.cpp')
    cmd_cpp = os.path.join(game_src, 'cmd_general.cpp')

    old_item = (
        b"\tLPITEM costumeHair = ch->GetWear(WEAR_COSTUME_HAIR);\r\n"
        b"\tconst bool hairLeaving = costumeHair && costumeHair == leaving;\r\n"
        b"\tif (hairLeaving) costumeHair = NULL;\r\n"
        b"\tif (costumeHair)\r\n"
        b"\t\tch->SetPart(PART_HAIR, (hiddenMask & 2) ? 0 : costumeHair->GetValue(3));\r\n"
        b"\telse if (hairLeaving)\r\n"
        b"\t\tch->SetPart(PART_HAIR, 0); // what the engine does for a hair costume taken off\r\n"
        b"\tch->UpdatePacket();"
    )

    new_item = (
        b"\tLPITEM costumeHair = ch->GetWear(WEAR_COSTUME_HAIR);\r\n"
        b"\tconst bool hairLeaving = costumeHair && costumeHair == leaving;\r\n"
        b"\tif (hairLeaving) costumeHair = NULL;\r\n"
        b"\tif (costumeHair)\r\n"
        b"\t\tch->SetPart(PART_HAIR, (hiddenMask & 2) ? 0 : costumeHair->GetValue(3));\r\n"
        b"\telse if (hairLeaving)\r\n"
        b"\t\tch->SetPart(PART_HAIR, 0); // what the engine does for a hair costume taken off\r\n"
        b"#ifdef ENABLE_ACCE_COSTUME_SYSTEM\r\n"
        b"\tLPITEM costumeAcce = ch->GetWear(WEAR_COSTUME_ACCE);\r\n"
        b"\tif (costumeAcce == leaving) costumeAcce = NULL;\r\n"
        b"\tch->SetPart(PART_ACCE, (!(hiddenMask & 8) && costumeAcce) ? costumeAcce->GetAcceVnum() : 0);\r\n"
        b"#endif\r\n"
        b"\tch->UpdatePacket();"
    )

    old_cmd = (
        b"ACMD(do_costume_hide)\r\n"
        b"{\r\n"
        b"\tchar arg1[32], arg2[32];\r\n"
        b"\ttwo_arguments(argument, arg1, sizeof(arg1), arg2, sizeof(arg2));\r\n"
        b"\tconst bool byMask = arg1[0] == 'm' && arg1[1] == '\\0';\r\n"
        b"\tint value = 0;\r\n"
        b"\tstr_to_number(value, byMask ? arg2 : arg1);\r\n"
        b"\tconst BYTE mask = byMask ? (BYTE)(value & 7) : (value ? 7 : 0);"
    )

    new_cmd = (
        b"ACMD(do_costume_hide)\r\n"
        b"{\r\n"
        b"\tchar arg1[32], arg2[32];\r\n"
        b"\ttwo_arguments(argument, arg1, sizeof(arg1), arg2, sizeof(arg2));\r\n"
        b"\tconst bool byMask = arg1[0] == 'm' && arg1[1] == '\\0';\r\n"
        b"\tint value = 0;\r\n"
        b"\tstr_to_number(value, byMask ? arg2 : arg1);\r\n"
        b"\tconst BYTE mask = byMask ? (BYTE)(value & 15) : (value ? 15 : 0);"
    )

    patch_file(item_cpp, old_item, new_item)
    patch_file(cmd_cpp, old_cmd, new_cmd)

if __name__ == '__main__':
    main()
