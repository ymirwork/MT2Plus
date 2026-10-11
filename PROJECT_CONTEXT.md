# PROJECT_CONTEXT: Metin2 Singleplayer Plus (MT2Plus)

Dokumentacja techniczna, struktura środowisk i stan projektu Metin2 opartego na repozytorium `mt2009-sp-plus`.

---

## 1. Wersjonowanie i Identyfikacja

- **Wersja serwera (`Server/VERSION`):** `2.30.0`
- **Wersja modyfikacji (`Server/MOD_VERSION`):** `mod-50`
- **Wersja klienta (`Klient/CLIENT_VERSION`):** `2.0.60`
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
- **Model wydawniczy:** Zmiany z gałęzi `dev` po pełnym przetestowaniu i zatwierdzeniu są scalane (**Merge / Pull Request**) do gałęzi `main`. Gałąź `main` stanowi oficjalną, w 100% stabilną wersję gry (Release).
- **Środowisko lokalne uruchomieniowe (opcjonalne / gracza):** `d:\MT2\Metin2 Singleplayer Plus` (jeśli uruchamiane niezależnie).
- **Koniec z ręcznym kopiowaniem:** Zarządzanie wersjami i zmianami odbywa się w pełni przez Git (`dev` -> `main`), eliminując konieczność ręcznego synchronizowania i kopiowania plików pomiędzy folderami.

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

### Krok 3: Dodanie naszych modyfikacji z `Server/addons/` (bezinwazyjnie dla Upstream)
1. Zaaplikowanie naszych autorskich systemów i modułów umieszczonych w `Server/addons/` oraz własnych komponentów:
   - System recyklingu bonów u Dozorcy (`recykling_bonusow.quest`, rejestracja w `Dockerfile`, paczka w `Server/addons/`).
   - Naprawa pętli wędkowania towarzysza (`playerbot_sidekick.h` – bezpośrednie sterowanie `rt.bFishing`).
   - Rozszerzony Pierścień Teleportacji (`teleport_ring.quest` – lochy, miasta).
   - Dom Aukcyjny / AH_V1 (`auction_house.cpp`, `cmd.cpp`, `ikarus_shop_manager.cpp`, `flea_market.quest`).
2. **Bezpieczne usuwanie zaadoptowanych modyfikacji (Addon Cleanup):** Jeżeli Upstream oficjalnie wprowadził fixa lub system, który dotychczas utrzymywaliśmy jako naszą modyfikację w `Server/addons/`, wówczas naszą paczkę/patch **bezpiecznie usuwamy z `Server/addons/`**, przechodząc na oficjalne rozwiązanie z Upstream i eliminując duplikację kodu.
3. Bezwzględny warunek: implementacja musi być bezinwazyjna – żadna nasza modyfikacja nie może usunąć ani zepsuć nowego kodu ani logiki wprowadzonej przez Upstream.

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

## 5. Kluczowe Własne Systemy i Modyfikacje (v2.30.0 / mod-50)

