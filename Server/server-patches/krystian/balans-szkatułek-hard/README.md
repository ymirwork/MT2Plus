# Balans Szkatułek pod Serwer Typu Hard oraz Poprawka Silnika C++ (Szarfy z Bossów)

## Opis Modułu
Kompleksowy pakiet rebalansu szkatułek i skrzyń (drop z bossów, mobów i eventów) dostosowujący rozgrywkę do specyfiki serwera **Hard**, naprawiający krytyczny błąd silnika C++ uniemożliwiający drop szarf z bossów oraz uzupełniający brakujące grupy konfiguracyjne.

---

### 1. Poprawka 1: Naprawa Silnika C++ dla Dropu Szarf z Bossów (`char_item.cpp`)
- **Identyfikacja problemu:**
  W silniku gry (`src/server/game/src/char_item.cpp:2405-2452`) kod odpowiedzialny za losowanie szarf tier-4 (unikalny bonusowy drop z bossów z szansą 6-10%) został umieszczony wewnątrz `case ITEM_TREASURE_KEY:` i opatrzony warunkiem:
  ```cpp
  if (GetDesc() && dwBoxVnum != 50006 && dwBoxVnum != 50007 && dwBoxVnum != 50012 && dwBoxVnum != 50013 && ...)
  ```
  Te 4 vnumy to jedyne w bazie przedmioty typu `ITEM_TREASURE_BOX` (Złota i Srebrna Szkatułka). Wszystkie szkatułki bossów w Metin2 (Wódz Orków, Umarły Rozpruwacz, Azrael itd.) to przedmioty typu `ITEM_GIFTBOX` otwierane prawym przyciskiem myszy, a nie kluczem. W rezultacie powyższy warunek był martwym kodem i szarfy z bossów **nigdy nie miały szansy wypaść**.
- **Wdrożone rozwiązanie:**
  - Utworzono pomocniczą funkcję `static bool IsBossChestVnum(DWORD dwBoxVnum)` obejmującą 22 vnumy szkatułek bossów (od klasycznych `50070-50098`, przez `50186` Azraela, `50254` Skrzynię Mroku, aż po `50266` Jotuna, `50270` Razadora, `50271` Nemere i `54701` Bagjanamu).
  - Przeniesiono mechanizm losowania szarf tier-4 (`85004`, `85008`, `85014`, `85018`, `85024`) do `case ITEM_GIFTBOX:` zaraz po pomyślnym otwarciu skrzynki (`if (bSuccess)`).
  - Usunięto martwy blok z `case ITEM_TREASURE_KEY:`.

---

### 2. Poprawka 2: Rebalans Zawartości Szkatułek pod Serwer Hard

#### A. Skrzynia Władcy Olbrzymów / Szkat. Chegala (`50098` w `special_item_group.txt`)
- **Problem:** Każda broń lv 70 (`3150, 170, 2180, 1120, 5130, 7150, 250`) miała ustawioną ilość **5 sztuk** i wagę **80**. Suma wag broni wynosiła 560 na 630 (~89% szansy na drop), co zalewało rynek pięcioma broniami lv 70 z każdego otwarcia.
- **Zmiana:** Zredukowano ilość z 5 do **1 sztuki**, a wagę z 80 do **6** (~5% na konkretną broń, łączna szansa na broń ~35%).

#### B. Spróchniała Skrzynia (`50124` w `special_item_group.txt`)
- **Problem:** Skrzynia dropiąca z mobów w Grocie Wygnańców zawierała wyłącznie pieczęcie wierzchowców IS (`71114-71120`) po **5 sztuk** przy wagach sięgających 40.
- **Zmiana:** Wprowadzono autentyczny, użyteczny drop Groty odpowiedni dla serwera Hard:
  - Małż (`27987`): 1 szt. (waga 20)
  - Nieznane Lekarstwo+ (`30091`): 1 szt. (waga 15)
  - Peleryna Męstwa (`70038`): 20 szt. (waga 15)
  - Zwój Błogosławieństwa (`25040`): 1 szt. (waga 15)
  - Fasolka Zen (`70102`): 1 szt. (waga 12)
  - Średni Kamień Metin (`71084`): 1 szt. (waga 10)
  - Rada Pustelnika (`71094`): 1 szt. (waga 5)
  - Pieczęć Dzika / Wilka / Tygrysa (żółta): 1 szt. (waga 2-3%, unikalny rzadki drop).

