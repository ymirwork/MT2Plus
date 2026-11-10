# Licznik Czasu Kostiumów i Wierzchowców Tylko Podczas Logowania / Noszenia

Modyfikacja zmieniająca zachowanie limitu czasu dla wszystkich kostiumów (zbroje, fryzury, nakładki na broń) oraz wierzchowców (`COSTUME_MOUNT`, subtype 2).

Dotychczas przedmioty te posiadały limit `LIMIT_REAL_TIME = 7` lub `LIMIT_REAL_TIME_START_FIRST_USE = 8`.
Powodowało to, że czas kostiumów i wierzchowców upływał bezpowrotnie w czasie rzeczywistym, nawet gdy gracz miał wyłączoną grę i komputer.

Po modyfikacji czas upływa **wyłącznie wtedy, gdy gracz jest zalogowany w grze i przedmiot jest założony** w odpowiednim slocie okna kostiumów (`LIMIT_TIMER_BASED_ON_WEAR = 9`). Gdy gracz jest wylogowany lub zdejmie kostium/wierzchowca do ekwipunku, czas nie upływa!

---

## 1. Zmiany w Silniku Serwera (C++)

1. **`Server/linux-port/docker/game/src/server/game/src/MountSystem.cpp` (`MountItem_GetRemainingSeconds`):**
   - Obsługa `LIMIT_TIMER_BASED_ON_WEAR`: czas pobierany jest bezpośrednio z `socket0` (jako pozostała liczba sekund trwania).
   - Zabezpieczenie przed podwójnym naliczaniem i odliczaniem czasu.
2. **`Server/linux-port/docker/game/src/server/game/src/item_manager.cpp` (`ITEM_MANAGER::CreateItem`):**
   - W przypadku przedmiotów typu `ITEM_COSTUME` z `LIMIT_TIMER_BASED_ON_WEAR`, jeśli domyślny czas trwania wynosi 0, przypisywane jest domyślne 7 dni (`60 * 60 * 24 * 7`) zamiast 10 godzin.
3. **`Server/linux-port/docker/game/src/server/game/src/playerbot_bonus.h` (`GetPlayerBotCostumeSecondsLeft`):**
   - PlayerBoty prawidłowo odczytują pozostały czas kostiumów z limitem `LIMIT_TIMER_BASED_ON_WEAR`.

---

## 2. Zmiany w Bazie Danych (MariaDB)

- **`world.item_proto` & `player.item_proto`:**
  - Wszystkie przedmioty `type = 28` z `limittype0 IN (7, 8)` zostały zaktualizowane:
    - `limittype0 = 9` (`LIMIT_TIMER_BASED_ON_WEAR`)
    - Jeśli `limitvalue0 = 0`, ustawiono `limitvalue0 = 604800` (7 dni).
  - Przedmioty z `limittype1 IN (7, 8)` analogicznie:
    - `limittype1 = 9`
    - Jeśli `limitvalue1 = 0`, ustawiono `limitvalue1 = 604800`.
- **`player.item`:**
  - Istniejące kostiumy graczy z timestampem w `socket0`: przeliczono pozostały czas (`GREATEST(socket0 - UNIX_TIMESTAMP(NOW()), 0)`), a dla przedmiotów niewykorzystanych lub wygasłych przywrócono nominalny czas z proto (`limitvalue0`).
- **Skrypty i seedy:**
  - `Server/linux-port/docker/mariadb/playerbot/item_proto.mt2009plus.sql`
  - `Server/linux-port/docker/mariadb/playerbot/apply.sh` (dodano krok migracji `MT2009_PLUS_COSTUMES_MOUNTS_WEAR_TIMER`).

---

## 3. Zmiany w Kliencie (Paczki Danych)

- **`Klient/pack/dbdata/gamedata/item_proto`:**
  - Binarny plik `item_proto` został zaktualizowany ze znacznikiem `limittype = 9` dla 2133 kostiumów i wierzchowców.
- **Paczka `dbdata` (`Klient/pack/dbdata.data`, `Klient/pack/dbdata.index`):**
  - Przekompilowana przy użyciu `Compile-ClientPack.ps1`.
- **Znacznik `dbdata_stamp.txt`:**
  - Zaktualizowany rozmiar paczki.
