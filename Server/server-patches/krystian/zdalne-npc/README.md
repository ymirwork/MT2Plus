# Panel Boczny — Zdalne NPC - MT2Plus

## Opis Modyfikacji
Dodanie estetycznego menu Zdalnego NPC pod 6. przyciskiem paska bocznego ekwipunku (dawny Battle Pass):
1. **Pasek boczny ekwipunku (`uiinventory.py`):**
   - Zmiana przycisku 6 na "remotenpc" ("Zdalne NPC").
   - Nowe tekstury `remotenpc_01.tga`, `remotenpc_02.tga`, `remotenpc_03.tga` w `mt2009_ui/sidebar/`.
2. **Okno Klienta (`uiremotenpc.py`):**
   - Okno `RemoteNPCWindow` z listą 7 NPC:
     * Handlarka Różności (9003) -> Sklep z miksturami i zaopatrzeniem
     * Handlarz Bronią (9001) -> Sklep z orężem
     * Handlarz Zbroją (9002) -> Sklep ze zbrojami
     * Heuk-Young (20090) -> Bezpośrednie otwarcie okna wytwarzania (CRAFTING_HALFDEMON)
     * Dozorca / Magazyn (9005) -> Pełne menu Dozorcy (Magazyn, Magazyn IS, Sztabki, Wytwarzanie, Materiały)
     * Alchemik (20001) -> Pełne menu Alchemika (Sklep, Ulepszanie Alchemii, Kryształ Energii)
     * Uriel (20011) -> Pełne menu i dialogi Uriela
   - Każdy przycisk posiada tooltip i wysyła pakiet `/remote_npc <vnum>`.
   - Pełna obsługa kodowania CP1250 (polskie znaki bez krzaków).
3. **Obsługa Klienta (`game.py`, `uishop.py`):**
   - Obsługa `vid == 0` przy zdalnym otwieraniu sklepów NPC (zapobieganie `KeyError: ownerName` w `offlineShopGuest.py`).
   - Włączenie przycisków Kup/Sprzedaj dla zdalnych sklepów NPC.
4. **Logika Serwera C++ (`shop_manager.cpp`, `cmd_general.cpp`, `questmanager.cpp`, `questlua_npc.cpp`):**
   - Komenda `do_remote_npc` w `cmd_general.cpp` zarejestrowana dla każdego gracza (`GM_PLAYER`) w `cmd.cpp`.
   - Bezpieczna blokada użycia na dungeonach i wojnach.
   - `CShopManager::StartShoppingRemote` dla bezpośrednich sklepów handlarzy (9003, 9001, 9002).
   - `CShopManager::Buy` oraz `CShopManager::Sell`: usunięcie blokady braku `GetShopOwner()` oraz walidacja dystansu tylko, gdy sklep posiada fizycznego właściciela w świecie gry (dla sklepów zdalnych pomijana).
   - `CQuestManager::ClickRace` dla Dozorcy (9005), Alchemika (20001), Heuk-Younga (20090) oraz Uriela (20011).
   - Zdalna obsługa `npc.open_shop()` w `questlua_npc.cpp` oparta o `GetCurrentNPCRace()` i `StartShoppingRemote`.
   - Quest `heuk_young_craft.quest` (trigger `when 20090.click`) otwierający bezpośrednio GUI wytwarzania `crafting.open(104)` bez zbędnych dialogów pośrednich.

## Dotknięte Pliki
- `Klient/pack/root/uiremotenpc.py`
- `Klient/pack/root/interfacemodule.py`
- `Klient/pack/root/uiinventory.py`
- `Klient/pack/root/game.py`
- `Klient/pack/root/uishop.py`
- `Klient/pack/root/mt2009_ui/sidebar/remotenpc_*.tga`
- `Server/linux-port/docker/game/quest/heuk_young_craft.quest`
- `Server/linux-port/docker/game/Dockerfile`
- `Server/linux-port/docker/game/src/server/game/src/shop_manager.h`
- `Server/linux-port/docker/game/src/server/game/src/shop_manager.cpp`
- `Server/linux-port/docker/game/src/server/game/src/questmanager.h`
- `Server/linux-port/docker/game/src/server/game/src/questmanager.cpp`
- `Server/linux-port/docker/game/src/server/game/src/questlua_npc.cpp`
- `Server/linux-port/docker/game/src/server/game/src/cmd.cpp`
- `Server/linux-port/docker/game/src/server/game/src/cmd_general.cpp`
