# Odblokowanie Kostiumów, Fryzur i Szarf Arezzo w ItemShopie

## Opis Modyfikacji
Upstream projektu domyślnie powiązał dostępność 22 zestawów kostiumów z Arezzo (kostiumy, fryzury, nakładki na broń, nakładki na szarfy) z globalną flagą `M2_AREZZO` / `mt2009_arezzo_closed`. W rezultacie przy wyłączonym module Arezzo (`M2_AREZZO=0`, mającym na celu wyłączenie map exp i dungeonów) kostiumy były blokowane w ItemShopie w grze oraz w sklepie WWW.

Ta modyfikacja odseparowuje warstwę wizualną (kostiumy, fryzury, nakładki) od warstwy map i lochów:
1. **Mapy i dungeony Arezzo pozostają wyłączone** (`M2_AREZZO=0` w `.env`) – teleporter nie posiada do nich wpisów, okno wypraw `X` ich nie wyświetla, a boty nie wchodzą na mapy Arezzo.
2. **Wszystkie 22 zestawy wizualne Arezzo są zawsze aktywne i dostępne w ItemShopie**:
   - Dostępne w ItemShopie w grze dla gracza oraz botów.
   - Dostępne w sklepie WWW (PHP).
   - Pełna obsługa nakładek na szarfy (przeciągnięcie nakładki na szarfę w gnieździe 2) oraz bonusów zestawowych.

---

## Zmodyfikowane pliki:
1. `Server/linux-port/overlays/playerbot/src/game/src/playerbot_arezzo_costumes.h`:
   - Zmiana `mt2009_arezzo_costumes::ModuleClosed()` na stałe zwracanie `false`.
2. `Server/linux-port/docker/game/src/server/game/src/playerbot_arezzo_costumes.h`:
   - Identyczna zmiana w roboczych źródłach silnika C++.
3. `Server/linux-port/docker/itemshop/app/itemshop/arezzo_costumes.php`:
   - Zmiana `mt2009_arezzo_closed($sqlServ)` na stałe zwracanie `false`.

---

## Status:
**Aktywny** (Modyfikacja autorska MT2Plus).
