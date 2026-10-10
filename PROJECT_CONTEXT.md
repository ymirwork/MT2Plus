# PROJECT_CONTEXT: Metin2 Singleplayer Plus (MT2Plus)

Dokumentacja techniczna i stan projektu Metin2 opartego na repozytorium `mt2009-sp-plus`.

---

## 1. Wersjonowanie i Identyfikacja

- **Wersja serwera (`Server/VERSION`):** `2.29.1`
- **Wersja modyfikacji (`Server/MOD_VERSION`):** `mod-49`
- **Wersja klienta (`Klient/CLIENT_VERSION`):** `2.0.60`
- **Baza kodu:** Fork projektu *Metin2 Playerbots Singleplayer* (`mt2009`) autorstwa Tieru, wywodzący się z bazy MartySama r41023 (oraz wczesnych serwerfiles AzzlackSyndicate).
- **Główni autorzy rozszerzenia SP+:** ZAXEP / SIZOWSKI, Digi Rasta, Vekirion, seban latino, OskarPWA, Iwakura.

---

## 2. Architektura Systemu

### 2.1. Warstwa Serwera (Linux / Docker)
Wszystkie usługi backendowe pracują w kontenerach Docker w sieci mostkowej (`backend`):
1. **`game`**:
   - Rdzeń C++20 kompilowany pod architekturę `i386` (Ubuntu 24.04 i386 rootfs).
   - Silnik: MartySama r41023 ze zintegrowanym systemem Playerbot (`PLAYERBOT_ENGINE_MT2009`).
   - Supervisor: [`m2-supervise`](file:///d:/Github/MT2Plus/Server/linux-port/docker/game/bin/m2-supervise) zarządzający procesami `db` (port 15000), `auth` (port 11000) oraz rdzeniami kanałów CH1–CH4 (`13000-13032`).
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

### 2.2. Warstwa Klienta (Windows)
- Plik wykonywalny: `metin2client.exe` (binarny, brak źródeł C++ w tym repozytorium).
- Patcher: `MT2009-Patcher.exe` (.NET 4.7.2).
- Paczki: format EterPack (`.data` / `.index`), spakowane narzędziem PackMakerLite (klucz `22srh2fgh3`) lub przez `m2clientpack` w panelu Seban.
- Konfiguracja połączenia: pliki `channel.inf` oraz `coop.cfg`.

---

## 3. Kluczowe Własne Systemy i Modyfikacje (v2.29.1 / mod-49)

- **Świątynia Zodiaku (Zodiac Temple) & Towarzysz (v2.29.1):** Mapa 358 (`metin2_12zi_stage`), 12 portali, Kule Animy, broń/zbroje Zodiaku, instancje pięter; pełna obsługa Towarzysza (wskrzeszanie Pryzmatami Ożywienia, automatyczne czyszczenie flag Zodiaku i autowstanie po 30s).
- **System Recyklingu Bonowanego Ekwipunku:** Quest `recykling_bonusow.quest` u Dozorcy – wymiana niepotrzebnych przedmiotów z 5 bonusami na Zaczarowania i Wzmocnienia Przedmiotu.
- **Naprawa Łowienia Towarzysza:** Bezpośrednie sterowanie pętlą wędkowania w trybie "Na ryby", zapobiegające porzucaniu łowienia.
- **Ruiny Atlantydy (Ruins of Atlantis):** Mapa 158, dungeon grupowy/solo od poziomu 75+.
- **Moduł Arezzo:** Nowe mapy exp (360-362) i dungeony (363-366).
- **Playerbots AI:** Ponad 18 000 linii kodu C++ wbudowane w `game/src/` (`playerbot_manager.cpp`, `playerbot_types.h`), obsługa dungeonów, tobołków offline, farming linków, walki i zrzutek na ziemie gildii.
- **System Szarf, Talizmanów i Kostiumów Broni:** Ulepszanie talizmanów +0..+200, szarfy z absorpcją.
- **Alchemia Smoczych Kamieni (Dragon Soul):** Mityczna alchemia, pełny obieg uszlachetniania.
- **Auto Hunting (Klawisz K):** Zautomatyzowane expienie dla gracza.
- **Szybkie ulepszanie (Enter-refine) & TAB Minimap Warp.**

---

## 4. Narzędzia i Skrypty Zarządzające

- `Server/start-server.ps1` – uruchamianie środowiska lokalnego z preflight checkami i trwałym zapisem `.env`.
- `Server/Metin2-Launcher.ps1` / `Metin2-Launcher-GUI.bat` – launcher Windows z ponad 40 akcjami (backup, reset świata, tuning botów, COOP).
- `Server/linux-port/tools/vps-install.sh` – automatyczna instalacja na dedykowanym serwerze Linux.
- `Server/tools/New-M2UpdatePackage.ps1` – pakowanie oficjalnych wydań modyfikacji.

---

## 5. Dobre Praktyki i Zasady Bezpieczeństwa

1. **Wymóg wersji MariaDB 11.8+**: Nie downgrade'ować do 10.x z powodu kolacji `utf8mb3_uca1400_ai_ci`.
2. **Tabele MyISAM**: Zawsze stosować czyste zatrzymywanie serwera (`docker compose down` lub `stop.bat`), aby uniknąć uszkodzenia indeksów.
3. **Synchronizacja bazy i klienta**: Zmiany w `world.item_proto` i `world.mob_proto` wymagają wygenerowania nowej paczki `dbdata` i wgrania jej do klienta (`Klient/pack/`).
4. **Edycja kodu C++**: Źródła serwera znajdują się w `Server/linux-port/docker/game/src/server/`. Wszelkie zmiany wymagają kompilacji w kontenerze 32-bitowym (`i386`).
5. **Automatyczny Push na GitHub**: Po każdej zmianie, pomyślnej kompilacji i poprawnym teście środowiska, gotowy fix / modyfikacja jest automatycznie commitowana i wypychana do repozytorium GitHub (`git push origin main`). Po teście serwer deweloperski jest zawsze czysto wyłączany (`docker compose down`).
6. **Katalog Addonów (`Server/addons/`)**: Wszelkie gotowe, zmodyfikowane systemy, paczki dodatków, spakowane fixy i customowe moduły przygotowywane dla serwera należy umieszczać w dedykowanym katalogu `Server/addons/`.

