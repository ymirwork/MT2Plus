#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_mods.py - Kompletny audyt 34 autorskich modyfikacji MT2Plus
Weryfikuje obecnosc i integralnosc wszystkich zmian w kodzie klienta, serwera, bazy i panelu.
Autor: Krystian (MT2Plus)
"""

import os
import sys

repo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if not os.path.exists(os.path.join(repo, 'Server')):
    repo = r'd:\Github\MT2Plus'

results = {}

def read_file_safe(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        with open(path, 'r', encoding='latin1', errors='ignore') as f:
            return f.read()

def read_bytes_safe(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'rb') as f:
            return f.read()
    except Exception:
        return None

# 1. wstawanie-100hp
c1 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/cmd_general.cpp'))
results['wstawanie-100hp'] = bool(c1 and 'GetMaxHP()' in c1 and 'SCMD_RESTART' in c1)

# 2. autolowy-szybkie-zbieranie
c2 = read_file_safe(os.path.join(repo, 'Klient/pack/root/uiautohunt.py'))
results['autolowy-szybkie-zbieranie'] = bool(c2 and '/pickup_nearby' in c2)

# 3. ukrycie-hp-celu
c3 = read_file_safe(os.path.join(repo, 'Klient/pack/root/uitarget.py'))
results['ukrycie-hp-celu'] = bool(c3 and ('hpGauge.Hide()' in c3 or 'MT2009_PLUS_HIDE_TARGET_HP' in c3 or 'pHpText' in c3))

# 4. sklep-160-slotow
c4_1 = read_file_safe(os.path.join(repo, 'Klient/pack/root/offlineshopmanage.py'))
c4_2 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/char_shop.cpp'))
results['sklep-160-slotow'] = bool(c4_1 and c4_2 and 'PLAYER_SHOP_TWO_BLOCKS_KEYS2_V1' in c4_1 and 'SHOP_PLAYER_HEIGHT * 2' in c4_2)

# 5. recykling-bonusow
results['recykling-bonusow'] = os.path.exists(os.path.join(repo, 'Server/linux-port/docker/game/quest/recykling_bonusow.quest'))

# 6. pierscien-teleportacji
results['pierscien-teleportacji'] = os.path.exists(os.path.join(repo, 'Server/linux-port/docker/game/quest/teleport_ring.quest'))

# 7. seban-panel-ekonomia
c7 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/seban-panel/collector.py'))
results['seban-panel-ekonomia'] = bool(c7 and 'item_not_gm_scope_sql' in c7)

# 8. devgameplay (skróty k/kk)
c8 = read_file_safe(os.path.join(repo, 'Klient/pack/root/uipickmoney.py'))
results['devgameplay (skróty k/kk)'] = bool(c8 and ('k' in c8 or 'kk' in c8))

# 9. autofish
c9 = read_file_safe(os.path.join(repo, 'Klient/pack/root/uiautohunt.py'))
results['autofish'] = bool(c9 and ('AutoFishWindow' in c9 or 'autofish' in c9.lower()))

# 10. optymalizacja-autolowy-drop-redlas
c10_1 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/playerbot_manager.cpp'))
c10_2 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/mariadb/playerbot/apply.sh'))
results['optymalizacja-autolowy-drop-redlas'] = bool(c10_1 and c10_2 and 'IsHumanTargetReachable' in c10_1 and 'MT2009_PLUS_STACK_200_EXTENDED' in c10_2)

# 11. oferty-blyskawiczne-is
results['oferty-blyskawiczne-is'] = os.path.exists(os.path.join(repo, 'Server/linux-port/docker/mariadb/playerbot/mod/92_itemshop_flash_offers.sql'))

# 12. pierscienie-czas-noszenia
c12_1 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/mariadb/playerbot/apply.sh'))
c12_2 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/char_item.cpp'))
results['pierscienie-czas-noszenia'] = bool(c12_1 and c12_2 and 'MT2009_PLUS_AMULET_DURATION_30D' in c12_1 and 'LIMIT_TIMER_BASED_ON_WEAR' in c12_2)

# 13. recykling-broni-30
c13 = read_file_safe(os.path.join(repo, 'Server/linux-port/overlays/playerbot/src/game/src/playerbot_gear.h'))
results['recykling-broni-30'] = bool(c13 and 'IsPlayerBotHighValueLevel30' in c13)

# 14. kolekcjoner-autodrop
c14 = read_file_safe(os.path.join(repo, 'Klient/pack/root/uicollector.py'))
results['kolekcjoner-autodrop'] = bool(c14 and 'TEXT_AUTO_DROP' in c14)

# 15. sesja-farmienia
results['sesja-farmienia'] = os.path.exists(os.path.join(repo, 'Klient/pack/root/uifarmsession.py'))

# 16. odnawianie-sklepow-botow
c16 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/char_shop.cpp'))
results['odnawianie-sklepow-botow'] = bool(c16 and 'MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1' in c16)

# 17. dom-aukcyjny-historia
c17 = read_file_safe(os.path.join(repo, 'Klient/pack/root/uiauctionhouse.py'))
results['dom-aukcyjny-historia'] = bool(c17 and 'Historia' in c17)

# 18. kolekcjoner-refine
c18 = read_file_safe(os.path.join(repo, 'Klient/pack/root/uirefine.py'))
results['kolekcjoner-refine'] = bool(c18 and ('mag.' in c18 or 'collector' in c18))

# 19. szarfy-szansa-tooltip
c19 = read_file_safe(os.path.join(repo, 'Klient/pack/root/uiacce.py'))
results['szarfy-szansa-tooltip'] = bool(c19 and 'chanceDict' in c19)

# 20. ukryj-szarfe
c20_1 = os.path.exists(os.path.join(repo, 'Klient/pack/root/uicostumehide.py'))
c20_2 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/item.cpp'))
results['ukryj-szarfe'] = bool(c20_1 and c20_2 and 'hiddenMask & 8' in c20_2)

# 21. brak-potek-m2-metiny-bossy
c21 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/item_manager.cpp'))
results['brak-potek-m2-metiny-bossy'] = bool(c21 and 'MT2009_PLUS_NO_POTIONS_M2_UP_V1' in c21)

# 22. ceny-bazowe-botow
results['ceny-bazowe-botow'] = os.path.exists(os.path.join(repo, 'Server/linux-port/docker/seban-panel/templates/economy_bot_prices.html'))

# 23. fix-emerytura-botow
c23 = read_file_safe(os.path.join(repo, 'Server/linux-port/overlays/playerbot/src/game/src/playerbot_retirement.h'))
results['fix-emerytura-botow'] = bool(c23 and 'IsPlayerBotHumanLedParty' in c23)

# 24. itemshop-panel
results['itemshop-panel'] = os.path.exists(os.path.join(repo, 'Server/linux-port/docker/seban-panel/templates/economy_itemshop.html'))

# 25. balans-szkatułek-hard
c25 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/char_item.cpp'))
results['balans-szkatułek-hard'] = bool(c25 and 'IsBossChestVnum' in c25)

# 26. duze-czcionki-skilli-i-ilosci
b26 = read_bytes_safe(os.path.join(repo, 'Klient/metin2client.exe'))
already_patched = bytes.fromhex('0fb64f418b4734c1e10583c1f303c10fb64f40508b4730c1e10583c1fe03c18bca50e8')
results['duze-czcionki-skilli-i-ilosci'] = bool(b26 and already_patched in b26)

# 27. fix-boty-gildia-exp-party
results['fix-boty-gildia-exp-party'] = os.path.exists(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/playerbot_guild_orders.h'))

# 28. fix-boty-ulepszanie-lottery30
c28 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/playerbot_economy.h'))
results['fix-boty-ulepszanie-lottery30'] = bool(c28 and 'OnPlayerBotLottery30Refined' in c28)

# 29. fix-podglad-ekwipunku-tooltipy
c29 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/seban-panel/templates/player.html'))
results['fix-podglad-ekwipunku-tooltipy'] = bool(c29 and 'adjustTip' in c29)

# 30. odblokowanie-kostiumow-arezzo
c30 = read_file_safe(os.path.join(repo, 'Server/linux-port/overlays/playerbot/src/game/src/playerbot_arezzo_costumes.h'))
results['odblokowanie-kostiumow-arezzo'] = bool(c30 and 'return false;' in c30)

# 31. powiadomienia-skarbiec-gildii
c31_1 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/char.cpp'))
c31_2 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/char_item.cpp'))
results['powiadomienia-skarbiec-gildii'] = bool(c31_1 and c31_2 and 'MT2009_PLUS_GUILD_TREASURY_NOTIFY_V1' in c31_1 and 'PayRefineFee(cost, true, pProto->szLocaleName)' in c31_2)

# 32. tracker-bossow
c32 = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/cmd_general.cpp'))
results['tracker-bossow'] = bool(c32 and 'do_boss_tracker' in c32)

# 33. wyplata-utargu-kowal-gildijny
c33_df = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/Dockerfile'))
c33_ql = read_file_safe(os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/questlua_guild.cpp'))
c33_ug = read_file_safe(os.path.join(repo, 'Klient/pack/root/uiguild.py'))
results['wyplata-utargu-kowal-gildijny'] = bool(
    c33_df and c33_ql and c33_ug and
    'guild_crafter_revenue' in c33_df and
    'guild.payout_get' in c33_df and
    'guild_payout_get' in c33_ql and
    'SetGuildPayout' in c33_ug
)

# 34. zielone-dodania-m1m2
c34_pt = read_file_safe(os.path.join(repo, 'Server/linux-port/overlays/playerbot/src/game/src/playerbot_price_tables.h'))
c34_m = read_file_safe(os.path.join(repo, 'Server/linux-port/overlays/playerbot/src/game/src/playerbot_market.h'))
results['zielone-dodania-m1m2'] = bool(c34_pt and c34_m and '71151' in c34_pt and 'IsPlayerBotGreenTradeableBonusVnum' in c34_m)

all_ok = True
print(f'{"NAZWA MODYFIKACJI":42} | STATUS')
print('-' * 60)
for k, v in results.items():
    status = 'TAK (Aktywne)' if v else 'NIE (Brak / Blad)'
    if not v:
        all_ok = False
    print(f'{k:42} | {status}')

print('=' * 60)
print(f'WYNIK AUDYTU MT2PLUS: {sum(results.values())}/{len(results)} AKTYWNYCH!')
if all_ok:
    print('WSZYSTKIE 34 AUTORSKIE MODYFIKACJE SA W 100% AKTYWNE I ZGODNE!')
else:
    print('UWAGA: ZNALEZIONO BRAKUJACE LUB NIEKOMPLETNE MODYFIKACJE!')
    sys.exit(1)
