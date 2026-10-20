# Oferty Błyskawiczne IS co 30 minut (Hard Edition)

## Opis modułu
Moduł ofert błyskawicznych w ItemShopie (zakładka "Oferty Błyskawiczne", indeksy 1001-1100).
- Pula 100 zbalansowanych pozycji dopasowanych ściśle do realiów serwera HARD (brak niszczących ulepszaczy biologa czy dropu z Berana-Setaou w IS, zbalansowane ilości i limity).
- Rotacja co 30 minut (1800 sekund): losowane 10 ofert z puli 100 deterministycznym generatorem Mersenne Twister synchronizującym wszystkie kanały (CH1-CH4).
- Automatyczne zerowanie limitów i odświeżanie okna aukcji u zalogowanych graczy.
- Obsługa zegara odliczającego w kliencie gry (`itemshop_shopwindow.py`, `uiitemshop.py`, `game.py`).
- Pełna integracja z panelem GM (Seban Panel: `AUCTION_TAB = ("blyskawiczne", "Oferty Błyskawiczne", ((906, 999), (1001, 1100)))`).

## Zmodyfikowane pliki
- **Baza danych SQL**: `Server/linux-port/docker/mariadb/playerbot/mod/92_itemshop_flash_offers.sql`
- **Serwer C++**:
  - `Server/linux-port/docker/game/src/server/game/src/itemshop_manager.h`
  - `Server/linux-port/docker/game/src/server/game/src/itemshop_manager.cpp`
  - `Server/linux-port/docker/game/src/server/game/src/main.cpp`
- **Panel WWW (Seban)**:
  - `Server/linux-port/docker/seban-panel/dbeditor/itemshop.py`
- **Klient gry**:
  - `Klient/pack/root/game.py`
  - `Klient/pack/root/uiitemshop.py`
  - `Klient/pack/root/itemshop_shopwindow.py`
  - `Klient/pack/gamedata.data` & `gamedata.index` (ikony olejku wygnania 71054 i olejku nazwy 71055)
