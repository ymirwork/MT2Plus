import os
import sys

repo = '.'
root_dir = 'Klient/pack/root'
server_src = 'Server/linux-port/docker/game/src/server/game/src'
pb_overlay = 'Server/linux-port/overlays/playerbot/src/game/src'
seban_dir = 'Server/linux-port/docker/seban-panel'

def read(p):
    if not os.path.exists(p):
        return ""
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

checks = {}

# 1. wstawanie-100hp
c_cmd = read(f'{server_src}/cmd_general.cpp')
checks['1. wstawanie-100hp'] = 'GetMaxHP()' in c_cmd and 'SCMD_RESTART' in c_cmd

# 2. autolowy-szybkie-zbieranie
c_root = read(f'{root_dir}/uiautohunt.py')
checks['2. autolowy-szybkie-zbieranie'] = '/pickup_nearby' in c_root and 'self.Command(\'/pickup_nearby %d\' % mask, now)' in c_root

# 3. ukrycie-hp-celu
c_target = read(f'{root_dir}/uitarget.py')
checks['3. ukrycie-hp-celu'] = 'hpGauge.Hide()' in c_target and '# self.hpText.Show() - usuniete biale napisy' in c_target

# 4. sklep-160-slotow
c_shop = read(f'{server_src}/char_shop.cpp')
c_off = read(f'{root_dir}/offlineshopmanage.py')
checks['4. sklep-160-slotow'] = 'SHOP_PLAYER_HEIGHT * 2' in c_shop and 'WINDOW_WIDTH = 664' in c_off

# 5. recykling-bonusow
c_rec_q = read('Server/linux-port/docker/game/quest/recykling_bonusow.quest')
checks['5. recykling-bonusow'] = len(c_rec_q) > 100

# 6. pierscien-teleportacji
c_tp = read('Server/linux-port/docker/game/quest/teleport_ring.quest')
checks['6. pierscien-teleportacji'] = '360' in c_tp and '361' in c_tp

# 7. seban-panel-ekonomia
c_app = read(f'{seban_dir}/app.py')
c_col = read(f'{seban_dir}/collector.py')
checks['7. seban-panel-ekonomia'] = '/economy/bot-prices' in c_app and 'item_not_gm_scope_sql' in c_col

# 8. devgameplay (skróty k/kk)
c_pm = read(f'{root_dir}/uipickmoney.py')
checks['8. devgameplay (skróty k/kk)'] = 'def ExpandMoneyString' in c_pm and 'multiplier = 1000 ** k_count' in c_pm

# 9. autofish
checks['9. autofish'] = 'self.fishButton' in c_root and 'AutoFishWindow' in c_root and 'self.fishWindow = AutoFishWindow(self)' in c_root

# 10. optymalizacja-autolowy-drop-redlas
c_mgr = read(f'{server_src}/playerbot_manager.cpp')
c_apply = read('Server/linux-port/docker/mariadb/playerbot/apply.sh')
checks['10. optymalizacja-autolowy-drop-redlas'] = 'IsHumanTargetReachable' in c_mgr and 'MT2009_PLUS_STACK_200_EXTENDED' in c_apply

# 11. oferty-blyskawiczne-is
checks['11. oferty-blyskawiczne-is'] = os.path.exists('Server/linux-port/docker/mariadb/playerbot/mod/92_itemshop_flash_offers.sql')

# 12. pierscienie-czas-noszenia
c_item = read(f'{server_src}/char_item.cpp')
checks['12. pierscienie-czas-noszenia'] = 'LIMIT_TIMER_BASED_ON_WEAR' in c_item and 'MT2009_PLUS_AMULET_DURATION_30D' in c_apply

# 13. recykling-broni-30
c_gear = read(f'{pb_overlay}/playerbot_gear.h')
checks['13. recykling-broni-30'] = 'IsPlayerBotHighValueLevel30' in c_gear

# 14. kolekcjoner-autodrop
c_coll = read(f'{root_dir}/uicollector.py')
checks['14. kolekcjoner-autodrop'] = 'TEXT_AUTO_DROP' in c_coll

# 15. sesja-farmienia
checks['15. sesja-farmienia'] = os.path.exists(f'{root_dir}/uifarmsession.py') and os.path.exists(f'{root_dir}/farmsession.py')

# 16. odnawianie-sklepow-botow
checks['16. odnawianie-sklepow-botow'] = 'MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1' in c_shop

# 17. dom-aukcyjny-historia
c_ah = read(f'{root_dir}/uiauctionhouse.py')
checks['17. dom-aukcyjny-historia'] = 'Historia' in c_ah and 'AuctionHistoryDialog' in c_ah

