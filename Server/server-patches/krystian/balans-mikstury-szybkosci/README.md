# Balans i Opisy Mikstur Szybkości Ataku i Ruchu (Zielone i Fioletowe)

Autorska modyfikacja MT2Plus ujednolicająca działanie, wartości w bazie oraz opisy w interfejsie klienta dla wszystkich Zielonych Mikstur (Szybkość Ataku) i Fioletowych Mikstur (Szybkość Ruchu).

---

## 🎯 Wartości i Balans
- **Mała Mikstura (M):** +10% szybkości (czas trwania: 10 min) — vnum 27100, 27110, 27103, 27113, 27053, 27054, 27123
- **Średnia Mikstura (Ś):** +20% szybkości (czas trwania: 10 min) — vnum 27101, 27111, 27104, 27114
- **Duża Mikstura (D):** +30% szybkości (czas trwania: 10 min) — vnum 27102, 27112, 27105, 27115

---

## 🛠️ Zmienione Pliki
1. **Baza przedmiotów klienta (`Klient/pack/dbdata/gamedata/item_proto`):**
   - Poprawiono `applyvalue0` na właściwe wartości 10, 20, 30 dla wszystkich wariantów mikstur zielonych (typ bonusu 17 = ATT_SPEED) i fioletowych (typ bonusu 19 = MOV_SPEED).
2. **Opisy w locale (`Klient/pack/dbdata/locale/pl/itemdesc.txt`):**
   - Dodano dokładne, estetyczne opisy ze znakiem `%` oraz właściwym kodowaniem CP1250 (bez krzaków).
3. **Tooltipy w kliencie (`Klient/pack/root/uitooltip.py`):**
   - Zarejestrowano opisy specjalnych mikstur startowych (27053, 27054, 27123) oraz ujednolicono formatki tooltipów.

---

## 🚀 Jak zaaplikować
Uruchom:
```powershell
python Server/server-patches/krystian/balans-mikstury-szybkosci/apply_patch.py
```
Skrypt automatycznie zaaplikuje poprawki do plików źródłowych klienta i spakuje paczki `dbdata` oraz `root`.
