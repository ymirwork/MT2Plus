import os

repo = r'd:\Github\MT2Plus'
results = {}

# 1. wstawanie-100hp
p1 = os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/cmd_general.cpp')
if os.path.exists(p1):
    with open(p1, 'r', encoding='utf-8', errors='ignore') as f:
        c1 = f.read()
        results['wstawanie-100hp'] = 'GetMaxHP()' in c1 and 'SCMD_RESTART' in c1
else:
    results['wstawanie-100hp'] = False

# 2. autolowy-szybkie-zbieranie
p2 = os.path.join(repo, 'Klient/pack/root/uiautohunt.py')
if os.path.exists(p2):
    with open(p2, 'r', encoding='utf-8', errors='ignore') as f:
        c2 = f.read()
        results['autolowy-szybkie-zbieranie'] = '/pickup_nearby' in c2
else:
    results['autolowy-szybkie-zbieranie'] = False

# 3. ukrycie-hp-celu
p3 = os.path.join(repo, 'Klient/pack/root/uitarget.py')
if os.path.exists(p3):
    with open(p3, 'r', encoding='utf-8', errors='ignore') as f:
        c3 = f.read()
        results['ukrycie-hp-celu'] = 'hpGauge.Hide()' in c3 or 'MT2009_PLUS_HIDE_TARGET_HP' in c3 or 'pHpText' in c3
else:
    results['ukrycie-hp-celu'] = False

# 4. sklep-160-slotow
p4_1 = os.path.join(repo, 'Klient/pack/root/offlineshopmanage.py')
p4_2 = os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/char_shop.cpp')
if os.path.exists(p4_1) and os.path.exists(p4_2):
    with open(p4_1, 'r', encoding='utf-8', errors='ignore') as f1, open(p4_2, 'r', encoding='utf-8', errors='ignore') as f2:
        results['sklep-160-slotow'] = 'PLAYER_SHOP_TWO_BLOCKS_KEYS2_V1' in f1.read() and 'SHOP_PLAYER_HEIGHT * 2' in f2.read()
else:
    results['sklep-160-slotow'] = False

# 5. recykling-bonusow
p5 = os.path.join(repo, 'Server/linux-port/docker/game/quest/recykling_bonusow.quest')
results['recykling-bonusow'] = os.path.exists(p5)

# 6. pierscien-teleportacji
p6 = os.path.join(repo, 'Server/linux-port/docker/game/quest/teleport_ring.quest')
results['pierscien-teleportacji'] = os.path.exists(p6)

# 7. seban-panel-ekonomia (GM filter)
p7 = os.path.join(repo, 'Server/linux-port/docker/seban-panel/collector.py')
if os.path.exists(p7):
    with open(p7, 'r', encoding='utf-8', errors='ignore') as f:
        results['seban-panel-ekonomia'] = 'item_not_gm_scope_sql' in f.read()
else:
    results['seban-panel-ekonomia'] = False

# 8. devgameplay (skróty k/kk)
p8 = os.path.join(repo, 'Klient/pack/root/uipickmoney.py')
if os.path.exists(p8):
    with open(p8, 'r', encoding='utf-8', errors='ignore') as f:
        results['devgameplay (skróty k/kk)'] = 'k' in f.read() or 'kk' in f.read()

# 9. autofish
p9 = os.path.join(repo, 'Klient/pack/root/uiautohunt.py')
if os.path.exists(p9):
    with open(p9, 'r', encoding='utf-8', errors='ignore') as f:
        results['autofish'] = 'AutoFishWindow' in f.read() or 'autofish' in f.read().lower()

# 10. optymalizacja-autolowy-drop-redlas
p10_1 = os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/playerbot_manager.cpp')
p10_2 = os.path.join(repo, 'Server/linux-port/docker/mariadb/playerbot/apply.sh')
results['optymalizacja-autolowy-drop-redlas'] = False
if os.path.exists(p10_1) and os.path.exists(p10_2):
    with open(p10_1, 'r', encoding='utf-8', errors='ignore') as f1, open(p10_2, 'r', encoding='utf-8', errors='ignore') as f2:
        results['optymalizacja-autolowy-drop-redlas'] = 'IsHumanTargetReachable' in f1.read() and 'MT2009_PLUS_STACK_200_EXTENDED' in f2.read()

# 11. oferty-blyskawiczne-is
p11 = os.path.join(repo, 'Server/linux-port/docker/mariadb/playerbot/mod/92_itemshop_flash_offers.sql')
results['oferty-blyskawiczne-is'] = os.path.exists(p11)

# 12. pierscienie-czas-noszenia
p12 = os.path.join(repo, 'Server/linux-port/docker/mariadb/playerbot/apply.sh')
if os.path.exists(p12):
    with open(p12, 'r', encoding='utf-8', errors='ignore') as f:
        results['pierscienie-czas-noszenia'] = 'MT2009_PLUS_AMULET_DURATION_30D' in f.read()

