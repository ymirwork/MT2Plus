# Ukrywanie Szarfy w Oknie Kostiumów (Hide Sash / Acce)

Autorska modyfikacja dodająca przycisk i funkcjonalność **„Ukryj szarfę” / „Pokaż szarfę”** w oknie kostiumów (`Kostiumy`).
Umożliwia graczowi niezależne ukrycie wizualnego modelu noszonej szarfy bez utraty jej bonusów i wchłoniętych statystyk, w analogiczny sposób jak w przypadku kostiumu zbroi, fryzury oraz nakładki na broń.

---

## 🚀 Główne Cechy i Działanie
- **Niezależny przycisk w UI**: W oknie kostiumów dodany został 5. przycisk:
  1. *Ukryj kostium* (zbroja) – maska bitowa: `1`
  2. *Ukryj fryzurę* (nakrycie głowy) – maska bitowa: `2`
  3. *Ukryj broń* (nakładka) – maska bitowa: `4`
  4. *Ukryj szarfę* (szarfa/acce) – maska bitowa: `8`
  5. *Ukryj cudze* (wyglądy innych graczy) – tryb lokalny
- **Zachowanie pełnych bonusów**: Szarfa pozostaje założona w slocie ekwipunku (`WEAR_COSTUME_ACCE`) i nadal przekazuje wszystkie statystyki/bonusy; usuwany jest jedynie model wizualny (`PART_ACCE = 0`).
- **Synchronizacja sieciowa**: Zmiana jest natychmiast rozsyłana pakietem `UpdatePacket()` do wszystkich graczy w zasięgu widzenia.
- **Trwałość ustawienia**: Stan ukrycia zapisywany jest w pliku konfiguracyjnym klienta `autohunt/kostiumy.cfg` (`mask=...`) i automatycznie synchronizowany przy każdym logowaniu oraz teleportacji gracza.

---

## 🛠️ Zmodyfikowane Pliki

### Klient (`Klient/pack/root/`):
- `uicostumehide.py`: Dodano stałą `SASH = 8`, włączono ją do maski `ALL = 15`, zdefiniowano teksty CP1250 (`Ukryj szarfę`, `Pokaż szarfę`, `Szarfa ukryta`, `Szarfa znowu widoczna.`), przesunięto flagę `OTHERS = 16`.
- `uiinventory.py`: Dodano `uicostumehide.SASH` do listy przycisków w `__AddHideButton(self)`, dynamicznie dopasowując wysokość okna `CostumeWindow`.

### Serwer (`Server/linux-port/docker/game/src/server/game/src/`):
- `item.cpp`: W funkcji `Mt2009PlusApplyCostumeParts(LPCHARACTER ch, LPITEM leaving)` dodano obsługę `PART_ACCE` na podstawie maski bitowej:
  ```cpp
  #ifdef ENABLE_ACCE_COSTUME_SYSTEM
  	LPITEM costumeAcce = ch->GetWear(WEAR_COSTUME_ACCE);
  	if (costumeAcce == leaving) costumeAcce = NULL;
  	ch->SetPart(PART_ACCE, (!(hiddenMask & 8) && costumeAcce) ? costumeAcce->GetAcceVnum() : 0);
  #endif
  ```
- `cmd_general.cpp`: W funkcji komendy `do_costume_hide` rozszerzono maskę z `7` (3 bity) do `15` (4 bity: `value & 15`), uwzględniając 4. bit szarfy.
