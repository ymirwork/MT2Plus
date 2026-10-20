#!/usr/bin/env python3
"""Safely reapply the MT2009 boss tracker after an official server update.

The patch is tested against a copy of the current sources. Unknown upstream
changes are rejected if neither bundled patch applies exactly.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime

HERE = Path(__file__).resolve().parent
NAMES = ("char.h", "cmd.cpp", "cmd_general.cpp", "regen.h", "regen.cpp")
REL = Path("linux-port/docker/game/src/server/game/src")
PATCHES = ("boss-tracker-2.31.0.patch", "boss-tracker-2.30.0.patch")
MARKERS = {
    "char.h": b"GetRegen() const",
    "cmd.cpp": b"MT2009_BOSS_TRACKER_V1",
    "cmd_general.cpp": b"ACMD(do_boss_tracker_tp)",
    "regen.h": b"tracker_kind",
    "regen.cpp": b"regen_boss_tracker_teleport",
}


def normalized(data):
    return data.replace(b"\r\n", b"\n")


def run(*argv, cwd=None, env=None, capture=False):
    return subprocess.run(argv, cwd=cwd, env=env, check=False,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if capture else None,
                          text=True)


def source_state(files):
    flags = [MARKERS[name] in files[name] for name in NAMES]
    if all(flags):
        return "installed"
    if any(flags):
        raise RuntimeError("CZESCIOWA INSTALACJA: sprawdz pliki; niczego nie zmieniono.")
    return "missing"


def prepare_patch(files):
    if not shutil.which("git"):
        raise RuntimeError("Brak Git; zainstaluj Git for Windows albo git na VPS.")
    for patch_name in PATCHES:
        patch = HERE / patch_name
        if not patch.is_file():
            continue
        with tempfile.TemporaryDirectory(prefix="mt2009-tracker-", dir=HERE) as tmp:
            work = Path(tmp)
            src = work / REL
            src.mkdir(parents=True)
            for name, data in files.items():
                (src / name).write_bytes(data)
            cmd = ("git", "apply", "--check", str(patch))
            checked = run(*cmd, cwd=work, capture=True)
            if checked.returncode:
                continue
            applied = run("git", "apply", str(patch), cwd=work, capture=True)
            if applied.returncode:
                continue
            result = {name: (src / name).read_bytes() for name in NAMES}
            if source_state(result) == "installed":
                return patch_name, result
    raise RuntimeError("NIEZGODNA AKTUALIZACJA: tracker wymaga nowej poprawki; niczego nie zmieniono.")


def fingerprint(root, files):
    h = hashlib.sha256(str(root).encode("utf-8"))
    version = (root / "VERSION").read_bytes() if (root / "VERSION").is_file() else b"?"
    h.update(version)
    for name in NAMES:
        h.update(name.encode("ascii"))
        h.update(files[name])
    return h.hexdigest()


def build_and_restart(root):
    compose = root / "linux-port/docker"
    env = os.environ.copy()
    if os.name != "nt":
        env.setdefault("M2_MAKE_JOBS", "1")
    base = ("docker", "compose", "--project-directory", str(compose))
    print("Budowanie gry z trackerem (to moze potrwac kilka minut)...", flush=True)
    if run(*base, "build", "game", env=env).returncode:
        raise RuntimeError("Budowanie gry nie powiodlo sie.")
    print("Uruchamianie nowej wersji gry...", flush=True)
    if run(*base, "up", "-d", "--no-deps", "--force-recreate", "game").returncode:
        raise RuntimeError("Nie udalo sie uruchomic kontenera game.")
    ident = run(*base, "ps", "-q", "game", capture=True)
    if ident.returncode or not ident.stdout.strip():
        raise RuntimeError("Brak dzialajacego kontenera game.")
    container = ident.stdout.strip().splitlines()[0]
    for _ in range(48):
        status = run("docker", "inspect", "-f", "{{.State.Health.Status}}",
                     container, capture=True)
        if status.returncode == 0 and status.stdout.strip() == "healthy":
            return
        if status.stdout.strip() == "unhealthy":
            break
        time.sleep(5)
    raise RuntimeError("Kontener game nie jest healthy; sprawdz jego logi.")


def main():
    parser = argparse.ArgumentParser(description="Tracker MT2009 Plus po aktualizacji")
    parser.add_argument("--server-root", type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--repair", action="store_true")
    args = parser.parse_args()
    root = args.server_root.resolve()
    source = root / REL
    if not (root / "VERSION").is_file() or not source.is_dir():
        raise RuntimeError("To nie jest glowny folder serwera MT2009 Plus.")
    original = {name: (source / name).read_bytes() for name in NAMES}
    clean = {name: normalized(data) for name, data in original.items()}
    state = source_state(clean)
    patch_name = None
    result = clean
    if state == "missing":
        patch_name, result = prepare_patch(clean)
    if args.check:
        print("ALREADY_INSTALLED" if state == "installed" else
              "PATCH_COMPATIBLE: " + patch_name)
        return

    backup = None
    if state == "missing":
        backup = root / ("backup-tracker-" +
                         datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
        for name, data in original.items():
            dest = backup / REL / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        try:
            for name, data in result.items():
                dest = source / name
                temp = dest.with_name(dest.name + ".tracker-new")
                temp.write_bytes(data)
                os.replace(temp, dest)
        except Exception:
            for name, data in original.items():
                (source / name).write_bytes(data)
            raise
        print("TRACKER_INSTALLED; kopia:", backup, flush=True)

    stamp = HERE / "tracker-ready.json"
    expected = fingerprint(root, result)
    if state == "installed" and stamp.is_file():
        try:
            if json.loads(stamp.read_text(encoding="utf-8"))["fingerprint"] == expected:
                print("TRACKER_READY: aktualna wersja jest juz zbudowana.")
                return
        except (OSError, ValueError, KeyError):
            pass
    try:
        build_and_restart(root)
    except Exception:
        if backup:
            for name, data in original.items():
                (source / name).write_bytes(data)
            print("Przywrocono zrodla sprzed instalacji trackera.", file=sys.stderr)
        raise
    stamp.write_text(json.dumps({"fingerprint": expected,
                                 "version": (root / "VERSION").read_text(encoding="utf-8-sig").strip(),
                                 "built_at": datetime.now().isoformat()}, indent=2) + "\n",
                     encoding="utf-8")
    print("TRACKER_READY")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        raise SystemExit(1)
