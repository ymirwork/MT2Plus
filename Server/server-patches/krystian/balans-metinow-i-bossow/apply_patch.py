# -*- coding: utf-8 -*-
import re

MOB_FILE = 'Server/linux-port/docker/game/src/serverfiles/share/locale/poland/mob_drop_item.txt'
SPECIAL_FILE = 'Server/linux-port/docker/game/src/serverfiles/share/locale/poland/special_item_group.txt'

with open(MOB_FILE, 'r', encoding='utf-8') as f:
    mob_text = f.read()

with open(SPECIAL_FILE, 'r', encoding='utf-8') as f:
    special_text = f.read()

# 1. Update special_item_group 50074
new_chest_50074 = """Group\tBaroness_Chest
{
\tVnum\t50074\t-- Szkatułka Olbrz. Pająka
\t-- Bronie 65 lvl
\t1\t150\t1\t20\t-- Miecz Szponu Ducha+0
\t2\t151\t1\t10\t-- Miecz Szponu Ducha+1
\t3\t5090\t1\t20\t-- Dzwon Burzowego Ptaka+0
\t4\t5091\t1\t10\t-- Dzwon Burzowego Ptaka+1
\t5\t140\t1\t20\t-- Miecz Bojowy+0
\t6\t141\t1\t10\t-- Miecz Bojowy+1
\t7\t3130\t1\t20\t-- Partyzana+0
\t8\t3131\t1\t10\t-- Partyzana+1
\t9\t1100\t1\t20\t-- Smoczy Nóż+0
\t10\t1101\t1\t10\t-- Smoczy Nóż+1
\t11\t7130\t1\t20\t-- Niebiań. Ptasi Wachl.+0
\t12\t7131\t1\t10\t-- Niebiań. Ptasi Wachl.+1
\t13\t2140\t1\t20\t-- Olbrz. Łuk Żółt. Smoka+0
\t14\t2141\t1\t10\t-- Olbrz. Łuk Żółt. Smoka+1
\t-- Zbroje 61 lvl
\t15\t11681\t1\t15\t-- Duchowa Zbroja Płyt.+1
\t16\t11682\t1\t25\t-- Duchowa Zbroja Płyt.+2
\t17\t11881\t1\t15\t-- Szata Baronów+1
\t18\t11882\t1\t25\t-- Szata Baronów+2
\t19\t11481\t1\t15\t-- Ubranie Fuksyjne+1
\t20\t11482\t1\t25\t-- Ubranie Fuksyjne+2
\t21\t11281\t1\t15\t-- Zbroja Boga Smoków+1
\t22\t11282\t1\t25\t-- Zbroja Boga Smoków+2
\t-- Tarcze 61 lvl
\t23\t13060\t1\t15\t-- Sokola Tarcza+0
\t24\t13080\t1\t15\t-- Tarcza Tygrysa+0
\t25\t13100\t1\t15\t-- Lwia Tarcza+0
\t26\t13120\t1\t15\t-- Tarcza Smoka+0
\t-- Biżuteria
\t27\t14200\t1\t15\t-- Bransol. Z Niebiań.Łez+0
\t28\t16200\t1\t15\t-- Naszyj. Z Niebiań.Łez+0
\t29\t17200\t1\t15\t-- Kolczyki Z Niebiań.Łez+0
\t30\t14163\t1\t15\t-- Kryształowa Bransoleta+3
\t31\t17163\t1\t15\t-- Kryształowe Kolczyki+3
\t32\t16163\t1\t15\t-- Kryształowy Naszyjnik+3
\t-- RZADKIE: Bronie 75 lvl (~2.5% każda, ~15% sumarycznie)
\t33\t180\t1\t25\t-- Zatruty miecz+0
\t34\t3160\t1\t25\t-- Miecz Żalu+0
\t35\t2170\t1\t20\t-- Stalowy Łuk Kruka+0
\t36\t1130\t1\t20\t-- Skrzydła Demona Chakr.+0
\t37\t190\t1\t18\t-- Lwi Miecz+0
\t38\t5120\t1\t18\t-- Bambusowy Dzwon+0
\t-- RZADKIE: Zbroje z Czarnej Stali (~2.2% każda, ~9% sumarycznie)
\t39\t11290\t1\t22\t-- Zbroja Z Czarnej Stali+0
\t40\t11490\t1\t22\t-- Ubranie Czarn. Wiatru+0
\t41\t11690\t1\t22\t-- Zbr. Płyt. Czar. Magii+0
\t42\t11890\t1\t22\t-- Czarna Szata+0
\t-- RZADKIE: Tarcza Tytanów (~1.5%)
\t43\t13140\t1\t15\t-- Tarcza Tytanów+0
\t-- Perły
\t44\t27992\t1\t20\t-- Biała Perła
\t45\t27993\t1\t15\t-- Niebieska Perła
\t46\t27994\t1\t10\t-- Krwawa Perła
\t-- Kamień Duchowy & Bodziak
\t47\t50513\t1\t25\t-- Kamień Duchowy
\t48\t25040\t1\t35\t-- Zwój Błogosławieństwa
\t-- Przedmioty użytkowe
\t49\t70038\t20\t25\t-- Peleryna Męstwa
\t50\t70037\t1\t15\t-- Księga Zapomnienia
\t51\t70014\t1\t15\t-- Pigułka Krwi
\t52\t70043\t1\t15\t-- Rękawica Złodzieja
\t53\t70005\t1\t15\t-- Pierścień Doświadczenia
\t54\t30370\t1\t15\t-- Pozwolenie na Zaczar. Przedmiotu
\t55\t30368\t1\t10\t-- Pozwolenie na Wzmocn. Przedmiotu
\t56\tgold\t100000\t25\t-- Unknown Item
\t57\tgold\t250000\t20\t-- Unknown Item
\t58\texp\t200000\t25\t-- Unknown Item
}"""

