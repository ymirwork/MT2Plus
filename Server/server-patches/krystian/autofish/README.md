# Auto-Wędkowanie (Auto-Fishing Hybryda V1)

System automatycznego łowienia ryb dla gracza łączący dedykowane okno w Autołowach (`uiautohunt.py`) z serwerowym automatem wędkarskim (`cmd_general.cpp`).

---

## 🚀 Główne Cechy i Możliwości
- **Pełne wsparcie dla pracy w tle i minimalizacji:** Logika zacięcia i minigry jest prowadzona na serwerze C++, dzięki czemu gracz może zminimalizować klienta gry do paska zadań (`_`) bez ryzyka utraty ryby przez dławienie FPS przez Windows/DirectX.
- **Bez kradzieży focusu:** Usunięto wybudzanie okna z minimalizacji (`app.SetWindowDisplay`) przy starcie minigry w `game.py`.
- **Zintegrowany interfejs w Autołowach (Klawisz K):**
  - Przycisk `Auto-Wędkowanie: [Otwórz]` w głównym oknie Autołowów (`uiautohunt.py`).
  - Okienko `AutoFishWindow` z włącznikiem/wyłącznikiem `[Start]` / `[Zatrzymaj]`.
  - Opcja: `[x] Patrosz ryby (małże / ości)` – natychmiastowe otwieranie wyłowionych żywych ryb (`FISH_ALIVE`).
  - Opcja: `[x] Wyrzucaj farby i wybielacze` – automatyczne usuwanie śmieci zapychających ekwipunek (`70201` - `70207`).
  - Opcja: `[x] Używaj drobnych ryb (priorytet)` – priorytetowe zakładanie Drobnych Ryb (`27802`) na haczyk (zwiększony bonus puli rybołówstwa); po wyczerpaniu lub odznaczeniu używa standardowych robaków/papki.
  - Opcja: `[x] Otwieraj małże (perły)` – automatyczne otwieranie wyłowionych małży (`27987`) w poszukiwaniu Pereł (Biała, Niebieska, Krwawa).
  - Opcja: `[x] Dokupuj robaki u Rybaka` – automatyczny zakup 50 szt. robaków za 2.000 Yang u pobliskiego Rybaka (NPC 9009 w zasięgu 30 m), gdy skończy się przynęta w ekwipunku.
  - **Licznik i Statystyki Sesji na żywo:**
    - Czas trwania bieżącej sesji (`GG:MM:SS`).
    - Licznik wyłowionych ryb oraz otwartych małży.
    - Licznik zdobytych Pereł (Biała / Niebieska / Krwawa) śledzony w czasie rzeczywistym.
    - Przycisk `[Reset]` do zerowania statystyk sesji.
- **Automatyzacja przygotowania:**
  - Samodzielne zakładanie wędki z ekwipunku, jeśli gracz trzyma inną broń.
  - Samodzielne zakładanie przynęty na haczyk przed każdym rzutem (z poszanowaniem priorytetu drobnych ryb).
  - Samodzielne sprawdzanie i zakładanie Karnetu Rybackiego (`27620`).
- **Inteligentne warunki bezpieczeństwa i zatrzymania:**
  - Automatyczne zatrzymanie przy braku robaków/papki w ekwipunku (jeśli opcja dokupowania jest wyłączona lub brak Rybaka/Yang).
  - Automatyczne zatrzymanie przy pełnym ekwipunku (`ch->GetEmptyInventory(1) < 0`).
  - Natychmiastowe przerwanie przy ruchu postaci (krok, skok, portal) lub zgonie.

---

## 📁 Zawartość Katalogu
- `server-patch/`:
  - `apply_autofish.py`: Skrypt Python do automatycznego aplikowania zmian do silnika gry (`game/src`).
  - `Apply-AutoFishPatch.ps1`: Skrypt PowerShell dla środowiska Windows.
  - `edits.json`: Precyzyjne bloki zmian (9 reguł z markerem `MT2009_PLUS_AUTOFISH_V1`).
- `client/root/`:
  - `game.py`: Obsługa pakietu `AutoFishStatus` oraz usunięcie kradzieży okna `app.SetWindowDisplay`.
  - `uiautohunt.py`: Okno `AutoFishWindow` oraz integracja w GUI Autołowów.

---

## 🛠️ Zmodyfikowane Pliki w Projekcie
- `Server/linux-port/docker/game/src/server/game/src/char.h`
- `Server/linux-port/docker/game/src/server/game/src/char.cpp`
- `Server/linux-port/docker/game/src/server/game/src/cmd.cpp`
- `Server/linux-port/docker/game/src/server/game/src/cmd_general.cpp`
- `Klient/pack/root/game.py`
- `Klient/pack/root/uiautohunt.py`
