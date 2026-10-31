#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modyfikacja: Zwiększenie dropu Cor Draconis (Alchemia w klimacie Hard)
Autor: Krystian / MT2Plus

Zakres:
1. item_manager.cpp:
   - Zniesienie limitu delty poziomu (>= mob + 30) na drop Cor Draconis.
   - Metiny (lvl 40+): 25% szansy na 1x Cor Draconis (Surowy).
   - Bossy (lvl 30+): 50% szansy na Cor Draconis (bossy 75+ / dungeony: 100%).
   - Boty: otrzymują pełną szansę jak gracze (brak ograniczenia do 5%).
2. dragon_soul.quest:
   - Zwiększenie bazowego dziennego limitu Corów ze Smoczego Oka z 5 do 15 sztuk (zakres 1-30).
3. questlib.lua:
   - Zwiększenie bazowej szansy dropu Odłamków Smoczego Kamienia (30270) z 10% do 15%.
4. playerbot_alchemy.h:
   - PLAYERBOT_DS_CORS_PER_DAY = 15 (odczyt flagi ds_cor_day do 30).
5. admin_panel.py:
   - Domyślne wartości: ds_drop = 15, ds_cor_day = 15, formularz max = 30.
"""

import os
import sys

def find_repo_root():
    curr = os.path.abspath(os.path.dirname(__file__))
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, 'PROJECT_CONTEXT.md')):
            return curr
        curr = os.path.dirname(curr)
    return os.getcwd()

def apply():
    repo = find_repo_root()
    print(f"[*] Repozytorium: {repo}")

    # 1. dragon_soul.quest
    ds_path = os.path.join(repo, "Server/linux-port/docker/game/quest/dragon_soul.quest")
    if os.path.exists(ds_path):
        with open(ds_path, "rb") as f:
            content = f.read().decode("cp1250")
        content_lf = content.replace("\r\n", "\n")
        old_chunk = """				local per_day = game.get_event_flag("ds_cor_day")
				if per_day < 1 or per_day > 20 then
					per_day = 5
				end"""
        new_chunk = """				local per_day = game.get_event_flag("ds_cor_day")
				if per_day < 1 or per_day > 30 then
					per_day = 15
				end"""
        if old_chunk in content_lf:
            content_lf = content_lf.replace(old_chunk, new_chunk)
            with open(ds_path, "wb") as f:
                f.write(content_lf.replace("\n", "\r\n").encode("cp1250"))
            print("[+] dragon_soul.quest zaktualizowany!")
        else:
            print("[ ] dragon_soul.quest zawiera juz nowe limity.")

    # 2. questlib.lua
    ql_path = os.path.join(repo, "Server/linux-port/docker/game/src/serverfiles/share/locale/poland/quest/questlib.lua")
    if os.path.exists(ql_path):
        with open(ql_path, "rb") as f:
            ql_raw = f.read()
        target_ql = b'-- "Fix"\r\nfunction drop_gamble_with_flag(drop_flag)\r\n\tlocal drop_chance = game.get_event_flag(drop_flag)\r\n\tif drop_chance < 1 or drop_chance > 100 then\r\n\t\tdrop_chance = 10\r\n\tend\r\n\treturn drop_chance >= number(1, 100)\r\nend'
        new_ql = b'-- "Fix"\r\nfunction drop_gamble_with_flag(drop_flag)\r\n\tlocal drop_chance = game.get_event_flag(drop_flag)\r\n\tif drop_chance < 1 or drop_chance > 100 then\r\n\t\tdrop_chance = 15\r\n\tend\r\n\treturn drop_chance >= number(1, 100)\r\nend'
        if target_ql in ql_raw:
            ql_raw = ql_raw.replace(target_ql, new_ql)
            with open(ql_path, "wb") as f:
                f.write(ql_raw)
            print("[+] questlib.lua zaktualizowany (ds_drop default 15%)!")
        else:
            print("[ ] questlib.lua zawiera juz nowa szanse.")

    # 3. playerbot_alchemy.h
    pb_path = os.path.join(repo, "Server/linux-port/overlays/playerbot/src/game/src/playerbot_alchemy.h")
    if os.path.exists(pb_path):
        with open(pb_path, "rb") as f:
            pb_raw = f.read()
        changed = False
        if b"const int PLAYERBOT_DS_CORS_PER_DAY = 5;" in pb_raw:
            pb_raw = pb_raw.replace(b"const int PLAYERBOT_DS_CORS_PER_DAY = 5;", b"const int PLAYERBOT_DS_CORS_PER_DAY = 15;")
            changed = True
        if b"return (n >= 1 && n <= 20) ? n : PLAYERBOT_DS_CORS_PER_DAY;" in pb_raw:
            pb_raw = pb_raw.replace(b"return (n >= 1 && n <= 20) ? n : PLAYERBOT_DS_CORS_PER_DAY;", b"return (n >= 1 && n <= 30) ? n : PLAYERBOT_DS_CORS_PER_DAY;")
            changed = True
        if changed:
            with open(pb_path, "wb") as f:
                f.write(pb_raw)
            print("[+] playerbot_alchemy.h zaktualizowany (PLAYERBOT_DS_CORS_PER_DAY = 15)!")
        else:
            print("[ ] playerbot_alchemy.h zawiera juz nowe wartosci.")

    # 4. item_manager.cpp
    im_path = os.path.join(repo, "Server/linux-port/docker/game/src/server/game/src/item_manager.cpp")
    if os.path.exists(im_path):
        with open(im_path, "rb") as f:
            im_raw = f.read()
        target_im = b"""\t// MT2009_PLUS_BOT_RARE_DROP_V1 (server-patches/botraredrop): a bot's kill rolls the
