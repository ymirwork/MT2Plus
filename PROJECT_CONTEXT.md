# PROJECT_CONTEXT: Metin2 Singleplayer Plus (MT2Plus)

Dokumentacja techniczna, struktura środowisk i stan projektu Metin2 opartego na repozytorium `mt2009-sp-plus`.

---

## 0. Szybki System Tagów i Dyrektyw (Komunikacja z Asystentem)

Aby przyspieszyć pracę i nadać precyzyjny kontekst zapytaniom, stosuj poniższe prefiksy tagów na początku wiadomości:

| Tag | Znaczenie i Cel | Zachowanie i Rola Asystenta |
| :--- | :--- | :--- |
| **`[AKTUALIZUJ]` / `[UPSTREAM]`** | Pobranie i merge nowości z oficjalnego repozytorium `mt2009-sp-plus`. | Ścisła realizacja 5-etapowej procedury merge (Krok 1–5): analiza diffa, adaptacja na `dev`, a następnie **bezwzględne ponowne wgranie i zintegrowanie wszystkich naszych autorskich modyfikacji/addonów** z rejestru `Server/addons/` (Krok 3). Weryfikacja ewentualnych kolizji z upstreamem i bezpieczne usunięcie tylko tych addonów, które oficjalny kod sam wdrożył. |
| **`[DEV]` / `[SERVER]`** | Rozwój serwera: modyfikacje C++, questy, baza danych MariaDB, kontenery Docker. | Pełne poszanowanie reguły bezpieczeństwa (Zasada nr 12: STOP serwera + backup bazy), kompilacja i386 C++20, tworzenie paczki w `Server/addons/`, testy w `mt2dev`. |
| **`[CLIENT]` / `[PACK]`** | Prace nad klientem gry: skrypty Pythona (`root`, `uiscript`), interfejsy UI, pakowanie paczek `.data`/`.index`. | Bez zatrzymywania serwera (brak przestoju); pakowanie przez `Klient/Kompiluj-Paczki.bat` lub `Compile-ClientPack.ps1`, zachowanie kompatybilności z `dbdata`. |
| **`[BUG]` / `[FIX]`** | Zgłoszenie i diagnoza błędu lub crasha w grze. | Natychmiastowa analiza logów (`syserr`, `syslog`, `docker logs`), identyfikacja przyczyny źródłowej (*root cause*), minimalny bezpieczny patch bez psucia logiki upstreamu. |
| **`[DISCORD]`** | Przygotowanie materiałów, ogłoszeń i instrukcji dla społeczności graczy na Discordzie. | Przejście na język gracza: brak zbędnego żargonu kompilacji, zwięzły opis zmian oraz jasna instrukcja instalacji krok po kroku (patrz szablony poniżej). |
| **`[DOCS]` / `[RELEASE]`** | Aktualizacja dokumentacji, generowanie podsumowań, tworzenie wydań na GitHub (Releases) oraz Changelogu. | Przygotowanie taga wydania, archiwów `.zip`/`.rar` typu Ready-to-Play (zawierających wyłącznie pliki niezbędne do uruchomienia serwera i klienta np. dla siostry/innych graczy bez zbędnego śmietnika) oraz sformatowanego Changelogu z kropkami i podsumowaniami. |

---

### 0.1. Szybka Mapa Ścieżek i Komend (Quick Reference)

| Zasób / Zadanie | Ścieżka / Komenda | Uwagi |
| :--- | :--- | :--- |
| **Logi błędów gry (syserr)** | `Server/linux-port/docker/game/logs/syserr` | Pierwsze miejsce diagnozy crashy i błędów silnika |
| **Źródła silnika C++ gry** | `Server/linux-port/docker/game/src/server/` | Rdzeń MartySama r41023 (i386 C++20) |
| **Kod C++ Playerbots AI** | `Server/linux-port/overlays/playerbot/src/game/src/` | Moduły `playerbot_*.cpp / .h` |
| **Skrypty i interfejsy klienta** | `Klient/pack/root/` oraz `Klient/pack/uiscript/` | Rozpakowane źródła Pythona klienta |
| **Pakowanie paczek klienta** | `Klient/Kompiluj-Paczki.bat` / `Klient/Compile-ClientPack.ps1` | PackMakerLite-RS (klucz `22srh2fgh3`) |
| **Katalog paczek dodatków** | `Server/addons/` | Wewnętrzne spakowane zipy modyfikacji i fixów |
| **Kopie zapasowe bazy SQL** | `Server/backups/` | Zrzuty bazy przed zmianami w serwerze |
| **Panele administracyjne** | Tieru: `http://localhost:7788` \| Seban: `http://localhost:7790` \| IS: `http://localhost:7791` | Login / zarządzanie / gospodarka botów |

---

### 0.2. Standardowe Szablony Publikacji

