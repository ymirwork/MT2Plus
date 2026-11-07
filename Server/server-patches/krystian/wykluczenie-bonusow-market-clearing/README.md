# Wykluczenie Przedmiotów Bonusowych z Market Clearing & Poprawa Floor Zielonych Bonusów — MT2Plus

## Problem
1. **Przecena Wzmocnień i Zaczarowań do 22k:**
   - Wprowadzony system czyszczenia nadpodaży rynku (`playerbot_market_clearing.h`) traktował każdy stackowalny przedmiot (`ITEM_FLAG_STACKABLE`) o typie innym niż broń/zbroja/IS jako ulepkę podlegającą automatycznemu zbijaniu ceny.
   - Gdy liczba wystawionych Wzmocnień (`71285`) i Zaczarowań (`71284`) w sklepach botów przekroczyła 200 sztuk, algorytm `market_clear_step` zaczął obniżać ich cenę o 10% co 30 minut, ignorując ceny bazowe.
   - Cena zeszła do minimalnego pułapu ~21 591 Yang, a funkcja `HumanizePlayerBotPrice` zaokrągliła ją do równego **22 000 Yang (22k)**.
2. **Floor Zielonego Czaru i Zielonej Siły:**
   - W `playerbot_town.h` w funkcji `GetPlayerBotBonusGoodsFloorUnit` każdy przedmiot `IsPlayerBotBonusStoneItem` z podtypem `USE_CHANGE_ATTRIBUTE` / `USE_ADD_ATTRIBUTE` otrzymywał dolny pułap cenowy z 71084 / 71085 (~1.4kk / 2kk Yang), przez co Zielony Czar i Zielone Wzmocnienie były sztucznie podnoszone do milionów Yang zamiast zachowywać swoją cenę bazową (50k - 100k / 100k - 250k).

## Rozwiązanie
1. **`playerbot_market_clearing.h`:**
   - W `IsPlayerBotClearingGoods(DWORD vnum)` dodano wykluczenie:
     - Wszystkich przedmiotów `ITEM_USE` o podtypach `USE_CHANGE_ATTRIBUTE`, `USE_ADD_ATTRIBUTE`, `USE_ADD_ATTRIBUTE2` (Wzmocnienia, Zaczarowania, Zielone Wzmocnienia/Czary, Marmury Błogosławieństwa).
     - `IsPlayerBotGreenBonusStone(vnum)` (71151, 71152, 76023, 76024).
     - Pozwoleń na bonusy (`30368`, `30369`, `30370`).
2. **`playerbot_town.h`:**
   - W `GetPlayerBotBonusGoodsFloorUnit(LPITEM item)` dodano bezpośrednią obsługę Zielonych Bonusów (`IsPlayerBotGreenBonusStone`), dzięki czemu ich cena minimalna odnosi się do ich własnej wyceny bazowej (`GetPlayerBotMaterialAskingBase`), a nie do drogich bonusów 71084/71085.

## Dotknięte Pliki
- `Server/linux-port/docker/game/src/server/game/src/playerbot_market_clearing.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_market_clearing.h`
- `Server/linux-port/docker/game/src/server/game/src/playerbot_town.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_town.h`
