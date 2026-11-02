# Balans Dropu: Metiny (40-105) oraz Złagodzenie Bossów (Hard z ułatwieniami)

Data wdrożenia: 2026-11-02
Autor: Krystian / Antigravity

## 1. Kontekst i Założenia

Serwer ma profil **Hard z delikatnymi ułatwieniami**. 
Wcześniejsze zmiany na bossach (Baronówna, Wiedźma, Smok) mocno ograniczyły wcześniejsze patologie (deszcz stalek i broni 75 bezpośrednio na ziemię), jednak mogły wydawać się zbyt surowe przy regularnym farmieniu dungeonów w party.

W tej iteracji wprowadziliśmy:
1. **Złagodzenie surowości bossów:**
   - **Baronówna Pająków (2092):**
     - Gwarantowane **2 skrzynie** (100% z killa + 100% z tabeli dropu) + 30% szansy na 3. skrzynię.
     - Gwarantowany **1x Kamień Duchowy (100%)** prosto na ziemię.
     - W szkatułce `50074`: podniesienie szansy na bronie 75 z 1.5% na ~2.5% per sztuka (~15% na jakąkolwiek broń 75 ze skrzyni).
     - W szkatułce `50074`: podniesienie stalek na ~2.2% per sztuka, dodanie Pereł (Biała 2.3%, Niebieska 1.7%, Krwawa 1.1%), Kamień Duchowy 2.8%, Bodziak 4.0%.
   - **Silna Lodowa Wiedźma (1192):**
     - Stalki podniesione z +2 na **+4** (zamiast +7). Gracz nie omija trudnych poziomów ulepszania (+6 -> +9), ale drop jest atrakcyjny.
     - Tarcze 61 podniesione z +3 na **+4**.
     - Szansa na KD+4 podniesiona z 5% na 7.5% per kamień (~1-2 KD+4 na wiedźmę).
     - Dodany gwarantowany **1x Kamień Duchowy (100%)** + 50% na drugi.
     - Dodana **Broszura Szermierki (70031)** z szansą 25%.
   - **Beran-Setaou / Smok (2493):**
     - Smocza Łuska & Smoczy Szpon: 1. sztuka gwarantowana 100%, 2. sztuka podniesiona z 50% na **75%**, dodana 3. sztuka z szansą **25%** (średnio 2 sztuki na run).
     - Kamień Duchowy: 1. sztuka gwarantowana 100%, 2. sztuka 50%.
     - Dodany **Magiczny Kamień (25041)** z szansą 25%.
     - Dodana **Broszura Szermierki (70031)** z szansą 50%.

2. **Gruntowny Balans Wszystkich Kamieni Metin (40 - 105):**
   - **Metiny 40 - 55 (Duszy 8008, Cienia 8009, Twardości 8010, Diabła 8011):**
     - Kamień Duchowy (50513): podniesiony z mikroskopijnych 0.025%-0.25% do **1.0% - 2.5%** (progresywnie).
     - Zwój Błogosławieństwa (25040): dodany z szansą **1.0% - 2.5%**.
   - **Metiny 60 - 70 (Upadku 8012, Śmierci 8013, Morderstwa 8014):**
     - Kamień Duchowy (50513): podniesiony do **3.0% - 5.0%**.
     - Zwój Błogosławieństwa (25040): dodany / podniesiony do **2.5% - 4.0%**.
   - **Metiny 75 - 90 (Pung-Ma 8024, Ma-An 8025, Tu-Young 8026, Jeon-Un 8027):**
     - **Kamienie Duszy (KD +3 / +4):** W standardowym silniku te metiny nie miały dropu KD. Dodano paczki `s10983` (KD+3) oraz `s10984` (KD+4):
       - Metin 75: 40% na KD+3, 15% na KD+4 (łącznie 55%).
       - Metin 80: 35% na KD+3, 25% na KD+4 (łącznie 60%).
       - Metin 85: 30% na KD+3, 40% na KD+4 (łącznie 70%).
       - Metin 90: 20% na KD+3, 50% na KD+4 (łącznie 70%).
     - Kamień Duchowy: podniesiony z 1.25%-2.5% do **6.0% - 12.5%**.
     - Zwój Błogosławieństwa: podniesiony do **6.0% - 12.5%**.
   - **Metiny 95 - 105 (Przylądek Smoczego Ognia / Mapy 95+): 8051 - 8056:**
     - Usunięto patologiczny drop gotowych broni 65 i stalek na +6 i +7.
     - Zastąpiono je wersjami **+3 / +4**.
     - Dodano **Kamień Duchowy (50513)**: 15.0% (60/400).
     - Dodano **Kamień Duszy +4 (`s10984`)**: 50.0% (200/400).
     - Wyrównano **Bodziaka (25040)** do 12.5% (50/400).

## 2. Zmodyfikowane Pliki
- `Server/linux-port/docker/game/src/serverfiles/share/locale/poland/mob_drop_item.txt`
- `Server/linux-port/docker/game/src/serverfiles/share/locale/poland/special_item_group.txt`
- Kontener `mt2dev-game`: `/opt/metin2/share/locale/poland/` oraz `/opt/m2spool/`
