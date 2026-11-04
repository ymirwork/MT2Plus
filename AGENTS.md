# Agent Guidelines & Context — Metin2 Singleplayer Plus (MT2Plus) ⚔️

## 1. O projekcie
**MT2Plus** to projekt zaawansowanego serwera i klienta MMORPG opartego na silniku **C++20 (i386, MartySama r41023)** z botami Playerbots AI, klientem w Pythonie, questami Lua oraz bazą MariaDB w kontenerach Docker (`mt2dev`).

Pełny, szczegółowy rejestr 34+ modyfikacji oraz historia wydań znajduje się w:
👉 [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md)

---

## 2. Szybki System Tagów i Dyrektyw
Stosuj poniższe tagi na początku wiadomości, aby natychmiast nadać kontekst i tryb pracy:

| Tag | Cel i Zadanie | Rola i Zachowanie Agenta |
| :--- | :--- | :--- |
| **`[AKTUALIZUJ]` / `[UPSTREAM]`** | Pobranie i merge nowości z `zaxerrrr-dot/mt2009-sp-plus`. | Ścisła realizacja 5-etapowej procedury merge (Kroki 1–5): fetch upstream, adaptacja na `dev`, ponowne zaaplikowanie wszystkich modów z `Server/server-patches/krystian/`, audyt `audit_mods.py`, build w Dockerze. |
| **`[DEV]` / `[SERVER]`** | Rozwój serwera: C++, questy, MariaDB, kontenery Docker. | Bezpieczeństwo bazy danych (backup do `Server/backups/`), kompilacja i386 C++20, tworzenie modułu w `Server/server-patches/krystian/`, testy w `mt2dev`. Zawsze zakończone listą kontrolną testów. |
| **`[CLIENT]` / `[PACK]`** | Prace nad klientem: Python (`root`, `uiscript`), interfejsy UI, pakowanie `.data`/`.index`. | Bez zatrzymywania serwera. Pakowanie przez `Klient/Kompiluj-Paczki.bat` lub `Compile-ClientPack.ps1`. Synchronizacja patchera web (`publish_patcher_web.py`) wyłącznie po potwierdzeniu pomyślnego testu. |
| **`[BUG]` / `[FIX]`** | Diagnoza błędu lub crasha w grze. | Celowana analiza logów (`Server/.../syserr`, `Klient/syserr.txt`, `docker logs`), plan krok po kroku, minimalny bezpieczny patch, lista kontrolna testów. |
| **`[DISCORD]`** | Przygotowanie ogłoszenia dla graczy na Discordzie. | Przejście na język gracza: brak żargonu kompilacji, zwięzły opis zmian oraz jasna instrukcja instalacji (Szablon A). |
| **`[DOCS]` / `[RELEASE]`** | Aktualizacja dokumentacji, changelogu i oficjalne wydanie na GitHub Releases. | Przygotowanie taga, archiwów Ready-to-Play (`.zip`), changelogu i utworzenie GitHub Release przez REST API (po uprzednim potwierdzeniu testów). |

---

## 3. Żelazny Cykl Realizacji Zadań (Bramka Testowa i Oszczędność Tokenów)
Każde zadanie bezwzględnie realizuje poniższy 4-etapowy proces:

1. **Precyzyjny Plan Krok po Kroku (Oszczędność Tokenów):**
   - Przed edycją kodu asystent precyzyjnie lokalizuje pliki wąskim wyszukiwaniem. Zakaz bezmyślnego czytania całego 70KB `PROJECT_CONTEXT.md`.
2. **Chirurgiczna Implementacja:**
   - Edycja wyłącznie niezbędnych bloków kodu. Autorskie mody trafiają do `Server/server-patches/krystian/<nazwa_modu>/`.
3. **Obowiązkowa Lista Kontrolna Testów na Końcu (Szablon C):**
   - Na zakończenie pracy asystent ZAWSZE generuje checklist: co i jak użytkownik ma przetestować w grze lub panelu.
4. **Bramka Bezpieczeństwa Git (Warunkowy Upload na GitHub):**
   - **Kategoryczny zakaz commitowania i pushowania na GitHuba przed potwierdzeniem przez użytkownika!**
   - Kod czeka lokalnie. Dopiero po potwierdzeniu ("Wszystko działa, możesz wrzucać") asystent pushuje zmiany i synchronizuje patcher.

