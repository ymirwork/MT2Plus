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

## 3. Żelazna Procedura Cyklu Aktualizacji (5 Kroków)

Każda aktualizacja serwera i systemów MUSI ściśle realizować poniższy 5-etapowy proces decyzyjno-wdrożeniowy:

### Krok 1: Sprawdzenie zmian w Upstream (Oficjalny SP+)
1. Pobranie najnowszych referencji: `git fetch upstream` w repozytorium Dev (`d:\Github\MT2Plus`).
2. Szczegółowa analiza diffa między wersją aktualną a nowym tagiem/wydaniem (np. `git diff v2.29.0 v2.29.1`):
   - Zmiany w silniku C++ (`linux-port/overlays/playerbot/...`).
   - Zmiany w questach (`linux-port/docker/game/quest/...`).
   - Zmiany w schematach i seedach bazy danych (`linux-port/docker/mariadb/playerbot/...`).
   - Zmiany w panelach www (`admin_panel.py`, panele seban/classic).
   - Zmiany w pakietach instalacyjnych i manifeście (`update-manifest-mt2009.json`, `CHANGELOG.md`).

### Krok 2: Wdrożenie zmian Upstream na Dev (`d:\Github\MT2Plus`)
1. Naniesienie oficjalnych zmian silnika, skryptów i paneli na drzewo deweloperskie.
2. Zaktualizowanie znaczników wersji:
   - `Server/VERSION` oraz `Server/MOD_VERSION`.
   - `Server/linux-port/docker/panel/app/VERSION` oraz `Server/linux-port/docker/seban-panel/VERSION`.
   - `Server/update-manifest-mt2009.json` oraz `Server/CHANGELOG.md`.

### Krok 3: Dodanie naszych modyfikacji z `Server/addons/` (bezinwazyjnie dla Upstream)
1. Zaaplikowanie naszych autorskich systemów i modułów umieszczonych w `Server/addons/` oraz własnych komponentów:
   - System recyklingu bonów u Dozorcy (`recykling_bonusow.quest`, rejestracja w `Dockerfile`, paczka w `Server/addons/`).
   - Naprawa pętli wędkowania towarzysza (`playerbot_sidekick.h` – bezpośrednie sterowanie `rt.bFishing`).
   - Rozszerzony Pierścień Teleportacji (`teleport_ring.quest` – lochy, miasta).
   - Dom Aukcyjny / AH_V1 (`auction_house.cpp`, `cmd.cpp`, `ikarus_shop_manager.cpp`, `flea_market.quest`).
2. **Bezpieczne usuwanie zaadoptowanych modyfikacji (Addon Cleanup):** Jeżeli Upstream oficjalnie wprowadził fixa lub system, który dotychczas utrzymywaliśmy jako naszą modyfikację w `Server/addons/`, wówczas naszą paczkę/patch **bezpiecznie usuwamy z `Server/addons/`**, przechodząc na oficjalne rozwiązanie z Upstream i eliminując duplikację kodu.
3. Bezwzględny warunek: implementacja musi być bezinwazyjna – żadna nasza modyfikacja nie może usunąć ani zepsuć nowego kodu ani logiki wprowadzonej przez Upstream.

### Krok 4: Rozwiązanie kolizji i adaptacja (Merge Resolution)
1. Jeżeli dochodzi do kolizji między naszym kodem a zmianami Upstream (np. nakładające się linie w C++, zmiany sygnatur funkcji w silniku, zmodyfikowane pętle questów):
   - **Zasada nadrzędna:** Przeprojektować i zrefaktoryzować nasz kod tak, aby **w 100% zachować oficjalną funkcjonalność z Upstream**, przy jednoczesnym **pełnym działaniu naszych modyfikacji**.
2. Weryfikacja integralności w Dockerze na Dev:
   - Przebudowa kontenerów: `docker compose build game panel seban-panel`.
   - Sprawdzenie kompilacji kodu C++20 (i386) oraz kompilatora questów `qc` – zero błędów.
   - Po teście czyste wygaszenie kontenerów: `docker compose down`.

### Krok 5: Publikacja na GitHub i wdrożenie na Oficjalny (`d:\MT2\Metin2 Singleplayer Plus`)
Dopiero po pomyślnym przejściu Kroków 1–4:
1. **GitHub Push:**
   - Zacommitowanie przetestowanych zmian z czytelnym opisem konwencji Conventional Commits.
   - Wypchnięcie zmian do repozytorium zdalnego: `git push origin main`.
