# Licznik Czasu Pierścieni i Amuletów Tylko Podczas Noszenia

Modyfikacja zmieniająca zachowanie limitu czasu pierścieni i amuletów (vnum: `71145`, `71149`, `71148`, `71136`, `71135`, `71143`).
Czas trwania (30 dni / 720 godzin) upływa **wyłącznie wtedy, gdy przedmiot jest założony** w slocie pierścienia / unikalnym ekwipunku (`LIMIT_TIMER_BASED_ON_WEAR = 9`), zamiast bezpowrotnie uciekać w czasie rzeczywistym (`LIMIT_REAL_TIME = 7`), nawet gdy leży w magazynie lub ekwipunku.

---

## 1. Modyfikowane Przedmioty (VNUM)

| VNUM | Nazwa Przedmiotu | Dawny Typ Limitu | Nowy Typ Limitu | Czas Noszenia |
| :--- | :--- | :--- | :--- | :--- |
| **71135** | Pierścień Półksiężyca | `LIMIT_REAL_TIME` (7) | `LIMIT_TIMER_BASED_ON_WEAR` (9) | 2 592 000 sek. (30 dni noszenia) |
| **71136** | Lizak Potęgi | `LIMIT_REAL_TIME` (7) | `LIMIT_TIMER_BASED_ON_WEAR` (9) | 2 592 000 sek. (30 dni noszenia) |
| **71143** | Pierścień Radości | `LIMIT_REAL_TIME` (7) | `LIMIT_TIMER_BASED_ON_WEAR` (9) | 2 592 000 sek. (30 dni noszenia) |
| **71145** | Amulet Wiecznej Miłości | `LIMIT_REAL_TIME` (7) | `LIMIT_TIMER_BASED_ON_WEAR` (9) | 2 592 000 sek. (30 dni noszenia) |
| **71148** | Pierścień Siły Woli | `LIMIT_REAL_TIME` (7) | `LIMIT_TIMER_BASED_ON_WEAR` (9) | 2 592 000 sek. (30 dni noszenia) |
| **71149** | Pierścień Śmiertelnej Mocy | `LIMIT_REAL_TIME` (7) | `LIMIT_TIMER_BASED_ON_WEAR` (9) | 2 592 000 sek. (30 dni noszenia) |

---

## 2. Zmiany w Silniku Serwera (C++)

- **`Server/linux-port/docker/game/src/server/game/src/item.cpp`:**
  - W `CItem::StartUniqueExpireEvent()` oraz `CItem::StopUniqueExpireEvent()` dodano zabezpieczenie przed wyzwalaniem legacy timera `ITEM_UNIQUE`:
    ```cpp
    if (-1 != GetProto()->cLimitTimerBasedOnWearIndex)
        return;
    ```
    Zapobiega to błędnemu usuwaniu pierścieni po 60 sekundach przez stary mechanizm `unique_expire_event` (sprawdzający socket 2, podczas gdy czas noszenia zapisywany jest w socket 0).
- **`Server/linux-port/docker/game/src/server/db/src/ItemAwardManager.cpp`:**
  - W `ItemAwardManager::CheckItemSocket` rozszerzono warunek pomijania slotowania socketów o `LIMIT_TIMER_BASED_ON_WEAR`.

---

## 3. Zmiany w Bazie Danych (MariaDB)

- **`world.item_proto`:**
  - `limittype0` zmienione z `7` na `9` dla wskazanych 6 VNUMów.
- **`player.item`:**
  - Istniejące przedmioty z wartością timestampu w `socket0` zostały zmigrowane do bazowego czasu noszenia (2 592 000 sekund).
- **Skrypty i seedery:**
  - `Server/linux-port/docker/mariadb/playerbot/item_proto.mt2009plus.sql`: zaktualizowano limity dla wierszy z VNUM 71135, 71136, 71143, 71145, 71148, 71149.
  - `Server/linux-port/docker/mariadb/playerbot/apply.sh`: dodano krok migracji `MT2009_PLUS_RINGS_WEAR_TIMER`.

---

## 4. Zmiany w Kliencie (Python & Paczki Danych)

- **`Klient/pack/root/uitooltip.py`:**
  - W `AddItemData()` przekazano `limitValue` do funkcji `AppendTimerBasedOnWearLastTime(metinSlot, limitValue)`.
  - W `AppendTimerBasedOnWearLastTime()` dodano obsługę podglądu (np. w ItemShopie, czacie czy na rynku): jeśli `metinSlot[0] == 0` oraz `limitValue > 0`, tooltip wyświetla pełny nominalny czas ("Pozostały czas: 30 dni") zamiast mylącego czerwonego napisu "Nie można użyć".
- **`dbdata` (`Klient/pack/dbdata.data`, `Klient/pack/dbdata.index`):**
  - Wygenerowano zaktualizowany binarny plik `gamedata/item_proto` ze znacznikiem `limittype0 = 9` oraz `limitvalue0 = 2592000`.
  - Zaktualizowano `Klient/dbdata_stamp.txt`.
