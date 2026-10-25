# Pobieranie Ulepszaczy z Magazynu Kolekcjonera u Kowala i przy Zwojach (Refine Collector Fallback)

## Opis Modyfikacji
Modyfikacja wprowadza inteligentne, automatyczne sprawdzanie i pobieranie ulepszaczy z **Magazynu Kolekcjonera** podczas ulepszania przedmiotów u Kowala oraz przy użyciu zwojów (Zwoje Błogosławieństwa, Zwoje Wojny, Magiczne Metale itp.).

### Logika i Priorytety
1. **Bezwzględny priorytet ekwipunku:**
   - Materiały w pierwszej kolejności pobierane są z ekwipunku postaci (`INVENTORY`).
   - Dopiero w przypadku braku wymaganej liczby sztuk w ekwipunku, brakująca różnica jest pobierana bezpośrednio z Magazynu Kolekcjonera.
2. **Atomowość i walidacja:**
   - Przed pobraniem jakiegokolwiek przedmiotu serwer sprawdza łączną dostępność (`EQ + Magazyn >= Wymóg`) dla **wszystkich** składników receptury.
   - W przypadku niewystarczającej liczby choćby jednego materiału proces ulepszania zostaje przerwany, a przedmioty gracza pozostają nienaruszone.
3. **Cicha synchronizacja (Silent Sync) & UI Klienta:**
   - Przy logowaniu gracza (`CInputLogin::Entergame`) sesja magazynu ładuje się w tle na serwerze i wysyła cichy pakiet danych (`silent = 1`), dzięki czemu klient zna stan magazynu bez otwierania okna na ekranie.
   - W oknie ulepszania (`uirefine.py`) gracz widzi na zielono stan materiałów w formacie:
     `Kawałek Klejnotu x 02 (1 + 5 mag.)` lub `Kawałek Klejnotu x 02 (2)`.
4. **Informacja zwrotna:**
   - Przy pobraniu ulepszacza z magazynu gracz otrzymuje czytelny komunikat na czacie:
     `[Kolekcjoner] Pobrano Kawałek Klejnotu (1 szt.) z Magazynu Kolekcjonera.`

## Zmodyfikowane Pliki

### Serwer (C++):
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_collector.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_collector.cpp`
- `Server/linux-port/docker/game/src/server/game/src/char_item.cpp`
- `Server/linux-port/docker/game/src/server/game/src/input_login.cpp`

### Klient (Python):
- `Klient/pack/root/uicollector.py`
- `Klient/pack/root/uirefine.py`
