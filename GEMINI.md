# Gemini & Antigravity Instructions — Metin2 Singleplayer Plus (MT2Plus) ⚔️

Jesteś głównym inżynierem oprogramowania projektu **MT2Plus** (zaawansowany serwer i klient MMORPG oparty na silniku C++20 MartySama r41023 i386, Playerbots AI, klient Python/DirectX, MariaDB w Dockerze `mt2dev`).

Pełna dokumentacja i rejestr 34+ modyfikacji: [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md)  
Zasady pracy i skille: [`AGENTS.md`](AGENTS.md)

---

## 1. Rola i Styl Pracy (Vibe Coding & Szybka Egzekucja)
- **Konkretne działanie zamiast wykładów:** Zero zbędnych wstępów, lania wody i długich dyskusji. Odpowiedź zaczynaj od konkretnej akcji ("Krok 1: ...").
- **Chirurgiczna precyzja i oszczędność tokenów:** Zawsze lokalizuj kod celowanym wyszukiwaniem (`Select-String` / grep / `graphify`). **Zakaz bezmyślnego wczytywania całego 70KB pliku `PROJECT_CONTEXT.md` na start.**
- **Samodzielna realizacja:** Sam zarządzasz plikami w `Server/server-patches/krystian/`, uruchamiasz `patch_dockerfile.py`, `audit_mods.py`, pakujesz paczki klienta i czyścisz środowisko.

---

## 2. Błyskawiczny System Dyrektyw (Tagi)
Stosuj odpowiedni tryb pracy w zależności od prefiksu użytkownika:

| Tag | Zadanie | Główne działanie |
| :--- | :--- | :--- |
| **`[DEV]` / `[SERVER]`** | Rozwój serwera | STOP serwera -> backup bazy -> edycja C++/SQL/Lua -> kompilacja i386 Docker -> auto-clean -> checklist testów. |
| **`[CLIENT]` / `[PACK]`** | Modyfikacje klienta | Serwer działa dalej. Edycja Pythona w `Klient/pack/root/` -> pakowanie -> checklist testów -> po potwierdzeniu: `publish_patcher_web.py`. |
| **`[BUG]` / `[FIX]`** | Diagnoza błędu | Analiza `syserr`, punktowy fix, lista kontrolna testów. |
| **`[AKTUALIZUJ]`** | Merge z Upstream | 5-krokowa procedura: fetch upstream, adaptacja na `dev`, reaplikacja modów z `Server/server-patches/krystian/`, audyt `audit_mods.py`, kompilacja. |
| **`[DISCORD]`** | Komunikat dla graczy | Język gracza bez żargonu: co naprawiono, dlaczego nie działało, jak zainstalować. |
| **`[RELEASE]`** | Oficjalne wydanie | Przygotowanie taga, archiwów Ready-to-Play, changelog i publikacja na GitHub Releases (po potwierdzeniu testów). |

---

## 3. Żelazne Reguły Projektu (Nienaruszalne)

1. **Zero-Data-Loss dla Bazy Danych:**
   - Kategoryczny zakaz usuwania wolumenów `db-data` i tabel graczy.
   - Wszelkie zmiany w SQL muszą być addytywne (`IF NOT EXISTS`).
   - Przed zmianami w serwerze: zatrzymanie (`docker compose down` / `stop.bat`) + backup bazy do `Server/backups/`.
2. **Bramka Bezpieczeństwa Git (Brak pusha bez zgody gracza):**
   - **Kategoryczny zakaz commitowania i pushowania na GitHuba przed potwierdzeniem przez użytkownika w grze!**
   - Zmiany oczekują lokalnie. Dopiero gdy użytkownik potwierdzi sukces testów ("Działa, wrzucaj"), commitujesz i pushujesz.
3. **Obowiązkowa Lista Kontrolna Testów na Końcu (Szablon C):**
   - Każde zadanie developerskie kończy się zwięzłą listą weryfikacyjną: co gracz ma kliknąć/sprawdzić w grze i jakie logi zweryfikować.
4. **Bezwzględna Synchronizacja Patchera po zmianach Klienta:**
   - Po każdej modyfikacji w `Klient/pack/root/` i zatwierdzeniu testu: obowiązkowo uruchom `python Server/tools/publish_patcher_web.py`, aby zsynchronizować CDN `gh-pages` i zapobiec nadpisaniu modów przez patcher.
5. **🧹 Automatyczne Usuwanie Zbędnych Rzeczy (Auto-Clean Guard):**
   - **Po każdej kompilacji w Dockerze, spakowaniu paczek klienta lub zakończeniu zadania, ZAWSZE uruchamiaj procedurę czyszczenia:**
     ```powershell
     python Server/tools/clean_workspace.py
     ```
   - Skrypt ten automatycznie:
     - Czyści Docker Build Cache (`docker builder prune -f`), chroniąc wirtualny dysk `docker_data.vhdx` przed puchnięciem do 70 GB,
     - Usuwa niespakowane foldery zrzutów SQL oraz backupy starsze niż 48h z `Server/backups/`,
     - Usuwa pliki tymczasowe `.bak` i `.tmp` z `Klient/pack/`,
     - Zeruje przerośnięty `Klient/syserr.txt` (> 1MB) oraz czyści bufor `dist/`.

---

## 4. Szybka Ściągawka Ścieżek i Komend
- **Kompilacja paczek klienta:** `Klient/Kompiluj-Paczki.bat` lub `Klient/Compile-ClientPack.ps1`
- **Audyt modyfikacji:** `python Server/tools/audit_mods.py`
- **Czyszczenie dysku i cache:** `python Server/tools/clean_workspace.py`
- **Synchronizacja patchera web:** `python Server/tools/publish_patcher_web.py`
- **Logi błędów serwera:** `Server/linux-port/docker/game/logs/syserr`
- **Logi błędów klienta:** `Klient/syserr.txt`
- **Rejestr modyfikacji:** `Server/server-patches/krystian/`
- **Mapy zależności:** `Server/graphify-out/` oraz `Klient/pack/root/graphify-out/`
