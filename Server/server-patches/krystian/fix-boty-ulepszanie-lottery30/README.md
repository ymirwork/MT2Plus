# Fix Ulepszania Broni 30 lvl przez Boty (MT2009_PLUS_UPSTREAM_BOTLOGIC_LOTTERY30_V1)

## 📌 Problem i Przyczyna
Gdy bot (np. postać o nicku `WTF`) odwiedza kowala gildyjnego lub zwykłego kowala w mieście, system botów (`PLAYERBOT_UPSTREAM_BOTLOGIC_LOTTERY30_V1`) wybiera z ekwipunku nadmiarową broń na 30. poziom (np. Wachlarz Jesiennego Wiatru +0) i podejmuje próbę jej ulepszenia.

### Błąd w kodzie źródłowym (`playerbot_economy.h` / `playerbot_upstream_botlogic.h`):
1. Po udanym ulepszeniu przedmiotu w Metin2 silnik niszczy stary egzemplarz (`RemoveItem`) i tworzy nowy obiekt przedmiotu o wyższym VNumie z **nowym unikalnym ID** (`CreateItem`).
2. Kod `ManagePlayerBotRefining` nie aktualizował flagi zadania bota `mt2009_botlogic.lot30_id` (`PLAYERBOT_LOTTERY30_ID_FLAG`) nowym ID ulepszonego przedmiotu.
3. W efekcie w kolejnym cyklu sprawdzania u kowala (co 4 sekundy podczas pobytu):
   * Świeżo wytworzony przedmiot +1 był pomijany (jego nowe ID nie pasowało do flagi),
   * Silnik sprawdzał, czy poprzedni przedmiot istnieje (`ITEM_MANAGER::instance().Find(old_id)` zwracał `NULL`),
   * Bot dochodził do błędnego wniosku, że poprzedni przedmiot zniknął i pobierał z plecaka **kolejny** Wachlarz +0,
   * Ulepszał go do +1, tracił jego ID, pobierał kolejny, itd.
4. Skutkowało to serią identycznych komunikatów na czacie:
   `[Skarbiec Gildii] Postać WTF ulepszyła Wachlarz Jes. Wiatru na +1 u Kowala Broni (+1 800 Yang).`
   powtórzonych kilkukrotnie z rzędu w odstępach kilku sekund oraz gromadzeniem dziesiątek nieukończonych broni +1 w plecakach botów.

---

## 🛠️ Rozwiązanie
1. Dodano funkcję `OnPlayerBotLottery30Refined(LPCHARACTER ch, DWORD dwOldId, LPITEM pkItemAfter)` w `playerbot_upstream_botlogic.h`:
   * Gdy ulepszany przedmiot jest aktualnie śledzoną bronią lottery30, jego ID we fladze `PLAYERBOT_LOTTERY30_ID_FLAG` jest natychmiast uaktualniane do nowego ID wytworzonego przedmiotu (`pkItemAfter->GetID()`).
   * Jeśli ulepszanie osiągnęło cel sprzedaży (np. +6) lub przedmiot spłonął na kowalu bez zwoju (`pkItemAfter == NULL`), flaga jest czyszczona do `0`.
2. Zintegrowano wywołanie w `playerbot_economy.h` w `ManagePlayerBotRefining`:
   * Zarówno po zwykłym ulepszeniu u kowala (`DoRefine`), jak i zwojem (`DoRefineWithScroll`).
3. Efekt w grze:
   * Bot konsekwentnie kontynuuje ulepszanie **tej samej broni**: +1 -> +2 -> +3 -> +4 -> +5...
   * Komunikaty na czacie pokazują naturalny, logiczny progres kolejnych poziomów przedmiotu oraz odpowiednio rosnące kwoty wpłacane do Skarbca Gildii (np. 1 800 Yang na +1, 3 600 Yang na +2, 7 200 Yang na +3 itd.).
   * Bot nie zużywa dziennego limitu na wielokrotne rozpoczynanie nowych broni +0.

---

## 📁 Zmodyfikowane Pliki
* `Server/linux-port/docker/game/src/server/game/src/playerbot_upstream_botlogic.h`
* `Server/linux-port/docker/game/src/server/game/src/playerbot_economy.h`
