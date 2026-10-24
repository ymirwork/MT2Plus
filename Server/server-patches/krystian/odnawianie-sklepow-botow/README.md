# Odnawianie Sklepów Offline Botów (4 Strony / 320 Slotów)

**Autor:** Krystian  
**Data:** 2026-10-24  
**Wersja:** 1.0.0 (dla MT2Plus v2.37.1 / mod-58+)  
**Status:** Aktywny  

---

## 1. Problem i Przyczyna Źródłowa (Root Cause)

W aktualizacji upstream 2.36.0 powiększono sklepy offline botów dwukrotnie — do **4 stron (łącznie 320 slotów)** (`playerbot_offline::BOT_SHOP_PAGES = 4`). Boty podczas bieżącej rozgrywki i wystawiania dropu umieszczały towary na polach od 0 do 319 (w tym na stronach 2, 3 i 4, a także w strefach specjalnych).

Po upływie 8 godzin (`duration = 0`) sklep offline bota wygasał. Silnik Playerbot AI (`playerbot_offline_shop.h`) podczas wizyty serwisowej bota podejmował próbę wznowienia stoiska (`manager.RecvShopReopenClientPacket(ch, sign, 1)`):
- Funkcja `RecvShopReopenClientPacket` weryfikowała każdy przedmiot znajdujący się w sklepie za pomocą `ch->CanPlaceItemOnShopSlot(pos, size)`.
- Metoda `CanPlaceItemOnShopSlot` w `char_shop.cpp` zawierała jednak sztywne ograniczenia dla **graczy**:
  1. `slot >= page * 2` (odrzucenie pól >= 160, czyli całej 3. i 4. strony sklepu bota),
  2. `IsInPremiumArea(slot)` (wymóg aktywnego pakietu Premium Shop),
  3. `IsInLockedArea(slot)` (wymóg odblokowania pól kluczami).
- W konsekwencji silnik odrzucał próbę wznowienia z błędem `SHOP_NO_PREMIUM`, a w logach `syslog` odnotowywano niepowodzenie:
  ```text
  PLAYERBOT_OFFLINE: stand left expired pid=... wanted=1 ... slots_ok=0
  ```
- Wszystkie wygasłe sklepy botów zostawały trwale zablokowane ze statusem `duration = 0`. W ciągu kilku dni liczba aktywnych sklepów spadła z ~1800 do zaledwie 796 (i spadała dalej w tempie wygasania kolejnych stoisk).

---

## 2. Rozwiązanie i Wprowadzone Zmiany

Wprowadzono modyfikację zdejmującą ograniczenia slotów zwykłego gracza dla postaci sterowanych przez AI (`GetDesc() && GetDesc()->IsBot()`):

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
   - W diagnostyce `slotsOk` uwzględniono wyjątek dla botów.

4. **Baza danych SQL (`player.ikashop_offlineshop`):**
   - Przywrócenie czasu trwania wygasłych sklepów botów:
     ```sql
     UPDATE player.ikashop_offlineshop SET duration = 480 WHERE duration = 0;
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
