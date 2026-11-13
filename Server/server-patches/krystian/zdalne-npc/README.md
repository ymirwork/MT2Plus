# Panel Boczny â€” Zdalne NPC - MT2Plus

## Opis Modyfikacji
Dodanie estetycznego menu Zdalnego NPC pod 6. przyciskiem paska bocznego ekwipunku (dawny Battle Pass):
1. **Pasek boczny ekwipunku (`uiinventory.py`):**
   - Zmiana przycisku 6 na "remotenpc" ("Zdalne NPC").
   - Nowe tekstury `remotenpc_01.tga`, `remotenpc_02.tga`, `remotenpc_03.tga` w `mt2009_ui/sidebar/`.
2. **Okno Klienta (`uiremotenpc.py`):**
   - Okno `RemoteNPCWindow` z listÄ… 7 NPC:
     * Handlarka RÃ³Å¼noÅ›ci (9003) -> Sklep z miksturami i zaopatrzeniem
     * Handlarz BroniÄ… (9001) -> Sklep z orÄ™Å¼em
     * Handlarz ZbrojÄ… (9002) -> Sklep ze zbrojami
     * Heuk-Young (20090) -> BezpoÅ›rednie otwarcie okna wytwarzania (CRAFTING_HALFDEMON)
     * Dozorca / Magazyn (9005) -> PeÅ‚ne menu Dozorcy (Magazyn, Magazyn IS, Sztabki, Wytwarzanie, MateriaÅ‚y)
     * Alchemik (20001) -> PeÅ‚ne menu Alchemika (Sklep, Ulepszanie Alchemii, KrysztaÅ‚ Energii)
     * Uriel (20011) -> PeÅ‚ne menu i dialogi Uriela
   - KaÅ¼dy przycisk posiada tooltip i wysyÅ‚a pakiet `/remote_npc <vnum>`.
   - PeÅ‚na obsÅ‚uga kodowania CP1250 (polskie znaki bez krzakÃ³w).
3. **ObsÅ‚uga Klienta (`game.py`, `uishop.py`):**
   - ObsÅ‚uga `vid == 0` przy zdalnym otwieraniu sklepÃ³w NPC (zapobieganie `KeyError: ownerName` w `offlineShopGuest.py`).
   - WÅ‚Ä…czenie przyciskÃ³w Kup/Sprzedaj dla zdalnych sklepÃ³w NPC.
4. **Logika Serwera C++ (`shop_manager.cpp`, `cmd_general.cpp`, `questmanager.cpp`, `questlua_npc.cpp`):**
   - Komenda `do_remote_npc` w `cmd_general.cpp` zarejestrowana dla kaÅ¼dego gracza (`GM_PLAYER`) w `cmd.cpp`.
   - Bezpieczna blokada uÅ¼ycia na dungeonach i wojnach.
   - `CShopManager::StartShoppingRemote` dla bezpoÅ›rednich sklepÃ³w handlarzy (9003, 9001, 9002).
   - `CShopManager::Buy` oraz `CShopManager::Sell`: usuniÄ™cie blokady braku `GetShopOwner()` oraz walidacja dystansu tylko, gdy sklep posiada fizycznego wÅ‚aÅ›ciciela w Å›wiecie gry (dla sklepÃ³w zdalnych pomijana).
   - `CQuestManager::ClickRace` dla Dozorcy (9005), Alchemika (20001), Heuk-Younga (20090) oraz Uriela (20011).
   - Zdalna obsÅ‚uga `npc.open_shop()` w `questlua_npc.cpp` oparta o `GetCurrentNPCRace()` i `StartShoppingRemote`.
   - Quest `heuk_young_craft.quest` (trigger `when 20090.click`) otwierajÄ…cy bezpoÅ›rednio GUI wytwarzania `crafting.open(104)` bez zbÄ™dnych dialogÃ³w poÅ›rednich.
5. **Poprawka Wytwarzania u Heuk-Younga (`crafting.lua`):**
   - UsuniÄ™cie bÅ‚Ä™du "JesteÅ› za daleko, podejdÅº bliÅ¼ej" przy wytwarzaniu u Heuk-Younga (zarÃ³wno zdalnie przez panel boczny, jak i fizycznie).
   - PominiÄ™cie restrykcji dystansu `npc.is_near` oraz walidacji `npc.get_vid()` dla kategorii 104 (`CRAFTING_HALFDEMON`) oraz zdalnych wywoÅ‚aÅ„ wytwarzania (`npc_vid <= 0`).

## DotkniÄ™te Pliki
- `Klient/pack/root/uiremotenpc.py`
- `Klient/pack/root/interfacemodule.py`
- `Klient/pack/root/uiinventory.py`
- `Klient/pack/root/game.py`
- `Klient/pack/root/uishop.py`
- `Klient/pack/root/mt2009_ui/sidebar/remotenpc_*.tga`
- `Server/linux-port/docker/game/quest/heuk_young_craft.quest`
- `Server/linux-port/docker/game/src/serverfiles/share/locale/poland/quest/libs/crafting/crafting.lua`
- `Server/server-patches/krystian/zdalne-npc/serverfiles/share/locale/poland/quest/libs/crafting/crafting.lua`
- `Server/linux-port/docker/game/Dockerfile`
- `Server/linux-port/docker/game/src/server/game/src/shop_manager.h`
- `Server/linux-port/docker/game/src/server/game/src/shop_manager.cpp`
- `Server/linux-port/docker/game/src/server/game/src/questmanager.h`
- `Server/linux-port/docker/game/src/server/game/src/questmanager.cpp`
- `Server/linux-port/docker/game/src/server/game/src/questlua_npc.cpp`
- `Server/linux-port/docker/game/src/server/game/src/cmd.cpp`
- `Server/linux-port/docker/game/src/server/game/src/cmd_general.cpp`
