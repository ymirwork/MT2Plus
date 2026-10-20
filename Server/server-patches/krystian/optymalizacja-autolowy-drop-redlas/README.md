# Optymalizacja Autołowów, Zniesienie Limitu Dropu i Mapa Red Lasu

Moduł wprowadzający ulepszenia w rozgrywce MT2Plus:
1. Usunięcie ograniczenia poziomu (+-15 lvl) dla dropu przedmiotów i Yang.
2. Skrócenie czasu akcji i oczekiwania na cel w Autołowach (`uiautohunt.py`).
3. Odblokowanie mapy Czerwonego Lasu (`metin2_map_trent02`) w oknie minimapy/atlasu (`M`).
4. Zwiększenie limitu stackowania Medalu Konnego (vnum `50050`) do 200.
5. Usprawnienie pathfindingu w Autołowach (filtr osiągalności komnat w Lochach Małp + wygładzanie zakrętów `WalkPath`).

---

## 1. Usunięcie Wymogu +-15 Poziomów na Drop

### Zmiany w Silniku Serwera (C++):
- `Server/linux-port/docker/game/src/server/game/src/item_manager.cpp`:
  - W `ITEM_MANAGER::GetDropPct` wymuszono stałe `iDeltaPercent = 100;` (usunięto tabele kar `PERCENT_LVDELTA` i `PERCENT_LVDELTA_BOSS`).
  - Usunięto ograniczenia `pkChr->GetLevel() <= pkKiller->GetLevel() + 15` dla dropu Cor Draconis, Szarf/Sukna, Ksiąg Umiejętności z kamieni Metin, Zwojów Błogosławieństwa oraz w podglądzie dropu `AddMobPreviewItem`.
- `Server/linux-port/docker/game/src/server/game/src/char_battle.cpp`:
  - W `CHARACTER::RewardGold` ustawiono `iPercent = iGoldPercent;` (eliminacja mnożnika delty poziomu przy dropie Yang).
- `Server/linux-port/docker/game/src/server/game/src/playerbot_alchemy.h` & `overlays/playerbot/src/game/src/playerbot_alchemy.h`:
  - W `NotePlayerBotDragonShardKill` usunięto warunek `victim->GetLevel() + 15 >= bot->GetLevel()`.
- `Server/linux-port/docker/game/src/server/game/src/playerbot_events.h` & `overlays/playerbot/src/game/src/playerbot_events.h`:
  - Usunięto warunek poziomu dla eventowych skrzyń (`Mt2009PlusChestDrops`).
- `Server/linux-port/docker/game/src/server/game/src/playerbot_newpet.h` & `overlays/playerbot/src/game/src/playerbot_newpet.h`:
  - Usunięto ograniczenie poziomu przy dropie jajek zwierzaków.
- `Server/linux-port/docker/game/quest/dragon_soul.quest`:
  - Zakomentowano warunek `if npc.get_level0() < pc.get_level() - 15 then return end`.

---

## 2. Optymalizacja Responsywności Autołowów

### Zmiany w Kliencie (`Klient/pack/root/uiautohunt.py`):
- Skrócono timeouty bezczynności i zmiany celu:
  - `STUCK_SECONDS`: `8.0s` -> `3.0s` (znacznie szybsze odpuszczanie niedostępnego celu).
  - `STUCK_PAUSE`: `2.0s` -> `0.3s` (błyskawiczne pytanie o kolejny cel po odpuszczeniu).
  - `COMBAT_STUCK_SECONDS`: `0.8s` -> `0.4s`.
  - `COMBAT_SKIP_SECONDS`: `2.0s` -> `1.0s`.
  - `TARGET_REQUEST_INTERVAL`: `0.8s` -> `0.35s` (szybsze pobieranie celów z serwera).
  - `MOVE_INTERVAL`: `0.35s` -> `0.2s`.
  - `RETURN_MOVE_INTERVAL`: `1.0s` -> `0.5s`.
  - `LOOT_PICK_INTERVAL`: `0.6s` -> `0.25s`, `LOOT_STUCK_SECONDS`: `6.0s` -> `2.0s`.
  - `SKILL_MIN_INTERVAL`: `1.5s` -> `0.8s`, `SKILL_MOTION_HOLD`: `1.3s` -> `0.7s`.
  - `ESCAPE_MAX_SECONDS`: `5.5s` -> `2.0s`, `PATH_STALL_SECONDS`: `3.0s` -> `1.0s`.

---

## 3. Odblokowanie Mapy Czerwonego Lasu (Atlas / M)

