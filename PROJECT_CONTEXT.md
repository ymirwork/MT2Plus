# PROJECT_CONTEXT: Metin2 Singleplayer Plus (MT2Plus)

Dokumentacja techniczna, struktura środowisk i stan projektu Metin2 opartego na repozytorium `mt2009-sp-plus`.

---

## 0. Szybki System Tagów i Dyrektyw (Komunikacja z Asystentem)

Aby przyspieszyć pracę i nadać precyzyjny kontekst zapytaniom, stosuj poniższe prefiksy tagów na początku wiadomości:

| Tag | Znaczenie i Cel | Zachowanie i Rola Asystenta |
| :--- | :--- | :--- |
| **`[AKTUALIZUJ]` / `[UPSTREAM]`** | Pobranie i merge nowości z oficjalnego repozytorium `mt2009-sp-plus`. | Ścisła realizacja 5-etapowej procedury merge (Krok 1–5): analiza diffa, adaptacja na `dev`, a następnie **bezwzględne ponowne wgranie i zintegrowanie wszystkich naszych autorskich modyfikacji** z rejestru `Server/server-patches/krystian/` (Krok 3). Weryfikacja ewentualnych kolizji z upstreamem i bezpieczne usunięcie tylko tych modów, które oficjalny kod sam wdrożył. |
| **`[DEV]` / `[SERVER]`** | Rozwój serwera: modyfikacje C++, questy, baza danych MariaDB, kontenery Docker. | Pełne poszanowanie reguły bezpieczeństwa (Zasada nr 12: STOP serwera + backup bazy), kompilacja i386 C++20, tworzenie modułu w `Server/server-patches/krystian/`, testy w `mt2dev`. |
| **`[CLIENT]` / `[PACK]`** | Prace nad klientem gry: skrypty Pythona (`root`, `uiscript`), interfejsy UI, pakowanie paczek `.data`/`.index`. | Bez zatrzymywania serwera (brak przestoju); pakowanie przez `Klient/Kompiluj-Paczki.bat` lub `Compile-ClientPack.ps1`, zachowanie kompatybilności z `dbdata`. **BEZWZGLĘDNY NAKAZ: Przy KAŻDEJ nowej modyfikacji/zmianie w kliencie ZAWSZE na zakończenie musi zostać zaktualizowany i zsynchronizowany patcher (`python Server/tools/publish_patcher_web.py`), aby patcher nie nadpisał nowości!** (Zasada nr 15) |
| **`[BUG]` / `[FIX]`** | Zgłoszenie i diagnoza błędu lub crasha w grze. | Natychmiastowa analiza logów (`syserr`, `syslog`, `docker logs`), identyfikacja przyczyny źródłowej (*root cause*), minimalny bezpieczny patch bez psucia logiki upstreamu. |
| **`[DISCORD]`** | Przygotowanie materiałów, ogłoszeń i instrukcji dla społeczności graczy na Discordzie. | Przejście na język gracza: brak zbędnego żargonu kompilacji, zwięzły opis zmian oraz jasna instrukcja instalacji krok po kroku (patrz szablony poniżej). |
| **`[DOCS]` / `[RELEASE]`** | Aktualizacja dokumentacji, generowanie podsumowań, tworzenie wydań na GitHub (Releases) oraz Changelogu. | Przygotowanie taga wydania, archiwów `.zip`/`.rar` typu Ready-to-Play (zawierających wyłącznie pliki niezbędne do uruchomienia serwera i klienta np. dla siostry/innych graczy bez zbędnego śmietnika), sformatowanego Changelogu z kropkami i podsumowaniami, a **na sam koniec bezwzględne utworzenie GitHub Release i wrzucenie obu paczek (serwera i klienta z naszymi modyfikacjami) na GitHub Releases**. |

---

### 0.1. Szybka Mapa Ścieżek i Komend (Quick Reference)

| Zasób / Zadanie | Ścieżka / Komenda | Uwagi |
| :--- | :--- | :--- |
| **Logi błędów gry (syserr)** | `Server/linux-port/docker/game/logs/syserr` | Pierwsze miejsce diagnozy crashy i błędów silnika |
| **Źródła silnika C++ gry** | `Server/linux-port/docker/game/src/server/` | Rdzeń MartySama r41023 (i386 C++20) |
| **Kod C++ Playerbots AI** | `Server/linux-port/overlays/playerbot/src/game/src/` | Moduły `playerbot_*.cpp / .h` |
| **Skrypty i interfejsy klienta** | `Klient/pack/root/` oraz `Klient/pack/uiscript/` | Rozpakowane źródła Pythona klienta |
| **Pakowanie paczek klienta** | `Klient/Kompiluj-Paczki.bat` / `Klient/Compile-ClientPack.ps1` | PackMakerLite-RS (klucz `22srh2fgh3`) |
| **Serwer aktualizacji Patchera (CDN)** | `Server/tools/publish_patcher_web.py` | Generowanie i synchronizacja drzewa patchera na gałąź `gh-pages` (raw CDN) |
| **Katalog autorskich modyfikacji** | `Server/server-patches/krystian/` | Podfoldery z autorskimi modyfikacjami i systemami |
| **Bufor wydań i higiena dysku** | `dist/` \| `Klient/syserr.txt` | Tymczasowy bufor wydań i logi do okresowego czyszczenia (Zasada nr 14) |
| **Kopie zapasowe bazy SQL** | `Server/backups/` | Zrzuty bazy przed zmianami w serwerze (retencja: maks. 2 dni, starsze usuwane) |
| **Panele i serwisy WWW** | Tieru: `http://localhost:7788` \| Seban: `http://localhost:7790` \| IS: `http://localhost:7791` | Login / zarządzanie / rynek |

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