pattern_50074 = r'Group\t[^\n]*\n\{\n\tVnum\t50074\b[^}]*\}'
assert re.search(pattern_50074, special_text), '50074 pattern not found in special_item_group'
special_text = re.sub(pattern_50074, new_chest_50074, special_text)

# 2. Update Baroness Drop in mob_drop_item (2092)
new_baroness = """Group\tBaronowna_Drop
{
\tMob\t2092\t-- Baronówna Pająków
\tType\tdrop
\t1\t50074\t1\t400\t-- Szkatułka Olbrz. Pająka (100% gwarantowana 2. szkatka!)
\t2\t50074\t1\t120\t-- Szkatułka Olbrz. Pająka (30% na 3. szkatkę)
\t3\t30025\t1\t400\t-- Worek z Pajęczą Trucizną (100%)
\t4\t30326\t1\t200\t-- Jad Królowej Pająków (50%)
\t5\t50513\t1\t400\t-- Kamień Duchowy (100% gwarantowany)
\t6\ts10743\t1\t400\t-- Boss_HighTier (100%)
\t7\ts10755\t1\t400\t-- MiniBoss_VeryHighTier (100%)
\t8\t30370\t2\t100\t-- Pozwolenie Zmianka (25%)
\t9\t30368\t1\t100\t-- Pozwolenie Dodanie (25%)
}"""
pattern_baroness = r'Group\tBaronowna_Drop\n\{[^}]*\}'
assert re.search(pattern_baroness, mob_text), 'Baronowna_Drop not found'
mob_text = re.sub(pattern_baroness, new_baroness, mob_text)

# 3. Update Lodowa Wiedźma in mob_drop_item (1192)
new_wiedzma = """Group\tSilnaLodowaWiedzma_Limit
{
\tLevel_limit\t80
\tMob\t1192\t-- Silna Lodowa Wiedźma
\tType\tdrop
\t1\t11294\t1\t50\t15\t-- Zbroja Z Czarnej Stali+4
\t2\t11494\t1\t50\t15\t-- Ubranie Czarn. Wiatru+4
\t3\t11694\t1\t50\t15\t-- Zbr. Płyt. Czar. Magii+4
\t4\t11894\t1\t50\t15\t-- Czarna Szata+4
\t5\t13064\t1\t50\t15\t-- Sokola Tarcza+4
\t6\t13084\t1\t50\t15\t-- Tarcza Tygrysa+4
\t7\t13104\t1\t50\t15\t-- Lwia Tarcza+4
\t8\t13124\t1\t50\t15\t-- Tarcza Smoka+4
\t9\t15184\t1\t50\t15\t-- Deszczowe Buty+4
\t10\t15164\t1\t50\t15\t-- Ekstazyjne Buty+4
\t11\t15204\t1\t50\t15\t-- Buty Feniksa+4
\t12\t15224\t1\t50\t15\t-- Buty Ognistego Ptaka+4
\t13\t16204\t1\t50\t15\t-- Naszyj. Z Niebiań.Łez+4
\t14\t16184\t1\t50\t15\t-- Ametystowy Naszyjnik+4
\t15\t17144\t1\t50\t15\t-- Kolczyki Z Biała.Złota+4
\t16\t17164\t1\t50\t15\t-- Kryształowe Kolczyki+4
\t17\t17184\t1\t50\t15\t-- Ametystowe Kolczyki+4
\t18\t17204\t1\t50\t15\t-- Kolczyki Z Niebiań.Łez+4
\t19\t28430\t1\t30\t15\t-- Kamień Duszy Penetr.+4
\t20\t28431\t1\t30\t15\t-- Kamień Duszy Śmierci+4
\t21\t28432\t1\t30\t15\t-- Kamień Duszy Powtórki+4
\t22\t28433\t1\t30\t15\t-- Kamień Duszy Wojownika+4
\t23\t28434\t1\t30\t15\t-- Kamień Duszy Ninja+4
\t24\t28435\t1\t30\t15\t-- Kamień Duszy Sury+4
\t25\t28436\t1\t30\t15\t-- Kamień Duszy Szamana+4
\t26\t28437\t1\t30\t15\t-- Kamień Duszy Potwora+4
\t27\t28438\t1\t30\t15\t-- Kamień Duszy Uchylenia+4
\t28\t28439\t1\t30\t15\t-- Kamień Duszy Uniku+4
\t29\t28440\t1\t30\t15\t-- Kamień Duszy Magii+4
\t30\t28441\t1\t30\t15\t-- Kamień Witalności+4
\t31\t28442\t1\t30\t15\t-- Kamień Duszy Obrony+4
\t32\t28443\t1\t30\t15\t-- Kamień Duszy Przysp.+4
\t33\t50513\t1\t400\t15\t-- Kamień Duchowy (100% gwarantowany)
\t34\t50513\t1\t200\t15\t-- Kamień Duchowy (50% na drugi)
\t35\t70031\t1\t100\t15\t-- Broszura Szermierki (25%)
}"""
pattern_wiedzma = r'Group\t[^\n]*\n\{\n\tLevel_limit\t80\n\tMob\t1192\b[^}]*\}'
assert re.search(pattern_wiedzma, mob_text), 'SilnaLodowaWiedzma_Limit not found'
mob_text = re.sub(pattern_wiedzma, new_wiedzma, mob_text)

