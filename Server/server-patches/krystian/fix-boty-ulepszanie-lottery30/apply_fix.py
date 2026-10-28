#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

def apply_patch_to_dir(upstream_path, economy_path):
    if not os.path.isfile(upstream_path) or not os.path.isfile(economy_path):
        return False

    with open(upstream_path, 'rb') as f:
        c1 = f.read()

    if b'OnPlayerBotLottery30Refined' not in c1:
        target1 = b'SumPlayerBotItemLines(item, APPLY_NORMAL_HIT_DAMAGE_BONUS), market, taken,\r\n\t\t\t\t(unsigned int)GetPlayerBotLevel30SaleTarget(item));\r\n\t\treturn true;\r\n\t}'
        addition1 = b'''\r\n\r\n\tvoid OnPlayerBotLottery30Refined(LPCHARACTER ch, DWORD dwOldId, LPITEM pkItemAfter)\r\n\t{\r\n\t\tif (!ch || ch->GetQuestFlag(PLAYERBOT_LOTTERY30_DAY_FLAG) != GetPlayerBotLottery30Today() ||\r\n\t\t\t\t(DWORD)ch->GetQuestFlag(PLAYERBOT_LOTTERY30_ID_FLAG) != dwOldId)\r\n\t\t\treturn;\r\n\r\n\t\tif (pkItemAfter && IsPlayerBotLottery30Surplus(ch, pkItemAfter))\r\n\t\t{\r\n\t\t\tch->SetQuestFlag(PLAYERBOT_LOTTERY30_ID_FLAG, (int)pkItemAfter->GetID());\r\n\t\t\tsys_log(0, "PLAYERBOT_SURPLUS: lottery30 updated pid=%u name=%s old_item=%u new_item=%u vnum=%u plus=%u",\r\n\t\t\t\t\tch->GetPlayerID(), ch->GetName(), dwOldId, pkItemAfter->GetID(),\r\n\t\t\t\t\tpkItemAfter->GetVnum(), (unsigned int)pkItemAfter->GetRefineLevel());\r\n\t\t}\r\n\t\telse\r\n\t\t{\r\n\t\t\tch->SetQuestFlag(PLAYERBOT_LOTTERY30_ID_FLAG, 0);\r\n\t\t\tsys_log(0, "PLAYERBOT_SURPLUS: lottery30 finished pid=%u name=%s old_item=%u",\r\n\t\t\t\t\tch->GetPlayerID(), ch->GetName(), dwOldId);\r\n\t\t}\r\n\t}'''
        if target1 in c1:
            c1 = c1.replace(target1, target1 + addition1, 1)
            with open(upstream_path, 'wb') as f:
                f.write(c1)
            print(f"Successfully patched {upstream_path}")
        else:
            print(f"Warning: target1 not found in {upstream_path}")

    with open(economy_path, 'rb') as f:
        c2 = f.read()

    if b'OnPlayerBotLottery30Refined' not in c2:
        target2a = b'bool TryPickPlayerBotLottery30(LPCHARACTER ch, LPITEM item);'
        replacement2a = b'bool TryPickPlayerBotLottery30(LPCHARACTER ch, LPITEM item);\r\n\tvoid OnPlayerBotLottery30Refined(LPCHARACTER ch, DWORD dwOldId, LPITEM pkItemAfter);'
        target2b = b'\t\t\tif (attempted && IsPlayerBotExplainOn())\r\n\t\t\t\tif (LPITEM made = ch->GetInventoryItem(cellBefore))\r\n\t\t\t\t\tif (made->GetID() != idBefore)\r\n\t\t\t\t\t\tNotePlayerBotExplainOrigin(made, per::ORIGIN_REFINED, idBefore);'
        addition2b = b'\r\n\r\n\t\t\t// MT2009_PLUS_UPSTREAM_BOTLOGIC_LOTTERY30_V1: track the lottery piece across upgrades\r\n\t\t\t// so the bot continues refining the same weapon instead of abandoning it at +1.\r\n\t\t\tif (attempted)\r\n\t\t\t\tOnPlayerBotLottery30Refined(ch, idBefore, ch->GetInventoryItem(cellBefore));'
        if target2a in c2 and target2b in c2:
            c2 = c2.replace(target2a, replacement2a, 1)
            c2 = c2.replace(target2b, target2b + addition2b, 1)
            with open(economy_path, 'wb') as f:
                f.write(c2)
            print(f"Successfully patched {economy_path}")
        else:
            print(f"Warning: target2a or target2b not found in {economy_path}")

    return True

def apply_patch(repo_root):
    # 1. Docker game src tree
    apply_patch_to_dir(
        os.path.join(repo_root, 'Server/linux-port/docker/game/src/server/game/src/playerbot_upstream_botlogic.h'),
        os.path.join(repo_root, 'Server/linux-port/docker/game/src/server/game/src/playerbot_economy.h')
    )
    # 2. Overlays playerbot tree
    apply_patch_to_dir(
        os.path.join(repo_root, 'Server/linux-port/overlays/playerbot/src/game/src/playerbot_upstream_botlogic.h'),
        os.path.join(repo_root, 'Server/linux-port/overlays/playerbot/src/game/src/playerbot_economy.h')
    )
    return True

if __name__ == '__main__':
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
    if len(sys.argv) > 1:
        root = sys.argv[1]
    apply_patch(root)
