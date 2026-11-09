# Recykling Broni 30 lvl & Ulepszanie u Kowala (Filar 1 - Hardcore Item & Gold Sink V2)

## Opis Modyfikacji
Modyfikacja usuwa zjawisko masowego gromadzenia i blokowania tysięcy sztuk broni na 30 poziom (Koziki, Wachlarze Jesiennego Wiatru, Antyczne Dzwony, Łuki Rogowe itp.) w ekwipunkach botów niskopoziomowych oraz likwiduje zalew rynku offline shopów śmieciowymi egzemplarzami +0.

Zgodnie z duchem klasycznego serwera **Hard**:
1. **Selekcja wartości (High Value vs Scrap):**
   - Egzemplarze wartościowe (Średnie Obrażenia $\ge 20\%$ lub Umiejętności $\ge 6\%$, lub ulepszone $\ge +7$) są traktowane jako **zasób strategiczny** (`IsPlayerBotHighValueLevel30`). Trafiają one na rynek dla graczy lub są ulepszane zwojami.
2. **Kowal jako Piec Hutniczy (Gold & Item Sink):**
   - Boty od 15 poziomu zdejmują restrykcję ulepszania broni 30 lvl. Nadmiarowe sztuki są ulepszane "na czysto" u wiejskiego kowala bez zwojów (do +6).
   - Zwiększono limit prób z 8 do **15 dziennie** (`PLAYERBOT_LOTTERY30_PER_DAY = 15`).
   - W przypadku porażki kowal niszczy przedmiot (naturalny Item Sink), a opłata za ulepszanie pochłania Yangi (Gold Sink).
3. **Blokada Wystawiania Złomu na Tobołkach (`playerbot_town.h`):**
   - W `GetPlayerBotGoodsPriority`: bronie 30 lvl na poziomie $+0..+3$ o słabych statystykach (`!IsPlayerBotHighValueLevel30`) otrzymują priorytet `-1` (zakaz wystawiania na tobołek). Rynek nie jest już śmiecony Kozikami z ujemnymi średnimi.
4. **Zdejmowanie Martwych Linii przez Zarządzanie Stoiskiem (`playerbot_offline_shop.h`):**
   - W `IsPlayerBotShopMgmtKept`: stoisko przetrzymuje wyłącznie egzemplarze `IsPlayerBotHighValueLevel30` lub ulepszone $\ge +6$. Śmieciowy złom stojący na tobołkach jest zdejmowany i złomowany.
5. **Sprzedaż śmieci u Handlarki (`playerbot_economy.h`):**
   - Złom (średnie $< 20\%$ i um $< 6\%$ na niskim plusie $+0..+3$) jest sprzedawany u Handlarki za standardową opłatę NPC, tak jak robi to każdy żywy gracz na dzikusach, aby zwolnić miejsce na mikstury i cenniejsze dropy.

## Zmodyfikowane Pliki
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_gear.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_economy.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_town.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_upstream_botlogic.h`
