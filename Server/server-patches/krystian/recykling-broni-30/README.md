# Recykling Broni 30 lvl & Ulepszanie u Kowala (Filar 1 - Hardcore Item & Gold Sink)

## Opis Modyfikacji
Modyfikacja usuwa zjawisko masowego gromadzenia i blokowania tysięcy sztuk broni na 30 poziom (Koziki, Wachlarze Jesiennego Wiatru, Antyczne Dzwony, Łuki Rogowe itp.) w ekwipunkach botów niskopoziomowych (14–30 lvl).

Zgodnie z duchem klasycznego serwera **Hard**:
1. **Selekcja wartości (High Value vs Scrap):**
   - Egzemplarze elitarne (Średnie Obrażenia $\ge 25\%$ lub Umiejętności $\ge 8\%$, lub ulepszone $\ge +7$) są traktowane jako **zasób strategiczny** (`IsPlayerBotHighValueLevel30`) i **NIGDY** nie są sprzedawane do NPC (Handlarki). Trafiają one wyłącznie na rynek dla graczy lub są ulepszane zwojami.
2. **Kowal jako Piec Hutniczy (Gold & Item Sink):**
   - Boty od 15 poziomu zdejmują restrykcję ulepszania broni 30 lvl. Nadmiarowe sztuki są ulepszane "na czysto" u wiejskiego kowala bez zwojów (do +6).
   - Zwiększono limit prób z 2 do 8 dziennie (`PLAYERBOT_LOTTERY30_PER_DAY`).
   - W przypadku porażki kowal niszczy przedmiot (naturalny Item Sink), a opłata za ulepszanie pochłania Yangi (Gold Sink).
3. **Sprzedaż śmieci u Handlarki (Hardcore Fallback):**
   - Skrajny złom (średnie $\le 10\%$ na niskim plusie $+0..+3$) oraz nadmiarowe sztuki zapychające plecak przy zapełnionym ekwipunku są sprzedawane u Handlarki za standardową opłatę NPC, tak jak robi to każdy żywy gracz na dzikusach, aby zwolnić miejsce na mikstury i cenniejsze dropy.

## Zmodyfikowane Pliki
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_gear.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_economy.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_upstream_botlogic.h`