- **Wersja serwera (`Server/VERSION`):** `2.37.1`
- **Wersja modyfikacji (`Server/MOD_VERSION`):** `mod-59`
- **Wersja klienta (`Klient/CLIENT_VERSION`):** `2.0.68`
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

### Krok 3: Ponowne wdrożenie wszystkich naszych modyfikacji z `Server/server-patches/krystian/`
1. **Dynamiczne wgrywanie z Rejestru Modyfikacji (`Server/server-patches/krystian/`):**
   - Po udanym naniesieniu zmian z oficjalnego repozytorium (Krok 2), asystent i deweloper **nie polegają na sztywnej liście**, lecz dynamicznie sprawdzają **Rejestr Modyfikacji (Sekcja 5.1)** oraz zawartość folderu `Server/server-patches/krystian/`.
   - **Wszystkie aktywne podfoldery i moduły** znajdujące się w `Server/server-patches/krystian/` (zarówno obecne, jak i nowo dodane w przyszłości) są sekwencyjnie aplikowane na gałąź `dev`.
   - **Zasada Dodawania Nowego Modułu:** Każda nowa modyfikacja autorska tworzona w projekcie musi:
     1. Posiadać dedykowany podfolder z dokumentacją `README.md` oraz skryptami/diffami w `Server/server-patches/krystian/`.
     2. Zostać dopisana do tabeli w **Sekcji 5.1** wraz z informacją o modyfikowanych plikach i statusie `Aktywny`.
     Dzięki temu podczas kolejnego `[AKTUALIZUJ]` nowy moduł zostanie automatycznie uwzględniony i ponownie wdrożony!
2. **Bezpieczne usuwanie zaadoptowanych modyfikacji (Mod Cleanup):** Jeżeli Upstream w nowej wersji oficjalnie wprowadził identycznego fixa lub system, który dotychczas utrzymywaliśmy w `Server/server-patches/krystian/`, wówczas dany moduł **bezpiecznie oznaczamy lub usuwamy z `Server/server-patches/krystian/`**, usuwamy/aktualizujemy wpis z Sekcji 5.1, przechodząc na oficjalne rozwiązanie z Upstream i eliminując duplikację kodu.
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
   - Utworzenie taga wydania na GitHub (np. `v2.34.0-mod55`) i wypchnięcie go: `git push origin [tag]`.
3. **Paczki klienta i serwera:**
   - W przypadku modyfikacji plików klienta (`pack/root` itp.): skompilowanie nowej paczki za pomocą `Kompiluj-Paczki.bat` / `Compile-ClientPack.ps1` i wygenerowanie archiwum wydania dla graczy.
   - Zbudowanie gotowych archiwów Ready-to-Play: serwera (`metin2-server-update-[wersja].zip`) oraz klienta (`metin2-client-update-[wersja].zip` ze zaktualizowanym `pack/root`).
4. **Bezwzględna Publikacja Wydania na GitHub Releases:**
   - **W procedurze wydania `[DOCS]` / `[RELEASE]` asystent ZAWSZE ma obowiązek utworzyć i opublikować oficjalne wydanie na GitHub Releases** (`https://api.github.com/repos/ymirwork/MT2Plus/releases` przez REST API / curl).
   - W załącznikach (Release Assets) muszą znaleźć się **obie paczki wydania**:
     1. Paczka serwera: `metin2-server-update-[wersja].zip`
     2. Paczka klienta z naszymi modyfikacjami: `metin2-client-update-[wersja].zip`
   - Opis wydania (Release Body) musi zawierać sformatowany Changelog (Szablon B) oraz sumy kontrolne SHA-256 obu plików.
5. **Synchronizacja i Publikacja Serwera Patchera (`gh-pages` / CDN):**
   - Na sam koniec asystent uruchamia generator i synchronizator patchera:
     `python Server/tools/publish_patcher_web.py`
   - Skrypt wstrzykuje nowe sumy MD5 i pliki naszych modyfikacji (`pack/root.data`, `pack/root.index`, `CLIENT_VERSION`, `MT2009-Patcher.exe.config`), synchronizuje pozostałe pliki upstreamu i automatycznie publikuje gotowe drzewo na gałąź `origin/gh-pages`.
   - Dzięki temu patcher graczy (`MT2009-Patcher.exe`) pobiera aktualizacje z adresu `https://raw.githubusercontent.com/ymirwork/MT2Plus/gh-pages/patcher/` i zawsze zachowuje nasze modyfikacje.

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
     - **Telemetria Modułu YmirWork V3 (Tier 1 + Tier 2):** Statystyki przetapiania ulepszaczy M1/M2 na Zieloną Siłę (71152) i Czar (71151) oraz Mid/Late na Wzmocnienia (71285) i Zaczarowania (71284), progi bazowe 40 szt. (rabat do 25), obieg w świecie i sklepach, dynamiczny skup ofert (3%–35%) przez boty.
     - **Półautomatyczny Doradca Rotacji Botów (Asystent Emerytur):** Algorytm oceniający dojrzałość populacji (poziomy botów 35+, 40+, 50+, cooldown &ge;12h/24h), wskaźnik gotowości rynkowej (%), ochrona przed zaburzeniem rozgrywki i szybka akcja 1-klik `[Zastosuj rekomendację doradcy]`.
6. **`seban-collector` & `seban-item-grants`**:
   - Demony tła odpowiedzialne za telemetrię, ogłoszenia ulepszeń +9 i transakcyjne nadawanie przedmiotów.
7. **`itemshop` (Port 7791)**:
   - Sklep www (PHP 8.2 + Apache) autorstwa OskarPWA, zintegrowany z SAS token w kliencie i tabelą `player.item_award`.
8. **`updater`**:
   - Demon aktualizacji orkiestrujący pobieranie manifestu i przebudowę kontenerów.