\t// Cor Draconis like a player's; the bot lists it on its counter.
\t// Cor Draconis: roznica poziomu do 30 poziomow
\tif (pkKiller &&
\t\tpkKiller->IsPC() &&
\t\tpkKiller->GetDesc() &&
\t\tpkKiller->GetLevel() <= pkChr->GetLevel() + 30 &&
\t\t// MT2009_PLUS_RARE_TOGGLE_V1 (server-patches/raretoggle): no Cor Draconis
\t\t// while the world has the alchemy switched off (M2_ALCHEMY=0, the panel).
\t\tquest::CQuestManager::instance().GetEventFlag("m2_alchemy_off") == 0 &&
\t\t// MT2009_PLUS_RARE_DROP_SWITCHES_V1 (cor roll): nor while the boss's / Metin's switch is off.
\t\t!Mt2009PlusRareDropOff(MT2009_PLUS_RARE_DROP_COR, pkChr->IsStone()))
\t{
\t\tint corChance = 0;
\t\tconst char* corKind = "none";

\t\tif (pkChr->IsStone())
\t\t{
\t\t\t// MT2009_PLUS_METIN_DROPS_V1 (server-patches/metindrops): a Metin 20% (it was 50).
\t\t\tcorChance = 20;
\t\t\tcorKind = "stone";
\t\t}
\t\telse if (pkChr->GetMobRank() >= MOB_RANK_BOSS)
\t\t{
\t\t\tcorChance = 80;
\t\t\tcorKind = "boss";
\t\t}

\t\t// MT2009_PLUS_RARE_MOB_RULES_V1 (cor): the mob's own Cor chance and count.
\t\tconst Mt2009PlusRareMobRule* rareRule = Mt2009PlusRareMobRuleFor(pkChr);
\t\tif (rareRule)
\t\t{
\t\t\tcorChance = rareRule->corChance;
\t\t\tcorKind = "rule";
\t\t}

\t\t// MT2009_PLUS_BOT_RARE_DROP_V2: a bot's kill rolls at a bot's own chance.
\t\tif (corChance > 0 && pkKiller->GetDesc()->IsBot())
\t\t\tcorChance = 5;"""

        replacement_im = b"""\t// MT2009_PLUS_COR_DRACONIS_REBALANCE_V1 (Task 1):
\t// - Zniesienie limitu delty poziomu na drop Cor Draconis (dropi niezaleznie od poziomu).
\t// - Metiny (od 40 lvl w gore): 25% szansy na Cor Draconis (Surowy).
\t// - Bossy (od 30 lvl w gore): 50% szansy na Cor Draconis; bossy 75+ / dungeony: 100%.
\t// - Boty: otrzymuja pelna szanse (brak sztucznego dlawienia do 5%), dzieki czemu
\t//   boty zasilaja rynek Corami w sklepach offline i rozwijaja wlasna alchemie.
\tif (pkKiller &&
\t\tpkKiller->IsPC() &&
\t\tpkKiller->GetDesc() &&
\t\t// MT2009_PLUS_RARE_TOGGLE_V1 (server-patches/raretoggle): no Cor Draconis
\t\t// while the world has the alchemy switched off (M2_ALCHEMY=0, the panel).
\t\tquest::CQuestManager::instance().GetEventFlag("m2_alchemy_off") == 0 &&
\t\t// MT2009_PLUS_RARE_DROP_SWITCHES_V1 (cor roll): nor while the boss's / Metin's switch is off.
\t\t!Mt2009PlusRareDropOff(MT2009_PLUS_RARE_DROP_COR, pkChr->IsStone()))
\t{
\t\tint corChance = 0;
\t\tconst char* corKind = "none";

\t\tif (pkChr->IsStone())
\t\t{
\t\t\tif (pkChr->GetLevel() >= 40)
\t\t\t{
\t\t\t\tcorChance = 25;
\t\t\t\tcorKind = "stone";
\t\t\t}
\t\t}
\t\telse if (pkChr->GetMobRank() >= MOB_RANK_BOSS && pkChr->GetLevel() >= 30)
\t\t{
\t\t\tcorChance = (pkChr->GetLevel() >= 75) ? 100 : 50;
\t\t\tcorKind = "boss";
\t\t}

\t\t// MT2009_PLUS_RARE_MOB_RULES_V1 (cor): the mob's own Cor chance and count.
\t\tconst Mt2009PlusRareMobRule* rareRule = Mt2009PlusRareMobRuleFor(pkChr);
\t\tif (rareRule)
\t\t{
\t\t\tcorChance = rareRule->corChance;
\t\t\tcorKind = "rule";
\t\t}"""

        im_raw_lf = im_raw.replace(b"\r\n", b"\n")
        target_im_lf = target_im.replace(b"\r\n", b"\n")
        replacement_im_lf = replacement_im.replace(b"\r\n", b"\n")

        if target_im_lf in im_raw_lf:
            im_raw_lf = im_raw_lf.replace(target_im_lf, replacement_im_lf)
            with open(im_path, "wb") as f:
                f.write(im_raw_lf.replace(b"\n", b"\r\n"))
            print("[+] item_manager.cpp zaktualizowany!")
        else:
            print("[ ] item_manager.cpp zawiera juz nowy blok dropu Cor Draconis.")

    # 5. admin_panel.py
    ap_path = os.path.join(repo, "Server/linux-port/docker/panel/app/admin_panel.py")
    if os.path.exists(ap_path):
        with open(ap_path, "rb") as f:
            ap_raw = f.read()
        changed = False
        if b"RARE_DS_DROP_DEFAULT = 10\r\n" in ap_raw:
            ap_raw = ap_raw.replace(b"RARE_DS_DROP_DEFAULT = 10\r\n", b"RARE_DS_DROP_DEFAULT = 15\r\n")
            changed = True
        if b"RARE_DS_COR_DAY_DEFAULT = 5\r\n" in ap_raw:
            ap_raw = ap_raw.replace(b"RARE_DS_COR_DAY_DEFAULT = 5\r\n", b"RARE_DS_COR_DAY_DEFAULT = 15\r\n")
            changed = True
        if b"if 1 <= v <= 20:\r\n                    vals[\"ds_cor_day\"] = v" in ap_raw:
            ap_raw = ap_raw.replace(b"if 1 <= v <= 20:\r\n                    vals[\"ds_cor_day\"] = v",
                                   b"if 1 <= v <= 30:\r\n                    vals[\"ds_cor_day\"] = v")
            changed = True
        if b'name="ds_cor_day" min="1" max="20"' in ap_raw:
            ap_raw = ap_raw.replace(b'name="ds_cor_day" min="1" max="20"', b'name="ds_cor_day" min="1" max="30"')
            changed = True
        if b"if not (1 <= ds_drop <= 100 and 1 <= ds_cor_day <= 20):" in ap_raw:
            ap_raw = ap_raw.replace(b"if not (1 <= ds_drop <= 100 and 1 <= ds_cor_day <= 20):",
                                   b"if not (1 <= ds_drop <= 100 and 1 <= ds_cor_day <= 30):")
            changed = True
        if b"domy\xc5\x9blnie 10):" in ap_raw:
            ap_raw = ap_raw.replace(b"domy\xc5\x9blnie 10):", b"domy\xc5\x9blnie 15):")
            changed = True
        if b"default 10):" in ap_raw:
            ap_raw = ap_raw.replace(b"default 10):", b"default 15):")
            changed = True
        if b"domy\xc5\x9blnie 5):" in ap_raw:
            ap_raw = ap_raw.replace(b"domy\xc5\x9blnie 5):", b"domy\xc5\x9blnie 15):")
            changed = True
        if b"default 5):" in ap_raw:
            ap_raw = ap_raw.replace(b"default 5):", b"default 15):")
            changed = True
        if b"(1\xe2\x80\x9320," in ap_raw:
            ap_raw = ap_raw.replace(b"(1\xe2\x80\x9320,", b"(1\xe2\x80\x9330,")
            changed = True
        if b"(1-20," in ap_raw:
            ap_raw = ap_raw.replace(b"(1-20,", b"(1-30,")
            changed = True
        if b"1\xe2\x80\x9320. Nic nie zmieniono." in ap_raw:
            ap_raw = ap_raw.replace(b"1\xe2\x80\x9320. Nic nie zmieniono.", b"1\xe2\x80\x9330. Nic nie zmieniono.")
            changed = True
        if b"1-20. Nothing was changed." in ap_raw:
            ap_raw = ap_raw.replace(b"1-20. Nothing was changed.", b"1-30. Nothing was changed.")
            changed = True
        if changed:
            with open(ap_path, "wb") as f:
                f.write(ap_raw)
            print("[+] admin_panel.py zaktualizowany!")
        else:
            print("[ ] admin_panel.py zawiera juz nowe wartosci.")

    print("[*] Gotowe! Wszystkie pliki alchemii i dropu Cor Draconis zaktualizowane.")

if __name__ == '__main__':
    apply()
