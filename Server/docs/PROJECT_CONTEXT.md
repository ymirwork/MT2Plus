# PROJECT_CONTEXT: Metin2 Singleplayer Plus (MT2Plus)

Dokumentacja techniczna, struktura środowisk i stan projektu Metin2 opartego na repozytorium `mt2009-sp-plus`.

---

## 1. Wersjonowanie i Identyfikacja

- **Wersja serwera (`Server/VERSION`):** `2.29.1`
- **Wersja modyfikacji (`Server/MOD_VERSION`):** `mod-49`
- **Wersja klienta (`Klient/CLIENT_VERSION`):** `2.0.60`
- **Baza kodu:** Fork projektu *Metin2 Playerbots Singleplayer* (`mt2009`) autorstwa Tieru, wywodzący się z bazy MartySama r41023 (oraz wczesnych serwerfiles AzzlackSyndicate).
- **Główni autorzy rozszerzenia SP+:** ZAXEP / SIZOWSKI, Digi Rasta, Vekirion, seban latino, OskarPWA, Iwakura.

---

## 2. Podział Środowisk i Źródła Aktualizacji

### 2.1. Źródło Nadrzędne (Upstream / Oficjalny SP+)
- **Repozytorium GitHub:** `https://github.com/zaxerrrr-dot/mt2009-sp-plus`
- **Rola:** Oficjalne źródło wydań, hotfixów, manifestów (`update-manifest-mt2009.json`) oraz paczek aktualizacji serwera i klienta.

### 2.2. Środowisko Developerskie (Dev)
- **Ścieżka robocza:** `d:\Github\MT2Plus`
- **Repozytorium zdalne:** `https://github.com/ymirwork/MT2Plus.git` (gałąź `main`)
- **Docker Project Name:** `mt2dev`
- **Rola:** Izolowane środowisko programistyczne. Tutaj wprowadzane są zmiany w kodzie C++, questach i konfiguracji, przeprowadzana jest kompilacja obrazów Docker (`docker compose build`), weryfikacja poprawności oraz automatyczny commit i push do GitHub.

### 2.3. Środowisko Oficjalne / Produkcyjne (Official)
- **Ścieżka robocza:** `d:\MT2\Metin2 Singleplayer Plus`
- **Docker Project Name:** `m2pb-07befa8f` (lub właściwy z lokalnego `.m2install.json` / `.env`)
- **Rola:** Docelowa instalacja uruchomieniowa dla gry. Zawiera:
  - Oficjalny serwer w kontenerach (`Server/`).
  - Klienta gry (`Klient/`) z plikami `.data`/`.index` (oraz rozpakowanym `pack/root`).
  - Launcher Windows: `Server/Metin2-Launcher-GUI.bat` / `Server/Metin2-Launcher.bat`.
  - Stan wersji launchera zapisany w `Server/.m2launcher-state.json`.

---

## 3. Procedura Aktualizacji do Nowych Wersji Upstream

Przy każdej aktualizacji z oficjalnego repozytorium `zaxerrrr-dot/mt2009-sp-plus`:
1. **Pobranie zmian:** `git fetch upstream` w folderze Dev.
2. **Analiza różnic:** Porównanie diffa między wersjami (np. `git diff v2.29.0 v2.29.1`) z wyodrębnieniem zmienionych plików C++, skryptów, baz SQL i manifestów.
3. **Zachowanie własnych modyfikacji:**
   - **Kod C++:** Nakładanie zmian w plikach `playerbot_*` z zachowaniem naszych poprawek (np. bezpośredniego sterowania łowieniem w `playerbot_sidekick.h` czy hooków Domu Aukcyjnego w `ikarus_shop_manager.cpp` i `cmd.cpp`).
   - **Questy:** Zachowanie naszych questów w `Server/linux-port/docker/game/quest/` (`recykling_bonusow.quest`, rozszerzony `teleport_ring.quest`, `flea_market.quest`).
   - **Dockerfile:** Utrzymanie dopisanych questów w pętli kompilacji qc (`recykling_bonusow`).
   - **Katalog Addonów:** Trzymanie gotowych zipów dodatków w `Server/addons/`.