2. **Wdrożenie na Oficjalny:**
   - Synchronizacja wszystkich zmodyfikowanych i zaktualizowanych plików do folderu produkcyjnego: `d:\MT2\Metin2 Singleplayer Plus\Server`.
   - Aktualizacja pliku stanu launchera: `Server/.m2launcher-state.json` (klucz `"server"` na nowy numer wersji).
   - W przypadku zmian w zasobach klienta (`pack/root` itp.): skompilowanie nowej paczki za pomocą `Kompiluj-Paczki.bat` / `Compile-ClientPack.ps1` i zsynchronizowanie do obu klientów.

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
- **Kompilacja i Pakowanie Klienta:**
  - Skrypt wsadowy: [`Klient/Kompiluj-Paczki.bat`](file:///d:/Github/MT2Plus/Klient/Kompiluj-Paczki.bat) (menu interaktywne).
  - Skrypt PowerShell: [`Klient/Compile-ClientPack.ps1`](file:///d:/Github/MT2Plus/Klient/Compile-ClientPack.ps1) / [`Server/tools/Compile-ClientPack.ps1`](file:///d:/Github/MT2Plus/Server/tools/Compile-ClientPack.ps1).
  - Silnik pakerów: `PackMakerLite-RS` (`packmakerlite-cli.exe` z konfiguracją `PackMakerLite.json`).
  - Funkcjonalności: szybkie pakowanie wybranej paczki (np. `root`), masowe pakowanie rozpakowanych folderów (`pack-all`), rozpakowywanie (`unpack`), tryb autokompilacji przy zapisie plików (`watch`), automatyczne tworzenie kopii zapasowej `.bak` oraz synchronizacja gotowych plików `.data`/`.index` między folderem Dev i Oficjalnym.

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

1. **Zasada Nienaruszalności Bazy Danych i Postaci Gracza (Zero-Data-Loss):**
   - Aktualizacje serwera i kompilacje silnika C++ **nigdy nie mogą modyfikować ani usuwać wolumenów bazy danych (`db-data`)**, tabel graczy (`player.player`, `player.item`, `account.account`) ani stanu ekwipunku/postaci.
   - Wszelkie migracje schematów SQL (z Upstream lub z naszych modyfikacji) muszą być ściśle **addytywne** (`CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ... ADD COLUMN ... IF NOT EXISTS`) i w 100% bezstratne dla istniejącego świata gry.

2. **Zasada Złotego Trójkąta Spójności Proto (Baza SQL ↔ Serwer ↔ Klient):**
   - Silnik ładuje definicje proto z bazy SQL (`PROTO_FROM_DB = 1`).
   - Każda zmiana w `world.item_proto` lub `world.mob_proto` (nowe bronie, zbroje, bonusy, ulepszenia) bezwzględnie wymaga wygenerowania zaktualizowanej paczki klienta `dbdata` (przez edytor bazy w panelu Seban lub `dbdata.py`) i jej rekompilacji do `Klient/pack/`.
   - Zapobiega to desynchronizacji opisów, błędnym ikonom i crashom klienta gry.

3. **Zasada Atomowej Izolacji Środowisk (Dev vs Oficjalny):**
   - **Dev (`MT2Plus`):** Poligon doświadczalny, edycja kodu C++, tworzenie questów, kompilacje kontenerów (`mt2dev`) oraz wersjonowanie Git.
   - **Oficjalny (`Metin2 Singleplayer Plus`):** Środowisko produkcyjne / docelowe gracza (Ready-to-Play). Trafia do niego wyłącznie kod i paczki w 100% przetestowane, skompilowane i zweryfikowane, gwarantując pełną stabilność rozgrywki.

4. **Zasada Weryfikacji Czystego Stanu Git (Clean Tree Guard):**
   - Przed przystąpieniem do jakiejkolwiek aktualizacji z Upstream stan repozytorium na Dev musi być czysty (`git status`).
   - Po każdej udanej zmianie, pomyślnej kompilacji i teście, gotowe zmiany są natychmiast commitowane i wypychane na zdalny GitHub (`git push origin main`), a serwer deweloperski czysto wyłączany (`docker compose down`).

5. **Wymóg wersji MariaDB 11.8+:** Nie wolno dokonywać downgrade'u do MariaDB 10.x z powodu twardego wymogu kolacji `utf8mb3_uca1400_ai_ci`.
6. **Tabele MyISAM i czyste zatrzymywanie:** Zawsze stosować czyste zatrzymywanie usług (`docker compose down` lub `stop.bat`), aby chronić tabele MyISAM przed uszkodzeniem indeksów.
7. **Edycja kodu C++ (i386):** Źródła serwera znajdują się w `Server/linux-port/docker/game/src/server/` oraz `Server/linux-port/overlays/playerbot/src/game/src/`. Wszelkie modyfikacje wymagają poprawnej kompilacji w kontenerze 32-bitowym (`i386`).
8. **Katalog Addonów (`Server/addons/`) i Zasada Cyklu Życia Dodatków:** Wszystkie gotowe paczki dodatków, spakowane fixy i moduły przygotowywane dla serwera należy umieszczać w dedykowanym katalogu `Server/addons/`. Jeżeli w nowym wydaniu Upstream oficjalnie wprowadził fixa lub funkcjonalność, którą wcześniej realizowaliśmy jako addon, dany dodatek można **bezpiecznie usunąć z `Server/addons/`**, przechodząc w pełni na oficjalny kod bazowy.
9. **Synchronizacja Stanu Launchera Windows:** Przy każdej zmianie wersji serwera należy zaktualizować zarówno `Server/VERSION`, jak i plik `Server/.m2launcher-state.json`, aby GUI launchera (`Metin2-Launcher-GUI.bat`) natychmiast odczytywało aktualny stan wersji.