- `Klient/pack/root/uiminimap.py`:
  - Usunięto wpis `"metin2_map_trent02": "metin2_map_trent02"` ze słownika `CANNOT_SEE_MAP_DICT`.
- `Klient/pack/root/uitooltip.py`:
  - Usunięto `"metin2_map_trent02"` ze słownika `blockedPreviewMapNames`.
- Utworzono pliki atlasu w `Klient/pack/root/ymir work/ui/atlas/metin2_map_trent02/` (`atlas.sub` i tekstura `atlas.dds`) oraz zsynchronizowano z paczką `etc`.
- Spakowano paczki `root` i `etc`.

---

## 4. Zwiększenie Stackowania Przedmiotów do 200

Podniesiono limit stackowania do 200 dla kluczowych grup przedmiotów użytkowej i rzemieślniczej rozgrywki:
- **Medal Konny:** vnum `50050`
- **Zioła z Małp:** vnum `50057`, `50058`, `50059`
- **Kowalstwo i Ulepszanie:** Zwoje Błogosławieństwa (`25040`, `25041`), Magiczny Kamień (`25042`), Podręczniki Kowala (`25043`, `70039`), Zwój Wojny (`25044`), Zwój Boga Smoków (`25045`, `71032`), Marmur Błogosławieństwa 5b (`70024`), Zwój Kamienia Duszy (`25100`), Kamień Kowala (`71025`), Magiczny Metal (`71026`)
- **Cenne Surowce i Łowienie:** Małże (`27987`), Perły (`27992`, `27993`, `27994`), Ryby surowe, pieczone i martwe (`27800`–`27899`)
- **Przetopy Rud:** Wszystkie przetopy (`50621`–`50640`)
- **Księgi Umiejętności Pasywnych:** Sztuki Wojny Sun Zi, Wu Zi, WeiLiao Zi, Combo, Języki, Polimorfia, Zbieractwo (`50301`–`50322`), Instrukcje Jazdy Konnej (`50060`, `50061`, `50062`)
- **Przedmioty Specjalne i Klucze:** Złoty Klucz (`50008`), Srebrny Klucz (`50009`), Pigułka Krwi (`70014`), Pierścień Doświadczenia (`70005`), Rękawice Złodzieja (`70042`, `70043`, `72005`, `72006`)

### Wdrożenie i spójność:
- Baza MariaDB (`world.item_proto`): zaktualizowano pole `stack = 200`.
- Skrypt migracji `apply.sh`: dodano automatyczny blok migracyjny `MT2009_PLUS_STACK_200_EXTENDED`.
- Rejestr edytora `player.web_dbeditor_history`: dodano wpisy historii zmian dla kolumny `stack`.
- Klient: wygenerowano nową binarną paczkę `dbdata.data` / `dbdata.index` ze znacznikiem `2.0.61-31f459ebe125` i zaktualizowano `Klient/dbdata_stamp.txt`.

---

## 5. Usprawnienie Pathfindingu w Autołowach (Lochy Małp)

### Diagnostyka Problemu:
Lochy Małp (i podobne krainy) posiadają oddzielone komnaty połączone portalami. Serwerowa pętla `FAutoHuntTarget` znajdowała potwory w promieniu 2D i wysyłała graczowi cel, który znajdował się za litą ścianą bez fizycznego dojścia. Gracz blokował się na ścianie komnaty.

### Rozwiązanie Serwerowe (`CPlayerBotManager::IsHumanTargetReachable`):
- W `playerbot_manager.h` i `playerbot_manager.cpp` dodano metodę weryfikującą spójność komponentu siatki nawigacyjnej:
  ```cpp
  bool CPlayerBotManager::IsHumanTargetReachable(LPCHARACTER ch, long targetX, long targetY)
  ```
  Sprawdza ona, czy `navigation.GetComponentAtWorld(...)` gracza i celu zwraca ten sam identyfikator.
- W `cmd_general.cpp` w `FAutoHuntTarget::operator()` wykluczono cele, do których postać nie może dotrzeć pieszo.

### Rozwiązanie Klienckie (`uiautohunt.py`):
- Zwiększono margines dotarcia do punktu nawigacji `PATH_POINT_REACH` z `70.0` do `140.0`.
- Wprowadzono wygładzanie zakrętów `WalkPath`: jeżeli gracz znajduje się bliżej punktu kolejnego (`pathPoints[1]`) niż bieżącego (`pathPoints[0]`), punkt jest natychmiast zaliczany, co zapobiega zacinaniu się na narożnikach.

---

## 6. Automatyczne Stackowanie Zakupów z Domu Aukcyjnego (AH), Sklepów i Depozytu

