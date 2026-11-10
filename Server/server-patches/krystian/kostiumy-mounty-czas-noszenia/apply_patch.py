#!/usr/bin/env python3
"""apply_patch.py - Reaplikacja zmian w kodzie C++ dla licznika czasu kostiumow i wierzchowcow tylko podczas logowania / noszenia (LIMIT_TIMER_BASED_ON_WEAR).
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

def patch_mount_system():
    path = os.path.join(REPO_ROOT, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "MountSystem.cpp")
    if not os.path.isfile(path):
        return
    content = open(path, "r", encoding="latin-1").read()
    marker = "MT2009_PLUS_COSTUMES_MOUNTS_WEAR_TIMER_V1"
    if marker in content:
        print("MountSystem.cpp: already patched")
        return

    old_block = 'static bool MountItem_GetRemainingSeconds(LPITEM mountItem, long* pDurationOut)\n{\n'
    new_block = '''static bool MountItem_GetRemainingSeconds(LPITEM mountItem, long* pDurationOut)
{
\t// MT2009_PLUS_COSTUMES_MOUNTS_WEAR_TIMER_V1: a mount seal with wear timer limit counts down in socket 0
\tfor (int i = 0; i < ITEM_LIMIT_MAX_NUM; ++i)
\t{
\t\tBYTE bLimit = mountItem->GetProto()->aLimits[i].bType;
\t\tif (LIMIT_TIMER_BASED_ON_WEAR == bLimit)
\t\t{
\t\t\tlong remain = mountItem->GetSocket(0);
\t\t\tif (remain <= 0)
\t\t\t{
\t\t\t\tremain = mountItem->GetProto()->aLimits[i].lValue;
\t\t\t\tif (!remain)
\t\t\t\t\tremain = 60 * 60 * 24 * 7;
\t\t\t\tif (mountItem->GetSocket(0) != 0 && remain <= 0)
\t\t\t\t{
\t\t\t\t\t*pDurationOut = 0;
\t\t\t\t\treturn false;
\t\t\t\t}
\t\t\t\tmountItem->SetSocket(0, remain);
\t\t\t}
\t\t\t*pDurationOut = remain;
\t\t\treturn true;
\t\t}
\t}

'''
    if old_block in content:
        content = content.replace(old_block, new_block, 1)
        open(path, "w", encoding="latin-1").write(content)
        print("MountSystem.cpp: patched")
    else:
        print("MountSystem.cpp: old block not found")

def patch_item_manager():
    path = os.path.join(REPO_ROOT, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "item_manager.cpp")
    if not os.path.isfile(path):
        return
    content = open(path, "r", encoding="latin-1").read()
    if "item->GetType() == ITEM_COSTUME" in content:
        print("item_manager.cpp: already patched")
        return
    old_target = '\t\t\t\tif (0 == duration)\n\t\t\t\t\tduration = 60 * 60 * 10;\n'
    new_target = '''\t\t\t\tif (0 == duration)
\t\t\t\t{
\t\t\t\t\tif (item->GetType() == ITEM_COSTUME)
\t\t\t\t\t\tduration = 60 * 60 * 24 * 7;
\t\t\t\t\telse
\t\t\t\t\tduration = 60 * 60 * 10;
\t\t\t\t}\n'''
    if old_target in content:
        content = content.replace(old_target, new_target, 1)
        open(path, "w", encoding="latin-1").write(content)
        print("item_manager.cpp: patched")
    elif "item->IsCostume()" in content:
        content = content.replace("item->IsCostume()", "item->GetType() == ITEM_COSTUME")
        open(path, "w", encoding="latin-1").write(content)
        print("item_manager.cpp: patched IsCostume to GetType")
    else:
        print("item_manager.cpp: old target not found")

def patch_playerbot_bonus():
    paths = [
        os.path.join(REPO_ROOT, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "playerbot_bonus.h"),
        os.path.join(REPO_ROOT, "Server", "linux-port", "overlays", "playerbot", "src", "game", "src", "playerbot_bonus.h")
    ]
    for path in paths:
        if not os.path.isfile(path):
            continue
        content = open(path, "r", encoding="latin-1").read()
        if "LIMIT_TIMER_BASED_ON_WEAR" in content:
            print(f"{os.path.basename(path)}: already patched")
            continue
        old_str = '''\t\t\tconst BYTE type = item->GetProto()->aLimits[i].bType;
\t\t\tif (type == LIMIT_REAL_TIME || type == LIMIT_REAL_TIME_START_FIRST_USE)'''
        new_str = '''\t\t\tconst BYTE type = item->GetProto()->aLimits[i].bType;
\t\t\tif (type == LIMIT_TIMER_BASED_ON_WEAR)
\t\t\t{
\t\t\t\tconst long remain = item->GetSocket(0);
\t\t\t\tif (remain <= 0)
\t\t\t\t\treturn item->GetProto()->aLimits[i].lValue;
\t\t\t\treturn remain;
\t\t\t}
\t\t\tif (type == LIMIT_REAL_TIME || type == LIMIT_REAL_TIME_START_FIRST_USE)'''
        if old_str in content:
            content = content.replace(old_str, new_str, 1)
            open(path, "w", encoding="latin-1").write(content)
            print(f"{path}: patched")

def main():
    patch_mount_system()
    patch_item_manager()
    patch_playerbot_bonus()

if __name__ == "__main__":
    main()
