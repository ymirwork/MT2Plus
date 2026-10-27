# Ceny Bazowe Botów (Edycja Gospodarki i Cennika Iwakury z Panelu)

**Autor:** Krystian  
**Data:** 2026-10-26 (zaktualizowano 2026-10-27)  
**Wersja:** 1.1.0 (dla MT2Plus v2.38.0 / mod-59+)  
**Status:** Aktywny  

---

## 1. Cel Modyfikacji

Wprowadzenie dedykowanego podmodułu w panelu administracyjnym Seban pod adresem `/economy/bot-prices` (menu Gospodarka -> pod *Bazą przedmiotów*), umożliwiającego podgląd, wyszukiwanie i bezpośrednią edycję bazowych cen dla **wszystkich przedmiotów używanych w grze** (~9,376 pozycji: ulepszacze, Kamienie Duszy KD, Księgi Umiejętności KU, księgi i zwoje, rudy i przetopy, mikstury i ryby, skrzynie i szkatułki, bronie, zbroje i hełmy/tarcze, biżuteria i pasy, kostiumy i szarfy, specjalne i IS oraz drop ogólny) używanych przez mechanizm sztucznej inteligencji PlayerBot.

Każda zmiana ceny zapisana w panelu natychmiast wysyła sygnał `queue_bot_reprice_now()` do silnika gry (`/opt/m2spool/playerbot_reprice_now`), wymuszając natychmiastową rekalkulację i przetasowanie cen na tobołkach botów w czasie rzeczywistym.

---

## 2. Architektura i Przepływ Danych

1. **Baza Danych (`player.playerbot_custom_price`)**:
   - Tabela przechowująca nadpisane ceny bazowe (`price_type` = 'item' lub 'skill', `target_id` = VNUM lub skill ID, `price` = kwota bazowa).
   - Tworzona automatycznie (`CREATE TABLE IF NOT EXISTS`).

2. **Silnik Gry C++ (PlayerBot AI)**:
   - `playerbot_custom_prices.h`: bufor w pamięci `s_mapItemPrices` oraz `s_mapSkillPrices` ładowany z bazy `player.playerbot_custom_price`.
   - `playerbot_town.h`: wpięcie w `GetPlayerBotMaterialAskingBase(vnum)`, `GetPlayerBotSoulStoneAskingBase(vnum)`, `GetPlayerBotBookAskingBase(skill)` oraz `GetPlayerBotItemBasePrice(vnum)`. Niestandardowa cena bazowa ma priorytet nad stałą tablicą statyczną `PLAYERBOT_*_PRICES` i jest automatycznie skalowana krzywą inflacji i raty Yang serwera (`ScalePlayerBotIwakuraPrice`).
   - `playerbot_reprice_now.h`: w `StartPlayerBotRepricePass()` następuje wywołanie `playerbot_custom_prices::Reload()`, co gwarantuje odświeżenie danych w RAM w momencie dotknięcia pliku spoola przez panel webowy.
   - `playerbot_manager.cpp`: doładowanie cen przy starcie serwera w `LoadRegisteredBots()`.

3. **Panel Webowy Seban**:
   - Route `GET /economy/bot-prices`:
     - Pełny katalog wszystkich przedmiotów w grze (~9,376 pozycji) buforowany w pamięci RAM (`_BOT_PRICES_CATALOG_CACHE`).
     - Podział na intuicyjne kategorie: ⭐ Zmodyfikowane, Ulepszacze, Kamienie Duszy KD, Księgi Umiejętności KU, Księgi i Zwoje, Rudy i Przetopy, Mikstury i Ryby, Skrzynie, Bronie, Zbroje i Tarcze, Biżuteria, Kostiumy i Szarfy, Specjalne i IS, Inne oraz Wszystkie.
     - Paginacja po 250 pozycji na stronę z zachowaniem filtrów i wyszukiwarki.
     - Wyszukiwarka hybrydowa: natychmiastowy filtr JS na bieżącej stronie oraz globalne wyszukiwanie w bazie po naciśnięciu Enter/Szukaj.
     - Ceny domyślne pobierane z cenników `market_preview.sheet` (`MATERIALS`, `GEAR` +0..+9, `SOUL_STONES`, `BOOKS`) oraz `item_proto` (`shop_buy_price`/`gold`).
     - Estymacja ceny rynkowej bota w czasie rzeczywistym (`Cena bazowa × Mnożnik Yang%`).
     - Prezentacja graficzna w pełni dostosowana do motywu **Cesarstwo (Empire)**: złocenia, krój Cinzel, ścięte narożniki (`clip-path`), imperialna paleta barw.
   - Route `POST /economy/bot-prices/update`: zapis nowej ceny (obsługa skrótów `1.5kk`, `800k`, `2m`, `40kk`), zapis do bazy i wywołanie `queue_bot_reprice_now()`.
   - Route `POST /economy/bot-prices/reset`: przywrócenie ceny domyślnej dla dowolnego przedmiotu z katalogu i wywołanie `queue_bot_reprice_now()`.
   - Route `POST /economy/bot-prices/reprice-all`: przycisk natychmiastowego wymuszenia przeliczenia cen wszystkich wystawionych stoisk.

---

## 3. Pliki Objęte Modyfikacją

- **C++ (Silnik Gry):**
  - `Server/linux-port/overlays/playerbot/src/game/src/playerbot_custom_prices.h`
  - `Server/linux-port/overlays/playerbot/src/game/src/playerbot_town.h`
  - `Server/linux-port/overlays/playerbot/src/game/src/playerbot_reprice_now.h`
  - `Server/linux-port/overlays/playerbot/src/game/src/playerbot_manager.cpp`
- **Panel Webowy (Seban Panel):**
  - `Server/linux-port/docker/seban-panel/templates/_nav.html` oraz overlay `Server/linux-port/overlays/seban-panel/templates/_nav.html`
  - `Server/linux-port/docker/seban-panel/templates/economy_bot_prices.html` oraz overlay `Server/linux-port/overlays/seban-panel/templates/economy_bot_prices.html`
  - `Server/linux-port/docker/seban-panel/app.py` oraz overlay `Server/linux-port/overlays/seban-panel/app.py`
