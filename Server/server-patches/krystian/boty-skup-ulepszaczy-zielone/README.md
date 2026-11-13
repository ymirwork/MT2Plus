# Boty â€” Skup Ulepszaczy i Wymiana na ZielonÄ… SiÅ‚Ä™ / Zielony Czar - MT2Plus

## Opis Modyfikacji
Modyfikacja gospodarki oraz zachowania sztucznej inteligencji botÃ³w (Playerbots AI):
1. **Diagnoza problemu:**
   - Boty czÄ™sto kumulowaÅ‚y znaczne iloÅ›ci YangÃ³w, majÄ…c jednoczeÅ›nie sÅ‚aby, niewybonowany ekwipunek poczÄ…tkowy.
   - Boty miaÅ‚y rÃ³wnieÅ¼ restrykcje uniemoÅ¼liwiajÄ…ce skupowanie pakietÃ³w Zielonych Kamieni (71151 / 71152) ze sklepÃ³w graczy oraz nie skupowaÅ‚y ulepszaczy na potrzeby rozwoju ekwipunku.
   - Zielone kamienie byÅ‚y uÅ¼ywane tylko na zbroje i bronie, z pominiÄ™ciem biÅ¼uterii i heÅ‚mÃ³w oraz wymagaÅ‚y poziomu ulepszenia +4.

2. **Nowa logika `PlayerBotWantsGreenExchange`:**
   - Gdy bot posiada nadwyÅ¼kÄ™ gotÃ³wki (>= 200 000 Yang powyÅ¼ej rezerwy handlowej) oraz sÅ‚aby ekwipunek (`PlayerBotHasWeakGreenGear`: brak 4 bonusÃ³w lub niewymieszane bonusy na noszonych przedmiotach <= 40 lv), bot wchodzi w tryb pozyskiwania zielonych kamieni.

3. **Skup ulepszaczy i Zielonych Kamieni (`playerbot_market.h`):**
   - **Ulepszacze:** Boty z nadmiarem gotÃ³wki i sÅ‚abym eq skupujÄ… ze sklepÃ³w graczy i innych botÃ³w materiaÅ‚y ulepszajÄ…ce (`IsPlayerBotCraftExchangeVnum`: 30000..30092, 30192..30199, 30343..30359, 30367) do puÅ‚apu 45 sztuk w ekwipunku, przy cenie jednostkowej <= 50k Yang (skalowane).
   - **Zielona SiÅ‚a i Zielony Czar:** Zniesiono restrykcjÄ™ zakupu wyÅ‚Ä…cznie pojedynczych sztuk (`offer->GetCount() > 1`) â€” boty mogÄ… teraz kupowaÄ‡ stosy do 10 sztuk z rynku, o ile nie majÄ… jeszcze peÅ‚nego zapasu w eq.

4. **ModuÅ‚ Wymian BotÃ³w (`ManagePlayerBotGreenExchange` w `playerbot_bonus.h`):**
   - Bot posiadajÄ…cy nadwyÅ¼kÄ™ gotÃ³wki i sÅ‚aby ekwipunek co 2 minuty moÅ¼e wymieniÄ‡ pakiet 15 ulepszaczy + 25 000 Yang na:
     * `71152` (Zielona SiÅ‚a) â€” jeÅ›li w noszonym eq brakuje 4 bonusÃ³w,
     * `71151` (Zielony Czar) â€” jeÅ›li noszone eq posiada 4 bonusy, ale wymagajÄ… one wymieszania.
   - PomyÅ›lna wymiana jest logowana do `ItemLog` oraz `sys_log` pod tagiem `PLAYERBOT_GREEN_EXCHANGE`.

5. **Rozszerzenie uÅ¼ywania Zielonych Kamieni na caÅ‚e EQ do 40 Lv:**
   - `CanPlayerBotSpendGreenBonusStoneOn` obejmuje: bronie, zbroje, heÅ‚my, tarcze, bransolety, buty, naszyjniki i kolczyki do 40 lv (zgodnie z `zielone-dodanie-bizuteria`).
   - `piece.greenRank` przydziela priorytety dla wszystkich 8 slotÃ³w (`WEAR_BODY` -> 0, `WEAR_WEAPON` -> 1, `WEAR_HEAD` -> 2, `WEAR_SHIELD` -> 3, `WEAR_FOOTS` -> 4, `WEAR_WRIST` -> 5, `WEAR_NECK` -> 6, `WEAR_EAR` -> 7).
   - `PickPiece` w `playerbot_bonus_rules.h` sprawdza wszystkie 8 rang (0..7), dziÄ™ki czemu boty bonujÄ… kolejno caÅ‚e swoje uzbrojenie.
   - UsuniÄ™to sztuczny wymÃ³g `+4` dla uÅ¼ycia zielonych kamieni â€” boty mogÄ… bonowaÄ‡ swÃ³j sprzÄ™t od +0.
   - Boty zachowujÄ… skupione ulepszacze dla siebie i nie wystawiajÄ… ich na wÅ‚asne sklepy (`playerbot_town.h`).

## DotkniÄ™te Pliki
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_types.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_bonus_rules.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_bonus.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_market.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_town.h`
- `Server/linux-port/docker/game/src/server/game/src/playerbot_types.h`
- `Server/linux-port/docker/game/src/server/game/src/playerbot_bonus_rules.h`
- `Server/linux-port/docker/game/src/server/game/src/playerbot_bonus.h`
- `Server/linux-port/docker/game/src/server/game/src/playerbot_market.h`
- `Server/linux-port/docker/game/src/server/game/src/playerbot_town.h`
