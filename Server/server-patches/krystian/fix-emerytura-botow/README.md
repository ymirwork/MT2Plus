# 🛠️ Fix: Emerytura Botów – Eliminacja Zapętlenia, Losowania 1 Poziomu oraz Naprawa Wystawiania Sklepu Offline (MT2009_PLUS_BOT_RETIREMENT_FIX_V3)

## 📌 Problem i Przyczyna (Root Cause)
1. **Problem V2 (Rozwiązany wcześniej):**
   Podczas włączenia rotacji/emerytury botów w panelu (`/advanced/retired-bots`), system losował postacie o poziomie 1, mimo że wskaźnik doradcy w Seban Panel pokazywał wysoki wskaźnik gotowości (`🟢 Zalecana rotacja`) i na serwerze znajdowały się setki botów 35+ / 40+ lvl.
2. **Problem V3 (Brak wystawiania sklepu i natychmiastowy reset):**
   W batchu emerytury (np. `batch=1793145285`) boty były natychmiast resetowane do 1 poziomu (etap `reset`) po kilkunastu sekundach od wylosowania, bez uprzedniego otwarcia sklepu offline (`stage=selling`) i bez wystawienia przedmiotów na rynek.
   
   **Przyczyny w kodzie silnika:**
   - W `playerbot_manager.cpp`: Gdy bot został wytypowany w trybie awaryjnym (`bForcedPick`), kod natychmiast wykonywał `BeginPlayerBotRetirementClose(dwPID, s_mapPlayerBotRetiring[dwPID], "forced: no bot could go to a market");`, całkowicie omijając etap `PLAYERBOT_RETIRE_SHOPPING` i czyszcząc postać bez handlu.
   - W `playerbot_retirement.h`: Warunek `if (ch->GetParty()) return false;` dyskwalifikował boty z normalnej puli, jeśli polowały w bot-party, zmuszając system do wymuszonego wyboru (`bForcedPick`).
   - W `playerbot_offline_shop.h`: Zabezpieczenie `now - state.dwSpawnTime < 120000` (2 minuty od spawnu bota) oraz rezerwacja Yang na medale konne (`GetPlayerBotReservedGold(ch)`) blokowały otwarcie sklepu offline.
   - W `playerbot_retirement.h`: Funkcja `ScorePlayerBotShopStock` odrzucała noszony ekwipunek jako "wartościowe wyposażenie do zatrzymania", zamiast bezwzględnie wystawiać cały zdjęty rynsztunek bota na sprzedaż.
   - W przypadku pełnego ekwipunku miksturami HP/MP, bot nie miał miejsca w plecaku na zdjęcie zbroi, broni i biżuterii (`ch->UnequipItem`).

---

## 🔧 Zastosowane Rozwiązanie (Fix V3)

1. **Eliminacja omijania sklepu (`bForcedPick`):**
   - Usunięto skrót natychmiastowego resetu postaci. Każdy wytypowany bot (zarówno z puli normalnej, jak i awaryjnej) przechodzi pełną procedurę: przejście do `PLAYERBOT_RETIRE_SHOPPING`, warp do rynku swojego królestwa (m1 / m21 / m41), zdjęcie ekwipunku, otwarcie sklepu offline `ikashop` i przejście w stan `selling`.
2. **Gwarancja wystawienia całego wyposażenia:**
   - Zdjęty rynsztunek (`wasWorn == 1`) jest bezwzględnie dodawany do listy towarów wystawianych w tobołku z realnymi cenami rynkowymi.
   - Przed zdjęciem ekwipunku bot usuwa zbędne mikstury z plecaka, jeśli ma mniej niż 8 wolnych slotów w inwentarzu.
   - Bot otrzymuje zapomogę 100 000 Yang, jeśli posiada za mało złota na opłacenie prowizji otwarcia sklepu.
3. **Bypass ograniczeń czasowych dla emerytów:**
   - W `playerbot_offline_shop.h` dodano wyjątek `IsPlayerBotRetiring(ch->GetPlayerID())` – brak blokady 2 minut od spawnu oraz zerowa rezerwa na oszczędności konne.
4. **Zezwolenie na emeryturę botów w drużynach bot-bot:**
   - Wykluczane są wyłącznie boty grające w party prowadzonym przez żywego gracza (`IsPlayerBotHumanLedParty`), co pozwala botom z grup NPC normalnie przechodzić na emeryturę.
5. **Zamknięcie otwartych okien dialogowych:**
   - Przed rozpoczęciem emerytury automatycznie zamykane są ewentualne otwarte okna handlu, magazynu czy gościa sklepu offline.

---

## 📂 Zmodyfikowane Pliki
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_retirement.h` (i kopia w `docker/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h` (i kopia w `docker/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp` (i kopia w `docker/`)
