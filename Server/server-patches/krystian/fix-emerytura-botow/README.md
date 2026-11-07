# 🛠️ Fix: Emerytura Botów – Eliminacja Zapętlenia, Losowania 1 Poziomu, Wystawiania Sklepu i Prawdziwe Wystawianie Worn EQ (MT2009_PLUS_BOT_RETIREMENT_FIX_V7)

## 📌 Problem i Przyczyna (Root Cause)

1. **Problem V2:**
   Podczas włączenia rotacji/emerytury botów w panelu (`/advanced/retired-bots`), system losował postacie o poziomie 1.
2. **Problem V3 (Brak wystawiania sklepu i natychmiastowy reset):**
   W batchu emerytury boty były natychmiast resetowane do 1 poziomu (etap `reset`) po kilkunastu sekundach od wylosowania, bez uprzedniego otwarcia sklepu offline.
3. **Problem V4 (Zawieszanie partii w toku przez sklepy offline):**
   Gdy partia została zlecona na np. 60–100 botów, brak timeoutu okna czasowego powodował nieskończone ponawianie prób.
4. **Problem V5 (Brak Yang na tobołek):**
   `ch->PointChange(POINT_GOLD, 100000)` odrzucało `POINT_GOLD`, zastąpiono `PlayerBotChangeGold`.
5. **Problem V6 (Puste sklepy emerytalne i brak wystawiania noszonego EQ):**
   W MT2Plus niemal cała populacja botów (97%+) prowadzi własne sklepy offline ze zwykłym dropem. Gdy bot posiadający taki sklep został wybrany na emeryturę, procedura zdejmowania noszonego wyposażenia została pominięta, a bot nie wystawiał noszonego wyposażenia na rynek.
6. **Problem V7 (Blokada zamykania sklepów dropu przez ENABLE_MT2009_DISABLE_IKASHOP_DEFAULT_SAFEBOX w rdzeniu DB):**
   W fixie V6 dodano `SendShopForceHardCloseDBPacket(pid)`. Jednak w `ClientManagerIkarusShop.cpp` (rdzeń DB) istniała blokada:
   ```cpp
   #ifdef ENABLE_MT2009_DISABLE_IKASHOP_DEFAULT_SAFEBOX
       if (shopCache->itemsmap.size() > 0)
           return false;
   #endif
   ```
   W efekcie: jeśli bot posiadał w starym sklepie drop (niesprzedane przedmioty), rdzeń bazy danych odrzucał zamykanie sklepu (`HARD CLOSE OFFLINESHOP WITH ITEM COUNT > 0`). Sklep nigdy się nie zamykał, a bot co 2 sekundy ponawiał próbę przez 30 minut, aż do timeoutu partii, kończąc z 0 wystawionymi przedmiotami.

---

## 🔧 Zastosowane Rozwiązanie (Fix V7)

1. **Dopuszczenie botów ze sklepem do puli kandydatów:**
   - W `IsPlayerBotRetirementCandidateInner` zdjęto blokadę `if (HasPlayerBotOfflineShop(ch)) return false;`.
2. **Odblokowanie twardego zamykania sklepu dla GM / emerytury w bazie (`subpack.gm = true`):**
   - W `ClientManagerIkarusShop.cpp`: warunek zmieniono na `if (!subpack.gm && shopCache->itemsmap.size() > 0)`.
   - Gdy `subpack.gm == true`, rdzeń DB bezwzględnie zamyka sklep bota, kasuje pozostałości dropu z tabeli `player.item` (`window='IKASHOP_OFFLINESHOP'`) i z pamięci podręcznej, odsyłając `SUBHEADER_DG_SHOP_FORCE_CLOSE` do silnika gry.
3. **Parametr `gm = true` w pakiecie zamykania sklepu:**
   - Rozszerzono `SendShopForceHardCloseDBPacket(DWORD pid, bool gm = false)` w `ikarus_shop_manager.h/cpp`.
   - W `AdvancePlayerBotRetirementStall`: wywołanie `ikashop::GetManager().SendShopForceHardCloseDBPacket(pid, true);`.
4. **Zwolnienie budżetu mutacji dla emerytów:**
   - W `SubmitPlayerBotOfflineShop`: warunek `(!IsPlayerBotRetiring(ch->GetPlayerID()) && !BotOfflineBudget(now))` zapobiega dławieniu otwierania straganów emerytalnych przez limit tokenów mutacji.
5. **Izolacja monitora sklepu emerytalnego:**
   - W `MonitorPlayerBotRetirementStall`: sklep jest uznawany za emerytalny WYŁĄCZNIE wtedy, gdy został pomyślnie zgłoszony przez procedurę emerytury (`entry.dwSubmittedAt > 0`).

---

## 📂 Zmodyfikowane Pliki
- `Server/linux-port/docker/game/src/server/db/src/ClientManagerIkarusShop.cpp`
- `Server/linux-port/docker/game/src/server/game/src/ikarus_shop_manager.h`
- `Server/linux-port/overlays/playerbot/src/game/src/ikarus_shop_manager.cpp` (i kopia w `docker/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_retirement.h` (i kopia w `docker/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h` (i kopia w `docker/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp` (i kopia w `docker/`)
- `Server/server-patches/krystian/fix-emerytura-botow/apply_patch.py`