# 4. Update Smok (2493) in mob_drop_item
new_smok = """Group\tWater_Dragon
{
\tMob\t2493\t-- Beran-Setaou
\tType\tdrop
\t1\t30190\t1\t400\t-- Krwisty Kamień
\t2\t30190\t2\t100\t-- Krwisty Kamień
\t3\t12284\t1\t20\t-- Hełm Mistrza Wojny+4
\t4\t12404\t1\t20\t-- Pajęczy Kaptur+4
\t5\t12544\t1\t20\t-- Magiczny Hełm+4
\t6\t12684\t1\t20\t-- Kapelusz Duszy+4
\t7\t15374\t1\t20\t-- Buty Euforii+4
\t8\t15394\t1\t20\t-- Kozaki Glorii+4
\t9\t15414\t1\t20\t-- Buty Qilina+4
\t10\t15434\t1\t20\t-- Buty Zimorodka+4
\t11\t27987\t1\t100\t-- Małż
\t12\t50124\t1\t20\t-- Próchniała Skrzynia
\t13\t50124\t1\t20\t-- Próchniała Skrzynia
\t14\t50124\t1\t20\t-- Próchniała Skrzynia
\t15\t50121\t1\t40\t-- Żelazne Pudełko
\t16\t50121\t1\t40\t-- Żelazne Pudełko
\t17\t71123\t1\t400\t-- Smocza Łuska (100% 1. sztuka)
\t18\t71129\t1\t400\t-- Smoczy Szpon (100% 1. sztuka)
\t19\t71123\t1\t300\t-- Smocza Łuska (75% 2. sztuka)
\t20\t71129\t1\t300\t-- Smoczy Szpon (75% 2. sztuka)
\t21\t71123\t1\t100\t-- Smocza Łuska (25% 3. sztuka)
\t22\t71129\t1\t100\t-- Smoczy Szpon (25% 3. sztuka)
\t23\t71083\t1\t100\t-- Księga Obróbki Kamienia
\t24\t25040\t2\t200\t-- Zwój Błogosławieństwa
\t25\t30370\t2\t200\t-- Pozwolenie Zmianka
\t26\t30368\t2\t200\t-- Pozwolenie Dodanie
\t27\t70031\t1\t200\t-- Broszura Szermierki (50%)
\t28\t25041\t1\t100\t-- Magiczny Kamień (25%)
}
Group\tWater_Dragon_HL
{
\tLevel_limit\t90
\tMob\t2493\t-- Beran-Setaou
\tType\tlimit
\t1\t30190\t4\t30\t-- Krwisty Kamień
\t2\t27992\t1\t100\t-- Biała Perła (25%)
\t3\t27993\t1\t80\t-- Niebieska Perła (20%)
\t4\t27994\t1\t60\t-- Krwawa Perła (15%)
\t5\t70024\t1\t20\t-- Marmur Błogosławieństwa (5%)
\t6\t50124\t1\t25\t-- Próchniała Skrzynia
\t7\t50124\t1\t25\t-- Próchniała Skrzynia
\t8\t50121\t1\t50\t-- Żelazne Pudełko
\t9\t50121\t1\t50\t-- Żelazne Pudełko
\t10\t50513\t1\t400\t-- Kamień Duchowy (100% gwarantowany)
\t11\t50513\t1\t200\t-- Kamień Duchowy (50% na drugi)
}"""
pattern_smok = r'Group\tWater_Dragon\n\{[^}]*\}\nGroup\tWater_Dragon_HL\n\{[^}]*\}'
assert re.search(pattern_smok, mob_text), 'Water_Dragon groups not found'
mob_text = re.sub(pattern_smok, new_smok, mob_text)

# 5. Metins 8008 - 8014
new_8008 = """Group\t혼마석
{
\tMob\t8008\t-- Metin Duszy
\tType\tdrop
\t1\ts8008\t1\t200\t-- Zlom
\t2\ts8008\t1\t100\t-- Zlom
\t3\ts8008\t1\t30\t-- Zlom
\t4\t50300\t1\t200\t-- Księga Umiejętności
\t5\t70014\t1\t1\t-- Pigułka Krwi
\t6\t70037\t1\t5\t-- Księga Zapomnienia
\t7\t50513\t1\t4\t-- Kamień Duchowy (1.0%)
\t8\t25040\t1\t4\t-- Zwój Błogosławieństwa (1.0%)
\t9\ts50901\t1\t20\t-- Receptury
\t10\t30370\t1\t1\t-- Pozwolenie na Zaczar. Przedmiotu
\t11\t30373\t1\t1\t-- Ksiega Erudyty
\t12\t30374\t1\t0.5\t-- Pióro Mędrca
\t13\ts10704\t1\t30\t-- herbs dolina
}"""

