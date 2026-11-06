# 🛠️ Fix: Emerytura Botów – Eliminacja Zapętlenia, Losowania 1 Poziomu, Wystawiania Sklepu i Prawdziwe Wystawianie Worn EQ (MT2009_PLUS_BOT_RETIREMENT_FIX_V6)

## 📌 Problem i Przyczyna (Root Cause)

1. **Problem V2:**
   Podczas włączenia rotacji/emerytury botów w panelu (`/advanced/retired-bots`), system losował postacie o poziomie 1.
2. **Problem V3 (Brak wystawiania sklepu i natychmiastowy reset):**
   W batchu emerytury boty były natychmiast resetowane do 1 poziomu (etap `reset`) po kilkunastu sekundach od wylosowania, bez uprzedniego otwarcia sklepu offline.
3. **Problem V4 (Zawieszanie partii w toku przez sklepy offline):**
   Gdy partia została zlecona na np. 60–100 botów, brak timeoutu okna časowego powodował nieskończone ponawianie prób.
4. **Problem V5 (Brak Yang na tobołek):**
   `ch->PointChange(POINT_GOLD, 100000)` odrzucało `POINT_GOLD`, zastąpiono `PlayerBotChangeGold`.
5. **Problem V6 (Puste sklepy emerytalne i brak wystawiania noszonego EQ):**
   W MT2Plus niemal cała populacja botów (97%+) prowadzi własne sklepy offline ze zwykłym dropem. Gdy bot posiadający taki sklep został wybrany na emeryturę (z `bForcedPick` lub normalnie), funkcja `MonitorPlayerBotRetirementStall` natychmiast fałszywie adoptowała jego **stary sklep ze śmieciami jako „sklep emerytalny”** (`bStallSeen = true`).
   W konsekwencji:
   - Procedura zdejmowania noszonego wyposażenia (`AdvancePlayerBotRetirementStall`) została całkowicie pominięta (`if (entry.bStallSeen || shop)` zwracało od razu `true`).
   - Boty nigdy nie ściągały noszonych mieczy, zbroi, hełmów ani biżuterii i nie wystawiały ich na rynek.
   - Do tabeli `common.playerbot_retire_item` trafiało 0 przedmiotów (w panelu Seban: 0 wystawionych przedmiotów).
   - Po upływie 45 minut silnik kasował postać do 1 poziomu, bezpowrotnie niszcząc całe wartościowe wyposażenie.

---

## 🔧 Zastosowane Rozwiązanie (Fix V6)

1. **Dopuszczenie botów ze sklepem do puli kandydatów:**
   - W `IsPlayerBotRetirementCandidateInner` zdjęto blokadę `if (HasPlayerBotOfflineShop(ch)) return false;`.
   - Każdy bot w przedziale poziomowym może przejść na emeryturę.
2. **Automatyczne zamknięcie starego sklepu z dropem:**
   - W `AdvancePlayerBotRetirementStall`: jeśli bot posiada aktywny sklep ze starym dropem, silnik wysyła `SendShopForceHardCloseDBPacket` i usuwa encję ze świata.
   - Po zwolnieniu slotu sklepu bot idzie na rynek, zdejmuje całe noszone wyposażenie (`ch->UnequipItem`), stawia **prawdziwy sklep emerytalny** i zapisuje przedmioty do `common.playerbot_retire_item`.
3. **Izolacja monitora sklepu emerytalnego:**
   - W `MonitorPlayerBotRetirementStall`: sklep jest uznawany za emerytalny WYŁĄCZNIE wtedy, gdy został pomyślnie zgłoszony przez procedurę emerytury (`entry.dwSubmittedAt > 0`). Żaden pre-existing drop shop nie zostanie omyłkowo potraktowany jako sklep emerytalny.
4. **Odblokowanie obsługi botów w pętli Update:**
   - W `ManagePlayerBotRetirement`: usunięto warunek `|| ikashop::GetManager().GetShopByOwnerID(pid)` – dopóki `entry.bStallSeen` nie jest prawdziwe, bot jest prowadzony przez procedurę emerytury (zdejmowanie eq, otwarcie stoiska).

---

## 📂 Zmodyfikowane Pliki
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_retirement.h` (i kopia w `docker/`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp` (i kopia w `docker/`)
- `Server/server-patches/krystian/fix-emerytura-botow/apply_patch.py`