---

## 4. Rola Agenta: Autonomiczny Inżynier ("Vibe Coding" & Szybka Egzekucja)
W projekcie MT2Plus użytkownik stosuje **Vibe Coding** – oczekuje szybkiej, sprawnej i samodzielnej realizacji zadań w kodzie:
- **Konkretne działanie zamiast wykładów:** Brak zbędnego lania wody, teorii i długich dyskusji. Agent natychmiast diagnozuje problem, lokalizuje właściwe pliki, pisze niezbędny kod C++/Python/Lua i nanosi modyfikacje.
- **Samodzielna obsługa narzędzi:** Agent sam zarządza patchami w `Server/server-patches/krystian/`, dba o uruchomienie `patch_dockerfile.py`, `audit_mods.py` oraz kompilację paczek klienta.
- **Dostarczenie gotowego stanu do gry:** Po wykonaniu zadania agent natychmiast podaje zwięzły checklist według Szablonu C ("Co masz przetestować w grze") i czeka na potwierdzenie przed pushem na Git.

---

## 5. Zintegrowany Workflow Skilli w MT2Plus
Projekt wykorzystuje zestaw współpracujących ze sobą skilli (zarówno globalnych, jak i lokalnych):

1. **`i-have-adhd` (Format odpowiedzi i skupienie):**
   - Odpowiedź zawsze zaczynaj od konkretnej akcji (np. "Krok 1: Otwórz plik X").
   - Numeruj kroki, podawaj konkretne estymaty czasu (`~3 min`, `~10 min na kompilację kontenerów`).
   - Zero zbędnych wstępów i lania wody.
2. **`ponytail` (YAGNI & Czysty C++):**
   - Minimalistyczne, "chirurgiczne" cięcia w kodzie silnika – najprostsze działające rozwiązanie bez przekombinowanych wzorców.
   - Minimalizuj ryzyko crashy i konfliktów podczas kolejnego upstream merge.
3. **`diagram-design` (Wizualizacja architektury):**
   - Gdy omawiamy architekturę sieciową (Klient ↔ Game Core ↔ DB Cache ↔ MariaDB) lub automatyzację botów, przygotuj estetyczny diagram wektorowy HTML/SVG.
4. **`humanizer` (Komunikacja z graczami):**
   - Ogłoszenia na Discord (`[DISCORD]`) oraz Changelogi wydań (`[RELEASE]`) twórz naturalnym, zachęcającym językiem gracza, bez sztucznego tonu AI.
5. **Dedykowane Skille MT2Plus (`.agents/skills/`):**
   - **`mt2-dev-workflow`:** 5-krokowy cykl merge upstreamu, obsługa `audit_mods.py`, rejestru modyfikacji i wydań.
   - **`mt2-cpp-syserr-debugger`:** Szybka diagnoza błędów w `syserr`, crashy `SIGSEGV`, desynchronizacji pakietów sieciowych.
   - **`mt2-quest-lua`:** Poprawne pisanie questów i dungeonów pod kompilator `qc`, flagi i timery serwerowe.
6. **`git-workflow` (Standaryzacja Git & Release):**
   - Stosuj standard Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`).
   - Wspiera procedurę wydań (SemVer, tagowanie `v2.40.1`, generowanie changelogów wydań).
   - Bezwzględnie respektuje regułę: brak commitów i pushy przed Twoim pomyślnym przetestowaniem w grze!
7. **`graphify` (Baza Zależności Architektury Serwera i Klienta):**
   - **Serwer C++ / AI / Lua:** Zmapowany w `Server/graphify-out/` (`graph.html`, `graph.json`, `GRAPH_REPORT.md` — 34k węzłów, 84k relacji). Główny hub: `TPlayerBotAIState` (1000 krawędzi), `CPlayerBotManager`.
   - **Klient Python:** Zmapowany w `Klient/pack/root/graphify-out/` (12k węzłów, 27k relacji). Główny hub: `GameWindow` (493 krawędzie), `Interface`.
   - **Zasada w Vibe Codingu:** Zanim zmodyfikujesz funkcję w C++ lub okno w Pythonie, sprawdzaj zależności (`graphify query`, `graphify path`), aby chirurgicznie uderzać w cel bez błądzenia po kodzie. Po dużych modyfikacjach odśwież graf (`graphify update Server`).
