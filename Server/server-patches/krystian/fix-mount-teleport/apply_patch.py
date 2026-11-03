#!/usr/bin/env python3
"""apply_patch.py -- Fix dla schodzenia z mounta / wierzchowca kostiumowego podczas teleportacji (np. Boss Tracker)

Problem:
  Dotychczas funkcja CHARACTER::CheckMount() (MountSystem.cpp), wywoływana po każdym logowaniu i warpie (input_login.cpp),
  jedynie przywoływała wierzchowca obok gracza (Summon), zamiast na niego wsiadać (Mount). W rezultacie każde użycie
  Boss Trackera, pierścienia teleportacji czy zmiana mapy zrzucała gracza z wierzchowca na ziemię.

Rozwiązanie:
  1. W CMountActor::Mount zapisywana jest flaga braku zejścia z mounta: `mount.dismounted = 0`.
  2. W CMountActor::Unmount (ręczne zejście np. Ctrl+G) ustawiane jest `mount.dismounted = 1`.
  3. W CHARACTER::MountUnsummon (zdjęcie pieczęci) flaga jest zerowana.
  4. W CHARACTER::CheckMount() jeżeli gracz nie zszedł celowo z wierzchowca (`mount.dismounted != 1`),
     automatycznie wsiada na założonego wierzchowca (`mountSystem->Mount`), zachowując stan jazdy po TP/loginie.
  5. W CMountSystem::Mount bezpiecznie alokowany jest CMountActor, jeśli jeszcze nie istniał.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TARGET_FILE = os.path.join(REPO_ROOT, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "MountSystem.cpp")

MARKER = 'm_pkOwner->SetQuestFlag("mount.dismounted", 0);'

def main():
    target = TARGET_FILE
    if len(sys.argv) > 1:
        target = sys.argv[1]

    if not os.path.exists(target):
        sys.exit(f"Target file not found: {target}")

    with open(target, "rb") as f:
        content = f.read().decode("latin-1")

    if MARKER in content:
        print("Mount teleport fix is already applied.")
        return

    # Check that required targets exist
    old_mount = '\tm_pkOwner->AddAffect(AFFECT_MOUNT_BONUS, mountItem->GetProto()->aApplies[i].bType, mountItem->GetProto()->aApplies[i].lValue, AFF_NONE, lDuration, 0, false);\n\t}\n\n\treturn m_pkOwner->GetMountVnum() == m_dwVnum;'
    new_mount = '\tm_pkOwner->AddAffect(AFFECT_MOUNT_BONUS, mountItem->GetProto()->aApplies[i].bType, mountItem->GetProto()->aApplies[i].lValue, AFF_NONE, lDuration, 0, false);\n\t}\n\n\tSetSummonItem(mountItem);\n\tm_pkOwner->SetQuestFlag("mount.dismounted", 0);\n\n\treturn m_pkOwner->GetMountVnum() == m_dwVnum;'

    if old_mount not in content:
        old_mount = old_mount.replace("\n", "\r\n")
        new_mount = new_mount.replace("\n", "\r\n")

    if old_mount not in content:
        sys.exit("Error: Could not locate target block in CMountActor::Mount")

    content = content.replace(old_mount, new_mount, 1)

    old_unmount = 'void CMountActor::Unmount()\n{\n\tif (0 == m_pkOwner)\n\t\treturn;\n\n\tif (!m_pkOwner->GetMountVnum())\n\t\treturn;\n\n\tm_pkOwner->RemoveAffect(AFFECT_MOUNT);'
    new_unmount = 'void CMountActor::Unmount()\n{\n\tif (0 == m_pkOwner)\n\t\treturn;\n\n\tif (!m_pkOwner->GetMountVnum())\n\t\treturn;\n\n\tm_pkOwner->SetQuestFlag("mount.dismounted", 1);\n\n\tm_pkOwner->RemoveAffect(AFFECT_MOUNT);'

    if old_unmount not in content:
        old_unmount = old_unmount.replace("\n", "\r\n")
        new_unmount = new_unmount.replace("\n", "\r\n")

    if old_unmount not in content:
        sys.exit("Error: Could not locate target block in CMountActor::Unmount")

    content = content.replace(old_unmount, new_unmount, 1)

    old_check = 'void CHARACTER::CheckMount()\n{\n\tCMountSystem* mountSystem = GetMountSystem();\n\tLPITEM mountItem = GetWear(WEAR_COSTUME_MOUNT);\n\n\tif (!mountSystem || !mountItem)\n\t\treturn;\n\n\tDWORD mobVnum = mountItem->GetValue(1);\n\n\tif (0 == mobVnum)\n\t\treturn;\n\n\tif (mountSystem->CountSummoned() == 0)\n\t\tmountSystem->Summon(mobVnum, mountItem, false);\n}'
    new_check = 'void CHARACTER::CheckMount()\n{\n\tCMountSystem* mountSystem = GetMountSystem();\n\tLPITEM mountItem = GetWear(WEAR_COSTUME_MOUNT);\n\n\tif (!mountSystem || !mountItem)\n\t\treturn;\n\n\tif (IsPolymorphed() || IsDead())\n\t\treturn;\n\n\tDWORD mobVnum = mountItem->GetValue(1);\n\n\tif (0 == mobVnum)\n\t\treturn;\n\n\tif (GetQuestFlag("mount.dismounted") != 1)\n\t{\n\t\tmountSystem->Mount(mobVnum, mountItem);\n\t}\n\telse if (mountSystem->CountSummoned() == 0)\n\t{\n\t\tmountSystem->Summon(mobVnum, mountItem, false);\n\t}\n}'

    if old_check not in content:
        old_check = old_check.replace("\n", "\r\n")
        new_check = new_check.replace("\n", "\r\n")

    if old_check not in content:
        sys.exit("Error: Could not locate target block in CHARACTER::CheckMount")

    content = content.replace(old_check, new_check, 1)

    with open(target, "wb") as f:
        f.write(content.encode("latin-1"))

    print(f"Successfully applied mount teleport fix to {target}")

if __name__ == "__main__":
    main()