new_8009 = """Group\t영마석
{
\tMob\t8009\t-- Metin Cienia
\tType\tdrop
\t1\ts8009\t1\t200\t-- Zlom
\t2\ts8009\t1\t100\t-- Zlom
\t3\ts8009\t1\t30\t-- Zlom
\t4\t50300\t1\t200\t-- Księga Umiejętności
\t5\t70014\t1\t1\t-- Pigułka Krwi
\t6\t70037\t1\t5\t-- Księga Zapomnienia
\t7\t50513\t1\t6\t-- Kamień Duchowy (1.5%)
\t8\t25040\t1\t6\t-- Zwój Błogosławieństwa (1.5%)
\t9\ts50901\t1\t21\t-- Receptury
\t10\t30370\t1\t2\t-- Pozwolenie na Zaczar. Przedmiotu
\t11\t30373\t1\t2\t-- Ksiega Erudyty
\t12\t30374\t1\t1\t-- Pióro Mędrca
\t13\ts10705\t1\t30\t-- herbs pustynia
}"""

new_8010 = """Group\t강마석
{
\tMob\t8010\t-- Metin Twardości
\tType\tdrop
\t1\ts8010\t1\t200\t-- Zlom
\t2\ts8010\t1\t70\t-- Zlom
\t3\ts8010\t1\t30\t-- Zlom
\t4\t50300\t1\t250\t-- Księga Umiejętności
\t5\t70014\t1\t1\t-- Pigułka Krwi
\t6\t70037\t1\t5\t-- Księga Zapomnienia
\t7\t50513\t1\t8\t-- Kamień Duchowy (2.0%)
\t8\t25040\t1\t8\t-- Zwój Błogosławieństwa (2.0%)
\t9\ts50901\t1\t22\t-- Receptury
\t10\t30370\t1\t4\t-- Pozwolenie na Zaczar. Przedmiotu
\t11\t50309\t1\t4\t-- Księga Misji (Trudna)
\t12\t30373\t1\t2.5\t-- Ksiega Erudyty
\t13\t30374\t1\t1.25\t-- Pióro Mędrca
\t14\ts10706\t1\t30\t-- herbs sohan
}"""

new_8011 = """Group\t악마석
{
\tMob\t8011\t-- Metin Diabła
\tType\tdrop
\t1\ts8011\t1\t200\t-- Zlom
\t2\ts8011\t1\t50\t-- Zlom
\t3\ts8011\t1\t15\t-- Zlom
\t4\t50300\t1\t250\t-- Księga Umiejętności
\t5\t70014\t1\t1\t-- Pigułka Krwi
\t6\t70037\t1\t5\t-- Księga Zapomnienia
\t7\t50513\t1\t10\t-- Kamień Duchowy (2.5%)
\t8\t25040\t1\t10\t-- Zwój Błogosławieństwa (2.5%)
\t9\ts50901\t1\t23\t-- Receptury
\t10\t30370\t1\t8\t-- Pozwolenie na Zaczar. Przedmiotu
\t11\t30373\t1\t3\t-- Ksiega Erudyty
\t12\t30374\t1\t1.5\t-- Pióro Mędrca
\t13\ts10707\t1\t30\t-- herbs hwang
}"""

new_8012 = """Group\t운마석
{
\tMob\t8012\t-- Metin Upadku
\tType\tdrop
\t1\ts8012\t1\t200\t-- Zlom
\t2\ts8012\t1\t50\t-- Zlom
\t3\ts8012\t1\t15\t-- Zlom
\t4\t50300\t1\t300\t-- Księga Umiejętności
\t5\t70014\t1\t1\t-- Pigułka Krwi
\t6\t70037\t1\t5\t-- Księga Zapomnienia
\t7\t50513\t1\t12\t-- Kamień Duchowy (3.0%)
\t8\t25040\t1\t10\t-- Zwój Błogosławieństwa (2.5%)
\t9\ts50901\t1\t24\t-- Receptury
\t10\t30370\t1\t12\t-- Pozwolenie na Zaczar. Przedmiotu
\t11\t50309\t1\t4\t-- Księga Misji (Trudna)
\t12\t72735\t1\t10\t-- Maska Sabaha
\t13\t30373\t1\t3.5\t-- Ksiega Erudyty
\t14\t30374\t1\t1.75\t-- Pióro Mędrca
\t15\ts10707\t1\t30\t-- herbs hwang
}"""

new_8013 = """Group\t사마석
{
\tMob\t8013\t-- Metin Śmierci
\tType\tdrop
\t1\ts8013\t1\t200\t-- Zlom
\t2\ts8013\t1\t40\t-- Zlom
\t3\ts8013\t1\t10\t-- Zlom
\t4\t50300\t1\t300\t-- Księga Umiejętności
\t5\t70014\t1\t1\t-- Pigułka Krwi
\t6\t70037\t1\t5\t-- Księga Zapomnienia
\t7\t50513\t1\t16\t-- Kamień Duchowy (4.0%)
\t8\t25040\t1\t12\t-- Zwój Błogosławieństwa (3.0%)
\t9\ts50901\t1\t25\t-- Receptury
\t10\t30370\t1\t16\t-- Pozwolenie na Zaczar. Przedmiotu
\t11\t30373\t1\t4\t-- Ksiega Erudyty
\t12\t30374\t1\t2\t-- Pióro Mędrca
\t13\ts10706\t1\t30\t-- herbs sohan
}"""