#### Szablon A: Ogłoszenie / Fix na Discordzie (`[DISCORD]`)
```markdown
> 🛠️ **Poprawka błędu: [Nazwa Funkcji / Błędu]**
> 
> **Co naprawia ten fix:**
> - [Krótki i jasny opis dla gracza, co znowu działa poprawnie]
> 
> **Dlaczego funkcja wcześniej nie działała (przyczyna):**
> - [Proste wyjaśnienie problemu bez nadmiernego żargonu]
> 
> **Instrukcja instalacji:**
> 1. Pobierz załączone archiwum `.zip` / `.rar`.
> 2. Wypakuj zawartość do głównego folderu gry (zastąp istniejące pliki, jeśli zapyta).
> 3. Zrestartuj grę (lub serwer poleceniem `stop.bat` -> `start.bat`).
```

#### Szablon B: Changelog Wydania (`[DOCS]` / `[RELEASE]`)
```markdown
# 📦 MT2Plus Wydanie [Wersja, np. v2.31.0-mod51]

### [Nazwa Głównego Systemu, np. Dom Aukcyjny]
• [Główny punkt opisujący co system robi, kogo zastępuje, gdzie się znajduje]
• [Szczegółowy podpunkt z kategoriami, usprawnieniami UI, filtrami, itp.]

### [Kolejny System / Usprawnienie, np. Gospodarka Botów & Recykling]
• [Opis zachowania modułu, np. boty przetapiają nadmiar ulepszaczy na bonusy]
• [Szczegóły techniczne istotne dla balansu gry]

### 🐛 Poprawki Błędów (Fixes)
• [Punkt 1: Co naprawiono]
• [Punkt 2: Co naprawiono]

---
📥 **Instrukcja Uruchomienia (Ready-to-Play dla Każdego):**
1. Pobierz paczkę wydania `MT2Plus-Server-[wersja].zip` oraz `MT2Plus-Client-[wersja].zip`.
2. Wypakuj paczkę Serwera i uruchom `start.bat` (wymagany zainstalowany Docker Desktop).
3. Wypakuj paczkę Klienta i uruchom grę przez `metin2client.exe`.
```

---


## 1. Wersjonowanie i Identyfikacja

- **Wersja serwera (`Server/VERSION`):** `2.33.0`
- **Wersja modyfikacji (`Server/MOD_VERSION`):** `mod-54`
- **Wersja klienta (`Klient/CLIENT_VERSION`):** `2.0.64`
- **Baza kodu:** Fork projektu *Metin2 Playerbots Singleplayer* (`mt2009`) autorstwa Tieru, wywodzący się z bazy MartySama r41023 (oraz wczesnych serwerfiles AzzlackSyndicate).
- **Główni autorzy rozszerzenia SP+:** ZAXEP / SIZOWSKI, Digi Rasta, Vekirion, seban latino, OskarPWA, Iwakura.

---

## 2. Podział Środowisk i Źródła Aktualizacji

### 2.1. Źródło Nadrzędne (Upstream / Oficjalny SP+)
- **Repozytorium GitHub:** `https://github.com/zaxerrrr-dot/mt2009-sp-plus`
- **Rola:** Oficjalne źródło wydań, hotfixów, manifestów (`update-manifest-mt2009.json`) oraz paczek aktualizacji serwera i klienta.

### 2.2. Środowisko Rozwojowe (Gałąź `dev`)
- **Ścieżka robocza:** `d:\Github\MT2Plus` (gałąź `dev`)
- **Repozytorium zdalne:** `https://github.com/ymirwork/MT2Plus.git` (gałąź `dev`)
- **Docker Project Name:** `mt2dev`
- **Rola:** Poligon doświadczalny i codzienne środowisko programistyczne. Tutaj wprowadzane są zmiany w kodzie C++, questach i konfiguracji, przeprowadzana jest kompilacja obrazów Docker (`docker compose build`), weryfikacja poprawności oraz commity i pushe do gałęzi `dev`.

### 2.3. Środowisko Oficjalne / Produkcyjne (Gałąź `main`)
- **Repozytorium zdalne:** `https://github.com/ymirwork/MT2Plus.git` (gałąź `main`)
- **Środowisko Oficjalne (Gra gracza):** Gracz gra na gałęzi `main` w `d:\Github\MT2Plus` jako wersji Oficjalnej/Stabilnej.
- **Koniec z ręcznym kopiowaniem:** Zarządzanie wersjami odbywa się wyłącznie przez Git (`dev` -> `main`). Żadne pliki nie są kopiowane do zewnętrznych folderów.

---

## 3. Żelazna Procedura Cyklu Aktualizacji i Merge (5 Kroków)

Każda aktualizacja serwera i systemów MUSI ściśle realizować poniższy 5-etapowy proces decyzyjno-wdrożeniowy:

### Krok 1: Sprawdzenie zmian w Upstream (Oficjalny SP+)
1. Pobranie najnowszych referencji: `git fetch upstream` w repozytorium Dev (`d:\Github\MT2Plus`, na gałęzi `dev`).
2. Szczegółowa analiza diffa między wersją aktualną a nowym tagiem/wydaniem (np. `git diff v2.29.0 v2.29.1`):
   - Zmiany w silniku C++ (`linux-port/overlays/playerbot/...`).
   - Zmiany w questach (`linux-port/docker/game/quest/...`).
   - Zmiany w schematach i seedach bazy danych (`linux-port/docker/mariadb/playerbot/...`).
   - Zmiany w panelach www (`admin_panel.py`, panele seban/classic).
   - Zmiany w pakietach instalacyjnych i manifeście (`update-manifest-mt2009.json`, `CHANGELOG.md`).

