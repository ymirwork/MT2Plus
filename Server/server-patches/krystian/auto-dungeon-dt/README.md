# Auto-Dungi DT (Wieża Demonów) - MT2Plus

## Opis Modyfikacji
Automatyzacja pokonywania pięter Wieży Demonów (DT) zintegrowana z modułem Auto-Łowów gracza (`/autohunt_target`).
Wykorzystuje zaawansowaną heurystykę i skanowanie z `playerbot_demon_tower.h`:
1. **Piętro 1 (Parter):** Priorytetowe namierzanie Metina Twardości (8015).
2. **Piętra z mobami i bossami:** Prawidłowe namierzanie demonów oraz bossów (Król Demonów 1091, Elitarny Król 1092, Umarły Rozpruwacz 1093).
3. **Piętro 4 (Labirynt Metinów):** Prawidłowy wybór prawdziwego Metina Cienia (8017) na podstawie logiki questowej.
4. **Piętro 5 (Pieczęcie):**
   - Automatyczne namierzanie demonów dropiących Kamień Otwarcia (50084).
   - Automatyczne przekazywanie kamienia do Starożytnej Pieczęci (20073) po zebraniu klucza i podejściu.
5. **Piętro 7 (Zin-Sa-Gui):** Automatyczne użycie Mapy Zin (30157).
6. **Piętro 8 (Sa-Soe):** Automatyczne przekazanie Klucza Zin-Bong-In (30304) do kolumny Sa-Soe (20078).

## Dotknięte Pliki
- `Server/linux-port/docker/game/src/server/game/src/playerbot_manager.h`
- `Server/linux-port/docker/game/src/server/game/src/playerbot_manager.cpp`
- `Server/linux-port/docker/game/src/server/game/src/cmd_general.cpp`
