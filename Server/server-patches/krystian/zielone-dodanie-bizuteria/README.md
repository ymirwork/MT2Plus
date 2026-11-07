# Zielone Dodanie i Zmianka na Biżuterię do 40 Lv - MT2Plus

## Opis Modyfikacji
Rozszerzenie działania Zielonego Dodania (71151 / 76023) oraz Zielonej Zmianki (71152 / 76024) o biżuterię, tarcze, hełmy i buty:
1. **Dozwolone podtypy:**
   - `ITEM_WEAPON` (Bronie)
   - `ARMOR_BODY` (Zbroje)
   - `ARMOR_HEAD` (Hełmy)
   - `ARMOR_SHIELD` (Tarcze)
   - `ARMOR_WRIST` (Bransolety)
   - `ARMOR_FOOTS` (Buty)
   - `ARMOR_NECK` (Naszyjniki)
   - `ARMOR_EAR` (Kolczyki)
2. **Limit poziomu:**
   - Wyłącznie przedmioty o poziomie wymaganym <= 40 (`GetLevelLimit() <= 40`).
3. **Bezwzględne blokady:**
   - Talizmany (`ARMOR_PENDANT`), pasy (`ITEM_BELT`), szarfy i kostiumy (`ITEM_COSTUME`) są bezwzględnie zablokowane z czytelnym komunikatem na czacie.
4. **Szanse wejścia bonusu (Zielone Dodanie 71151):**
   - 1. bonus (0 -> 1): **90%**
   - 2. bonus (1 -> 2): **80%**
   - 3. bonus (2 -> 3): **65%**
   - 4. bonus (3 -> 4): **55%**

## Dotknięte Pliki
- `Server/linux-port/docker/game/src/server/game/src/char_item.cpp`
