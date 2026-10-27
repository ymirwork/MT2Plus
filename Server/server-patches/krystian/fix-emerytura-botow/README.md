# 🛠️ Fix: Emerytura Botów – Eliminacja Zapętlenia i Losowania 1 Poziomu (MT2009_PLUS_BOT_RETIREMENT_FIX_V2)

## 📌 Problem i Przyczyna (Root Cause)
Podczas włączenia rotacji/emerytury botów w panelu (`/advanced/retired-bots`), system losował postacie o poziomie 1, mimo że wskaźnik doradcy w Seban Panel pokazywał wysoki wskaźnik gotowości (`🟢 Zalecana rotacja`) i na serwerze znajdowały się setki botów 35+ / 40+ lvl.

### Diagnoza:
1. **Pętla powtórnego losowania:**
   Gdy bot o wysokim poziomie (np. 35 czy 39 lvl) został wytypowany i zresetowany do 1 poziomu (co jest standardowym końcowym etapem emerytury – postać zaczyna grę od nowa od 1 lvl), silnik gry natychmiast usuwał go z mapy aktywnych procesów emerytury (`s_mapPlayerBotRetiring.erase(pid)`).
   Ponieważ bot stał bezczynnie w mieście, silnik w tej samej turze **losował go ponownie** (w skrajnych przypadkach ten sam bot był losowany nawet 10 razy z rzędu w ciągu kilkunastu minut!).
2. **Nadpisywanie pierwotnego poziomu w bazie danych:**
   Tabela `common.playerbot_retire_pick` posiada `PRIMARY KEY (pid)` i zapytanie `ON DUPLICATE KEY UPDATE level=VALUES(level)`. Przy ponownym wylosowaniu tego samego bota (mającego już 1 lvl po resecie) baza danych bezpowrotnie zastępowała jego pierwotny poziom (np. 35 lvl) wartością `1`.
3. **Brak minimalnego limitu poziomu:**
   W silniku nie istniał żaden dolny próg poziomu (np. 10 lvl). W połączeniu z dużą liczbą nieaktywnych botów o poziomie 1, percentyle "środka stawki" (35%-65%) wyliczały się na poziomie 1.

---

## 🔧 Zastosowane Rozwiązanie (Fix)

1. **Zabezpieczenie przed powtórnym wyborem w tej samej turze (`s_setPlayerBotRetireBatchPIDs`):**
   - Wprowadzono zestaw `s_setPlayerBotRetireBatchPIDs`, który pamięta wszystkie identyfikatory botów wytypowanych w bieżącej partii.
   - Stan jest synchronizowany z bazą danych przy starcie partii (`SELECT pid FROM common.playerbot_retire_pick WHERE batch_id=%u`).
   - Ani w trybie normalnym, ani w trybie awaryjnym (`bForcedPick`), żaden bot nie może zostać wylosowany więcej niż jeden raz w ramach tej samej tury.
2. **Twardy minimalny próg poziomu (`PLAYERBOT_RETIRE_MIN_LEVEL`):**
   - Wprowadzono zmienną `s_bPlayerBotRetireMinLevel = 10` (konfigurowalną przez zmienną środowiskową `PLAYERBOT_RETIRE_MIN_LEVEL`, domyślnie 10 lvl).
   - Postacie poniżej 10 poziomu są całkowicie ignorowane przy wyliczaniu puli percentyli oraz odrzucane z kandydatów.
3. **Dynamiczna weryfikacja poziomu online:**
   - Przy budowaniu puli `live` silnik odpytuje w czasie rzeczywistym aktualny poziom w pamięci gry (`ch->GetLevel()`) i synchronizuje lokalną mapę kont `m_mapBotAccounts`.
4. **Zabezpieczenie SQL przed degradacją poziomu w bazie:**
   - Zapytanie `ON DUPLICATE KEY UPDATE` wykorzystuje `level=IF(batch_id=VALUES(batch_id), GREATEST(level, VALUES(level)), VALUES(level))`, co uniemożliwia nadpisanie wyższego poziomu jedynką.

---

## 📂 Zmodyfikowane Pliki
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_retirement.h` (oraz kopia `docker/game/src/server/game/src/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp` (oraz kopia `docker/game/src/server/game/src/`)
- `Server/server-patches/krystian/fix-emerytura-botow/apply_patch.py`
