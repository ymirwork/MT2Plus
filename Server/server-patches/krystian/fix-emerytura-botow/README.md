# 🛠️ Fix: Emerytura Botów – Eliminacja Zapętlenia, Losowania 1 Poziomu, Wystawiania Sklepu i Zawieszania Partii (MT2009_PLUS_BOT_RETIREMENT_FIX_V5)

## 📌 Problem i Przyczyna (Root Cause)
1. **Problem V2 (Rozwiązany wcześniej):**
   Podczas włączenia rotacji/emerytury botów w panelu (`/advanced/retired-bots`), system losował postacie o poziomie 1, mimo że wskaźnik doradcy w Seban Panel pokazywał wysoki wskaźnik gotowości (`🟢 Zalecana rotacja`) i na serwerze znajdowały się setki botów 35+ / 40+ lvl.
2. **Problem V3 (Rozwiązany wcześniej – Brak wystawiania sklepu i natychmiastowy reset):**
   W batchu emerytury boty były natychmiast resetowane do 1 poziomu (etap `reset`) po kilkunastu sekundach od wylosowania, bez uprzedniego otwarcia sklepu offline (`stage=selling`) i bez wystawienia przedmiotów na rynek.
3. **Problem V4 (Rozwiązany wcześniej – Zawieszanie partii w toku i brak kandydatów przez sklepy offline):**
   Gdy partia została zlecona na np. 60 botów, silnik dobierał jedynie boty niemające sklepu offline (np. 19 sztuk). Ponieważ niemal cała pozostała populacja botów (97%+) prowadziła już sklepy offline w m1, warunek `if (HasPlayerBotOfflineShop(ch)) continue;` w `bForcedPick` odrzucał wszystkich pozostałych kandydatów.
   Dodatkowo silnik nie posiadał timeoutu okna czasowego (`window_minutes`), przez co po wygaśnięciu okna ponawiał próby w nieskończoność co 60 sekund, a panel utrzymywał stan `● Tura w toku` bez możliwości rozpoczęcia kolejnej partii.
4. **Problem V5 (Brak Yang na tobołek/opłatę tobołka i odrzucanie otwarcia sklepu):**
   W `playerbot_retirement.h` funkcja `AdvancePlayerBotRetirementStall` próbowała zagwarantować botowi minimum 100 000 Yang na opłatę tobołka i otwarcie sklepu poprzez `ch->PointChange(POINT_GOLD, 100000)`. W silniku mt2009 metoda `PointChange` odrzuca `POINT_GOLD` (zwracając w `syserr`: `CHARACTER::PointChange: %s: unknown point change type 11`). Gdy wylosowany bot posiadał zbyt mało Yang (np. poniżej kosztu tobołka/opłaty, np. 4 492 Yang), nie otrzymywał środków, przez co `SubmitPlayerBotOfflineShop` odrzucał próbę otwarcia kramu przy każdej klatce przez 30 minut, aż do zadziałania timeoutu `no stall could be opened in 30 minutes` i resetu bez sprzedaży ekwipunku na rynku.
5. **Problem V5.1 (Timeout bazy 1969 / 503 na podglądzie emerytury w Seban Panel):**
   Przy bazie ponad 2,5 miliona wpisów w `log.ikarusshop_log`, zapytanie łączące transakcje kupna (`shop_owner`, `itemid`) bez indeksu kompozytowego skanowało całą tabelę i przekraczało limit 10 sekund (`SEBAN_DB_STATEMENT_TIMEOUT`), powodując błąd MariaDB 1969.

---

## 🔧 Zastosowane Rozwiązanie (Fix V5)

1. **Poprawne zasilanie Yang dla emerytów (`PlayerBotChangeGold`):**
   - Zastąpiono nieskuteczne wywołanie `ch->PointChange(POINT_GOLD, 100000)` dedykowanym helperem silnika `PlayerBotChangeGold(ch, 100000)`.
   - Każdy bot typowany na emeryturę ma gwarantowany zapas Yang na tobołek i otwarcie sklepu offline.
2. **Optymalizacja indeksów bazy danych (`log.ikarusshop_log`):**
   - Dodano indeks kompozytowy `idx_shopowner_what_itemid ON log.ikarusshop_log (shop_owner, what, itemid)`.
   - Zapytania na stronie `/advanced/retired-bots` ładują się natychmiastowo (< 0.05s).
3. **Obsługa botów z otwartym sklepem w trybie awaryjnym (`bForcedPick`):**
   - Jeśli pula botów bez sklepu się wyczerpie, system emerytalny w `bForcedPick` typuje boty posiadające już aktywny sklep offline.
   - Ich istniejący tobołek zostaje automatycznie przejęty jako sklep emerytalny i monitorowany przez `MonitorPlayerBotRetirementStall` bez natychmiastowego resetu postaci.
4. **Automatyczne zakończenie fazy doboru po upływie okna (`window_minutes`):**
   - W `playerbot_manager.cpp`: jeśli czas od startu partii przekroczy `window_minutes` i brak dostępnych kandydatów, silnik automatycznie domyka fazę naboru (`s_bPlayerBotRetireBatchDone = true`), dostosowuje `bot_count = queued_count` i synchronizuje bazę `common.playerbot_retire_control`.
5. **Auto-heal w panelu Seban (`retirement_control_status`):**
   - W `app.py`: jeśli minął łączny czas (`window_minutes + shop_minutes`) i w grze nie ma żadnych aktywnych emerytów (`active_count == 0`), panel automatycznie synchronizuje `c.bot_count = b.queued_count` i oznacza turę jako `complete` (`✓ Tura zakończona`).

---

## 📂 Zmodyfikowane Pliki
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_retirement.h` (i kopia w `docker/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h` (i kopia w `docker/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp` (i kopia w `docker/`)
- `Server/linux-port/overlays/seban-panel/app.py` (i kopia w `docker/` oraz patchu)
- `Baza danych (MariaDB log.ikarusshop_log)`: indeks `idx_shopowner_what_itemid`