### 4.2. Warstwa Klienta (Windows)
- Plik wykonywalny: `metin2client.exe` (binarny, brak źródeł C++ w tym repozytorium).
- Patcher: `MT2009-Patcher.exe` (.NET 4.7.2/4.8 WPF).
  - Skonfigurowany w `MT2009-Patcher.exe.config` do pobierania aktualizacji z naszego repozytorium (`https://raw.githubusercontent.com/ymirwork/MT2Plus/gh-pages/patcher/`).
  - Serwer aktualizacji jest w 100% zsynchronizowany z naszymi modyfikacjami (`publish_patcher_web.py`), dzięki czemu patcher nie nadpisuje autorskich zmian w `root.data` i wspiera aktualizacje upstreamu.
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
- **Modul YmirWork (Krystian) - Plynne Uplynnianie Ulepszaczy M1/M2(+) i Dynamiczny Balans Rynku (MODUL YMIRWORK (KRYSTIAN) V3 AKTYWNY):** Wewnetrzny mechanizm symulacji gospodarki botow w playerbot_bonus.h / playerbot_market.h / playerbot_energy_shards.h / playerbot_price_tables.h / playerbot_town.h:
  - **Dwuetapowy Tiering Ulepek (Styl Hard):**
    - **Tier 1 (M1/M2 i Dzicy Ludzie):** Przetapianie nadmiaru ulepek wczesnej fazy gry (Wilk, Dzik, Niedzwiedz, Biala Wstega, Kawalek Klejnotu, Kawalek Zepsutej Zbroi itp.) na handlowalne **Zielony Czar (71151)** oraz **Zielona Sile (71152)**. Oplata: 50 000 Yang (skalowana inflacja).
    - **Tier 2 (Dolina Orkow, Pustynia, DT, Sohan, Swiatynia):** Przetapianie trudniejszych ulepek na elitarne **Zolte Zaczarowanie (71284)** oraz **Wzmocnienie (71285)**. Oplata: 150 000 Yang (skalowana inflacja).
  - **Progi Ulepek w Duchu Hard:** Baza wynosi **40 sztuk** dla wszystkich materialow (zwykle i z plusem), z dynamicznym rabatem rynkowym u Kolekcjonera az do **25 sztuk** w przypadku powodzi towarowej (>1500 sztuk w sklepach).
  - **Pelna Zbywalnosc Zielonych Kamieni:** W world.item_proto ustawiono ntiflag = 0 (brak blokad handlu, tobolka, dozorcy) oraz lag = 8196 (stackowalne do 200 sztuk). Ceny katalogowe w playerbot_price_tables.h: 100 000 Yang (Czar) oraz 250 000 Yang (Sila) - automatycznie skalowane przez mnoznik inflacji (WorldYangFactor).
  - **Zachowanie Botow:** Boty <= 40 lvl aktywnie uzywaja zielonych kamieni do bonowania noszonego eq <= 40 lvl (FMS, RIB, zbroje 18/26/34 lvl), skupuja zielone kamienie z rynku (od gracza i innych botow) w ramach budzetu do 20% wolnego Yang, a nadmiary wystawiaja w tobolkach offline.
  - **Plynny wskaznik skupu botow (1% - 35%):** Zamiast sztywnego 15%, odsetek botow skupujacych towary z tobolkow gracza i rynku skaluje sie dynamicznie na podstawie aktualnej podazy ulepszaczy w sklepach (od 3% przy niskiej podazy do 35% przy powodzi towarowej).
  - **Telemetria w panelu Seban:** Dynamiczne sledzenie mnoznika inflacji, wskaznika skupu botow, podazy ulepszaczy oraz historii przetopien. Modul w Server/server-patches/krystian/zielone-dodania-m1m2/.
