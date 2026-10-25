# Sesja Farmienia (Farming Session Tracker)

Autorski moduł śledzenia i analityki sesji dropu, zniszczonych Kamieni Metin, pokonanych Bossów oraz szacowanej wartości rynkowej łupów dla projektu **Metin2 Singleplayer Plus (MT2Plus)**.

---

## 1. Główne Funkcjonalności

- **Stoper i kontrola sesji:**
  - Dokładny stoper (czas trwania w formacie `HH:MM:SS`) oparty na monotonicznym zegarze `clientclock.Now()`.
  - Możliwość wstrzymania (`Wstrzymaj` / `Wznów`) oraz zresetowania sesji (`Reset`).
  - Domyślny skrót klawiszowy: **`F6`** (z możliwością zmiany w menu *Skróty klawiszowe*).
- **Zliczanie zniszczonych celów (Lewy panel):**
  - *Wszystkie źródła* (ogólna liczba zabitych potworów).
  - *Kamienie Metin* (liczba rozbitych metinów).
  - *Bossy* (liczba pokonanych bossów).
  - *Zdobyty EXP* (zdobyte punkty doświadczenia oraz awanse).
- **Podsumowanie finansowe (Finanse):**
  - *Przełącznik trybu wyceny:* **Rynkowa** (sugerowana ze sklepów offline i bazy rynku botów ~3250 pozycji) vs **NPC** (wartość sprzedaży u handlarza po potrąceniu podatku 3%).
  - *Surowe Yang* – czysta waluta podniesiona z ziemi.
  - *Wartość łupów* – suma wartości zebranych przedmiotów w wybranym trybie.
  - *Szacowana wartość* – całkowity dochód sesji (Surowe Yang + Łupy).
- **Wskaźniki tempa (Propozycja 1 i 4):**
  - *Zarobek / godz.* (np. `~2.1 mld Yang / h`).
  - *Metiny / godz.* (np. `~320 Metin / h`).
  - *EXP / godz.* (np. `~120 M EXP / h`).
- **Lista zdobytych łupów (Prawy panel):**
  - Ikona przedmiotu wraz z pełnym dymkiem tooltipu (`ItemToolTip`).
  - Automatyczne skalowanie ikon (`ExpandedImageBox`) dla przedmiotów zajmujących 2 lub 3 sloty w pionie (np. łuki, miecze dwuręczne, zbroje) – ikony mieszczą się w kwadracie slotu 32x32 bez nachodzenia na sąsiednie wiersze.
  - Ilość i nazwa: `<ilość>x <Nazwa Przedmiotu>` (np. `3x Olbrz. Skrzydl. Łuk+2`).
  - Szacowana wartość danej pozycji w Yang (np. `280.000 Yang` rynkowo lub `194 Yang (NPC netto)`).
  - Wyszukiwarka w czasie rzeczywistym (pole tekstowe filtrujące po nazwie).
  - Przycisk **Cena** – otwiera okno dialogowe pozwalające nadać **własną, indywidualną wycenę rynkową** za sztukę (z obsługą skrótów `k`, `kk`, `m`, `b`), która nadpisuje ceny sugerowane i zapisuje się trwale w `autohunt/farmsession_prices.json`.
  - Przycisk **Wyklucz / Wlicz** – wykluczenie/włączenie przedmiotu z łącznej wyceny sesji (zastępuje dawne Oko).
- **Stabilność ekwipunku i odporność na sortowanie:**
  - Zastosowano globalny licznik sumaryczny przedmiotów `{vnum: count}` zamiast porównywania po slotach – dzięki temu funkcje sortowania ("Ułóż i scal", "Tylko scal stosy", przestawianie przedmiotów) nie powodują ponownego zliczania istniejących przedmiotów do sesji.
- **Kompaktowy mini-widżet HUD (Propozycja 2):**
  - Podręczny pasek ze stoperem, zyskiem i tempem zarobku, który można swobodnie przemieszczać po ekranie lub przypiąć pod minimapą.
- **Udostępnianie raportu na Czat:**
  - Przycisk `Czat` generuje gotowe podsumowanie na czat gry, np.:
    `[Sesja Farmienia] Czas: 00:31:01 | Metiny: 168 | Bossy: 12 | Zarobek (Rynkowa): 1.055.794.520 Yang (~2.04 mld/h)`.
- **Zapisywanie sesji i historia dropów:**
  - Przycisk **Zapisz** – tworzy trwały snapshot sesji z sugerowaną nazwą mapy (np. `Loch Pajakow V2 (21:09)`) lub własną nazwą gracza i zapisuje w `autohunt/farmsessions_history.json`.
- **Zaawansowane porównanie sesji (Porównaj):**
  - Przycisk **Porownaj** – otwiera dedykowane okno analizy porównawczej (`FarmSessionCompareWindow`).
  - Niezależny wybór sesji bazowej (Panel A) oraz porównywanej (Panel B) ze wskaźnikami pozycji i zabezpieczeniem przed dublowaniem.
  - Karty metryk KPI: delta tempa zarobku (~Yang/h z % przyrostu), delta łącznego zysku, delta rozbitych Metinów/h, delta pokonanych bossów i EXP/h.
  - Pełne zestawienie łupów w tabeli: kolumny Sesja A, Sesja B, różnica sztuk i różnica w Yang, z dymkami tooltipu.
  - Narzędzia zarządzania: zmiana nazwy sesji, usuwanie starych zapisów, zamiana sesji miejscami (`<>`), dynamiczne przeliczanie w trybie Rynkowa / NPC.

---

## 2. Zmodyfikowane i Dodane Pliki

- `Klient/pack/root/farmsession.py` (Nowy: menadżer sesji, historia sesji, silnik wyceny i porównywania)
- `Klient/pack/root/farmsession_prices.py` (Nowy: baza ponad 3200 sugerowanych cen rynkowych zintegrowana z rynkiem botów)
- `Klient/pack/root/uifarmsession.py` (Nowy: główne okno UI, mini-HUD oraz okno porównania sesji)
- `Klient/pack/root/uicommon.py` (Dodana obsługa `SetText` dla dialogów tekstowych `InputDialog`)
- `Klient/pack/root/keybind.py` (Dodana akcja `farm_session` pod klawiszem `F6`)
- `Klient/pack/root/interfacemodule.py` (Metoda `ToggleFarmSessionWindow`, cykl życia okna)
- `Klient/pack/root/game.py` (Hooki na `OnPickMoney`, `PickupSound`, `__TargetHP`, `OnUpdate`, skrót `F6`)
- `Klient/pack/root/uiinventory.py` (Detekcja przyrostów slotów w ekwipunku)