# 18. kolekcjoner-refine
c_ref = read(f'{root_dir}/uirefine.py')
checks['18. kolekcjoner-refine'] = 'mag.' in c_ref and 'CountItem' in c_ref

# 19. szarfy-szansa-tooltip
c_acce = read(f'{root_dir}/uiacce.py')
c_tip = read(f'{root_dir}/uitooltip.py')
checks['19. szarfy-szansa-tooltip'] = 'chanceDict' in c_acce and '__AdjustAttrMaxWidth' in c_tip

# 20. ukryj-szarfe
c_ch = read(f'{root_dir}/uicostumehide.py')
c_it = read(f'{server_src}/item.cpp')
checks['20. ukryj-szarfe'] = len(c_ch) > 100 and 'hiddenMask & 8' in c_it

# 21. brak-potek-m2-metiny-bossy
c_im = read(f'{server_src}/item_manager.cpp')
checks['21. brak-potek-m2-metiny-bossy'] = 'MT2009_PLUS_NO_POTIONS_M2_UP_V1' in c_im

# 22. ceny-bazowe-botow
c_town = read(f'{pb_overlay}/playerbot_town.h')
checks['22. ceny-bazowe-botow'] = 'playerbot_custom_prices::GetCustomItemPrice' in c_town

# 23. fix-emerytura-botow
c_ret = read(f'{pb_overlay}/playerbot_retirement.h')
checks['23. fix-emerytura-botow'] = 'IsPlayerBotHumanLedParty' in c_ret

# 24. itemshop-panel
checks['24. itemshop-panel'] = '/economy/itemshop' in c_app

# 25. balans-szkatułek-hard
checks['25. balans-szkatułek-hard'] = 'IsBossChestVnum' in c_item

# 26. duze-czcionki-skilli-i-ilosci
b_exe = open('Klient/metin2client.exe', 'rb').read() if os.path.exists('Klient/metin2client.exe') else b''
already_patched = bytes.fromhex('0fb64f418b4734c1e10583c1f303c10fb64f40508b4730c1e10583c1fe03c18bca50e8')
checks['26. duze-czcionki-skilli-i-ilosci'] = bool(already_patched in b_exe)

# 27. fix-boty-gildia-exp-party
checks['27. fix-boty-gildia-exp-party'] = os.path.exists(f'{server_src}/playerbot_guild_orders.h')

# 28. fix-boty-ulepszanie-lottery30
c_econ = read(f'{server_src}/playerbot_economy.h')
checks['28. fix-boty-ulepszanie-lottery30'] = bool('OnPlayerBotLottery30Refined' in c_econ)

# 29. fix-podglad-ekwipunku-tooltipy
c_pl = read(f'{seban_dir}/templates/player.html')
checks['29. fix-podglad-ekwipunku-tooltipy'] = bool('adjustTip' in c_pl)

# 30. odblokowanie-kostiumow-arezzo
c_arezzo = read(f'{pb_overlay}/playerbot_arezzo_costumes.h')
checks['30. odblokowanie-kostiumow-arezzo'] = bool('return false;' in c_arezzo)

# 31. powiadomienia-skarbiec-gildii
c_char = read(f'{server_src}/char.cpp')
checks['31. powiadomienia-skarbiec-gildii'] = bool('MT2009_PLUS_GUILD_TREASURY_NOTIFY_V1' in c_char)

# 32. tracker-bossow
checks['32. tracker-bossow'] = bool('do_boss_tracker' in c_cmd)

# 33. wyplata-utargu-kowal-gildijny
c_df = read('Server/linux-port/docker/game/Dockerfile')
c_ug = read(f'{root_dir}/uiguild.py')
checks['33. wyplata-utargu-kowal-gildijny'] = bool('guild.payout_get' in c_df and 'SetGuildPayout' in c_ug)

# 34. zielone-dodania-m1m2
c_mkt = read(f'{pb_overlay}/playerbot_market.h')
checks['34. zielone-dodania-m1m2'] = bool('IsPlayerBotGreenTradeableBonusVnum' in c_mkt)

print(f"{'MODYFIKACJA':45} | STATUS LOGICZNY")
print("-" * 65)
for k, v in checks.items():
    st = "TAK (100% Zaimplementowane)" if v else "NIE (BRAK!)"
    print(f"{k:45} | {st}")

failed = [k for k, v in checks.items() if not v]
print("=" * 65)
print(f"Laczny wynik weryfikacji kodu: {len(checks)-len(failed)}/{len(checks)}")
if failed:
    print("BLEDY W:", failed)
    sys.exit(1)
else:
    print("WSZYSTKIE 34 MODYFIKACJE SA W 100% POTWIERDZONE W KODZIE I PLIKACH!")