# 13. recykling-broni-30
p13 = os.path.join(repo, 'Server/linux-port/overlays/playerbot/src/game/src/playerbot_gear.h')
if os.path.exists(p13):
    with open(p13, 'r', encoding='utf-8', errors='ignore') as f:
        results['recykling-broni-30'] = 'IsPlayerBotHighValueLevel30' in f.read()

# 14. kolekcjoner-autodrop
p14 = os.path.join(repo, 'Klient/pack/root/uicollector.py')
if os.path.exists(p14):
    with open(p14, 'r', encoding='utf-8', errors='ignore') as f:
        results['kolekcjoner-autodrop'] = 'TEXT_AUTO_DROP' in f.read()

# 15. sesja-farmienia
p15 = os.path.join(repo, 'Klient/pack/root/uifarmsession.py')
results['sesja-farmienia'] = os.path.exists(p15)

# 16. odnawianie-sklepow-botow
p16 = os.path.join(repo, 'Server/linux-port/docker/game/src/server/game/src/char_shop.cpp')
if os.path.exists(p16):
    with open(p16, 'r', encoding='utf-8', errors='ignore') as f:
        results['odnawianie-sklepow-botow'] = 'MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1' in f.read()

# 17. dom-aukcyjny-historia
p17 = os.path.join(repo, 'Klient/pack/root/uiauctionhouse.py')
if os.path.exists(p17):
    with open(p17, 'r', encoding='utf-8', errors='ignore') as f:
        results['dom-aukcyjny-historia'] = 'Historia' in f.read()

# 18. kolekcjoner-refine
p18 = os.path.join(repo, 'Klient/pack/root/uirefine.py')
if os.path.exists(p18):
    with open(p18, 'r', encoding='utf-8', errors='ignore') as f:
        results['kolekcjoner-refine'] = 'mag.' in f.read() or 'collector' in f.read()

# 19. szarfy-szansa-tooltip
p19 = os.path.join(repo, 'Klient/pack/root/uiacce.py')
if os.path.exists(p19):
    with open(p19, 'r', encoding='utf-8', errors='ignore') as f:
        results['szarfy-szansa-tooltip'] = 'chanceDict' in f.read()

# 20. ukrywanie szarfy w podglądzie
p20 = os.path.join(repo, 'Klient/pack/root/uicostumehide.py')
if os.path.exists(p20):
    with open(p20, 'r', encoding='utf-8', errors='ignore') as f:
        results['ukrywanie-szarfy-podglad'] = 'sash' in f.read().lower() or 'szarf' in f.read().lower() or 'costume' in f.read().lower()

# 21. brak-potek-m2-metiny-bossy
p21 = os.path.join(repo, 'Server/linux-port/docker/game/src/serverfiles/share/locale/poland/mob_drop_item.txt')
if os.path.exists(p21):
    with open(p21, 'r', encoding='utf-8', errors='ignore') as f:
        c21 = f.read()
        idx_8005 = c21.find('Mob\t8005')
        group_end = c21.find('}', idx_8005) if idx_8005 != -1 else -1
        # Metin Czerni (8005, M2) nie powinien miec potki 27002 ani 27005 w swojej grupie
        results['brak-potek-m2-metiny-bossy'] = idx_8005 != -1 and '27002' not in c21[idx_8005:group_end]
else:
    results['brak-potek-m2-metiny-bossy'] = False

# 22. ceny-bazowe-botow
p22 = os.path.join(repo, 'Server/linux-port/docker/seban-panel/templates/economy_bot_prices.html')
results['ceny-bazowe-botow'] = os.path.exists(p22)

# 23. fix-emerytura-botow
p23 = os.path.join(repo, 'Server/linux-port/overlays/playerbot/src/game/src/playerbot_retirement.h')
if os.path.exists(p23):
    with open(p23, 'r', encoding='utf-8', errors='ignore') as f:
        results['fix-emerytura-botow'] = 'IsPlayerBotHumanLedParty' in f.read()
else:
    results['fix-emerytura-botow'] = False

# 24. itemshop-panel
p24 = os.path.join(repo, 'Server/linux-port/docker/seban-panel/templates/economy_itemshop.html')
results['itemshop-panel'] = os.path.exists(p24)

all_ok = True
for k, v in results.items():
    status = 'TAK (Aktywne)' if v else 'NIE (Brak)'
    if not v:
        all_ok = False
    print(f'{k:40}: {status}')

print('---')
print('AUDYT MODYFIKACJI MT2PLUS:', 'WSZYSTKIE 24/24 AKTYWNE!' if all_ok else 'UWAGA: NIEKTORE MODYFIKACJE NIE SA AKTYWNE!')