### Krok 2: Wdrożenie zmian Upstream na Gałąź `dev` (`d:\Github\MT2Plus`)
1. Naniesienie oficjalnych zmian silnika, skryptów i paneli na gałąź `dev`.
2. Zaktualizowanie znaczników wersji:
   - `Server/VERSION` oraz `Server/MOD_VERSION`.
   - `Server/linux-port/docker/panel/app/VERSION` oraz `Server/linux-port/docker/seban-panel/VERSION`.
   - `Server/update-manifest-mt2009.json` oraz `Server/CHANGELOG.md`.

### Krok 3: Ponowne wdrożenie wszystkich naszych modyfikacji i addonów z `Server/addons/`
1. **Dynamiczne wgrywanie z Rejestru Addonów (`Server/addons/`):**
   - Po udanym naniesieniu zmian z oficjalnego repozytorium (Krok 2), asystent i deweloper **nie polegają na sztywnej liście**, lecz dynamicznie sprawdzają **Rejestr Paczek (Sekcja 5.1)** oraz zawartość folderu `Server/addons/`.
   - **Wszystkie aktywne paczki i moduły** znajdujące się w `Server/addons/` (zarówno obecne, jak i nowo dodane w przyszłości) są sekwencyjnie aplikowane na gałąź `dev`.
   - **Zasada Dodawania Nowego Modułu:** Każda nowa modyfikacja autorska tworzona w projekcie musi:
     1. Posiadać spakowane archiwum `.zip` / skrypt w `Server/addons/`.
     2. Zostać dopisana do tabeli w **Sekcji 5.1** wraz z informacją o modyfikowanych plikach i statusie `Aktywny`.
     Dzięki temu podczas kolejnego `[AKTUALIZUJ]` nowy moduł zostanie automatycznie uwzględniony i ponownie wdrożony!
2. **Bezpieczne usuwanie zaadoptowanych modyfikacji (Addon Cleanup):** Jeżeli Upstream w nowej wersji oficjalnie wprowadził identycznego fixa lub system, który dotychczas utrzymywaliśmy jako addon w `Server/addons/`, wówczas naszą paczkę/patch **bezpiecznie usuwamy z `Server/addons/`**, usuwamy wpis z Sekcji 5.1, przechodząc na oficjalne rozwiązanie z Upstream i eliminując duplikację kodu.
3. **Zasada Bezinwazyjności i Integralności:** Żadna nasza modyfikacja nie może usunąć ani zepsuć nowego kodu ani logiki wprowadzonej przez Upstream. Wszelkie nakładające się fragmenty są harmonijnie integrowane w Kroku 4.

### Krok 4: Rozwiązanie kolizji i weryfikacja w kontenerach (`dev`)
1. Jeżeli dochodzi do kolizji między naszym kodem a zmianami Upstream (np. nakładające się linie w C++, zmiany sygnatur funkcji w silniku, zmodyfikowane pętle questów):
   - **Zasada nadrzędna:** Przeprojektować i zrefaktoryzować nasz kod tak, aby **w 100% zachować oficjalną funkcjonalność z Upstream**, przy jednoczesnym **pełnym działaniu naszych modyfikacji**.
2. Weryfikacja integralności w Dockerze na `dev`:
   - Przebudowa kontenerów: `docker compose build game panel seban-panel`.
   - Sprawdzenie kompilacji kodu C++20 (i386) oraz kompilatora questów `qc` – zero błędów.
   - Po teście czyste wygaszenie kontenerów: `docker compose down`.

### Krok 5: Publikacja na GitHub (`dev`) i Merge do `main` (Oficjalny Release)
Dopiero po pomyślnym przejściu Kroków 1–4:
1. **Zatwierdzenie na gałęzi `dev`:**
   - Commit przetestowanych zmian z czytelnym opisem konwencji Conventional Commits.
   - Wypchnięcie zmian: `git push origin dev`.
2. **Scalenie do gałęzi `main` (Release):**
   - Przełączenie na gałąź `main`: `git checkout main`.
   - Scalenie zmian: `git merge dev`.
   - Wypchnięcie oficjalnej wersji: `git push origin main`.
   - Powrót do gałęzi roboczej: `git checkout dev`.
   - Opcjonalnie: Utworzenie taga wydania na GitHub (np. `v2.30.0-mod50`).
3. **Paczki klienta:**
   - W przypadku modyfikacji plików klienta (`pack/root` itp.): skompilowanie nowej paczki za pomocą `Kompiluj-Paczki.bat` / `Compile-ClientPack.ps1` i wygenerowanie archiwum wydania dla graczy.

---

## 4. Architektura Systemu

