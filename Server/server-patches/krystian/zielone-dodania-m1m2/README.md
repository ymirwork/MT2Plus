# Zielone Dodania i Zmianki Bonusu (Tier 1 M1/M2) - Styl Hard

## Opis Modyfikacji
Modyfikacja gospodarki serwera rozwiązująca problem zatoru rynkowego i braku bonowania wczesnego ekwipunku przez boty:
1. **Tiering Likwidacji Ulepek M1/M2:**
   - **Tier 1 (M1/M2 i Dzicy Ludzie):** Przetapianie ulepek w paczkach 40 sztuk (z rabatem do 25 sztuk przy zalaniu rynku >1500 sztuk) na zbywalne **Zielony Czar (71151)** oraz **Zieloną Siłę (71152)**. Opłata: 50 000 Yang (skalowana inflacją).
   - **Tier 2 (Dolina Orków, Pustynia, DT, Sohan, Świątynia):** Przetapianie ulepek wyższych na elitarne **Zaczarowanie (71284)** oraz **Wzmocnienie (71285)**. Opłata: 150 000 Yang (skalowana inflacją).
2. **Pełna Zbywalność i Obsługa Sklepów Offline:**
   - W `world.item_proto`: `antiflag = 0` (brak blokad handlu/tobołka/dozorcy) oraz `flag = 8196` (stackowalne do 200 sztuk) dla 71151 i 71152.
   - Ceny katalogowe w `playerbot_price_tables.h`: 100 000 Yang (Czar) oraz 250 000 Yang (Siła) – automatycznie skalowane przez mnożnik inflacji (`WorldYangFactor`).
3. **Logika Botów:**
   - Boty <= 40 lvl aktywnie zużywają zielone kamienie na noszone bronie i zbroje <= 40 lvl (FMS, RIB, zbroje 18/26/34 lvl).
   - Boty <= 40 lvl skupują zielone kamienie ze sklepów graczy i innych botów, jeśli ich koszt nie przekracza 20% wolnego budżetu.
   - Nadmiar zielonych kamieni boty wystawiają na rynek w tobołkach offline.

## Dotknięte Pliki
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_price_tables.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_energy_shards.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_bonus.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_market.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_town.h`
- `Server/linux-port/docker/mariadb/playerbot/item_proto.mt2009plus.sql`
- Baza danych MariaDB: `world.item_proto` (VNUM 71151, 71152)
- Panel Administracyjny Seban (`/economy`):
  - `Server/server-patches/krystian/seban-panel-ekonomia/app.py` oraz `templates/economy.html`
  - `Server/linux-port/overlays/seban-panel/app.py` oraz `templates/economy.html`
  - `Server/linux-port/docker/seban-panel/app.py` oraz `templates/economy.html`