Wyeliminowano problem rozbijania zakupów na pojedyncze/odrębne sloty w ekwipunku oraz blokadę wyciągania przedmiotów z depozytu:

1. **Dom Aukcyjny (AH) i Sklepy Offline (`ikarus_shop_manager.cpp`):**
   - W `RecvShopBuyDBPacket` przy zakupie częściowym (`part`) oraz całej oferty (`itemInstance`), przed poszukiwaniem nowego slotu w inwentarzu uruchamiane jest automatyczne łączenie stosu `ch->AutoStackItem(item)`.
   - Kupno wielu sztuk (np. 40 sztuk w opcji "Kup wiele" / hurt w AH z kilku różnych ofert) natychmiast łączy zakupione sztuki w **jeden wspólny stos w ekwipunku**, zamiast zapełniać odrębne kratki.
   - Przedmioty nie lądują w depozycie, dopóki w ekwipunku jest wolne miejsce w istniejącym stosie (do 200).
2. **Sklepy NPC (`shop.cpp`):**
   - W `CShop::Buy` przed weryfikacją wolnego slotu sprawdzane jest, czy ekwipunek posiada już ten sam przedmiot z wolnym miejscem na stack (`bCanStackToExisting`). Gracz może dokupić przedmioty nawet przy 0 wolnych kratek, jeśli zmieszczą się w stosie.
   - Po zakupie wywoływane jest `ch->AutoStackItem(item)` – kolejne zakupy dopełniają istniejący stos.
3. **Depozyt Sklepowy Ikarusa (`ikarus_shop_manager.cpp`):**
   - W `RecvShopSafeboxGetItemClientPacket` usunięto blokadę pobierania ("Brak miejsca w ekwipunku"), gdy przedmiot może zostać wchłonięty przez istniejący stos w inwentarzu gracza.
   - W `RecvShopSafeboxGetItemConfirm` wyciągany przedmiot najpierw dołącza do istniejącego stosu w ekwipunku (`AutoStackItem`).
4. **Magazyn Dozorcy (`safebox.cpp` i `input_main.cpp`):**
   - Odblokowano łączenie stosów wewnątrz magazynu (`safebox.cpp`) dla wszystkich przedmiotów ze stackiem > 1.
   - W `SafeboxCheckin` oraz `SafeboxCheckout` (`input_main.cpp`) dodano obsługę dopełniania istniejącego stosu przy przeciąganiu myszką między inwentarzem a magazynem.
5. **Obsługa przedmiotów z `GetMaxStack() > 1` (`char_item.cpp`):**
   - W `AutoStackItem` oraz `MoveItem` zniesiono blokadę łączenia dla przedmiotów posiadających stary atrybut `ITEM_ANTIFLAG_STACK` z GF (np. Magiczny Metal, Marmur Błogosławieństwa), jeżeli ich `GetMaxStack() > 1`. Przedmioty łączą się prawidłowo w ekwipunku i przy zakupie.

---

## 7. Zabezpieczenie Ekwipunku Przed Przypadkowym Stackowaniem (CanStack)

### Przyczyna Problemu:
Kolumna stack w tabeli bazy danych world.item_proto posiadała domyślną definicję DEFAULT 200. Sprawiało to, że w silniku C++ item->GetMaxStack() zwracało 200 również dla całego rynsztunku (bronie, zbroje, hełmy, tarcze, biżuteria itp.). Użycie warunku (item->GetMaxStack() > 1) jako alternatywy sprawiło, że miecze i zbroje zaczęły być traktowane jako stackowalne.

### Rozwiązanie (item.h, item.cpp):
Wprowadzono dedykowaną metodę ool CItem::CanStack() const, która:
1. **Bezwzględnie odrzuca ekwipunek i przedmioty unikalne:**
   ITEM_WEAPON, ITEM_ARMOR, ITEM_COSTUME, ITEM_RING, ITEM_BELT, ITEM_ROD, ITEM_PICK, ITEM_PET, ITEM_BLEND, ITEM_UNIQUE.
2. **Wymaga flagi stackowalności:**
   IsStackable() (ITEM_FLAG_STACKABLE) lub IsStackableCorDraconisVnum(GetVnum()).
3. Wykorzystano item->CanStack() we wszystkich mechanizmach silnika:
   - char_item.cpp (MoveItem, AutoStackItem)
   - ikarus_shop_manager.cpp (zakup częściowy, zakup całości, depozyt AH)
   - shop.cpp (sklepy NPC)
   - safebox.cpp (magazyn Dozorcy)
   - input_main.cpp (przenoszenie między magazynem a inwentarzem)
