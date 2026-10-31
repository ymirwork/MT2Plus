#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_patch.py - Moduł: quest-mob-podswietlenie-aqua (MT2009_PLUS_QUEST_MOB_AQUA_V1)
Aplikuje podswietlenie potworow misyjnych na kolor Aqua (0.0, 0.85, 1.0)
w kodzie silnika C++ oraz skryptach klienta gry.
"""

import os
import sys

def patch_file(path, target, replacement, marker):
    if not os.path.exists(path):
        print(f"[!] Plik nie istnieje: {path}")
        return False

    with open(path, "r", encoding="latin1") as f:
        content = f.read()

    if marker in content:
        print(f"[-] Modul juz zaaplikowany w {os.path.basename(path)}")
        return True

    # Normalize CRLF
    is_crlf = "\r\n" in content
    norm_target = target.replace("\n", "\r\n") if is_crlf else target.replace("\r\n", "\n")
    norm_replacement = replacement.replace("\n", "\r\n") if is_crlf else replacement.replace("\r\n", "\n")

    if norm_target not in content:
        print(f"[!] Nie znaleziono targetu w {os.path.basename(path)}")
        return False

    content = content.replace(norm_target, norm_replacement, 1)

    with open(path, "w", encoding="latin1") as f:
        f.write(content)

    print(f"[+] Zaaplikowano zmiane w {os.path.basename(path)}")
    return True

def apply_all():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

    # 1. char.h
    char_h = os.path.join(base_dir, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "char.h")
    patch_file(
        char_h,
        "void\t\t\t\tSendFractionInfoBoard(LPDESC d);",
        "void\t\t\t\tSendFractionInfoBoard(LPDESC d);\n\t\tvoid\t\t\t\tRefreshQuestMobMarks(); // MT2009_PLUS_QUEST_MOB_AQUA_V1 (Task 3)",
        "RefreshQuestMobMarks"
    )

    # 2. char.cpp
    char_cpp = os.path.join(base_dir, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "char.cpp")
    patch_file(
        char_cpp,
        'if (IsMonster() && !IsDead() && GetMobRank() >= MOB_RANK_BOSS &&\n\t\t\tch && ch->IsPC() && !d->IsBot())\n\t\tch->ChatPacket(CHAT_TYPE_COMMAND, "BossMark %u", (DWORD) m_vid);',
        'if (IsMonster() && !IsDead() && GetMobRank() >= MOB_RANK_BOSS &&\n\t\t\tch && ch->IsPC() && !d->IsBot())\n\t\tch->ChatPacket(CHAT_TYPE_COMMAND, "BossMark %u", (DWORD) m_vid);\n\n\t// MT2009_PLUS_QUEST_MOB_AQUA_V1 (Task 3):\n\t// Podswietlenie potworow misyjnych na kolor Aqua (0.0, 0.85, 1.0)\n\tif ((IsMonster() || IsStone()) && !IsDead() && ch && ch->IsPC() && !d->IsBot())\n\t{\n\t\textern bool IsPlayerQuestTargetMob(LPCHARACTER ch, DWORD dwRaceNum);\n\t\tif (IsPlayerQuestTargetMob(ch, GetRaceNum()))\n\t\t\tch->ChatPacket(CHAT_TYPE_COMMAND, "QuestMobMark %u 1", (DWORD) m_vid);\n\t}',
        "QuestMobMark %u 1"
    )

    # 3. questmanager.cpp
    questmanager_cpp = os.path.join(base_dir, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "questmanager.cpp")
    quest_impl = '''#include "mob_manager.h"

// MT2009_PLUS_QUEST_MOB_AQUA_V1 (Task 3):
// Weryfikacja czy dany potwor jest celem aktywnej misji gracza
bool IsPlayerQuestTargetMob(LPCHARACTER ch, DWORD dwRaceNum)
{
	if (!ch || !ch->IsPC() || dwRaceNum == 0)
		return false;

	quest::CQuestManager& qm = quest::CQuestManager::instance();
	quest::PC* pPC = qm.GetPCForce(ch->GetPlayerID());
	if (!pPC)
		return false;

	// 1. Sprawdzenie flag polowania (hunting.quest)
	int huntingVnum = pPC->GetFlag("hunting.huntingMobVnum");
	if (huntingVnum == 0)
		huntingVnum = pPC->GetFlag("huntingMobVnum");
	int huntingCount = pPC->GetFlag("hunting.huntingMobCount");
	if (huntingCount == 0)
		huntingCount = pPC->GetFlag("huntingMobCount");
	if (huntingCount > 0 && huntingVnum > 0 && (DWORD)huntingVnum == dwRaceNum)
		return true;

	// 2. Iteracja po wszystkich aktywnych misjach z licznikami potworow
	for (quest::PC::QuestInfoIterator it = pPC->quest_begin(); it != pPC->quest_end(); ++it)
	{
		const quest::QuestState& qs = it->second;
		if (qs._counter_value > 0 && !qs._counter_name.empty())
		{
			const std::string& cname = qs._counter_name;
			size_t mpos = cname.find("{m");
			if (mpos != std::string::npos)
			{
				size_t endpos = cname.find('}', mpos + 2);
				if (endpos != std::string::npos)
				{
					std::string vnumStr = cname.substr(mpos + 2, endpos - (mpos + 2));
					DWORD targetVnum = (DWORD) atoi(vnumStr.c_str());
					if (targetVnum == dwRaceNum)
						return true;
				}
			}
			else
			{
				const CMob* pMob = CMobManager::instance().Get(dwRaceNum);
				if (pMob && pMob->m_table.szLocaleName[0] != '\\0')
				{
					if (cname == pMob->m_table.szLocaleName)
						return true;
				}
			}
		}
	}

	return false;
}'''
    patch_file(
        questmanager_cpp,
        '\tsys_err("QUEST: no such pc id : %d", pc);\n\t}\n}',
        f'\tsys_err("QUEST: no such pc id : %d", pc);\n\t}}\n\n{quest_impl}',
        "bool IsPlayerQuestTargetMob"
    )

    # 4. questpc.cpp
    questpc_cpp = os.path.join(base_dir, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "questpc.cpp")
    patch_file(
        questpc_cpp,
        '#include "char.h"',
        '#include "char.h"\n#include "char_manager.h"',
        '#include "char_manager.h"'
    )
    patch_file(
        questpc_cpp,
        '\tvoid PC::SetCurrentQuestCounterValue(int value)\n\t{\n\t\tSetSendFlag(QUEST_SEND_COUNTER_VALUE);\n\t\tm_RunningQuestState->_counter_value = value;\n\t}',
        '\tvoid PC::SetCurrentQuestCounterValue(int value)\n\t{\n\t\tSetSendFlag(QUEST_SEND_COUNTER_VALUE);\n\t\tm_RunningQuestState->_counter_value = value;\n\t\tLPCHARACTER ch = CHARACTER_MANAGER::instance().FindByPID(m_dwID);\n\t\tif (ch)\n\t\t\tch->RefreshQuestMobMarks();\n\t}',
        "RefreshQuestMobMarks()"
    )

    # 5. cmd.cpp & cmd_general.cpp
    cmd_cpp = os.path.join(base_dir, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "cmd.cpp")
    patch_file(
        cmd_cpp,
        'ACMD(do_click_mall);',
        'ACMD(do_click_mall);\nACMD(do_refresh_quest_mobs); // MT2009_PLUS_QUEST_MOB_AQUA_V1',
        'ACMD(do_refresh_quest_mobs)'
    )
    patch_file(
        cmd_cpp,
        '\t{ "click_mall",\t\t\tdo_click_mall,\t\t\t0,\tPOS_DEAD,\tGM_PLAYER\t\t},',
        '\t{ "click_mall",\t\t\tdo_click_mall,\t\t\t0,\tPOS_DEAD,\tGM_PLAYER\t\t},\n\t{ "refresh_quest_mobs",\tdo_refresh_quest_mobs,\t0,\tPOS_DEAD,\tGM_PLAYER\t},',
        '"refresh_quest_mobs"'
    )

    cmd_gen_cpp = os.path.join(base_dir, "Server", "linux-port", "docker", "game", "src", "server", "game", "src", "cmd_general.cpp")
    patch_file(
        cmd_gen_cpp,
        '//martysama0134\'s 4e4e75d8b719b9240e033009cf4d7b0f',
        '// MT2009_PLUS_QUEST_MOB_AQUA_V1 (Task 3):\nACMD(do_refresh_quest_mobs)\n{\n\tch->RefreshQuestMobMarks();\n}\n\n//martysama0134\'s 4e4e75d8b719b9240e033009cf4d7b0f',
        'do_refresh_quest_mobs'
    )

    print("[*] Wszystkie latki modulu quest-mob-podswietlenie-aqua zostaly sprawdzone/zaaplikowane.")

if __name__ == "__main__":
    apply_all()