#### C. Skrzynia Azraela (`50186` w `special_item_group.starter.txt`)
- **Problem:** Jako grupa typu `Pct` (niezależne losowanie każdego wiersza), zawierała 4 linie mikstur dające łącznie **600 mikstur** przy 100% szansie (`200 Czerwonych S`, `100 Czerwonych D`, `200 Niebieskich S`, `100 Niebieskich D`). Dodatkowo szansa na Stal +1 wynosiła 30%, Stal +2 - 20%, a na każdą broń 70+2 - 25% (średnio 2 stalki i 1.5 broni 70 z 1 skrzyni).
- **Zmiana:**
  - Zgodnie z dyspozycją użytkownika, mikstury zostały całkowicie wycofane i zastąpione cennymi przedmiotami:
    - 30x Peleryna Męstwa (`70038`): 40% szansy
    - 2x Zwój Błogosławieństwa (`25040`): 35% szansy
    - 2x Fasolka Zen (`70102`): 35% szansy
    - 2x Zwój Egzorcyzmu (`71201`): 30% szansy
  - Bronie 70+2 (`172, 252, 1122, 2182, 3152, 7152`): zredukowano z 25% do **10%**.
  - Zbroje z Czarnej Stali +1: zredukowano z 30% do **10%**.
  - Zbroje z Czarnej Stali +2: zredukowano z 20% do **5%**.
  - Biżuteria z Niebiańskich Łez +4 / +5 / +6: zredukowano z 30/20/10% do **15/10/7%**.

#### D. Skrzynia Atlantydy (`30921` w `special_item_group.atlantyda.txt`)
- **Problem:** Nadmierne ilości ulepszaczy (5x Kamień Duchowy, 10x handlowe Zaczarowanie, 4x Wzmocnienie, 5x Bodziak) oraz 100x mikstury zapychające ekwipunek.
- **Zmiana:**
  - Kamień Duchowy (`50513`): zredukowano z 5 do **1 szt.**
  - Zaczarowanie Przedmiotu (`71284`, handlowe): zredukowano z 10 do **3 szt.**
  - Wzmocnienie Przedmiotu (`71285`, handlowe): zredukowano z 4 do **1 szt.**
  - W podgrupie zapychaczy (`950922`): 100 Czerwonych/Niebieskich Mikstur zastąpiono **20x Peleryną Męstwa** i **1x Fasolką Zen**.
  - Zwój Błogosławieństwa w zapychaczach: zredukowano z 5 do **1 szt.**

#### E. Skrzynie Okey (`special_item_group.rumi.txt`)
- **Złota Skrzynia Okey (`950403`):**
  - Zaczarowanie Przedmiotu: 5x -> **2x**
  - Wzmocnienie Przedmiotu: 3x -> **1x**
  - Zwój Błogosławieństwa: 5x -> **2x**
  - Biała i Niebieska Perła: 2x -> **1x**
  - Owoc Życia: 2x -> **1x**
- **Srebrna Skrzynia Okey (`950402`):**
  - Zaczarowanie Przedmiotu: 3x -> **1x**
  - Zwój Błogosławieństwa: 3x -> **1x**
- **Brązowa Skrzynia Okey (`950401`):**
  - Fasolka Zen: 2x -> **1x**

#### F. Uzupełnienie Brakujących Grup SIG w `special_item_group.txt`
Dodano brakujące definicje skrzynek, które wcześniej nie miały wpisów (wyświetlały "Nic nie otrzymałeś"):
- `50072` (Szkat. Odrodz. Władcy) – Odrodzony Ezoteryczny Władca / Wódz.
- `50075` (Szkat. Nosiciela Plagi) – Olbrzymi Nosiciel Plagi (Sohan / DT).
- `50080` (Szkat. Czerwonego Smoka) – Czerwony Smok (Doyyumhwan).
- `38055` (Skrzynia Szczeniaka) – Pieczęcie Khana/Boczusia, Kamień Kowala, Magiczny Metal, Egzorcyzmy, Fasolki, Peleryny.
- `71159` (Skrzynia Milona) & `71160` (Skrzynia Ateny) – Magiczny Metal, Bodziak, Kamień Duchowy, Owoc Życia, Fasolki, Peleryny.

---

### 3. Zmodyfikowane Pliki
- `Server/linux-port/docker/game/src/server/game/src/char_item.cpp`
- `Server/linux-port/docker/game/src/serverfiles/share/locale/poland/special_item_group.txt`
- `Server/linux-port/docker/game/special_item_group.starter.txt`
- `Server/linux-port/docker/game/atlantyda/special_item_group.atlantyda.txt`
- `Server/linux-port/docker/game/special_item_group.rumi.txt`
