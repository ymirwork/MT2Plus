# Fix: Zachowanie wierzchowca podczas teleportacji (Boss Tracker / Warp)

Autorska modyfikacja systemu wierzchowców kostiumowych (`ENABLE_MOUNT_COSTUME_SYSTEM`) na serwerze MT2Plus.

## Problem
Podczas korzystania z Boss Trackera (`/boss_tracker_tp <slot>`), pierścieni teleportacji, zwojów powrotu lub teleportacji u Teleportera, gracz po przeniesieniu na miejsce docelowe zawsze lądował na nogach, a wierzchowiec stał obok jako przywołany pet towarzysz. Wymagało to każdorazowego ponownego wsiadania (Ctrl+G).

### Przyczyna techniczna
1. `CHARACTER::Disconnect()` przed warpem usuwa afekty `AFFECT_MOUNT` i `AFFECT_MOUNT_BONUS`, aby nie zapisywać efemerycznych afektów w tabeli `affect` bazy danych.
2. Po załadowaniu nowej mapy w `input_login.cpp` wywoływana jest funkcja `ch->CheckMount()`.
3. Dotychczasowa implementacja `CHARACTER::CheckMount()` w `MountSystem.cpp` wykonywała jedynie `mountSystem->Summon(mobVnum, mountItem, false)` – czyli przywoływała moba wierzchowca na piechotę obok gracza, nigdy nie wywołując `mountSystem->Mount()`.

## Rozwiązanie
1. **Flaga stanu jazdy:**
   - Gdy gracz dosiada wierzchowca (`CMountActor::Mount()`), zerowana jest flaga zejścia: `mount.dismounted = 0`.
   - Gdy gracz świadomie sam schodzi z wierzchowca klawiszem Ctrl+G (`CMountActor::Unmount()`), ustawiana jest flaga `mount.dismounted = 1`.
   - Przy zdjęciu pieczęci z ekwipunku (`CHARACTER::MountUnsummon()`), flaga jest resetowana do `0`.
2. **Zachowanie stanu po TP i logowaniu (`CHARACTER::CheckMount()`):**
   - Jeśli gracz ma założoną pieczęć wierzchowca w slocie kostiumu (`WEAR_COSTUME_MOUNT`) oraz nie zszedł z niego celowo (`mount.dismounted != 1`), serwer automatycznie wsiada na wierzchowca (`mountSystem->Mount(mobVnum, mountItem)`).
   - Jeśli gracz celowo zszedł na ziemię przed teleportacją (`mount.dismounted == 1`), wierzchowiec tak jak wcześniej stoi obok gracza.
3. **Płynność i odporność:**
   - W `CMountSystem::Mount()` dodano bezpieczne pobieranie/tworzenie aktora wierzchowca w przypadku jego braku na liście przed dosiadem.
   - Gracz po kliknięciu "Teleportuj" w Boss Trackerze ląduje bezpośrednio na wierzchowcu i może natychmiast walczyć z bossem/metinem.

## Zmodyfikowane pliki
- `Server/linux-port/docker/game/src/server/game/src/MountSystem.cpp`
