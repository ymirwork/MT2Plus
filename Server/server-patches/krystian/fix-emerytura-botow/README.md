# 🛠️ Fix: Emerytura Botów – Eliminacja Zapętlenia, Losowania 1 Poziomu, Wystawiania Sklepu i Zawieszania Partii (MT2009_PLUS_BOT_RETIREMENT_FIX_V4)

## 📌 Problem i Przyczyna (Root Cause)
1. **Problem V2 (Rozwiązany wcześniej):**
   Podczas włączenia rotacji/emerytury botów w panelu (`/advanced/retired-bots`), system losował postacie o poziomie 1, mimo że wskaźnik doradcy w Seban Panel pokazywał wysoki wskaźnik gotowości (`🟢 Zalecana rotacja`) i na serwerze znajdowały się setki botów 35+ / 40+ lvl.
2. **Problem V3 (Rozwiązany wcześniej – Brak wystawiania sklepu i natychmiastowy reset):**
   W batchu emerytury boty były natychmiast resetowane do 1 poziomu (etap `reset`) po kilkunastu sekundach od wylosowania, bez uprzedniego otwarcia sklepu offline (`stage=selling`) i bez wystawienia przedmiotów na rynek.
3. **Problem V4 (Zawieszanie partii w toku i brak kandydatów przez sklepy offline):**
   Gdy partia została zlecona na np. 60 botów, silnik dobierał jedynie boty niemające sklepu offline (np. 19 sztuk). Ponieważ niemal cała pozostała populacja botów (97%+) prowadziła już sklepy offline w m1, warunek `if (HasPlayerBotOfflineShop(ch)) continue;` w `bForcedPick` odrzucał wszystkich pozostałych kandydatów.
   Dodatkowo silnik nie posiadał timeoutu okna czasowego (`window_minutes`), przez co po wygaśnięciu okna ponawiał próby w nieskończoność co 60 sekund, a panel utrzymywał stan `● Tura w toku` bez możliwości rozpoczęcia kolejnej partii.

---

## 🔧 Zastosowane Rozwiązanie (Fix V4)

1. **Obsługa botów z otwartym sklepem w trybie awaryjnym (`bForcedPick`):**
   - Jeśli pula botów bez sklepu się wyczerpie, system emerytalny w `bForcedPick` typuje boty posiadające już aktywny sklep offline.
   - Ich istniejący tobołek zostaje automatycznie przejęty jako sklep emerytalny i monitorowany przez `MonitorPlayerBotRetirementStall` bez natychmiastowego resetu postaci.
2. **Automatyczne zakończenie fazy doboru po upływie okna (`window_minutes`):**
   - W `playerbot_manager.cpp`: jeśli czas od startu partii przekroczy `window_minutes` i brak dostępnych kandydatów, silnik automatycznie domyka fazę naboru (`s_bPlayerBotRetireBatchDone = true`), dostosowuje `bot_count = queued_count` i synchronizuje bazę `common.playerbot_retire_control`.
3. **Auto-heal w panelu Seban (`retirement_control_status`):**
   - W `app.py`: jeśli minął łączny czas (`window_minutes + shop_minutes`) i w grze nie ma żadnych aktywnych emerytów (`active_count == 0`), panel automatycznie synchronizuje `c.bot_count = b.queued_count` i oznacza turę jako `complete` (`✓ Tura zakończona`).

---

## 📂 Zmodyfikowane Pliki
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_retirement.h` (i kopia w `docker/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h` (i kopia w `docker/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp` (i kopia w `docker/`)
- `Server/linux-port/overlays/seban-panel/app.py` (i kopia w `docker/` oraz patchu)
