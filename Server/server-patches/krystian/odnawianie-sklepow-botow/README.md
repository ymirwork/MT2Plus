# Odnawianie Sklepów Offline Botów (4 Strony / 320 Slotów & Fix V2 Reopen)

**Autor:** Krystian  
**Data:** 2026-11-05 (Aktualizacja V2)  
**Wersja:** 2.0.0 (dla MT2Plus v2.41.0 / mod-58)  
**Status:** Aktywny  

---

## 1. Problem i Przyczyna Źródłowa (Root Cause)

### Wersja 1.0.0 (v2.36 - v2.37)
W aktualizacji upstream 2.36.0 powiększono sklepy offline botów dwukrotnie — do **4 stron (łącznie 320 slotów)** (`playerbot_offline::BOT_SHOP_PAGES = 4`). Boty podczas bieżącej rozgrywki i wystawiania dropu umieszczały towary na polach od 0 do 319. Po upływie 8 godzin (`duration = 0`) próba wznowienia stoiska (`RecvShopReopenClientPacket`) sprawdzała sloty przez `ch->CanPlaceItemOnShopSlot` z limitami dla graczy (max 160 slotów, klucze, premium), co skutkowało błędem `SHOP_NO_PREMIUM` i wygasaniem stoisk.

### Wersja 2.0.0 (v2.41.0 - Spadek do 759 sklepów)
W aktualizacji v2.41.0 (commit `7d3e2cc2`) dodano mechanikę oszczędzania Yang na konia bojowego (`GetPlayerBotReservedGold`). Wykryto 3 krytyczne blokady:
1. **Rezerwacja Yang (`BotOfflineWouldRenew`):** Warunek `ch->GetGold() - price >= GetPlayerBotReservedGold(ch)` blokował opłatę 6,000 Yang u każdego bota z oszczędnościami na konia (np. bot miał 565,000 Yang, a rezerwa wynosiła 500,000 Yang, więc warunek fałszywie stwierdzał brak funduszy).
2. **Kolejność obsługi wygasłego sklepu (`ManagePlayerBotOfflineService`):** W sekcji `if (shop->GetDuration() == 0)` przed próbą wznowienia stoiska silnik wykonywał procedury zdejmowania niechcianych przedmiotów (`BotOfflineUnwantedLine`, `BotOfflineTakeOffStaleRare`, `BotOfflineTakeOffWeakScrap`, `BotOfflineTakeOffShopMgmt`). Każda z nich zdejmowała tylko 1 przedmiot i przerywała wizytę (`return false`), nakazując powrót za 15 minut. Przy pełnych ekwipunkach botów lub dziesiątkach przedmiotów boty nigdy nie docierały do wznowienia (`reopen`), a sklep pozostawał wygasły.
3. **Przypisanie do nieaktywnego CH2:** W bazie `common.playerbot_channel_assignment` 419 botów handlowych miało ustawiony `channel = 2`. Na serwerze Singleplayer działa wyłącznie CH1, przez co boty te w ogóle nie logowały się na świat gry.

---

## 2. Rozwiązanie i Wprowadzone Zmiany

1. **`Server/linux-port/overlays/playerbot/src/game/src/char_shop.cpp`** (oraz kopia w drzewie `docker/game/src/`):
   - W `CHARACTER::CanPlaceOnShopSlot(BYTE slot)` dodano warunek:
     ```cpp
     // MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1: bot shops are not subject to player lock or premium restrictions
     if (GetDesc() && GetDesc()->IsBot())
         return true;
     ```
   - W `CHARACTER::CanPlaceItemOnShopSlot(BYTE slot, BYTE itemHeight)` dodano warunek:
     ```cpp
     // MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1: bot shops have up to 4 pages (BOT_SHOP_PAGES) without human limits
     if (GetDesc() && GetDesc()->IsBot())
         return true;
     ```

2. **`Server/linux-port/overlays/playerbot/src/game/src/ikarus_shop_manager.cpp`** (oraz kopia w drzewie `docker/game/src/`):
   - W `CShopManager::RecvShopReopenClientPacket` pominięto walidację slotów gracza dla botów:
     ```cpp
     if (!(ch->GetDesc() && ch->GetDesc()->IsBot()) && !ch->CanPlaceItemOnShopSlot(itemHandle->GetInfo().pos, itemHandle->GetTable()->bSize))
     ```

3. **`Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h`** (oraz kopia w drzewie `docker/game/src/`):
   - **V1:** W diagnostyce `slotsOk` uwzględniono wyjątek dla botów.
   - **V2 (Kluczowe odnawianie):**
     - W `BotOfflineWouldRenew` odblokowano opłatę 6,000 Yang: bot płaci za sklep, o ile ma w kieszeni 6,000 Yang, ignorując rezerwę na konia bojowego.
     - W `ManagePlayerBotOfflineService` przestawiono `reopen` na sam początek bloku `if (shop->GetDuration() == 0)` — stoisko jest wznawiane natychmiast na 480 minut, a dopiero potem bot porządkuje asortyment.

4. **Baza danych SQL (`player.ikashop_offlineshop` & `common.playerbot_channel_assignment`):**
   - Przywrócenie czasu trwania wygasłych sklepów botów:
     ```sql
     UPDATE player.ikashop_offlineshop SET duration = 480 WHERE duration = 0;
     ```
   - Przeniesienie botów z nieaktywnego CH2 na aktywny CH1:
     ```sql
     UPDATE common.playerbot_channel_assignment SET channel = 1 WHERE channel != 1;
     ```

---

## 3. Instalacja i Rekompilacja

Skrypt automatyczny w folderze modyfikacji:
```bash
python Server/server-patches/krystian/odnawianie-sklepow-botow/apply_patch.py
```
Po zaaplikowaniu wymagana jest rekompilacja kontenera `game`:
```bash
docker compose build game
```
