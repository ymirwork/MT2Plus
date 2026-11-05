#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_workspace.py - Automatyczne czyszczenie niepotrzebnych plikow i higiena dysku MT2Plus.
Usuwa zbedny Docker build cache, stare backupy (>48h), duplikaty zrzutow SQL,
pliki .bak pakera klienta, wielkie logi syserr oraz bufor dist/.
Bezpieczny dla bazy danych, obrazow i kontenerow gry.
"""

import os
import sys
import time
import shutil
import subprocess

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if not os.path.exists(os.path.join(REPO_DIR, 'Server')):
    REPO_DIR = r'd:\Github\MT2Plus'

def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def get_dir_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if not os.path.islink(fp) and os.path.exists(fp):
                total += os.path.getsize(fp)
    return total

def clean_docker_cache():
    print("[1/5] Czyszczenie Docker Build Cache...")
    freed = 0
    try:
        # Sprawdz czy docker odpowiada
        res = subprocess.run(["docker", "builder", "prune", "-f"], capture_output=True, text=True, timeout=60)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if "Total:" in line or "Total reclaimed space:" in line:
                    print(f"  -> Docker builder prune: {line.strip()}")
            return True
        else:
            print("  -> Docker daemon nie jest uruchomiony (pomijanie).")
    except Exception as e:
        print(f"  -> Docker pominiety: {e}")
    return False

def clean_backups():
    print("[2/5] Porzadkowanie kopii zapasowych (Server/backups/)...")
    backups_dir = os.path.join(REPO_DIR, 'Server', 'backups')
    if not os.path.exists(backups_dir):
        print("  -> Katalog Server/backups nie istnieje.")
        return 0

    freed = 0
    now = time.time()
    cutoff_48h = now - (48 * 3600)

    # 1. Usun niespakowane foldery zrzutow, jesli istnieje odpowiednik .zip
    for item in os.listdir(backups_dir):
        item_path = os.path.join(backups_dir, item)
        if os.path.isdir(item_path):
            if item.lower() == 'reset-swiata':
                continue # wazny seed, nie ruszac
            matching_zip = item_path + '.zip'
            if os.path.exists(matching_zip):
                sz = get_dir_size(item_path)
                try:
                    shutil.rmtree(item_path)
                    freed += sz
                    print(f"  -> Usunieto niespakowany folder zrzutu (istnieje .zip): {item} ({format_bytes(sz)})")
                except Exception as e:
                    print(f"  -> Blad usuwania {item}: {e}")

    # 2. Usun archiwa zip starsze niz 48h
    for item in os.listdir(backups_dir):
        item_path = os.path.join(backups_dir, item)
        if os.path.isfile(item_path) and item.endswith('.zip'):
            mtime = os.path.getmtime(item_path)
            if mtime < cutoff_48h:
                sz = os.path.getsize(item_path)
                try:
                    os.remove(item_path)
                    freed += sz
                    print(f"  -> Usunieto stary backup (>48h): {item} ({format_bytes(sz)})")
                except Exception as e:
                    print(f"  -> Blad usuwania {item}: {e}")

    return freed

def clean_pack_backups():
    print("[3/5] Czyszczenie plikow tymczasowych pakera klienta (Klient/pack/)...")
    pack_dir = os.path.join(REPO_DIR, 'Klient', 'pack')
    if not os.path.exists(pack_dir):
        return 0

    freed = 0
    for root, _, files in os.walk(pack_dir):
        for f in files:
            if f.endswith('.bak') or f.endswith('.tmp'):
                fp = os.path.join(root, f)
                try:
                    sz = os.path.getsize(fp)
                    os.remove(fp)
                    freed += sz
                    print(f"  -> Usunieto plik tymczasowy: {f} ({format_bytes(sz)})")
                except Exception as e:
                    print(f"  -> Blad usuwania {fp}: {e}")
    return freed

def clean_logs():
    print("[4/5] Sprawdzanie i czyszczenie logow diagnostycznych...")
    freed = 0
    syserr_client = os.path.join(REPO_DIR, 'Klient', 'syserr.txt')
    if os.path.exists(syserr_client):
        sz = os.path.getsize(syserr_client)
        # Jesli plik przekracza 1 MB, wyzeruj go
        if sz > 1024 * 1024:
            try:
                with open(syserr_client, 'w', encoding='utf-8') as f:
                    f.truncate(0)
                freed += sz
                print(f"  -> Wyzerowano przerośniety Klient/syserr.txt ({format_bytes(sz)})")
            except Exception as e:
                print(f"  -> Blad zerowania syserr.txt: {e}")

    return freed

def clean_dist():
    print("[5/5] Czyszczenie bufora wydań (dist/)...")
    dist_dir = os.path.join(REPO_DIR, 'dist')
    if not os.path.exists(dist_dir):
        return 0

    freed = 0
    for item in os.listdir(dist_dir):
        ip = os.path.join(dist_dir, item)
        if item.lower() == 'patcher-web':
            continue # synchronizacja web patchera moze miec wlasne zarzadzanie
        try:
            if os.path.isdir(ip):
                sz = get_dir_size(ip)
                shutil.rmtree(ip)
                freed += sz
                print(f"  -> Usunieto bufor wydania: {item} ({format_bytes(sz)})")
            elif os.path.isfile(ip):
                sz = os.path.getsize(ip)
                os.remove(ip)
                freed += sz
                print(f"  -> Usunieto plik bufora: {item} ({format_bytes(sz)})")
        except Exception as e:
            print(f"  -> Blad czyszczenia dist/{item}: {e}")

    return freed

def main():
    print("=" * 65)
    print("🧹 MT2Plus - Automatyczna Higiena Dysku i Czyszczenie Śmieci")
    print(f"Repozytorium: {REPO_DIR}")
    print("=" * 65)

    clean_docker_cache()
    freed_b = clean_backups()
    freed_p = clean_pack_backups()
    freed_l = clean_logs()
    freed_d = clean_dist()

    total_freed = freed_b + freed_p + freed_l + freed_d
    print("=" * 65)
    print(f"✅ Czyszczenie zakonczone pomyslnie! Zwolniono z dysku: {format_bytes(total_freed)}")
    print("=" * 65)

if __name__ == '__main__':
    main()
