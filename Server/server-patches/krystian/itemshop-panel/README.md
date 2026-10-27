# ItemShop i Smocze Monety - Kompleksowa Modernizacja i Narzędzia GM

**Autor:** Krystian  
**Data:** 2026-10-27  
**Wersja:** 1.0.0 (dla MT2Plus v2.38.0 / mod-60+)  
**Status:** Aktywny  

---

## 1. Cel Modyfikacji

Kompleksowa modernizacja i rozbudowa modułu administracyjnego ItemShopu (`/economy/itemshop`) w panelu Seban:
1. **Eliminacja błędów kodowania (Mojibake):** Usunięcie uszkodzonych znaków i symboli Unicode w nagłówkach i etykietach na rzecz czystego UTF-8 i nowoczesnej estetyki.
2. **Pełna spójność wizualna z motywem "Cesarstwo" (Empire) oraz motywem ciemnym:**
   - Dedykowane reguły dla `body[data-theme="empire"]`:
     - Płaskorzeźbione kafelki z charakterystycznymi ciętymi rogami (`clip-path: polygon(...)`),
     - Imponujące nagłówki szeryfowe w kroju `'Cinzel'`,
     - Złociste obramowania (`--edge`, `--gold`),
     - Przyciski w kolorystyce cesarskiego złota (`#e8b93f`) i karmazynowego ognia (`#c94a2a`),
     - Wykres Chart.js z dynamiczną paletą dostosowaną do aktywnego motywu (złota linia obrotu SM + płomienne słupki liczby transakcji).
3. **Wzbogacenie rejestru zakupów (`log.itemshop`):**
   - Wyświetlanie ikonek kupowanych przedmiotów (`item_icon_url`),
   - Ilość zakupionych sztuk (`quantity`),
   - Dokładna cena i czytelny badge waluty (złoty SM vs niebieski SZ),
   - Saldo kupującego przed realizacją transakcji (`money_before`),
   - Bezpośredni link do postaci kupującego (`/player/<pid>`) oraz login konta wraz z odróżnieniem graczy od botów.
4. **Inteligentny filtr widoku (Wszyscy / Tylko gracze / Tylko boty):**
   - Zapobiega zniekształcaniu statystyk finansowych i wykresów przez automatyczne zakupy playerbotów (~964 kont botów).
   - Przełącznik w postaci pillsów na górze strony (`?view=all`, `?view=players`, `?view=bots`).
5. **Wskaźniki analityczne i wykres obrotu:**
   - Prezentacja realnego wolumenu wydatków SM/SZ w ujęciu dziennym z ostatnich 14 dni (wykres Chart.js z podwójną osią: linia obrotu SM + słupki liczby transakcji).
   - Karty KPI: SM w obiegu, SZ w obiegu, łączny obrót SM, łączny obrót SZ, łączna liczba transakcji.
6. **Narzędzie szybkiego doładowania / korekty walut kont (`/economy/itemshop/grant`):**
   - Bezpośrednie doładowanie lub odjęcie SM / SZ po wpisaniu loginu konta lub nicku dowolnej postaci tego konta.
   - Szybkie przyciski kwot (`+100`, `+500`, `+1 000`, `+5 000`, `-100`, `-500`).
   - Bezpiecznik `GREATEST(0, ...)` zapobiegający ujemnym saldom.
   - Zapis operacji w `log.log` (`PANEL_ITEMSHOP_GRANT`) z audytem wartości przed i po oraz notatką administratora.
   - Błyskawiczny skrót `⚡` przy każdym koncie na liście Top i w historii zakupów automatycznie uzupełniający pole formularza.
7. **Podgląd Aukcji Błyskawicznych i Ofert Czasowych:**
   - Karty aktywnych aukcji pobierane z `common.itemshop_time_auctions` + `common.itemshop_items` + `player.item_proto` (ikonka, nazwa, cena SM/SZ, limit na konto, pula sztuk).
8. **Przeładowanie ItemShopu w grze (`/economy/itemshop/reload`):**
   - Przycisk wysyłający natychmiastowe polecenie `queue_gm_command("ISHOP_RELOAD")` (/reload i) bez konieczności restartu serwera.
9. **Ranking najbardziej dochodowych przedmiotów (Top 10):**
   - Tabela z rankingiem przedmiotów generujących największy przychód SM i SZ wraz z wolumenem sprzedaży.
10. **Wyszukiwarka na żywo w historii zakupów:**
   - Błyskawiczne filtrowanie w tabeli po nazwie przedmiotu, kupującym, loginie konta lub numerze VNUM.

---

## 2. Architektura i Przepływ Danych

1. **Backend Flask (`app.py`)**:
   - `GET /economy/itemshop`: Parametr `view` filtruje zapytania SQL (`login LIKE/NOT LIKE 'playerbot_%'`).
   - `POST /economy/itemshop/grant`: Walidacja wejścia, mapowanie nicku postaci na `account.id`, aktualizacja `account.account.cash` lub `cash_mark`, wpis do `log.log`, odpowiedź JSON.
   - `POST /economy/itemshop/reload`: Uruchamia `queue_gm_command("ISHOP_RELOAD")` przez kolejkę `player.web_admin_queue`.
2. **Frontend Jinja2 / Chart.js (`economy_itemshop.html`)**:
   - Spójny layout z systemem szablonów Seban (`base.html`), obsługa stylizacji dynamicznej pod motyw Cesarstwo (`data-theme="empire"`), asynchroniczne fetch requests z powiadomieniami toast (`#is-toast`), interaktywny wykres Chart.js 4.4.7.

---

## 3. Pliki Objęte Modyfikacją

- `Server/linux-port/docker/seban-panel/app.py`
- `Server/linux-port/overlays/seban-panel/app.py`
- `Server/linux-port/docker/seban-panel/templates/economy_itemshop.html`
- `Server/linux-port/overlays/seban-panel/templates/economy_itemshop.html`
- `Server/linux-port/docker/docker-compose.yml` (przebudowany obraz `metin2/seban-panel:latest`)
