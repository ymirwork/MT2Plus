# Zniesienie Limitu Poziomu dla Dropu i Yang (Brak Kary Level Delta)

Autorska modyfikacja MT2Plus całkowicie eliminująca redukcję szansy na drop przedmiotów, złota (Yang), szarf oraz odłamków Smoczego Kamienia i skrzyń eventowych wynikającą z przewagi poziomu postaci nad potworem, kamieniem Metin lub bossem.

---

## 🎯 Cel Modyfikacji
1. **Pełna swoboda endgame / farming:** Postacie na wysokich poziomach (np. 90-120 lvl) mogą swobodnie zbijać dowolne Metiny (np. Metiny w M1/M2, Dolinie, Pustyni, Sohan, Doyyumhwan, Red Las) oraz polować na dowolnych bossów z zachowaniem 100% bazowej szansy na drop.
2. **Koniec z koniecznością tworzenia "droperów":** Gracz nie musi sztucznie blokować poziomu postaci ani utrzymywać armii postaci pobocznych na 35 lub 55 poziomie tylko po to, by farmić ulepszacze lub odłamki.
3. **Płynny drop Yang:** Usunięcie kary `PERCENT_LVDELTA` przy dropie Yangów (`char_battle.cpp`), dzięki czemu ubijanie mobów o niższym poziomie nagradza pełną pulą złota.
4. **Brak kary na Odłamki Smoczego Kamienia i Skrzynie:**
   - W queście alchemii (`dragon_soul.quest`) zniesiono wymóg maksymalnie 30 poziomów różnicy.
   - W logice botów (`playerbot_alchemy.h` i `playerbot_events.h`) usunięto warunki sprawdzające deltę poziomu.

---

## 🛠️ Modyfikowane Pliki
- `Server/linux-port/docker/game/src/server/game/src/item_manager.cpp`:
  - `ITEM_MANAGER::GetDropPct`: stała wartość `iDeltaPercent = 100;` (brak obcinania szansy na drop).
  - `ITEM_MANAGER::CreateDropItem`: zniesienie warunku `pkKiller->GetLevel() <= pkChr->GetLevel() + 30` na drop sukna na szarfy.
- `Server/linux-port/docker/game/src/server/game/src/char_battle.cpp`:
  - `CHARACTER::RewardGold`: `iPercent = iGoldPercent;` zamiast mnożenia przez `PERCENT_LVDELTA`.
- `Server/linux-port/docker/game/quest/dragon_soul.quest`:
  - Wyłączenie blokady dropu odłamków przy różnicy >30 poziomów.
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_alchemy.h`:
  - Odłamki Smoczego Kamienia dla botów bez limitu poziomu.
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_events.h`:
  - Skrzynie eventowe dla botów bez limitu poziomu zabójcy.

---

## 🚀 Jak zaaplikować
Uruchom skrypt:
```powershell
python Server/server-patches/krystian/zniesienie-limitu-poziomu-drop/apply_patch.py
```
Po nałożeniu zrekompiluj kontener `game` lub cały serwer w Dockerze.