4. **Weryfikacja kompilacji:** Zbudowanie kontenerów w Dev (`docker compose build game panel seban-panel`).
5. **Aktualizacja znaczników wersji i launchera:**
   - `Server/VERSION`, `Server/MOD_VERSION`.
   - `Server/update-manifest-mt2009.json`, `Server/CHANGELOG.md`.
   - `Server/linux-port/docker/panel/app/VERSION` oraz `Server/linux-port/docker/seban-panel/VERSION`.
   - `Server/.m2launcher-state.json` (ustawienie pola `"server"` na nowy numer wersji, aby `Metin2-Launcher-GUI.bat` od razu widział zgodność bez monitów o konieczność pobierania).
6. **Synchronizacja do Oficjalnego Folderu:** Przeniesienie zaktualizowanych i zmodyfikowanych plików do `d:\MT2\Metin2 Singleplayer Plus\Server`.
7. **Automatyczny Push:** Zatwierdzenie zmian i wypchnięcie commitu na `origin/main`.

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
   - Zaawansowany panel Seban latino (Flask + Gunicorn), edytor bazy danych `dbeditor`, kompilator `m2clientpack` (EterPack/LZO/XTEA w Pythonie), Live Heatmap.
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

---

## 5. Kluczowe Własne Systemy i Modyfikacje (v2.29.1 / mod-49)

- **Świątynia Zodiaku (Zodiac Temple) & Towarzysz (v2.29.1):** Mapa 358 (`metin2_12zi_stage`), 12 portali, Kule Animy, broń/zbroje Zodiaku, instancje pięter; pełna obsługa Towarzysza (wskrzeszanie Pryzmatami Ożywienia, automatyczne czyszczenie flag Zodiaku i autowstanie po 30s).
- **System Recyklingu Bonowanego Ekwipunku:** Quest `recykling_bonusow.quest` u Dozorcy – wymiana niepotrzebnych przedmiotów z 5 bonusami na Zaczarowania i Wzmocnienia Przedmiotu. Paczka instalacyjna w `Server/addons/Paczka_Recykling_Bonusow.zip`.
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

---

## 6. Dobre Praktyki i Zasady Bezpieczeństwa

1. **Wymóg wersji MariaDB 11.8+**: Nie downgrade'ować do 10.x z powodu kolacji `utf8mb3_uca1400_ai_ci`.
2. **Tabele MyISAM**: Zawsze stosować czyste zatrzymywanie serwera (`docker compose down` lub `stop.bat`), aby uniknąć uszkodzenia indeksów.
3. **Synchronizacja bazy i klienta**: Zmiany w `world.item_proto` i `world.mob_proto` wymagają wygenerowania nowej paczki `dbdata` i wgrania jej do klienta (`Klient/pack/`).
4. **Edycja kodu C++**: Źródła serwera znajdują się w `Server/linux-port/docker/game/src/server/` oraz `Server/linux-port/overlays/playerbot/src/game/src/`. Wszelkie zmiany wymagają kompilacji w kontenerze 32-bitowym (`i386`).
5. **Automatyczny Push na GitHub**: Po każdej zmianie, pomyślnej kompilacji i poprawnym teście środowiska, gotowy fix / modyfikacja jest automatycznie commitowana i wypychana do repozytorium GitHub (`git push origin main`). Po teście serwer deweloperski jest zawsze czysto wyłączany (`docker compose down`).
6. **Katalog Addonów (`Server/addons/`)**: Wszelkie gotowe, zmodyfikowane systemy, paczki dodatków, spakowane fixy i customowe moduły przygotowywane dla serwera należy umieszczać w dedykowanym katalogu `Server/addons/`.
7. **Launcher Windows**: Przy zmianie wersji serwera zawsze aktualizować `Server/.m2launcher-state.json` oraz `Server/VERSION`, aby GUI launchera (`Metin2-Launcher-GUI.bat`) poprawnie prezentowało stan wersji.
