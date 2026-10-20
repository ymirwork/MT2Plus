# Fix Podglądu Ekwipunku i Dymków Przedmiotów (Player Profile Tooltip Fix)

**Autor:** Krystian | MT2Plus  
**Komponent:** Web Panel (Seban Panel / mt2009-sp-plus)  
**Środowisko:** Docker / VPS / Standalone Python  

---

## 🎯 Opis Problemu

Na podglądzie postaci (`/player/<PID>`) po najechaniu kursorem na przedmioty w górnych slotach ekwipunku (`head`, `weapon`, `body`, `shield`, `ear`, `wrist`, `neck`, `arrow`) dymek przedmiotu (`.item-tip`) był obcinany przez górną krawędź okna przeglądarki:
1. Dymki miały sztywne pozycjonowanie w CSS: `bottom: calc(100% + 4px)`.
2. Przy przedmiotach z dużą liczbą bonusów, Kamieniami Duszy i przetopami wysokość dymku przekraczała 180–220 px, przez co nazwa przedmiotu i statystyki wychodziły poza widoczny obszar ekranu (`top < 0`).
3. Szerokość `190px` powodowała nieestetyczne łamanie nazw bonusów w wiele linii.
4. Skrypt JS w `player.html` sprawdzał `overflow !== 'visible'` u rodziców (którzy go nie posiadali), przez co zmienna `limit` wynosiła stale `0` i mechanizm `.tip-below` nie działał.

---

## 💡 Rozwiązanie

1. **CSS (`static/player-profile.css`):**
   - Górne sloty ekwipunku domyślnie otwierają się w dół (`top: calc(100% + 6px); bottom: auto;`), wykorzystując przestrzeń na sylwetce postaci.
   - Poszerzono dymek do `min-width: 210px; max-width: 290px; width: max-content;` (oraz do `340px` z sekcją `explain`).
   - Wprowadzono `max-height: 85vh; overflow-y: auto; scrollbar-width: thin;` oraz wysoki priorytet `z-index: 1000 !important;`.
   - Zaimplementowano uniwersalne reguły dla klas kierunkowych: `.tip-below`, `.tip-above`, `.tip-left`, `.tip-right`.

2. **JavaScript (`templates/player.html`):**
   - Po najechaniu na dowolny slot (ekwipunek, magazyn, sklep, alchemia, umiejętności) skrypt dynamicznie kalkuluje przestrzeń nad i pod slotem względem wysokości okna przeglądarki (`window.innerHeight`).
   - Jeśli przestrzeń u góry jest niewystarczająca, automatycznie aplikowana jest klasa `.tip-below`.
   - Dodatkowo kalkulowany jest margines boczny, chroniący dymki przed ucinaniem przy lewej i prawej krawędzi ekranu.

---

## 📁 Zawartość Paczki

```text
Fix_Podglad_Ekwipunku_Tooltipy_Seban_Panel/
├── INSTALUJ_AUTOMATYCZNIE.bat      # Automatyczny instalator dla Windows / Docker (1 klik)
├── install_vps.sh                  # Skrypt instalacyjny dla serwerów Linux / VPS
├── fix_player_tooltip.patch        # Czysty plik łatki diff/patch (git apply)
├── INSTRUKCJA_PL.txt               # Szybka instrukcja tekstowa (gotowa na Discord)
├── README.md                       # Pełna dokumentacja modułu
└── pliki_panelu/
    ├── static/
    │   └── player-profile.css      # Zaktualizowany arkusz styli
    └── templates/
        └── player.html             # Zaktualizowany szablon z dynamicznym pozycjonowaniem
```

---

## 🚀 Instalacja

- **Windows (Docker / dev):** Uruchom `INSTALUJ_AUTOMATYCZNIE.bat`.
- **Linux VPS:** Uruchom `bash install_vps.sh`.
- **Ręcznie:** Skopiuj zawartość katalogu `pliki_panelu/` do swojego panelu i zrestartuj usługę (`docker restart mt2dev-seban-panel`).
- **Przeglądarka:** Po instalacji wciśnij **Ctrl + F5**, aby załadować nowy arkusz CSS.
