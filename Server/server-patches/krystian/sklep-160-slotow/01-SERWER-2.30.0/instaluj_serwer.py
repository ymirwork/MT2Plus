#!/usr/bin/env python3
"""Guarded MT2009 Plus 2.30.0 shop source installer. Python 3, no network."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime


BASE = Path(__file__).resolve().parent
SOURCE = BASE / 'pliki'
ROUTES = {
    'src/server/game/src/char_shop.cpp': 'char_shop.cpp',
    'src/server/game/src/ikarus_shop_manager.cpp': 'ikarus_shop_manager.cpp',
    'quest/shop_unlock_slots.quest': 'shop_unlock_slots.quest',
    'src/serverfiles/share/locale/poland/quest/pre_qc/shop_unlock_slots.quest': 'shop_unlock_slots.quest',
    'src/serverfiles/share/locale/poland/quest/quest/systems/shop_unlock_slots.quest': 'shop_unlock_slots.quest',
    'Dockerfile': 'Dockerfile',
}


def digest(data):
    # The Windows checkout may use CRLF while VPS sources use LF.
    return hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()


def main():
    ap = argparse.ArgumentParser(description='MT2009 Plus: 160 pol sklepu za klucze')
    ap.add_argument('--server-root', required=True, type=Path,
                    help='katalog serwera z VERSION lub MOD_VERSION i linux-port')
    action = ap.add_mutually_exclusive_group(required=True)
    action.add_argument('--check', action='store_true')
    action.add_argument('--install', action='store_true')
    args = ap.parse_args()
    root = args.server_root.resolve()
    version_paths = [path for path in (root / 'VERSION', root / 'MOD_VERSION') if path.is_file()]
    if not version_paths or any(path.read_text(encoding='utf-8-sig').strip() != '2.30.0'
                                for path in version_paths):
        raise SystemExit('Wymagana baza MT2009 Plus 2.30.0 (VERSION lub MOD_VERSION).')
    docker_game = root / 'linux-port/docker/game'
    if not docker_game.is_dir():
        raise SystemExit('Brak linux-port/docker/game. Wskaz katalog glowny serwera.')
    manifest = json.loads((BASE / 'manifest.json').read_text(encoding='utf-8'))
    overlay = root / 'linux-port/overlays/playerbot/src/game/src'
    plan = []
    bad = []
    for rel, source_name in ROUTES.items():
        expected = manifest[rel]
        payload = (SOURCE / source_name).read_bytes()
        if digest(payload) != expected['after']:
            raise SystemExit('Uszkodzony plik paczki: ' + source_name)
        targets = [docker_game / rel]
        if rel.startswith('src/server/game/src/') and overlay.is_dir():
            candidate = overlay / Path(rel).name
            if candidate.exists():
                targets.append(candidate)
        for target in targets:
            current = digest(target.read_bytes()) if target.is_file() else None
            if current == expected['after']:
                print('JUZ ZAINSTALOWANE:', target)
                continue
            if current != expected['before']:
                bad.append('%s (SHA256: %s)' % (target, current or 'brak'))
                continue
            plan.append((target, payload))
            print('GOTOWE DO ZMIANY:', target)
    if bad:
        print('WERSJA NIEZGODNA. Niczego nie zmieniono.', file=sys.stderr)
        for entry in bad:
            print(entry, file=sys.stderr)
        raise SystemExit(2)
    if not plan:
        print('Wszystkie pliki sa juz zainstalowane.')
        return
    if args.check:
        print('KONTROLA OK:', len(plan), 'plikow do zmiany; uruchom ponownie z --install.')
        return
    backup = root / ('backup-sklep-160-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
    backups = []
    try:
        for target, payload in plan:
            relative = target.relative_to(root)
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                shutil.copy2(target, saved)
            backups.append((target, saved if target.exists() else None))
        for target, payload in plan:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + '.shop160-new')
            temporary.write_bytes(payload)
            temporary.replace(target)
            if digest(target.read_bytes()) != digest(payload):
                raise IOError('Kontrola zapisu nie powiodla sie: ' + str(target))
    except Exception:
        for target, saved in backups:
            if saved is None:
                target.unlink(missing_ok=True)
            else:
                shutil.copy2(saved, target)
        raise
    print('ZAINSTALOWANO. Kopia:', backup)
    print('Teraz zbuduj i uruchom caly stos Docker zgodnie z instrukcja.')


if __name__ == '__main__':
    main()