- **Świątynia Zodiaku (Zodiac Temple) & Towarzysz (v2.29.1):** Mapa 358 (`metin2_12zi_stage`), 12 portali, Kule Animy, broń/zbroje Zodiaku, instancje pięter; pełna obsługa Towarzysza (wskrzeszanie Pryzmatami Ożywienia, automatyczne czyszczenie flag Zodiaku i autowstanie po 30s).
- **System Recyklingu Bonowanego Ekwipunku:** Quest `recykling_bonusow.quest` u Dozorcy – wymiana niepotrzebnych przedmiotów z 5 bonusami na Zaczarowania i Wzmocnienia Przedmiotu dla gracza. Moduł w [`Server/server-patches/krystian/recykling-bonusow/`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/recykling-bonusow).
- **Sklep Offline 160 Pól (Odblokowanie Kluczami):** Dwa bloki sklepu offline (po 80 pól każdy, łącznie 160 pól). Pierwszy blok zachowuje 40 pól darmowych, 20 za klucze (po 1 Drewnianym Kluczu `30376` na 5 pól) oraz 20 pól premium. Drugi blok 80 pól odblokowywany jest krokami po 5 pól za 2 Drewniane Klucze (`shop_unlock_slots.quest`). Przy tworzeniu sklepu obowiązuje limit do 80 przedmiotów naraz; kolejne sloty uzupełnia się w otwartym sklepie. Zmiany silnikowe w `char_shop.cpp` i `ikarus_shop_manager.cpp`, interfejs w `dualshop.py`, `offlineshopui.py`, `offlineshopbuilder.py` i `offlineshopmanage.py`. Moduł w [`Server/server-patches/krystian/sklep-160-slotow/`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/sklep-160-slotow).
- **Naprawa Łowienia Towarzysza:** Bezpośrednie sterowanie pętlą wędkowania w trybie "Na ryby" (`playerbot_sidekick.h`), zapobiegające porzucaniu łowienia przez bota.
- **Dom Aukcyjny (AH_V1, Autor: Vekirion):** Wyszukiwarka i zakupy ofert ze sklepów offline (Ikarus) bez nowych pakietów binarnych, komendy `/ah_*` w `auction_house.cpp`, hooki transakcyjne w `ikarus_shop_manager.cpp` i `cmd.cpp`, quest `flea_market.quest` oraz interfejs klienta `uiauctionhouse.py`.
- **Rozszerzony Pierścień Teleportacji:** Quest `teleport_ring.quest` ze skrótami do lochów (Loch Pająków V1, Trudny/Normalny/Łatwy Loch Małp) oraz map Arezzo (360 Dolina Cyklopów, 361 Pustkowie Faraona). Moduł w [`Server/server-patches/krystian/pierscien-teleportacji/`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/pierscien-teleportacji).
- **Ruiny Atlantydy (Ruins of Atlantis):** Mapa 158, dungeon grupowy/solo od poziomu 75+.
- **Moduł Arezzo:** Nowe mapy exp (360-362) i dungeony (363-366).
- **Playerbots AI:** Ponad 18 000 linii kodu C++ wbudowane w `game/src/` (`playerbot_manager.cpp`, `playerbot_types.h`), obsługa dungeonów, tobołków offline, farming linków, walki i zrzutek na ziemie gildii.
- **System Szarf, Talizmanów i Kostiumów Broni:** Ulepszanie talizmanów +0..+200, szarfy z absorpcją.
- **Alchemia Smoczych Kamieni (Dragon Soul):** Mityczna alchemia, pełny obieg uszlachetniania.
- **Auto Hunting (Klawisz K):** Zautomatyzowane expienie dla gracza.
- **Szybkie ulepszanie (Enter-refine) & TAB Minimap Warp.**
- **Pakiet Optymalizacji Autołowów, Dropu, Sklepów i Magazynów (v2.33.0 / Krystian):**
  - **Automatyczne stackowanie zakupów (AH, Sklep NPC, Depozyt):** Przedmioty kupowane w Domu Aukcyjnym (pojedyncze oferty i hurt `/ah_bulk_buy`), w sklepach NPC oraz wyciągane z depozytu/safeboxa łączą się natychmiast w jeden wspólny stos w ekwipunku (`AutoStackItem`) do limitu (np. 200) zamiast rozbijać się na osobne sloty (`ikarus_shop_manager.cpp`, `shop.cpp`, `char_item.cpp`, `safebox.cpp`, `input_main.cpp`). Umożliwiono zakup i wyciąganie z depozytu nawet przy pełnym ekwipunku, o ile przedmioty mieszczą się w istniejących stosach.
  - **Usunięcie limitu +-15 poziomów na drop:** Zniesiono ograniczenia delty poziomu w silniku serwera (`item_manager.cpp`, `char_battle.cpp`, `playerbot_alchemy.h`, `playerbot_events.h`, `playerbot_newpet.h`, `dragon_soul.quest`). Drop przedmiotów, Yang, Odłamków Kamienia Smoczego, Cor Draconis, Szarf/Sukna oraz Jaj Zwierzaków leci niezależnie od poziomu postaci.
  - **Usprawnienia i skrócenie akcji w Autołowach:** Zoptymalizowano `uiautohunt.py` (skrócenie `STUCK_SECONDS` z 8.0s do 3.0s, błyskawiczne pytanie o kolejny cel po 0.3s, szybsze zapytania `TARGET_REQUEST_INTERVAL` 0.35s i zbieranie lootu).
  - **Usprawnienie Pathfindingu w Autołowach (Lochy Małp):** Wprowadzono filtr osiągalności celów `CPlayerBotManager::IsHumanTargetReachable` (`playerbot_manager.cpp`, `cmd_general.cpp`), zapobiegający obieraniu potworów za ścianami w odciętych komnatach. W kliencie (`WalkPath`) zwiększono margines punktów i dodano wygładzanie zakrętów.
  - **Odblokowanie mapy Czerwonego Lasu:** Dodano atlas `metin2_map_trent02` w minimapie (`M`) klienta (`uiminimap.py`, `uitooltip.py`).
  - **Zwiększenie stosu przedmiotów do 200:** Podniesiono limit stackowania z 5/10/20 do 200 sztuk dla Medalu Konnego, Ziół z Małp, Zwojów Błogosławieństwa/Wojny/Boga Smoków, Magicznych Metali/Kamieni Kowala, Małży, Pereł, Ryb, Przetopów Rud, Ksiąg Pasywnych (Sun Zi, Combo, Języki, Polimorfia, Instrukcje Konne) oraz Kluczy i Przedmiotów Specjalnych (`world.item_proto`, `apply.sh` + paczka binarnego `dbdata` 2.0.61-31f459ebe125).
- **Pakiet Usprawnień Rozgrywki (Dev Gameplay V1):**
  - Czytanie Ksiąg Umiejętności (KU) bez wymogu posiadania punktów doświadczenia (EXP) w `char_skill.cpp`.
  - Zdjęcie limiterów Movement Speed i Attack Speed, odblokowanie górnego limitu obrażeń (damage cap) oraz usunięcie disconnectów i cofania gracza przez antyhack (`CheckComboHack` / `IS_SPEED_HACK`).
  - Natychmiastowe ulepszanie u kowala bez 1-sekundowego opóźnienia "Odczekaj przed następnym ulepszaniem" w `input_main.cpp`.
  - Zapisywanie lochów (Loch Pająków V1/V2/V3, Lochy Małp, Grota Wygnańców) w Zwoju Powrotu z walidacją VIP-a lub Przepustki przy teleportacji oraz poprawka zapisywania dla czystych zwojów (quest `tp_bookmarks.quest`, `char_item.cpp`).
  - Wprowadzanie kwot Yang ze skrótami `k`, `kk`, `kkk` w oknach dialogowych (np. `1kk` = `1.000.000`) w `uiPickMoney.py`, `uiCommon.py`, `uiexchange.py` i skryptach dialogów.
  - Zwiększenie obrażeń PvP o 5% przy ataku na gracza z wrogiego królestwa, jeśli napastnik posiada język tej nacji na poziomie minimum M1 w `char_battle.cpp`.