new_8014 = """Group\t살마석
{
\tMob\t8014\t-- Metin Morderstwa
\tType\tdrop
\t1\ts8014\t1\t200\t-- Zlom
\t2\ts8014\t1\t40\t-- Zlom
\t3\ts8014\t1\t10\t-- Zlom
\t4\t50300\t1\t300\t-- Księga Umiejętności
\t5\t70014\t1\t50\t-- Pigułka Krwi
\t6\t70037\t1\t50\t-- Księga Zapomnienia
\t7\t50513\t1\t20\t-- Kamień Duchowy (5.0%)
\t8\t25040\t1\t16\t-- Zwój Błogosławieństwa (4.0%)
\t9\ts50901\t1\t25\t-- Receptury
\t10\t30370\t1\t20\t-- Pozwolenie na Zaczar. Przedmiotu
\t11\t30368\t1\t0.3\t-- Pozwolenie na Wzmocn. Przedmiotu
\t12\t50310\t1\t4\t-- Księga Misji (ekspert)
\t13\t30373\t1\t4.5\t-- Ksiega Erudyty
\t14\t30374\t1\t2.25\t-- Pióro Mędrca
\t15\ts10708\t1\t30\t-- herbs pieklo
}"""

for mob_id, new_txt in [(8008, new_8008), (8009, new_8009), (8010, new_8010), (8011, new_8011), (8012, new_8012), (8013, new_8013), (8014, new_8014)]:
    p = rf'Group\t[^\n]*\n\{{\n\tMob\t{mob_id}\b[^}}]*\}}'
    assert re.search(p, mob_text), f'Metin {mob_id} not found'
    mob_text = re.sub(p, new_txt, mob_text)

# 6. Metins 8024 - 8027
new_8024 = """Group\t풍마석
{
\tMob\t8024\t-- Metin Pung-Ma
\tType\tdrop
\t1\ts8024\t1\t200\t-- Zlom
\t2\ts8024\t1\t40\t-- Zlom
\t3\ts8024\t1\t10\t-- Zlom
\t4\t70014\t1\t2\t-- Pigułka Krwi
\t5\t70037\t1\t5\t-- Księga Zapomnienia
\t6\t50513\t1\t24\t-- Kamień Duchowy (6.0%)
\t7\t25040\t1\t24\t-- Zwój Błogosławieństwa (6.0%)
\t8\ts10983\t1\t160\t-- Kamień Duszy +3 (40%)
\t9\ts10984\t1\t60\t-- Kamień Duszy +4 (15%)
\t10\ts50901\t1\t30\t-- Receptury
\t11\t30370\t1\t25\t-- Pozwolenie na Zaczar. Przedmiotu
\t12\t30368\t1\t1\t-- Pozwolenie na Wzmocn. Przedmiotu
\t13\t50300\t1\t400\t-- Księga Umiejętności
\t14\t30373\t1\t5\t-- Ksiega Erudyty
\t15\t30374\t1\t2.5\t-- Pióro Mędrca
\t16\t30375\t1\t1.25\t-- Magiczna Ruda
\t17\ts10709\t1\t30\t-- herbs las
}"""

new_8025 = """Group\t마안석
{
\tMob\t8025\t-- Metin Ma-An
\tType\tdrop
\t1\ts8025\t1\t200\t-- Zlom
\t2\ts8025\t1\t40\t-- Zlom
\t3\ts8025\t1\t10\t-- Zlom
\t4\t70014\t1\t2\t-- Pigułka Krwi
\t5\t70037\t1\t5\t-- Księga Zapomnienia
\t6\t50513\t1\t30\t-- Kamień Duchowy (7.5%)
\t7\t25040\t1\t30\t-- Zwój Błogosławieństwa (7.5%)
\t8\ts10983\t1\t140\t-- Kamień Duszy +3 (35%)
\t9\ts10984\t1\t100\t-- Kamień Duszy +4 (25%)
\t10\ts50901\t1\t30\t-- Receptury
\t11\t30370\t1\t30\t-- Pozwolenie na Zaczar. Przedmiotu
\t12\t30368\t1\t2.5\t-- Pozwolenie na Wzmocn. Przedmiotu
\t13\t50310\t1\t4\t-- Księga Misji (ekspert)
\t14\t50300\t1\t400\t-- Księga Umiejętności
\t15\t30373\t1\t5.5\t-- Ksiega Erudyty
\t16\t30374\t1\t2.75\t-- Pióro Mędrca
\t17\t30375\t1\t1\t-- Magiczna Ruda
\t18\ts10709\t1\t30\t-- herbs las
}"""