### 4.1. Warstwa Serwera (Linux / Docker)
Wszystkie usługi backendowe pracują w kontenerach Docker w sieci mostkowej (`backend`):
1. **`game`**:
   - Rdzeń C++20 kompilowany pod architekturę `i386` (Ubuntu 24.04 i386 rootfs).
   - Silnik: MartySama r41023 ze zintegrowanym systemem Playerbot (`PLAYERBOT_ENGINE_MT2009`).
   - Supervisor: `m2-supervise` zarządzający procesami `db` (port 15000), `auth` (port 11000) oraz rdzeniami kanałów CH1–CH4 (`13000-13032`).
   - Tryb map: domyślnie `unified` (`MAP_ALLOW_LIMIT = 48` na rdzeniu `game1`).
2. **`mariadb`**:
   - Wersja: `MariaDB 11.8` (wymóg kolacji `utf8mb3_uca1400_ai_ci`).
   - Port wewnętrzny/bindowany: `127.0.0.1:3306`.
   - Schematy baz danych: `account`, `common`, `player`, `world`, `log`, `hotbackup`, `itemshop`.
   - Proto: ładowane z bazy SQL (`PROTO_FROM_DB = 1`).
3. **`playerbot-migrate`**:
   - Kontener zadaniowy uruchamiający skrypt `apply.sh` przed startem silnika gry.
   - Odpowiada za migracje schematów tabel, seeding botów (350 botów, polskie nicki, system dropek/farmer link) i weryfikację sum SHA256.
4. **`panel` (Port 7788)**:
   - Tieru Classic Admin Panel w Pythonie 3.12 (Flask + Waitress).
5. **`seban-panel` (Port 7790)**:
   - Zaawansowany panel Seban latino (Flask + Gunicorn), edytor bazy danych `dbeditor`, kompilator `m2clientpack` (EterPack/LZO/XTEA w Pythonie), Live Heatmap oraz rozszerzone Centrum Gospodarki i Obiegu Dóbr:
     - **Wskaźnik Inflacji:** `WorldYangFactor` (wzór silnika C++ z `playerbot_town.h`), całkowita masa Yang, średnia zamożność, podaż Zaczarowań/Wzmocnień.
     - **Bilans Walutowy (Faucet vs Sink · 24h):** Dobowy bilans kreacji waluty (drop mobów, drop ziemi, sprzedaż NPC) vs niszczenia (Kowal, podatki offline shopów `TAX`). Wskaźniki Net Delta oraz Net Burn Rate, zasilenie rynku z zakupów botów.
     - **Wycena Rynkowa i Płynność (`/economy/item/<vnum>`):** Cena Godziwa (Fair Value / Mediana), rozstęp cen (Spread %) oraz dobowy wolumen transakcji i odznaka płynności (Bardzo Wysoka, Umiarkowana, Niska, Zastój).
     - **Eksport Danych:** Eksport zestawień przedmiotów w obiegu do `.csv` oraz `.json`.
     - **Raporty Discord:** Wysyłanie dobowych raportów embed na skonfigurowany Webhook Discorda.
     - **Telemetria Modułu YmirWork (Krystian):** Statystyki przetapiania ulepszaczy M1/M2 i skupu ofert przez boty z pełnym graceful fallback.
6. **`seban-collector` & `seban-item-grants`**:
   - Demony tła odpowiedzialne za telemetrię, ogłoszenia ulepszeń +9 i transakcyjne nadawanie przedmiotów.
7. **`itemshop` (Port 7791)**:
   - Sklep www (PHP 8.2 + Apache) autorstwa OskarPWA, zintegrowany z SAS token w kliencie i tabelą `player.item_award`.
8. **`updater`**:
   - Demon aktualizacji orkiestrujący pobieranie manifestu i przebudowę kontenerów.