- **Recykling Broni 30 lvl & Ulepszanie u Kowala (Filar 1 - Hardcore Item & Gold Sink):** Eliminacja zjawiska chomikowania broni 30 lvl (Koziki, Antyki, Wachlarze Jesienne, Rogowe Łuki) w plecakach botów. Elitarne bronie (Średnie >= 25% lub Umiejętności >= 8% lub +7..+9) są chronione jako zasób strategiczny i nigdy nie trafiają do NPC (`IsPlayerBotHighValueLevel30`). Zwykły złom (<= 10% śr na niskim plusie +0..+3) lub nadmiar zapychający ekwipunek jest sprzedawany u Handlarki, a nadmiary od 15 poziomu są ulepszane "na czysto" u wiejskiego kowala bez zwojów (limit 8 prób dziennie, co stanowi naturalny pochłaniacz przedmiotów i Yangów). Moduł w [`Server/server-patches/krystian/recykling-broni-30/`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/recykling-broni-30).
- **Sesja Farmienia (Farming Session Tracker & Valuation):** Nowoczesne okno analityki pod klawiszem `F6` (rebindowalne w menu skrotow). Sledzi czas sesji ze stoperem (pauza/wznowienie/reset), zniszczone Kamienie Metin, pokonanych Bossow, wszystkie zrodla oraz zdobyty EXP i tempo (`EXP / godz.`). Zlicza surowe Yang z ziemi oraz dokladna liczbe i szacowana wartosc zebranych przedmiotow z mozliwoscia przelaczania trybu wyceny: **Rynkowa** (baza ponad 3250 sugerowanych cen z rynku botow i sklepow offline, np. Klejnot Demona = 140k) vs **NPC** (wartosc sprzedazy u handlarza po odliczeniu 3% podatku handlowego). Umozliwia wlasna edycje cen (przycisk Cena z obsluga k/kk/m/b), wykluczanie z sumy (przycisk Wyklucz / Wlicz), dynamiczne tempo dochodu (`~Yang / godz.`, `~Metin / godz.`), udostepnianie raportu na czat oraz kompaktowy, ruchomy mini-widzet HUD. Modul w [`Server/server-patches/krystian/sesja-farmienia/`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/sesja-farmienia).
- **Automatyczny Drop do Magazynu Kolekcjonera przy Pełnym Ekwipunku (Kolekcjoner Auto-Drop):** Checkbox pod przyciskiem "Rozbuduj" w oknie Magazynu Kolekcjonera (`uicollector.py`). Gdy opcja jest zaznaczona i gracz ma zapełniony ekwipunek (`full EQ`), zbierany drop z ziemi (`PickupItem`) oraz przedmioty z zadań/skrzynek (`AutoGiveItem`) automatycznie trafiają do Magazynu Kolekcjonera zamiast leżeć na ziemi. Obsługuje łączenie stosów (stack merge) do 2 mld sztuk dla ulepszaczy i kamieni, uwzględnia limit pojemności magazynu (`Capacity(tier)` do 10 000 slotów), blokuje przedmioty specjalne (szarfy, alchemia smoczych kamieni, pasy, zablokowane) oraz trwale zapamiętuje ustawienie na koncie gracza (`collector_autodrop`). Moduł w [`Server/server-patches/krystian/kolekcjoner-autodrop/`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/kolekcjoner-autodrop).
- **Naprawa i Odblokowanie Odnawiania Sklepów Botów (4 Strony / 320 Slotów):** Usunięcie błędu silnika C++ w `char_shop.cpp` (`CanPlaceOnShopSlot`, `CanPlaceItemOnShopSlot`) oraz `ikarus_shop_manager.cpp` (`RecvShopReopenClientPacket`), który blokował wznawianie wygasłych po 8h sklepów offline botów po powiększeniu ich stoisk do 4 stron w 2.36.0 (`slots_ok=0` / `SHOP_NO_PREMIUM`). Zapewnia automatyczne odnawianie stoisk botów na CH1 i utrzymanie stałej puli ~1800 aktywnych sklepów na rynku. Moduł w [`Server/server-patches/krystian/odnawianie-sklepow-botow/`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/odnawianie-sklepow-botow).
- **Pobieranie Ulepszaczy z Magazynu Kolekcjonera u Kowala i przy Zwojach (Refine Collector Fallback):** Inteligentne pobieranie ulepszaczy z Magazynu Kolekcjonera podczas ulepszania u kowala (`CHARACTER::DoRefine`) oraz przy użyciu zwojów (`CHARACTER::DoRefineWithScroll`). Bezwzględny priorytet ekwipunku postaci (materiały pobierane najpierw z `INVENTORY`, a brakująca różnica z magazynu). W pełni atomowa walidacja (sprawdzenie łącznej dostępności wszystkich składników przed pobraniem czegokolwiek). Cicha synchronizacja w tle przy logowaniu postaci (`CInputLogin::Entergame` z flagą `silent = 1`), dzięki czemu okno ulepszania (`uirefine.py`) natychmiast pokazuje dostępność materiałów na zielono w formacie `Nazwa x 02 (1 + 5 mag.)`, a gracz otrzymuje powiadomienie informacyjne na czacie o pobraniu ulepek z magazynu. Moduł w [`Server/server-patches/krystian/kolekcjoner-refine/`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/kolekcjoner-refine).

### 5.1. Rejestr Autorskich Modyfikacji w `Server/server-patches/krystian/`