- **Szybkie Podnoszenie Przedmiotów (Fast Area Pickup):** Natychmiastowe zbieranie dropu w promieniu postaci pod klawiszem `Z` / `~` (`/pickup_nearby` wywoływane w pierwszej klatce naciśnięcia, interwał przytrzymania skrócony do 150 ms, cooldown po stronie serwera w `char_item.cpp` zredukowany do 100 ms).
- **Szybkie Ulepszanie (Fast Refine without Animation Lock):** Usunięte blokujące wyskakujące okienka dialogowe sukcesu/porażki z `game.py` i `digiserverqol.py` (przekierowane na czytelne komunikaty na czacie), natychmiastowe zatwierdzanie klawiszem Enter i wysoka responsywność u kowala.
- **Zdalny Biolog (Remote Biologist):** Quest `zdalny_biolog.quest` od poziomu 30+ umożliwiający zdalne oddawanie próbek biologa oraz sprawdzanie aktualnego stanu badań i oczekiwania bez konieczności każdorazowego biegania do Chaegiraba / Beak-Go.
- **Skrócony Czas Oczekiwania po Zamknięciu Okien (3s Portal/Safebox/Trade Cooldown):** Zredukowany z 10 sekund do 3 sekund (`g_nPortalLimitTime = 3` w `char_item.cpp`) po zamknięciu handlu, magazynu lub dozorcy przed przejściem przez portal.
- **Upłynnianie Ulepszaczy M1/M2 przez Boty (Bot-Only M1/M2 Liquidation & Market Balance):** Wewnętrzny mechanizm symulacji gospodarki botów w `playerbot_bonus.h` / `playerbot_market.h` / `playerbot_types.h`:
  - Przetapianie nadmiaru ulepszaczy M1/M2 (50 szt. pospolitych lub 25 szt. rzadkich + opłata Yang skalowana inflacją) na handlowalne Zaczarowania (`71284`) i Wzmocnienia (`71285`).
  - Priorytet zużycia na własne uzbrojenie bota (do 4–5 bonusów i rollowanie statystyk).
  - Nadwyżki wystawiane w tobołkach z twardym limitem maks. 20% sklepów na rynku i do 3 slotów na sklep (`PLAYERBOT_RARE_GOODS_TRADEABLE_BONUS`), analogicznie do szarf i Cor Draconis.
  - **Skup z tobołków (15% botów):** 15% puli botów aktywnie skupuje ulepszacze M1/M2 z rynku graczy/botów po uczciwych cenach rynkowych (do 120% cennika, maks. 20% sakiewki bota), aby zamieniać je na bonusy, zapewniając stały popyt na drop z początkowych map i stabilizując gospodarkę Hard.
  - *Uwaga:* Emerytury botów pozostają domyślnie wyłączone do późniejszej konfiguracji przez operatora.
- **Świątynia Zodiaku (Zodiac Temple) & Towarzysz (v2.29.1):** Mapa 358 (`metin2_12zi_stage`), 12 portali, Kule Animy, broń/zbroje Zodiaku, instancje pięter; pełna obsługa Towarzysza (wskrzeszanie Pryzmatami Ożywienia, automatyczne czyszczenie flag Zodiaku i autowstanie po 30s).
- **System Recyklingu Bonowanego Ekwipunku:** Quest `recykling_bonusow.quest` u Dozorcy – wymiana niepotrzebnych przedmiotów z 5 bonusami na Zaczarowania i Wzmocnienia Przedmiotu dla gracza. Paczka instalacyjna w `Server/addons/Paczka_Recykling_Bonusow.zip`.
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

12. **Zasada Weryfikacji Stanu Serwera Przed Zmianami (Selective Shutdown & Safe Backup Guard):**
    - **Weryfikacja stanu serwera:** Przed przystąpieniem do wprowadzania jakichkolwiek zmian, instalacji dodatków, modyfikacji bazy danych lub kodu silnika gry, zawsze najpierw sprawdź, czy serwer jest aktualnie uruchomiony (`docker ps`).
    - **Minimalizacja przestojów (Wyłączaj/restartuj tylko gdy to konieczne):**
      - Wyłączaj lub restartuj serwer **tylko i wyłącznie wtedy, kiedy musisz / jest to bezwzględnie konieczne** (np. rekompilacja silnika C++, zmiany schematów i tabel w MariaDB wymagające zatrzymania, modyfikacje plików montowanych bezpośrednio w aktywnych rdzeniach gry).
      - Jeżeli wyłączenie serwera nie jest konieczne (np. przygotowywanie paczek klienta, pisanie kodu w folderze deweloperskim, edycja dokumentacji czy skryptów pomocniczych), **nie wyłączaj serwera** – niech działa nieprzerwanie.
    - **Procedura przy konieczności wyłączenia serwera do zmian:**
      1. **Bezpieczne zatrzymanie:** Jeżeli serwer jest włączony i jego wyłączenie jest wymagane, zatrzymaj go czysto i bezpiecznie (np. `.\Metin2-Launcher.ps1 -Action Stop` lub `docker compose stop`), aby procesy gry (`m2-supervise`) i MariaDB dokonały bezpiecznego zrzutu (flush) danych na dysk.
      2. **Kopia zapasowa bazy danych (Backup):** Przed wprowadzeniem modyfikacji zrób kopię zapasową bazy danych do katalogu `Server/backups/` (np. procedurą launchera `BackupDb` lub zrzutem bazy).
      3. **Wprowadzenie zmian:** Zaaplikuj przygotowane modyfikacje, fixy lub konfigurację.
      4. **Restart i weryfikacja:** Uruchom serwer ponownie (`docker compose up -d`) i upewnij się, że wszystkie rdzenie poprawnie nasłuchują.
