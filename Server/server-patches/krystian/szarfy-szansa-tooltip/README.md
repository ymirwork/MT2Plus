# Szarfy – Szansa na Ulepszenie oraz Fix Pustego Tooltipa

## Opis Modułu
Autorska poprawka i usprawnienie interfejsu łączenia szarf (`uiacce.py`, `uitooltip.py`, `uiscript/acce_combinewindow.py`):
1. **Wyświetlanie szansy na ulepszenie (jak u Kowala):**
   - Dodano etykietę `SuccessPercentage` do okna `Acce_CombineWindow`.
   - Dynamiczne pobieranie stopnia szarfy umieszczonej w slocie 1 (`item.GetValue(0)`) i wyświetlanie szansy zgodnie z wartościami silnika (`ACCE_COMBINE_GRADE_1 = 80%`, `GRADE_2 = 70%`, `GRADE_3 = 50%`, `GRADE_4 = 30%`).
   - Formatowanie tekstu zgodne z Kowalem (`localeInfo.REFINE_SUCCESS_PROBALITY % pct` -> `Szansa na Ulepszenie X%`).
   - Respektowanie ustawienia `constInfo.ENABLE_REFINE_PCT`.
   - Zwiększenie wysokości okna z 270 do 290 px dla estetycznego rozmieszczenia: szansa, koszt Yang oraz przyciski OK/Anuluj.
2. **Naprawa pustego dymka / tooltipa (Screenshot_211):**
   - Przyczyna: w `uiToolTip.py` metoda `__AdjustMaxWidth` wywoływała nieistniejące metody `__AdjustAttrMaxWidth` oraz `__AdjustDescMaxWidth`, co rzucało wyjątkiem `AttributeError: 'ItemToolTip' object has no attribute '_ItemToolTip__AdjustAttrMaxWidth'`.
   - Ponieważ błąd następował zaraz po `self.ClearToolTip()`, na ekranie pozostawała pusta czarna ramka tooltipa (z widocznymi jedynie 4 narożnikami).
   - Wdrożono pełne implementacje `__AdjustAttrMaxWidth` (wykorzystującą słownik szerokości `ATTRIBUTE_NEED_WIDTH`) oraz `__AdjustDescMaxWidth` z zabezpieczeniem przed `IndexError` i pustymi opisami.
   - Zabezpieczono metody `SetAcceResultItem` i `SetAcceResultAbsItem` przed pozostawianiem pustego dymka w przypadku przedwczesnego powrotu (`self.HideToolTip()`).
3. **Kompleksowy audyt i zabezpieczenie innych miejsc w kliencie:**
   - Zabezpieczono `SetItemToolTip(itemVnum)` oraz `SetItemShopItemToolTip` przed podaniem `vnum == 0` (natychmiastowe ukrycie i wyjście zamiast czyszczenia do pustego okna).
   - Zabezpieczono `uicube.py` (`__OverInMaterialSlot`): sprawdzanie istnienia recepty przed wyczyszczeniem tooltipa, ukrycie dymka w razie braku materiału.

## Zmodyfikowane Pliki
- `Klient/pack/root/uiscript/acce_combinewindow.py`
- `Klient/pack/root/uiacce.py`
- `Klient/pack/root/uitooltip.py`
- `Klient/pack/root/uicube.py`
