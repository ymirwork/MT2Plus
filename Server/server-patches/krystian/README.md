# Autorskie Modyfikacje i Systemy – Krystian (`server-patches/krystian`)

Katalog zawiera zbiór autorskich łatek, systemów, skryptów klienta i serwera oraz modułów przygotowanych dla projektu MT2Plus.

---

## 📁 Indeks Podfolderów z Modyfikacjami

| Podfolder | Typ / Warstwa | Opis działania |
| :--- | :--- | :--- |
| [**`wstawanie-100hp`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/wstawanie-100hp) | Serwer (C++) | Odradzanie się postaci z pełnym paskiem 100% HP po śmierci w mieście lub na miejscu (`cmd_general.cpp`, `char.cpp`). |
| [**`autolowy-szybkie-zbieranie`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/autolowy-szybkie-zbieranie) | Klient (Python) | Błyskawiczne podnoszenie dropu w oknie Autołowów (`uiautohunt.py`) za pomocą komendy obszarowej `/pickup_nearby`. |
| [**`ukrycie-hp-celu`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/ukrycie-hp-celu) | Klient (Python) | Usunięcie cyfrowego wyświetlania wartości HP innych graczy i potworów w interfejsie celu (`uitarget.py`). |
| [**`sklep-160-slotow`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/sklep-160-slotow) | Serwer (C++) + Klient | Rozszerzenie tobołka offline do 160 slotów w 2 blokach, odblokowywanych kluczami (`char_shop.cpp`, `ikarus_shop_manager.cpp`, `dualshop.py`). |
| [**`tracker-bossow`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/tracker-bossow) | Klient + Serwer | System i aplikacja desktopowa do monitorowania czasu i respawnu bossów w grze (patch, skrypty, maintenance). |
| [**`recykling-bonusow`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/recykling-bonusow) | Serwer (Quest) + Klient | Wymiana niepotrzebnego ekwipunku z 5 bonusami u Dozorcy na Zaczarowania i Wzmocnienia Przedmiotu (`recykling_bonusow.quest`). |
| [**`pierscien-teleportacji`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/pierscien-teleportacji) | Serwer (Quest) | Quest `teleport_ring.quest` rozbudowany o teleporty do lochów (v1 pająków, małpy) oraz krain Arezzo (360, 361). |
| [**`seban-panel-ekonomia`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/seban-panel-ekonomia) | Web / Flask (Panel) | Rozszerzenie Centrum Gospodarki panelu Seban: telemetria ulepszaczy M1/M2, płynny skup botów (1-35%) i bilans emerytur. |
| [**`devgameplay`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/devgameplay) | Serwer (C++) + Klient | Poprawki mechaniki rozgrywki: przeciąganie Yang, wymiana handlowa, skróty teleportacyjne (`tp_bookmarks.quest`). |
| [**`fix-boty-gildia-exp-party`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/fix-boty-gildia-exp-party) | Serwer (C++) | Poprawki zrzutek botów na ziemie gildii oraz naliczania expa w grupie (włączone w upstream od v2.32.0). |
| [**`fix-podglad-ekwipunku-tooltipy`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/fix-podglad-ekwipunku-tooltipy) | Web / Flask (Panel) | Poprawka dymków ekwipunku na karcie postaci: eliminacja ucinania od góry, dynamiczny viewport i czytelna szerokość. |
| [**`autofish`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/autofish) | Serwer (C++) + Klient | Auto-Wędkowanie: hybrydowy system z serwerowym automatem w tle (brak throttlingu przy minimalizacji) i oknem w Autołowach (`K`). |
| [**`duze-czcionki-skilli-i-ilosci`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/duze-czcionki-skilli-i-ilosci) | Klient (Zasoby/UI) | Powiększone, czytelne cyfry i oznaczenia stopni umiejętności (12px Bold z obrysem: 1-20, M1-M10, G1-G10, P oraz liczniki stacków 200). |
| [**`optymalizacja-autolowy-drop-redlas`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/optymalizacja-autolowy-drop-redlas) | Serwer (C++) + Klient + Baza | Zniesienie limitu +-15 lvl na drop/yang/alchemię, auto-stackowanie w AH/sklepach/depozycie w 1 stos, optymalizacja autołowów, pathfinding komnat (Lochy Małp), mapa Red Lasu i stack 200 (Medale, Zioła, Ryby, Perły, Małże, Przetopy, Bodziaki, Metale, Księgi). |
| [**`ukryj-szarfe`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/ukryj-szarfe) | Klient (Python) + Serwer (C++) | Osobne ukrywanie szarfy w oknie kostiumów: przycisk „Ukryj szarfę” / „Pokaż szarfę” (bit 8 maski `/kostiumy_ukryj m <maska>`), model szarfy ukryty z zachowaniem wszystkich bonusów. |
| [**`odblokowanie-kostiumow-arezzo`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/odblokowanie-kostiumow-arezzo) | Serwer (C++ / Web) | Odpięcie 22 zestawów kostiumów, fryzur i szarf Arezzo od flagi lochów Arezzo – pełna dostępność w ItemShopie (gra + WWW) przy wyłączonych dungeonach/mapach (`M2_AREZZO=0`). |
| [**`pierscienie-czas-noszenia`**](file:///d:/Github/MT2Plus/Server/server-patches/krystian/pierscienie-czas-noszenia) | Serwer (C++ / Baza) + Klient | Pierścienie i amulety (71145, 71149, 71148, 71136, 71135, 71143): czas upływa tylko podczas noszenia (`LIMIT_TIMER_BASED_ON_WEAR = 9`), fix kasowania przedmiotu unikalnego po 60s, obsługa tooltipa. |

---

## 🛠️ Zastosowanie i Dobre Praktyki
- Wszystkie systemy są uporządkowane w autonomicznych folderach wraz ze swoją dokumentacją `README.md`, skryptami instalacyjnymi i kodem źródłowym.
- W przypadku aktualizacji z oficjalnego repozytorium (Upstream), ten katalog służy jako główne źródło autorskich modyfikacji do weryfikacji i reintegracji na gałęzi `dev`.
