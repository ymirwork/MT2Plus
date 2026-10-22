# Magazyn Kolekcjonera - Automatyczny Drop przy Pełnym Ekwipunku (Collector Auto-Drop)

Autorski moduł rozszerzający funkcjonalność **Magazynu Kolekcjonera** o możliwość automatycznego przekierowywania zbieranego / otrzymywanego łupu (dropu) prosto do Magazynu Kolekcjonera w sytuacji, gdy ekwipunek postaci jest w 100% zapełniony (`full EQ`).

---

## 🚀 Główne Funkcjonalności

- **Checkbox pod przyciskiem "Rozbuduj" w oknie Magazynu Kolekcjonera**:
  - Dedykowany przełącznik `[x] Drop do magazynu przy pełnym EQ` umieszczony tuż pod przyciskiem `[Rozbuduj]`.
  - Posiada czytelny tooltip wyjaśniający działanie funkcji: *„Gdy ekwipunek jest pełny, podnoszony drop trafia bezpośrednio do Magazynu Kolekcjonera.”*.
  - Zachowuje pełną odporność graficzną (fallback tekstowy `[x]` / `[ ]` przy braku ikony).
- **Automatyczne przekierowanie lootu przy braku miejsca w ekwipunku**:
  - **Szybkie zbieranie (Z / ~ / Fast Area Pickup)**: Gdy ekwipunek nie mieści już nowego przedmiotu, przedmiot trafia automatycznie do Magazynu Kolekcjonera zamiast leżeć na ziemi.
  - **Autołowy (Auto Hunt / K)**: Bot łowów zbierający loot obszarowo zapełnia magazyn kolekcjonera, eliminując problem zacinania się zbierania przy pełnym plecaku.
  - **Ręczne podnoszenie / Drop z ziemi**: Obsłużone w `CHARACTER::PickupItem`.
  - **Przekazywanie dropu w grupie (Party Drop)**: Gdy gracz otrzymuje przydział dropu z grupy, a ma pełne EQ, drop wpada do jego magazynu kolekcjonera.
  - **Nagrody bezpośrednie (`AutoGiveItem`)**: Wszelkie bezpośrednie nagrody (np. bossy, Cor Draconis, eventy), które normalnie wypadłyby na ziemię przy pełnym plecaku, bezpiecznie trafiają do magazynu.
- **Inteligentne stackowanie (Auto-Stacking)**:
  - Jeżeli w magazynie kolekcjonera istnieje już stos danego ulepszacza / przedmiotu bez bonusów, przedmioty natychmiast się łączą (nawet do 2 miliardów sztuk).
  - W przypadku przedmiotów niestakowalnych lub z bonusami tworzony jest nowy bezpieczny wpis w wolnym slocie magazynu konta.
  - Weryfikacja pojemności poziomu rozbudowy (`Capacity(tier)`).
- **Pełna synchronizacja stanu i trwałość konta**:
  - Stan opcji zapisywany jest na poziomie konta gracza (`ch->SetAccountFlag("collector_autodrop", ...)`), dzięki czemu wybór gracza jest trwały pomiędzy restartami, relogami i wspólny dla postaci na koncie.
  - Natychmiastowe odświeżanie UI klienta poleceniami `COLL autodrop <0|1>` oraz synchronizacja w nagłówku `COLL begin`.
  - Powiadomienie na czacie informacyjne: `[Kolekcjoner] Ekwipunek pełny! Przedmiot %s trafia do Magazynu.`.

---

## 🛠️ Zmodyfikowane Pliki i Architektura

1. **Serwer C++ (`Server/linux-port/docker/game/src/server/game/src/` oraz `overlays/playerbot/src/game/src/`)**:
   - `playerbot_collector.h` / `playerbot_collector.cpp`:
     - Deklaracja i implementacja `TryAutoCollector(LPCHARACTER ch, LPITEM item)`.
     - Dodanie obsługi sesji w tle (`EnsureLoaded(LPCHARACTER ch, bool forOpen)`), utrzymywanie sesji w pamięci przy włączonym auto-dropie.
     - Komenda `/kolekcjoner autodrop <0|1>` i pakiet zwrotny `COLL autodrop`.
     - Parametr auto-drop w pakiecie otwarcia `COLL begin`.
   - `char_item.cpp`:
     - `CHARACTER::PickupItem`: routing do `playerbot_collector::TryAutoCollector(this, item)` przy braku miejsca w ekwipunku (`iEmptyCell == -1`).
     - Party pickup: routing do `playerbot_collector::TryAutoCollector(owner, item)`.
     - `CHARACTER::AutoGiveItem` (obie przeciążenia): routing do kolekcjonera zamiast wyrzucania na ziemię przy braku pustych slotów.
   - `char.cpp`:
     - `CHARACTER::Disconnect`: zwalnianie sesji `playerbot_collector::OnDisconnect(this)`.
   - `input_login.cpp`:
     - `CInputLogin::Entergame`: pre-loading sesji kolekcjonera `playerbot_collector::EnsureLoaded(ch, false)` gdy flaga `collector_autodrop` jest aktywna.

2. **Klient (`Klient/pack/root/` oraz `Klient/client-patches/client-2.0.30/root/`)**:
   - `uicollector.py`:
     - Kontrolka `CollectorCheckBox`.
     - Umieszczenie checkboxa `self.autoDropCheckBox` pod przyciskiem `[Rozbuduj]` (y=444).
     - Zwiększenie wysokości okna `HEIGHT = 496` dla estetycznego ułożenia.
     - Obsługa komend `COLL begin` (5. argument) oraz `COLL autodrop`.
