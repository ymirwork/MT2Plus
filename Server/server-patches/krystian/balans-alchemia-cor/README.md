# Balans Alchemii & Zwiększenie Dropu Cor Draconis (Hard Edition)

Autorska modyfikacja systemu alchemii oraz źródeł pozyskiwania Cor Draconis na serwerze MT2Plus.

## Cel Modyfikacji
Zachowanie klimatu serwera Hard przy jednoczesnym odczuwalnym odblokowaniu progresu Smoczych Kamieni dla aktywnych graczy oraz botów.

## Wprowadzone Zmiany

1. **Zwiększenie Dziennego Limitu Corów ze Smoczego Oka (z 5 do 15 sztuk):**
   - Plik: `Server/linux-port/docker/game/quest/dragon_soul.quest`
   - Domyślny limit Corów za misję dzienną podniesiony z 5 do **15 sztuk na dobę** (zakres konfiguracyjny 1–30).
   - Logika botów w `playerbot_alchemy.h` dostosowana (`PLAYERBOT_DS_CORS_PER_DAY = 15`).

2. **Zwiększenie Szansy na Odłamek Smoczego Kamienia (30270):**
   - Plik: `Server/linux-port/docker/game/src/serverfiles/share/locale/poland/quest/questlib.lua`
   - Bazowa szansa z potworów (`ds_drop`) podniesiona z 10% do **15%**.

3. **Bezpośredni Drop Cor Draconis (50255) z Metinów i Bossów:**
   - Plik: `Server/linux-port/docker/game/src/server/game/src/item_manager.cpp`
   - **Kamienie Metin (od 40 lvl w górę):** **25% szansy** na 1x Cor Draconis (Surowy).
   - **Bossy (od 30 lvl w górę):** **50% szansy** na 1x Cor Draconis; bossy wysokopoziomowe / dungeonowe (&ge; 75 lvl): **100% szansy**.
   - **Całkowite zniesienie limitu delty poziomu:** Cor Draconis dropi niezależnie od różnicy poziomów między graczem a potworem (usunięto warunek `pkKiller->GetLevel() <= pkChr->GetLevel() + 30`).
   - **Równość Szans dla Botów:** Usunięto sztuczny dławik obniżający szansę botów do 5% (`if (pkKiller->GetDesc()->IsBot()) corChance = 5;`). Boty dropią Cory na takich samych zasadach jak gracze, co stymuluje ich rozwój i zasilanie rynku tobołkami Corów.

4. **Synchronizacja Panelu Administratora:**
   - Plik: `Server/linux-port/docker/panel/app/admin_panel.py`
   - Zaktualizowano domyślne wartości i zakresy (`ds_cor_day` do 30, `ds_drop` domyślnie 15%).