### 4.2. Warstwa Klienta (Windows)
- Plik wykonywalny: `metin2client.exe` (binarny, brak źródeł C++ w tym repozytorium).
- Patcher: `MT2009-Patcher.exe` (.NET 4.7.2).
- Paczki: format EterPack (`.data` / `.index`), spakowane narzędziem PackMakerLite (klucz `22srh2fgh3`) lub przez `m2clientpack` w panelu Seban.
- Konfiguracja połączenia: pliki `channel.inf` oraz `coop.cfg`.
- **Kompilacja i Pakowanie Klienta:**
  - Skrypt wsadowy: [`Klient/Kompiluj-Paczki.bat`](file:///d:/Github/MT2Plus/Klient/Kompiluj-Paczki.bat) (menu interaktywne).
  - Skrypt PowerShell: [`Klient/Compile-ClientPack.ps1`](file:///d:/Github/MT2Plus/Klient/Compile-ClientPack.ps1) / [`Server/tools/Compile-ClientPack.ps1`](file:///d:/Github/MT2Plus/Server/tools/Compile-ClientPack.ps1).
  - Silnik pakerów: `PackMakerLite-RS` (`packmakerlite-cli.exe` z konfiguracją `PackMakerLite.json`).
  - Funkcjonalności: szybkie pakowanie wybranej paczki (np. `root`), masowe pakowanie rozpakowanych folderów (`pack-all`), rozpakowywanie (`unpack`), tryb autokompilacji przy zapisie plików (`watch`), automatyczne tworzenie kopii zapasowej `.bak` oraz synchronizacja gotowych plików `.data`/`.index` między folderem Dev i Oficjalnym.

---

## 5. Kluczowe Własne Systemy i Modyfikacje (v2.30.0 / mod-50)

- **Szybkie Podnoszenie Przedmiotów (Fast Area Pickup):** Natychmiastowe zbieranie dropu w promieniu postaci pod klawiszem `Z` / `~` (`/pickup_nearby` wywoływane w pierwszej klatce naciśnięcia, interwał przytrzymania skrócony do 150 ms, cooldown po stronie serwera w `char_item.cpp` zredukowany do 100 ms).
- **Szybkie Ulepszanie (Fast Refine without Animation Lock):** Usunięte blokujące wyskakujące okienka dialogowe sukcesu/porażki z `game.py` i `digiserverqol.py` (przekierowane na czytelne komunikaty na czacie), natychmiastowe zatwierdzanie klawiszem Enter i wysoka responsywność u kowala.
- **Pełne Zdrowie po Odrodzeniu (100% HP Revive):** Po śmierci postaci i wybraniu opcji odrodzenia w mieście (`SCMD_RESTART_TOWN`) lub w miejscu zgonu (`SCMD_RESTART_HERE`), a także po wznowieniu gry z ekranu wyboru postaci, postać odradza się natychmiast z pełnym 100% paskiem HP (`ch->GetMaxHP() - ch->GetHP()`), eliminując mozolne leczenie z 50 HP.
- **Szybkie Zbieranie w Autołowach (Fast Area Pickup in Auto Hunt):** Moduł Autołowów (`uiautohunt.py`) podczas zbierania dropu z ziemi korzysta natychmiastowo z mechanizmu szybkiego zbierania obszarowego (`/pickup_nearby`) zamiast powolnego pojedynczego podnoszenia każdego przedmiotu z osobna.
- **Skrócony Czas Oczekiwania po Zamknięciu Okien (3s Portal/Safebox/Trade/Logout Cooldown):** Zredukowany z 10 sekund do 3 sekund (`g_nPortalLimitTime = 3` w `char_item.cpp`, `cmd_general.cpp`, `char.cpp`, `ikarus_shop_manager.cpp`) po zamknięciu handlu, magazynu (IS i zwykłego) lub tobołka/sklepu przed przejściem przez portal, wylogowaniem czy zmianą postaci. Usunięto mylący komunikat o magazynie przy zamykaniu tobołka na rzecz prawidłowego komunikatu o handlu.
- **Moduł YmirWork (Krystian) – Płynne Upłynnianie Ulepszaczy M1/M2(+) i Dynamiczny Balans Rynku (MODUŁ YMIRWORK (KRYSTIAN) V2 AKTYWNY):** Wewnętrzny mechanizm symulacji gospodarki botów w `playerbot_bonus.h` / `playerbot_market.h` / `playerbot_types.h`:
  - Przetapianie nadmiaru ulepszaczy M1/M2 oraz wszystkich materiałów z plusem (+) na handlowalne Zaczarowania (`71284`) i Wzmocnienia (`71285`).
  - **Płynne progi wymaganych sztuk ulepszaczy:** Baza wynosi 50 szt. (pospolite) / 25 szt. (rzadkie/z plusem), z automatyczną zniżką hurtową u Kolekcjonera w przypadku powodzi rynkowej aż do 25 szt. (pospolite) / 12 szt. (rzadkie) + opłata Yang skalowana inflacją (`ScalePlayerBotIwakuraPrice`).
  - **Płynny wskaźnik skupu botów (1% – 35%):** Zamiast sztywnego 15%, odsetek botów skupujących towary z tobołków gracza i rynku skaluje się dynamicznie na podstawie aktualnej podaży ulepszaczy w sklepach (od 3% przy niskiej podaży do 35% przy powodzi towarowej).
  - Priorytet zużycia na własne uzbrojenie bota (do 4–5 bonusów i rollowanie statystyk), a nadwyżki wystawiane w tobołkach (maks. 20% sklepów na rynku, do 3 slotów na sklep).
  - **Telemetria w panelu Seban:** Dynamiczne śledzenie mnożnika inflacji, aktualnego wskaźnika skupu botów (płynne %), zliczonej podaży ulepszaczy oraz historii przetopień.
  - *Uwaga:* Emerytury botów pozostają domyślnie wyłączone do późniejszej konfiguracji przez operatora.
- **Świątynia Zodiaku (Zodiac Temple) & Towarzysz (v2.29.1):** Mapa 358 (`metin2_12zi_stage`), 12 portali, Kule Animy, broń/zbroje Zodiaku, instancje pięter; pełna obsługa Towarzysza (wskrzeszanie Pryzmatami Ożywienia, automatyczne czyszczenie flag Zodiaku i autowstanie po 30s).
- **System Recyklingu Bonowanego Ekwipunku:** Quest `recykling_bonusow.quest` u Dozorcy – wymiana niepotrzebnych przedmiotów z 5 bonusami na Zaczarowania i Wzmocnienia Przedmiotu dla gracza. Paczka instalacyjna w `Server/addons/Paczka_Recykling_Bonusow.zip`.
- **Sklep Offline 160 Pól (Odblokowanie Kluczami):** Dwa bloki sklepu offline (po 80 pól każdy, łącznie 160 pól). Pierwszy blok zachowuje 40 pól darmowych, 20 za klucze (po 1 Drewnianym Kluczu `30376` na 5 pól) oraz 20 pól premium. Drugi blok 80 pól odblokowywany jest krokami po 5 pól za 2 Drewniane Klucze (`shop_unlock_slots.quest`). Przy tworzeniu sklepu obowiązuje limit do 80 przedmiotów naraz; kolejne sloty uzupełnia się w otwartym sklepie. Zmiany silnikowe w `char_shop.cpp` i `ikarus_shop_manager.cpp`, interfejs w `dualshop.py`, `offlineshopui.py`, `offlineshopbuilder.py` i `offlineshopmanage.py`. Paczka w `Server/addons/MT2009-PLUS-SKLEP-160-SLOTOW-KLUCZE-2.30.0.zip`.
- **Naprawa Łowienia Towarzysza:** Bezpośrednie sterowanie pętlą wędkowania w trybie "Na ryby" (`playerbot_sidekick.h`), zapobiegające porzucaniu łowienia przez bota.
- **Dom Aukcyjny (AH_V1, Autor: Vekirion):** Wyszukiwarka i zakupy ofert ze sklepów offline (Ikarus) bez nowych pakietów binarnych, komendy `/ah_*` w `auction_house.cpp`, hooki transakcyjne w `ikarus_shop_manager.cpp` i `cmd.cpp`, quest `flea_market.quest` oraz interfejs klienta `uiauctionhouse.py`.
- **Rozszerzony Pierścień Teleportacji:** Quest `teleport_ring.quest` ze skrótami do lochów (Loch Pająków V1, Trudny/Normalny/Łatwy Loch Małp) oraz map Arezzo (360 Dolina Cyklopów, 361 Pustkowie Faraona).
- **Ruiny Atlantydy (Ruins of Atlantis):** Mapa 158, dungeon grupowy/solo od poziomu 75+.
- **Moduł Arezzo:** Nowe mapy exp (360-362) i dungeony (363-366).
- **Playerbots AI:** Ponad 18 000 linii kodu C++ wbudowane w `game/src/` (`playerbot_manager.cpp`, `playerbot_types.h`), obsługa dungeonów, tobołków offline, farming linków, walki i zrzutek na ziemie gildii.
- **System Szarf, Talizmanów i Kostiumów Broni:** Ulepszanie talizmanów +0..+200, szarfy z absorpcją.
- **Alchemia Smoczych Kamieni (Dragon Soul):** Mityczna alchemia, pełny obieg uszlachetniania.
- **Auto Hunting (Klawisz K):** Zautomatyzowane expienie dla gracza.
- **Szybkie ulepszanie (Enter-refine) & TAB Minimap Warp.**

### 5.1. Rejestr Paczek i Modułów w `Server/addons/`

Poniższa tabela stanowi bieżący stan modułów w `Server/addons/`. Zgodnie z **Zasadą nr 8**, jeśli dany fix/mod zostanie oficjalnie dodany w Upstream, jego paczka jest bezpiecznie usuwana.

| Nazwa Pliku / Archiwum | Typ / Zawartość | Pliki i Obszary Modyfikacji | Status |
| :--- | :--- | :--- | :--- |
| `Szybkie_Zbieranie_Autolowy.zip` | Klient (Python) | `Klient/pack/root/uiautohunt.py` (obszarowe podnoszenie dropu) | **Aktywny** |
| `Ukrycie_Wartosci_HP_Celu.zip` | Klient (Python) | `Klient/pack/root/uitarget.py` (usunięcie cyfrowego HP innych graczy/mobów) | **Aktywny** |
| `Wstawanie_100_Procent_HP.zip` | Serwer (C++) | `game/src/cmd_general.cpp`, `char.cpp` (100% HP po ożywieniu) | **Aktywny** |
| `Fix_Boty_Gildia_Exp_Party.zip` | Serwer (C++) | `playerbot_manager.cpp`, `char.cpp` (zrzutki botów na ziemie gildii, party exp) | **Włączony w Upstream 2.32.0** |
| `Seban_Panel_Rozszerzona_Ekonomia_V2.zip` | Web / Panel Seban | `Server/linux-port/overlays/seban-panel/` -> `docker/seban-panel/` (Centrum Gospodarki, YmirWork telemetria, interpretacja inflacji, bilans emerytur botów, zachowywane automatycznie po aktualizacjach z upstream) | **Aktywny (Auto-Overlay)** |
| `MT2009-PLUS-SKLEP-160-SLOTOW-KLUCZE-2.30.0.zip` | Serwer + Klient | `char_shop.cpp`, `ikarus_shop_manager.cpp`, `dualshop.py`, `offlineshopui.py` | **Aktywny** |
| `Paczka_Recykling_Bonusow.zip` | Serwer (Quest/C++) | `recykling_bonusow.quest`, Dozorca, wymiana 5b na dodania/zmianki | **Aktywny** |
| `teleport_ring.quest` | Serwer (Quest) | Quest z dodatkowymi lochami i mapami Arezzo | **Aktywny** |

---

## 6. Dobre Praktyki i Zasady Bezpieczeństwa

1. **Zasada Nienaruszalności Bazy Danych i Postaci Gracza (Zero-Data-Loss):**
   - Aktualizacje serwera i kompilacje silnika C++ **nigdy nie mogą modyfikować ani usuwać wolumenów bazy danych (`db-data`)**, tabel graczy (`player.player`, `player.item`, `account.account`) ani stanu ekwipunku/postaci.
   - Wszelkie migracje schematów SQL (z Upstream lub z naszych modyfikacji) muszą być ściśle **addytywne** (`CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ... ADD COLUMN ... IF NOT EXISTS`) i w 100% bezstratne dla istniejącego świata gry.

2. **Zasada Złotego Trójkąta Spójności Proto (Baza SQL ↔ Serwer ↔ Klient):**
   - Silnik ładuje definicje proto z bazy SQL (`PROTO_FROM_DB = 1`).
   - Każda zmiana w `world.item_proto` lub `world.mob_proto` (nowe bronie, zbroje, bonusy, ulepszenia) bezwzględnie wymaga wygenerowania zaktualizowanej paczki klienta `dbdata` (przez edytor bazy w panelu Seban lub `dbdata.py`) i jej rekompilacji do `Klient/pack/`.
   - Zapobiega to desynchronizacji opisów, błędnym ikonom i crashom klienta gry.

3. **Zasada Atomowej Izolacji Gałęzi (`dev` vs `main`):**
   - **Gałąź `dev` (`MT2Plus`):** Poligon doświadczalny, edycja kodu C++, tworzenie questów, kompilacje kontenerów (`mt2dev`) oraz wersjonowanie robocze.
   - **Gałąź `main`:** Oficjalna wersja produkcyjna / docelowa (Ready-to-Play). Trafia do niej wyłącznie kod i paczki w 100% przetestowane, skompilowane i zweryfikowane poprzez kontrolowany merge z `dev`.
   - **Eliminacja ręcznej synchronizacji:** Zarządzanie spójnością kodu odbywa się bezpośrednio przez mechanizmy Git, eliminując zawodne ręczne kopiowanie plików między folderami.

4. **Zasada Weryfikacji Czystego Stanu Git (Clean Tree Guard):**
   - Przed przystąpieniem do jakiejkolwiek aktualizacji z Upstream stan repozytorium na gałęzi `dev` musi być czysty (`git status`).
   - Po każdej udanej zmianie, pomyślnej kompilacji i teście, gotowe zmiany są commitowane i wypychane na gałąź zdalną `dev` (`git push origin dev`). Po decyzji o wydaniu nowej wersji oficjalnej następuje merge do `main` (`git checkout main && git merge dev && git push origin main`), a serwer deweloperski czysto wyłączany (`docker compose down`).

5. **Wymóg wersji MariaDB 11.8+:** Nie wolno dokonywać downgrade'u do MariaDB 10.x z powodu twardego wymogu kolacji `utf8mb3_uca1400_ai_ci`.
6. **Tabele MyISAM i czyste zatrzymywanie:** Zawsze stosować czyste zatrzymywanie usług (`docker compose down` lub `stop.bat`), aby chronić tabele MyISAM przed uszkodzeniem indeksów.
7. **Edycja kodu C++ (i386):** Źródła serwera znajdują się w `Server/linux-port/docker/game/src/server/` oraz `Server/linux-port/overlays/playerbot/src/game/src/`. Wszelkie modyfikacje wymagają poprawnej kompilacji w kontenerze 32-bitowym (`i386`).
8. **Katalog Addonów (`Server/addons/`) i Zasada Cyklu Życia Dodatków:** Wszystkie gotowe paczki dodatków, spakowane fixy i moduły przygotowywane dla serwera należy umieszczać w dedykowanym katalogu `Server/addons/`. Jeżeli w nowym wydaniu Upstream oficjalnie wprowadził fixa lub funkcjonalność, którą wcześniej realizowaliśmy jako addon, dany dodatek można **bezpiecznie usunąć z `Server/addons/`**, przechodząc w pełni na oficjalny kod bazowy.
9. **Synchronizacja Stanu Launchera Windows:** Przy każdej zmianie wersji serwera należy zaktualizować zarówno `Server/VERSION`, jak i plik `Server/.m2launcher-state.json`, aby GUI launchera (`Metin2-Launcher-GUI.bat`) natychmiast odczytywało aktualny stan wersji.
10. **Raportowanie Poprawek z Discorda (Standard Opisu Błędów i Instalacji):**
    - W przypadku naprawy błędu pochodzącego ze zgłoszeń społeczności Discord (gdy użytkownik wskaże, że problem pochodzi z Discorda), asystent po wdrożeniu fixa bezwzględnie generuje zwięzły opis w formacie Markdown dla graczy na Discordzie zawierający:
      1. **Co dokładnie naprawia ten fix**
      2. **Dlaczego funkcja wcześniej nie działała (przyczyna techniczna / root cause)**
      3. **Krótki opis jak zainstalować** (proste, precyzyjne kroki dla graczy pobierających udostępniony plik `.zip` / `.rar`; pamiętać, że `Server/addons/` to wyłącznie nasz wewnętrzny katalog projektowy, a społeczność na Discordzie otrzymuje bezpośrednią paczkę archiwum).
    - Wzorzec formatu:
      > **Opis poprawki:**
      > - Naprawia błąd w silniku (`char.cpp`), gdzie funkcja powrotu po wojnie przekazywała zerowe koordynaty (`m_posWarp`) zamiast zapamiętanych (`m_posExit`), przez co gracze zostawali uwięzieni na zamykanej instancji mapy.
      >
      > **Instrukcja instalacji:**
      > 1. Pobierz załączone archiwum `.zip` / `.rar`.
      > 2. Wypakuj zawartość do głównego folderu gry / serwera (zastąp istniejące pliki).
      > 3. Zrestartuj serwer (`stop.bat` -> `start.bat`) lub uruchom ponownie klienta gry.

11. **Niezawodność Poleceń Terminala i Synchronizacji (Zero-Hang Execution Guard):**
    - Przy wywoływaniu operacji terminala Windows / PowerShell:
      - **Kopiowanie i synchronizacja:** Bezwzględnie preferować sprawdzone polecenia natywne `robocopy <src> <dst> [pliki] /E /NFL /NDL /NJH /NJS` (kod wyjścia 1 = sukces) lub jednoznaczne cmdlety PowerShell `Copy-Item -Path ... -Destination ... -Force` bez wieloliniowych skomplikowanych pętli i bez używania niesprawdzonych konstrukcji potoków/cudzysłowów narażonych na zacinanie.
      - **Śledzenie zadań w tle (Task Watchdog):** Jeżeli zadanie uruchomione asynchronicznie (np. robocopy, git, powershell) nie zgłosi zakończenia w ciągu spodziewanego czasu (maksymalnie 15–30 sekund dla operacji plikowych), natychmiast sprawdzić jego log (`manage_task action='status'`), zamiast biernie czekać. W przypadku błędu składniowego lub zawieszenia natychmiast anulować proces (`manage_task action='kill'`) i dokończyć operację niezawodną metodą synchroniczną.

12. **Żelazna Zasada Weryfikacji Serwera i Spójności Bazy (Server Change Shutdown & Safe Backup Rule):**
    - **Rozróżnienie typu wprowadzanych zmian:**
      - **A. ZMIANY PO STRONIE SERWERA (Kod C++, baza MariaDB, pliki konfiguracyjne, tabele, migracje, questy i pliki montowane w kontenerach):**
        - **Zasada nadrzędna:** W przypadku jakichkolwiek modyfikacji serwerowych **ZAWSZE bezwzględnie zatrzymaj serwer i wykonaj kopię zapasową przed wprowadzeniem zmian**. Silnik Metin2 agresywnie buforuje dane w pamięci RAM (`db cache`), a MariaDB trzyma blokady transakcyjne – wprowadzanie zmian lub robienie backupu na działającym serwerze grozi nadpisaniem danych starym stanem z RAM przy wyłączeniu lub uszkodzeniem tabel InnoDB.
        - **Ścisła 4-etapowa procedura zmian serwerowych:**
          1. **Weryfikacja i bezpieczne zatrzymanie:** Sprawdź stan (`docker ps`). Jeżeli serwer działa, zatrzymaj go czysto i bezpiecznie (np. `.\Metin2-Launcher.ps1 -Action Stop` lub `docker compose stop`), pozwalając procesom `m2-supervise` i MariaDB na kompletny zrzut (flush) buforów pamięci na dysk.
          2. **Automatyczny backup bazy (Zero-Data-Loss):** Wykonaj pełną kopię zapasową bazy danych do katalogu `Server/backups/` (używając akcji launchera `BackupDb` lub procedury tworzenia zrzutu `.zip`).
          3. **Aplikacja zmian:** Wprowadź zaplanowane modyfikacje kodu, schematów SQL, konfiguracji lub plików dodatków.
          4. **Uruchomienie i weryfikacja:** Uruchom serwer ponownie (`docker compose up -d`) i zweryfikuj brak błędów w logach `docker logs` oraz `syserr` rdzeni (`all cores up`).
      - **B. ZMIANY PO STRONIE KLIENTA / DOKUMENTACJI (Skrypty Pythona klienta, pakowanie paczek w `Klient/pack/`, edycja `PROJECT_CONTEXT.md`, narzędzia w `Server/tools/`):**
        - **Brak przestojów:** Ponieważ te operacje w ogóle nie ingerują w procesy ani wolumeny bazy danych serwera, **serwera NIE trzeba wyłączać** – może bezpiecznie działać w tle, oszczędzając czas.