new_8026 = """Group\t투용석
{
\tMob\t8026\t-- Metin Tu-Young
\tType\tdrop
\t1\ts8026\t1\t200\t-- Zlom
\t2\ts8026\t1\t100\t-- Zlom
\t3\ts8026\t1\t50\t-- Zlom
\t4\ts8026\t1\t20\t-- Zlom
\t5\ts8026\t1\t5\t-- Zlom
\t6\t70038\t1\t15\t-- Peleryna Męstwa
\t7\t25040\t1\t40\t-- Zwój Błogosławieństwa (10.0%)
\t8\t70048\t1\t20\t-- Płaszcz Uciekiniera
\t9\t70037\t1\t25\t-- Księga Zapomnienia
\t10\t70014\t1\t25\t-- Pigułka Krwi
\t11\t70043\t1\t20\t-- Rękawica Złodzieja
\t12\t70005\t1\t20\t-- Pierścień Doświadczenia
\t13\t50513\t1\t40\t-- Kamień Duchowy (10.0%)
\t14\ts10983\t1\t120\t-- Kamień Duszy +3 (30%)
\t15\ts10984\t1\t160\t-- Kamień Duszy +4 (40%)
\t16\ts50901\t1\t30\t-- Receptury
\t17\t30370\t1\t35\t-- Pozwolenie na Zaczar. Przedmiotu
\t18\t30368\t1\t5\t-- Pozwolenie na Wzmocn. Przedmiotu
\t19\t25100\t1\t1.5\t-- Zwój Kamienia Duszy
\t20\t71282\t1\t1.5\t-- Ekstraktor Skaz
\t21\ts50902\t1\t3\t-- Super Receptury
\t22\t50300\t1\t400\t-- Księga Umiejętności
\t23\t71201\t1\t2.5\t-- Zwoj Egzo
\t24\t71294\t1\t1.25\t-- Rada
\t25\t30373\t1\t6\t-- Ksiega Erudyty
\t26\t30374\t1\t3\t-- Pióro Mędrca
\t27\t30375\t1\t1.5\t-- Magiczna Ruda
\t28\ts10710\t1\t30\t-- herbs redlas
}"""

new_8027 = """Group\t전운석
{
\tMob\t8027\t-- Metin Jeon-Un
\tType\tdrop
\t1\ts8027\t1\t200\t-- Zlom
\t2\ts8027\t1\t140\t-- Zlom
\t3\ts8027\t1\t80\t-- Zlom
\t4\ts8027\t1\t40\t-- Zlom
\t5\ts8027\t1\t16\t-- Zlom
\t6\t70012\t1\t15\t-- Łza Bogini
\t7\t70038\t1\t15\t-- Peleryna Męstwa
\t8\t25040\t1\t50\t-- Zwój Błogosławieństwa (12.5%)
\t9\t70048\t1\t20\t-- Płaszcz Uciekiniera
\t10\t70037\t1\t25\t-- Księga Zapomnienia
\t11\t70014\t1\t25\t-- Pigułka Krwi
\t12\t70043\t1\t20\t-- Rękawica Złodzieja
\t13\t70005\t1\t20\t-- Pierścień Doświadczenia
\t14\t50300\t1\t400\t-- Księga Umiejętności
\t15\t50513\t1\t50\t-- Kamień Duchowy (12.5%)
\t16\ts10983\t1\t80\t-- Kamień Duszy +3 (20%)
\t17\ts10984\t1\t200\t-- Kamień Duszy +4 (50%)
\t18\ts50901\t1\t40\t-- Receptury
\t19\t30370\t1\t40\t-- Pozwolenie na Zaczar. Przedmiotu
\t20\t30368\t1\t8\t-- Pozwolenie na Wzmocn. Przedmiotu
\t21\t25100\t1\t3\t-- Zwój Kamienia Duszy
\t22\t71282\t1\t2.5\t-- Ekstraktor Skaz
\t23\ts50902\t1\t8\t-- Super Receptury
\t24\t71201\t1\t5\t-- Zwoj Egzo
\t25\t71294\t1\t2.5\t-- Rada
\t26\t30373\t1\t8\t-- Ksiega Erudyty
\t27\t30374\t1\t4\t-- Pióro Mędrca
\t28\t30375\t1\t2\t-- Magiczna Ruda
\t29\ts10710\t1\t30\t-- herbs redlas
}"""

for mob_id, new_txt in [(8024, new_8024), (8025, new_8025), (8026, new_8026), (8027, new_8027)]:
    p = rf'Group\t[^\n]*\n\{{\n\tMob\t{mob_id}\b[^}}]*\}}'
    assert re.search(p, mob_text), f'Metin {mob_id} not found'
    mob_text = re.sub(p, new_txt, mob_text)

