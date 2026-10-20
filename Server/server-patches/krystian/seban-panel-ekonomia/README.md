# Seban Panel: Rozszerzona Ekonomia V2 (Moduł YmirWork / Krystian)

Rozszerzenie panelu administracyjnego i monitoringu gospodarki serwera (Flask / Web).

## Funkcjonalności
- **Centrum Gospodarki i Podgląd Rynku:**
  - Klikalne przedmioty w podglądzie rynku przenoszące bezpośrednio do szczegółowej analizy `/economy/item/<vnum>`.
  - Wykluczenie kont i postaci administracyjnych (`Admin%`, `[%`, `gmlist`) z rankingu Największych Posiadaczy danego przedmiotu.
  - Pełna obsługa Ksiąg Umiejętności (VNUM 50300) z podziałem i filtrowaniem wg konkretnych skilli (`?skill=<ID>`), selektorem umiejętności oraz tabelą zbiorczą.
  - Zaawansowany panel telemetrii YmirWork: karty bilansu dobowego (Faucet/Sink/Boty), monitorowanie obiegu Zaczarowań/Wzmocnień (71284/71285), wskaźniki skupu botów (1% – 35%), interpretacja inflacji oraz kosztu przetopień.
  - Tabela ostatnich operacji przetopień z interaktywnym tooltipem z dokładną datą i czasem rejestracji (`dd.mm.yyyy HH:MM:SS`).
  - Statystyki emerytur i bilansu majątku botów (`retired_bots.html`).
  - **Półautomatyczny Doradca Rotacji Botów (Emerytury Półautomat):**
    - Dynamiczny algorytm oceniający gotowość serwera do rotacji (`get_bot_retirement_advisor()`): liczba botów 35+, 40+, 50+, średni lvl oraz czas od ostatniej partii (strażnik cooldownu $\ge$12h/24h).
    - Statusy gotowości: 🔴 Za wcześnie (ochrona przed wyludnieniem i niszczeniem gameplayu), 🟡 Umiarkowany (mała rotacja 30 botów), 🟢 Optymalny (pełna partia 60 botów).
    - Dedykowana karta z paskiem gotowości (%), wyjaśnieniem dlaczego warto lub nie warto teraz resetować botów oraz szybkim przyciskiem 1-klik `[ Zastosuj rekomendację doradcy ]`.
    - Pasek doradcy na stronie głównej Centrum Gospodarki (`/economy`) z linkiem do asystenta.
- **Optymalizacja wydajności bazy danych i kolektora (`collector.py`):**
  - **Zbiorcze wstawianie pozycji (Batch Insert):** Zastąpienie pętli 1800 pojedynczych `cur.execute` jednym zapytaniem `cur.executemany`, co redukuje ponad 500 000 zapytań SQL na dobę.
  - **Automatyczna retencja i czyszczenie (Auto-Pruning):** Usuwanie starych migawek oraz tabel logów gry na koniec każdego cyklu z limitem `LIMIT 50000` (pozycje botów: 48h, przedmioty: 15 dni, sklepy: 30 dni, mapy i system: 14 dni, `log.log`, `log.item_meta_log`, `log.ikarusshop_log`, `log.refinelog`: 30 dni), zapobiegając rozrastaniu się bazy do setek milionów wierszy.
  - **Indeksy optymalizacyjne (`idx_time`):** Dodanie indeksów na kolumnie `time` w tabelach `log.log`, `log.item_meta_log` i `log.refinelog`, eliminujące operacje Full Table Scan na milionach rekordów podczas zapytań czasowych i czyszczenia.
- **Optymalizacja backendu Flask (`app.py`):**
  - **Pamięć podręczna metryk dashboardu (`get_dashboard_totals`):** Współdzielony cache (TTL 30s) dla kosztownych przeliczeń `COUNT(*)` tabeli `player.item` (240k wierszy) oraz `SUM(gold)`, eliminujący podwójne wykonanie przy renderowaniu strony głównej i asynchronicznym wywołaniu `/api/dashboard-deferred`.
  - **Mikro-cache dla `/api/live-bots` i rankingów:** Zapamiętywanie wyliczeń rankingu top 10 (15s), przełączników bazy (30s) oraz odpowiedzi live mapy (1.5s), co drastycznie odciąża MariaDB przy wielu otwartych kartach.
- **Optymalizacja frontendu (Page Visibility API):**
  - Wdrożenie nasłuchu `document.hidden` oraz zdarzenia `visibilitychange` w `static/live-widget.js`, `templates/player.html` i `templates/economy_shops.html`.
  - Wstrzymywanie pętli odpytywania (1.5s mapa live, 5s stan ekwipunku, 1.5s logi live, 20s feed sprzedaży), gdy karta przeglądarki jest zminimalizowana lub nieaktywna, oraz natychmiastowe odświeżenie danych po powrocie użytkownika.
- **Warstwa wizualna i skrypty:**
  - `collector.py`, `app.py`.
  - `templates/economy.html`, `templates/economy_item.html`, `templates/economy_shops.html`, `templates/retired_bots.html`, `templates/player.html`.
  - `static/market-preview.css`, `static/market-preview.js`, `static/live-widget.js`.
  - `market_preview/__init__.py`.

## Zastosowanie
Instalowany w `Server/linux-port/overlays/seban-panel/` -> `docker/seban-panel/`.