Wszystkie nasze autorskie modyfikacje, systemy oraz poprawki są zorganizowane w dedykowanych, modularnych podfolderach w katalogu [`Server/server-patches/krystian/`](file:///d:/Github/MT2Plus/Server/server-patches/krystian). Każdy podfolder zawiera kompletną dokumentację `README.md`, skrypty instalacyjne oraz kody źródłowe / diffy. Zgodnie z **Zasadą nr 8**, jeśli dany fix/mod zostanie oficjalnie dodany w Upstream, jego moduł jest oznaczany jako włączony w Upstream lub bezpiecznie usuwany.

| Podfolder w `server-patches/krystian/` | Typ / Warstwa | Pliki i Obszary Modyfikacji | Status |
| :--- | :--- | :--- | :--- |
| [`wstawanie-100hp`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/wstawanie-100hp) | Serwer (C++) | `game/src/cmd_general.cpp`, `char.cpp` (100% HP po ożywieniu) | **Aktywny** |
| [`autolowy-szybkie-zbieranie`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/autolowy-szybkie-zbieranie) | Klient (Python) | `Klient/pack/root/uiautohunt.py` (obszarowe podnoszenie dropu) | **Aktywny** |
| [`ukrycie-hp-celu`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/ukrycie-hp-celu) | Klient (Python) | `Klient/pack/root/uitarget.py` (usunięcie cyfrowego HP innych graczy/mobów) | **Aktywny** |
| [`tracker-bossow`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/tracker-bossow) | Klient + Serwer | Boss Tracker: aplikacja Windows, maintenance bot, patche serwera | **Aktywny** |
| [`sklep-160-slotow`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/sklep-160-slotow) | Serwer + Klient | `char_shop.cpp`, `ikarus_shop_manager.cpp`, `dualshop.py`, `offlineshopui.py` | **Aktywny** |
| [`recykling-bonusow`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/recykling-bonusow) | Serwer (Quest/C++) | `recykling_bonusow.quest`, Dozorca, wymiana 5b na dodania/zmianki | **Aktywny** |
| [`pierscien-teleportacji`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/pierscien-teleportacji) | Serwer (Quest) | Quest z dodatkowymi lochami i mapami Arezzo | **Aktywny** |
| [`seban-panel-ekonomia`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/seban-panel-ekonomia) | Web / Panel Seban | `Server/linux-port/overlays/seban-panel/` -> `docker/seban-panel/` (Centrum Gospodarki, YmirWork telemetria, interpretacja inflacji, Doradca Rotacji Botów Półautomat, optymalizacja collector.py batch insert & auto-pruning, indeksy idx_time na log.log/item_meta_log/refinelog, Page Visibility API w live-widget/player/economy_shops, cache dashboard totals & live-bots) | **Aktywny (Auto-Overlay)** |
| [`devgameplay`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/devgameplay) | Serwer + Klient | `char_skill.cpp`, `char.cpp`, `battle.cpp`, `input_main.cpp`, `char_battle.cpp`, `char_item.cpp`, `tp_bookmarks.quest`, `uipickmoney.py`, `uicommon.py`, `uiexchange.py` | **Aktywny** |
| [`fix-boty-gildia-exp-party`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/fix-boty-gildia-exp-party) | Serwer (C++) | `playerbot_manager.cpp`, `char.cpp` (zrzutki botów na ziemie gildii, party exp) | **Włączony w Upstream 2.32.0** |
| [`fix-podglad-ekwipunku-tooltipy`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/fix-podglad-ekwipunku-tooltipy) | Web / Panel Seban | `player.html`, `player-profile.css` (eliminacja ucinania dymków ekwipunku) | **Aktywny** |
| [`autofish`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/autofish) | Serwer (C++) + Klient | `char.h`, `char.cpp`, `cmd.cpp`, `cmd_general.cpp`, `game.py`, `uiautohunt.py` (Auto-Wędkowanie w tle / minimalizacja) | **Aktywny** |
| [`duze-czcionki-skilli-i-ilosci`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/duze-czcionki-skilli-i-ilosci) | Klient (UI/Zasoby) | `TaskBar.tga`, `0.sub`..`9.sub`, `m.sub`, `g.sub`, `p.sub` w `etc` (12px Bold z obrysem: 1-20, M1-M10, G1-G10, P, stacki 200) | **Aktywny** |
| [optymalizacja-autolowy-drop-redlas](file:///d:/Github/MT2Plus/Server/server-patches/krystian/optymalizacja-autolowy-drop-redlas) | Serwer + Klient + Baza | item.h/item.cpp, char_item.cpp, shop.cpp, ikarus_shop_manager.cpp, safebox.cpp, input_main.cpp, item_manager.cpp, char_battle.cpp, uiautohunt.py, uiminimap.py, item_proto (zniesienie limitu +-15 lvl, optymalizacja autołowów, pathfinding komnat w lochach małp, mapa Red Lasu, stack przedmiotów 200 (Medale, Zioła, Ryby, Perły, Małże, Przetopy, Bodziaki, Metale, Księgi), auto-stackowanie przy zakupie z AH/sklepu/depozytu, twarda blokada stackowania rynsztunku CanStack) | **Aktywny** |
| [`oferty-blyskawiczne-is`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/oferty-blyskawiczne-is) | Serwer + Klient + Baza + Panel | `itemshop_manager.cpp/h`, `main.cpp`, `92_itemshop_flash_offers.sql`, `itemshop.py` (seban-panel), `game.py`, `uiitemshop.py`, `itemshop_shopwindow.py`, `gamedata` ikony (pula 100 ofert Hard Edition, rotacja 10/100 co 30 min, odliczanie czasu, auto-zerowanie limitów, synchro CH1-4) | **Aktywny** |
| [`odblokowanie-kostiumow-arezzo`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/odblokowanie-kostiumow-arezzo) | Serwer (C++ / Web) | Odpięcie 22 zestawów kostiumów, fryzur i szarf Arezzo od flagi lochów Arezzo – pełna dostępność w ItemShopie (gra + WWW) przy wyłączonych dungeonach/mapach (`M2_AREZZO=0`). | **Aktywny** |
| [`pierscienie-czas-noszenia`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/pierscienie-czas-noszenia) | Serwer (C++ / Baza) + Klient | `item.cpp`, `ItemAwardManager.cpp`, `item_proto` (vnum 71145, 71149, 71148, 71136, 71135, 71143: czas ucieka tylko gdy założone `LIMIT_TIMER_BASED_ON_WEAR = 9`), fix kasowania unique item po 60s, `uitooltip.py` | **Aktywny** |
| [`recykling-broni-30`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/recykling-broni-30) | Serwer (C++) | `playerbot_gear.h`, `playerbot_economy.h`, `playerbot_upstream_botlogic.h` (ochrona perełek L30 >=25% śr, kowal sink do +6, sprzedaż śmieci u handlarki) | **Aktywny** |
| [`kolekcjoner-autodrop`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/kolekcjoner-autodrop) | Serwer (C++) + Klient (Python) | `playerbot_collector.cpp/h`, `char_item.cpp`, `char.cpp`, `input_login.cpp`, `uicollector.py` (checkbox auto-dropu do magazynu kolekcjonera przy pełnym EQ, stack merge, account flag) | **Aktywny** |
| [`sesja-farmienia`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/sesja-farmienia) | Klient (Python) | `farmsession.py`, `farmsession_prices.py`, `uifarmsession.py`, `keybind.py`, `interfacemodule.py`, `game.py`, `uiinventory.py` (okno Sesji Farmienia, wycena Rynkowa z baza 3250 cen / NPC -3%, liczniki Metinow/Bossow/Yang, tempo /h, mini-HUD) | **Aktywny** |
| [`odnawianie-sklepow-botow`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/odnawianie-sklepow-botow) | Serwer (C++) | `char_shop.cpp`, `ikarus_shop_manager.cpp`, `playerbot_offline_shop.h` (zdjęcie ograniczeń slotów/premium gracza dla botów przy reopenie, automatyczne odnawianie 4-stronicowych sklepów offline botów) | **Aktywny** |
| [`dom-aukcyjny-historia`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/dom-aukcyjny-historia) | Klient (Python) | `Klient/pack/root/uiauctionhouse.py` (Przycisk "Historia" obok Reset, okno historii zakupów, tooltip z bonusami/KD, wyszukiwanie 1-klik, czyszczenie, bufor JSON) | **Aktywny** |
| [`kolekcjoner-refine`](file:///d:/Github/MT2Plus/Server/server-patches/krystian/kolekcjoner-refine) | Serwer (C++) + Klient (Python) | `playerbot_collector.cpp/h`, `char_item.cpp`, `input_login.cpp`, `uirefine.py`, `uicollector.py` (pobieranie ulepszaczy z magazynu kolekcjonera u kowala i zwojami z priorytetem EQ, silent sync, zielony licznik w UI) | **Aktywny** |

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
8. **Katalog Autorskich Modyfikacji (`Server/server-patches/krystian/`) i Cykl Życia Dodatków:** Wszystkie autorskie modyfikacje, fixy i rozszerzenia serwera/klienta są utrzymywane w czytelnych podfolderach w `Server/server-patches/krystian/`. Jeżeli w nowym wydaniu Upstream oficjalnie wprowadził fixa lub funkcjonalność, którą wcześniej realizowaliśmy własnym modułem, dany dodatek można **bezpiecznie oznaczyć lub usunąć**, przechodząc w pełni na oficjalny kod bazowy.
9. **Synchronizacja Stanu Launchera Windows:** Przy każdej zmianie wersji serwera należy zaktualizować zarówno `Server/VERSION`, jak i plik `Server/.m2launcher-state.json`, aby GUI launchera (`Metin2-Launcher-GUI.bat`) natychmiast odczytywało aktualny stan wersji.
10. **Raportowanie Poprawek z Discorda (Standard Opisu Błędów i Instalacji):**
    - W przypadku naprawy błędu pochodzącego ze zgłoszeń społeczności Discord (gdy użytkownik wskaże, że problem pochodzi z Discorda), asystent po wdrożeniu fixa bezwzględnie generuje zwięzły opis w formacie Markdown dla graczy na Discordzie zawierający:
      1. **Co dokładnie naprawia ten fix**
      2. **Dlaczego funkcja wcześniej nie działała (przyczyna techniczna / root cause)**
      3. **Krótki opis jak zainstalować** (proste, precyzyjne kroki dla graczy pobierających udostępniony plik `.zip` / `.rar`; pamiętać, że `Server/server-patches/krystian/` to wyłącznie nasz wewnętrzny katalog projektowy, a społeczność na Discordzie otrzymuje bezpośrednią paczkę archiwum).
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
          2. **Automatyczny backup bazy (Zero-Data-Loss) i rotacja (retencja 2 dni):** Wykonaj pełną kopię zapasową bazy danych do katalogu `Server/backups/` (używając akcji launchera `BackupDb` lub procedury tworzenia zrzutu `.zip`). **Reguła czyszczenia:** Przy każdym tworzeniu kopii zapasowej (lub w celu zwolnienia miejsca na dysku) usuwaj stare backupy (`.zip` oraz rozpakowane foldery zrzutów w `Server/backups/`), które mają **więcej niż 2 dni** (starsze niż 48h). Chroni to dysk przed zapełnieniem, zachowując najświeższy punkt przywracania.
          3. **Aplikacja zmian:** Wprowadź zaplanowane modyfikacje kodu, schematów SQL, konfiguracji lub plików dodatków.
          4. **Uruchomienie i weryfikacja:** Uruchom serwer ponownie (`docker compose up -d`) i zweryfikuj brak błędów w logach `docker logs` oraz `syserr` rdzeni (`all cores up`).
      - **B. ZMIANY PO STRONIE KLIENTA / DOKUMENTACJI (Skrypty Pythona klienta, pakowanie paczek w `Klient/pack/`, edycja `PROJECT_CONTEXT.md`, narzędzia w `Server/tools/`):**
        - **Brak przestojów:** Ponieważ te operacje w ogóle nie ingerują w procesy ani wolumeny bazy danych serwera, **serwera NIE trzeba wyłączać** – może bezpiecznie działać w tle, oszczędzając czas.

13. **Żelazna Zasada Końcowej Publikacji GitHub Release przy `[DOCS]` / `[RELEASE]`:**
    - Procedura `[DOCS]` / `[RELEASE]` **nigdy nie kończy się** na samym commitowaniu, pushu do gita czy wygenerowaniu tekstu changelogu.
    - **Na sam koniec każdego wydania asystent ma bezwzględny obowiązek utworzyć i opublikować wydanie na GitHub Releases**, dołączając do niego obie gotowe paczki aktualizacyjne (`metin2-server-update-*.zip` oraz `metin2-client-update-*.zip` ze zintegrowanymi naszymi autorskimi modyfikacjami) oraz udostępniając użytkownikowi bezpośredni link do opublikowanego wydania na GitHubie.

14. **Zasada Higieny Dysku i Konserwacji Środowiska (Disk Hygiene & Space Reclamation Guard):**
    - W miarę intensywnych prac deweloperskich, testów w grze i budowania wydań, środowisko lokalne generuje pliki tymczasowe i logi, które mogą niekontrolowanie zająć wiele gigabajtów dysku:
      - **A. Logi błędów klienta (`Klient/syserr.txt`):** W przypadku zapętlonych ostrzeżeń graficznych lub brakujących pakietów plik ten potrafi szybko urosnąć do ponad 1–2 GB. Jest to plik czysto diagnostyczny – można go w dowolnym momencie bezpiecznie usunąć lub wyzerować (klient utworzy świeży plik przy kolejnym starcie gry).
      - **B. Kompresja, retencja i czyszczenie kopii zapasowych (`Server/backups/`):**
        - Kopie zapasowe baz danych zawsze należy przechowywać w postaci skompresowanej (`.zip`). Rozpakowane foldery z surowymi zrzutami SQL (w szczególności wielogigabajtowy plik `log.sql`) stanowią zbędną duplikację i powinny być usuwane po utworzeniu archiwum `.zip`, co oszczędza od 2 do 3 GB miejsca.
        - **Żelazna Zasada Retencji 2 Dni (Usuwanie Starych Backupów):** Zarówno **podczas procedury tworzenia nowego backupu**, jak i **podczas rutynowego czyszczenia dysku w celu zwiększenia wolnego miejsca**, należy bezwzględnie usuwać stare kopie zapasowe (zarówno pliki `.zip`, jak i niespakowane katalogi w `Server/backups/`), które mają **więcej niż 2 dni (starsze niż 48 godzin)**. Utrzymywanie wyłącznie kopii z ostatnich 2 dni w zupełności wystarcza do bezpiecznego powrotu po awarii, a zapobiega gromadzeniu się dziesiątek gigabajtów starych zrzutów baz danych.
        - *Polecenie czyszczenia starych backupów (> 2 dni) w PowerShell:*
          ```powershell
          Get-ChildItem -Path "Server/backups" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-2) } | Remove-Item -Recurse -Force
          ```
      - **C. Czyszczenie bufora wydań (`dist/`):** Katalog `dist/` służy wyłącznie jako tymczasowy bufor roboczy skryptu `build_release_packages.py`. Po pomyślnej publikacji paczek na GitHub Releases, cała zawartość `dist/` może zostać bezpiecznie wyczyszczona do zera (~1.4 GB oszczędności).
      - **D. Tymczasowe kopie pakerów i modułów (`Klient/pack/*.bak` oraz `Klient/backup-*`):** Automatyczne kopie `.bak` tworzone przez paker przy zapisie paczek (`root.data.bak` itp.) oraz foldery tymczasowe po testach modułów można bezpiecznie usuwać po zweryfikowaniu stabilności gry.

15. **Żelazna Zasada Bezwzględnej Synchronizacji Patchera po Nowych Modyfikacjach / Zmianach (Patcher Guard Rule):**
    - Patcher gry (`MT2009-Patcher.exe`) weryfikuje sumy kontrolne MD5 wszystkich plików klienta z listą `patchlist.json` na serwerze CDN (`gh-pages`).
    - Każda modyfikacja skryptów Pythona, interfejsów w `Klient/pack/root/` (np. autołowy, dom aukcyjny, sklep, okno kostiumów, UI), zmiana parametrów czy dodanie nowej funkcji oraz rekompilacja paczek do `root.data` i `root.index` zmienia sumy MD5 tych archiwów.
    - **Twardy wymóg workflow (Zawsze Zaktualizowany Patcher):** Przy **każdych** nowych modyfikacjach lub zmianach w plikach klienta asystent i deweloper mają **bezwzględny obowiązek ZAWSZE na zakończenie zadania zaktualizować i zsynchronizować serwer aktualizacji patchera** poleceniem:
      ```powershell
      python Server/tools/publish_patcher_web.py
      ```
    - **Zakaz zamykania zadania bez synchronizacji CDN:** Żadne zadanie dotyczące zmian w kliencie gry nie może zostać uznane za ukończone przed pomyślnym wykonaniem powyższego skryptu i wypchnięciem zmian na gałąź `gh-pages`.
    - **Konsekwencje zaniechania:** Jeżeli pliki na CDN nie zostaną natychmiast zaktualizowane, uruchomienie gry przez `MT2009-Patcher.exe` potraktuje lokalne modyfikacje jako "uszkodzone/niezgodne" i natychmiast **pobierze starszą wersję z CDN, bezpowrotnie nadpisując autorskie zmiany w `root.data`**. Synchronizacja patchera jest integralną, obowiązkową częścią każdego taska modyfikującego klienta.