# 7. Metins 8051 - 8056
new_8051 = """Group\t혼마석\t\t\t
{				
\tmob\t8051\t\t
\tType\tdrop\t\t
\t1\t30500\t1\t100\t-- Rubinowy Ozdobny Nóż
\t2\t30506\t1\t100\t-- Szafirowy Ozdobny Nóż
\t3\t30512\t1\t100\t-- Czerwona Smocza Stal
\t4\t30518\t1\t100\t-- Złota Przędza
\t5\t143\t1\t40\t-- Miecz Bojowy+3
\t6\t154\t1\t30\t-- Miecz Szponu Ducha+4
\t7\t1104\t1\t20\t-- Smoczy Nóż+4
\t8\t7143\t1\t40\t-- Wachlarz Zbawienia+3
\t9\t11293\t1\t30\t-- Zbroja Z Czarnej Stali+3
\t10\t11494\t1\t20\t-- Ubranie Czarn. Wiatru+4
\t11\t50513\t1\t60\t-- Kamień Duchowy (15%)
\t12\ts10984\t1\t200\t-- Kamień Duszy +4 (50%)
\t13\t25040\t1\t50\t-- Zwój Błogosławieństwa (12.5%)
\t14\t70012\t1\t30\t-- Łza Bogini
\t15\t39006\t1\t30\t-- Peleryna Męstwa
\t16\t70048\t1\t40\t-- Płaszcz Uciekiniera
\t17\t70037\t1\t50\t-- Księga Zapomnienia
\t18\t70014\t1\t50\t-- Pigułka Krwi
\t19\t70043\t1\t40\t-- Rękawica Złodzieja
\t20\t39002\t1\t40\t-- Pierścień Doświadczenia
\t21\t50300\t1\t400\t-- Księga Umiejętności
\t22\t100300\t1\t1\t-- Zielona Smocza Fasola
}"""

new_8052 = """Group\t귀마석\t\t\t
{				
\tmob\t8052\t\t
\tType\tdrop\t\t
\t1\t30501\t1\t100\t-- Złota Sprzączka
\t2\t30507\t1\t100\t-- Brązowy Zacisk
\t3\t30513\t1\t100\t-- Szlachetny Naramiennik
\t4\t30519\t1\t100\t-- Złoty Hak
\t5\t144\t1\t30\t-- Miecz Bojowy+4
\t6\t154\t1\t20\t-- Miecz Szponu Ducha+4
\t7\t5103\t1\t40\t-- Dzwon Nieba I Ziemi+3
\t8\t7144\t1\t30\t-- Wachlarz Zbawienia+4
\t9\t11294\t1\t20\t-- Zbroja Z Czarnej Stali+4
\t10\t50513\t1\t60\t-- Kamień Duchowy (15%)
\t11\ts10984\t1\t200\t-- Kamień Duszy +4 (50%)
\t12\t25040\t1\t50\t-- Zwój Błogosławieństwa (12.5%)
\t13\t70012\t1\t30\t-- Łza Bogini
\t14\t39006\t1\t30\t-- Peleryna Męstwa
\t15\t70048\t1\t40\t-- Płaszcz Uciekiniera
\t16\t70037\t1\t50\t-- Księga Zapomnienia
\t17\t70014\t1\t50\t-- Pigułka Krwi
\t18\t70043\t1\t40\t-- Rękawica Złodzieja
\t19\t39002\t1\t40\t-- Pierścień Doświadczenia
\t20\t50300\t1\t400\t-- Księga Umiejętności
\t21\t100300\t1\t1\t-- Zielona Smocza Fasola
}"""

new_8053 = """Group\t광마석\t\t\t
{				
\tmob\t8053\t\t
\tType\tdrop\t\t
\t1\t30502\t1\t100\t-- Rubinowa Ozdoba
\t2\t30508\t1\t100\t-- Szafirowa Ozdoba
\t3\t30514\t1\t100\t-- Fioletowy Materiał
\t4\t30520\t1\t100\t-- Złota Spinka
\t5\t144\t1\t20\t-- Miecz Bojowy+4
\t6\t3143\t1\t40\t-- Magnetyczne Ostrze+3
\t7\t5104\t1\t30\t-- Dzwon Nieba I Ziemi+4
\t8\t7144\t1\t20\t-- Wachlarz Zbawienia+4
\t9\t11893\t1\t40\t-- Czarna Szata+3
\t10\t50513\t1\t60\t-- Kamień Duchowy (15%)
\t11\ts10984\t1\t200\t-- Kamień Duszy +4 (50%)
\t12\t25040\t1\t50\t-- Zwój Błogosławieństwa (12.5%)
\t13\t70012\t1\t30\t-- Łza Bogini
\t14\t39006\t1\t30\t-- Peleryna Męstwa
\t15\t70048\t1\t40\t-- Płaszcz Uciekiniera
\t16\t70037\t1\t50\t-- Księga Zapomnienia
\t17\t70014\t1\t50\t-- Pigułka Krwi
\t18\t70043\t1\t40\t-- Rękawica Złodzieja
\t19\t39002\t1\t40\t-- Pierścień Doświadczenia
\t20\t50300\t1\t400\t-- Księga Umiejętności
\t21\t100300\t1\t1\t-- Zielona Smocza Fasola
}"""

