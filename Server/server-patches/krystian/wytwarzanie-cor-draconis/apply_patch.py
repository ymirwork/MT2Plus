#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patch: Wytwarzanie Cor Draconis u NPC Mistrz (Opcja A - proporcja 3:1)
Autor: Krystian
Data: 2026-11-02
"""

import os
import shutil
import subprocess

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(PATCH_DIR, "..", "..", ".."))

def apply():
    print("=== [PATCH] Wytwarzanie Cor Draconis (3:1) u NPC Mistrz ===")
    
    # 1. Kopiowanie plikow klienta
    klient_root = os.path.join(REPO_ROOT, "Klient", "pack", "root")
    src_root = os.path.join(PATCH_DIR, "klient_pliki", "root")
    if os.path.exists(klient_root) and os.path.exists(src_root):
        for f in ["game.py", "uicube.py"]:
            src_f = os.path.join(src_root, f)
            dst_f = os.path.join(klient_root, f)
            if os.path.exists(src_f):
                shutil.copy2(src_f, dst_f)
                print(f"[OK] Skopiowano do klienta: {f}")
    
    # 2. Weryfikacja cube.pasy.txt
    cube_pasy_path = os.path.join(REPO_ROOT, "Server", "linux-port", "docker", "game", "cube.pasy.txt")
    if os.path.exists(cube_pasy_path):
        with open(cube_pasy_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "50255" not in content:
            cor_recipes = """

# Cor Draconis (szlifowane) (3:1)
section
npc\t20082
item\t50255\t3
reward\t50256\t1
gold\t0
percent\t100
end

# Cor Draconis (rzadkie) (3:1)
section
npc\t20082
item\t50256\t3
reward\t50257\t1
gold\t0
percent\t100
end

# Cor Draconis (antyczne) (3:1)
section
npc\t20082
item\t50257\t3
reward\t50258\t1
gold\t0
percent\t100
end

# Cor Draconis (legendarne) (3:1)
section
npc\t20082
item\t50258\t3
reward\t50259\t1
gold\t0
percent\t100
end
"""
            with open(cube_pasy_path, "a", encoding="utf-8") as f:
                f.write(cor_recipes)
            print("[OK] Dodano receptury Cor Draconis do cube.pasy.txt")
        else:
            print("[INFO] Receptury Cor Draconis juz obecne w cube.pasy.txt")
            
    print("[SUCCESS] Patch wytwarzania Cor Draconis zostal zastosowany!")

if __name__ == "__main__":
    apply()