new_8054 = """Group\t용마석\t\t\t
{				
\tmob\t8054\t\t
\tType\tdrop\t\t
\t1\t30503\t1\t100\t-- Ametystowy Ozdobny Nóż
\t2\t30509\t1\t100\t-- Niebieska Smocza Stal
\t3\t30515\t1\t100\t-- Purpurowa Smocza Stal
\t4\t30521\t1\t100\t-- Element Pierścienia
\t5\t2143\t1\t40\t-- Olbrz. Łuk Żółt. Smoka+3
\t6\t3144\t1\t30\t-- Magnetyczne Ostrze+4
\t7\t5104\t1\t20\t-- Dzwon Nieba I Ziemi+4
\t8\t11693\t1\t40\t-- Zbr. Płyt. Czar. Magii+3
\t9\t11894\t1\t30\t-- Czarna Szata+4
\t10\t50513\t1\t60\t-- Kamień Duchowy (15%)
\t11\ts10984\t1\t200\t-- Kamień Duszy +4 (50%)
\t12\t25040\t1\t50\t-- Zwój Błogosławieństwa (12.5%)
\t13\t70012\t1\t30\t-- Łza Bogini
\t14\t39006\t1\t30\t-- Peleryna Męstwa
\t15\t70048\t1\t40\t-- Płaszcz Uciekiniera
\t16\t70037\t1\t50\t-- Księga Zapomnienia
\t17\t70014\t1\t50\t-- Pigułka Krwi
\t18\t70043\t1\t40\t-- Rękawica Złodzieja
\t19\t39002\t1\t40\t-- Pierścień Doświadczenia
\t20\t50300\t1\t400\t-- Księga Umiejętności
\t21\t100300\t1\t1\t-- Zielona Smocza Fasola
}"""

new_8055 = """Group\t지마석\t\t\t
{				
\tmob\t8055\t\t
\tType\tdrop\t\t
\t1\t30504\t1\t100\t-- Srebrny Zacisk
\t2\t30510\t1\t100\t-- Wytworny Naramiennik
\t3\t30516\t1\t100\t-- Antyczny Naramiennik
\t4\t30522\t1\t100\t-- Ogniwa Łańcucha
\t5\t1103\t1\t40\t-- Smoczy Nóż+3
\t6\t2144\t1\t30\t-- Olbrz. Łuk Żółt. Smoka+4
\t7\t3144\t1\t20\t-- Magnetyczne Ostrze+4
\t8\t11493\t1\t40\t-- Ubranie Czarn. Wiatru+3
\t9\t11694\t1\t30\t-- Zbr. Płyt. Czar. Magii+4
\t10\t11894\t1\t20\t-- Czarna Szata+4
\t11\t50513\t1\t60\t-- Kamień Duchowy (15%)
\t12\ts10984\t1\t200\t-- Kamień Duszy +4 (50%)
\t13\t25040\t1\t50\t-- Zwój Błogosławieństwa (12.5%)
\t14\t70012\t1\t30\t-- Łza Bogini
\t15\t39006\t1\t30\t-- Peleryna Męstwa
\t16\t70048\t1\t40\t-- Płaszcz Uciekiniera
\t17\t70037\t1\t50\t-- Księga Zapomnienia
\t18\t70014\t1\t50\t-- Pigułka Krwi
\t19\t70043\t1\t40\t-- Rękawica Złodzieja
\t20\t39002\t1\t40\t-- Pierścień Doświadczenia
\t21\t50300\t1\t400\t-- Księga Umiejętności
\t22\t100300\t1\t1\t-- Zielona Smocza Fasola
}"""

new_8056 = """Group\t마마석\t\t\t
{				
\tmob\t8056\t\t
\tType\tdrop\t\t
\t1\t30505\t1\t100\t-- Szmaragdowa Ozdoba
\t2\t30511\t1\t100\t-- Czerwony Materiał
\t3\t30517\t1\t100\t-- Złoty Materiał
\t4\t30523\t1\t100\t-- Element Ozdoby
\t5\t153\t1\t40\t-- Miecz Szponu Ducha+3
\t6\t1104\t1\t30\t-- Smoczy Nóż+4
\t7\t2144\t1\t20\t-- Olbrz. Łuk Żółt. Smoka+4
\t8\t11293\t1\t40\t-- Zbroja Z Czarnej Stali+3
\t9\t11494\t1\t30\t-- Ubranie Czarn. Wiatru+4
\t10\t11694\t1\t20\t-- Zbr. Płyt. Czar. Magii+4
\t11\t50513\t1\t60\t-- Kamień Duchowy (15%)
\t12\ts10984\t1\t200\t-- Kamień Duszy +4 (50%)
\t13\t25040\t1\t50\t-- Zwój Błogosławieństwa (12.5%)
\t14\t70012\t1\t30\t-- Łza Bogini
\t15\t39006\t1\t30\t-- Peleryna Męstwa
\t16\t70048\t1\t40\t-- Płaszcz Uciekiniera
\t17\t70037\t1\t50\t-- Księga Zapomnienia
\t18\t70014\t1\t50\t-- Pigułka Krwi
\t19\t70043\t1\t40\t-- Rękawica Złodzieja
\t20\t39002\t1\t40\t-- Pierścień Doświadczenia
\t21\t50300\t1\t400\t-- Księga Umiejętności
\t22\t100300\t1\t1\t-- Zielona Smocza Fasola
}"""

for mob_id, new_txt in [(8051, new_8051), (8052, new_8052), (8053, new_8053), (8054, new_8054), (8055, new_8055), (8056, new_8056)]:
    p = rf'Group[^\n]*\n\{{[^\n]*\n[ \t]*mob\t{mob_id}\b[^}}]*\}}'
    assert re.search(p, mob_text), f'Metin {mob_id} not found'
    mob_text = re.sub(p, new_txt, mob_text)

with open(MOB_FILE, 'w', encoding='utf-8') as f:
    f.write(mob_text)

with open(SPECIAL_FILE, 'w', encoding='utf-8') as f:
    f.write(special_text)

print('SUCCESS! Files updated successfully.')
