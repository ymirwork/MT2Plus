# 🌟 Obieg, Napełnianie, Rynek i Retencja Auto-Potek Botów (MT2009_PLUS_BOT_AUTOPOTION_ECO_V1)

## 📌 Problem i Cel
1. **Zapychanie ekwipunku:** Boty otwierające skrzynki eventowe (np. `Pudełko ze Słonecznikiem` 83027 z 30% szansą na Eliksir Księżyca M 72727) gromadziły po kilkadziesiąt sztuk autopotek w plecaku.
2. **Puste flaszki (`socket1 == socket2`):** Po wypiciu eliksiru silnik MT2009 nie usuwał przedmiotu (`// MT2009 edit: do not remove empty potion, just deactivate`). Boty nie sprzedawały ich u NPC (blokada `ITEM_ANTIFLAG_SELL`) i nie usuwały, przez co puste flakony blokowały dziesiątki slotów na stałe.
3. **Brak obiegu rynkowego:** Boty nigdy nie wystawiały nadmiaru na tobołki w m1, a inne boty potrzebujące many/PŻ ich nie odkupowały.

---

## 🛠️ Wprowadzone Rozwiązania

1. **Limity posiadania (Hierarchia slotów):**
   - **Podręczny ekwipunek:** `PLAYERBOT_AUTO_POTION_BAG_KEEP = 3` (1 aktywna + max 2 w zapasie).
   - **Magazyn Dozorcy (Safebox):** `PLAYERBOT_AUTO_POTION_SAFEBOX_KEEP = 3` sztuki żelaznej rezerwy.
   - **Sklepik offline (Tobołek):** `PLAYERBOT_AUTO_POTION_SHOP_MAX = 4` stoiska z autopotkami (ochrona przed floodingiem rynku).
   - **Niszczenie nadmiaru:** Każda kolejna autopotka powyżej limitów jest bezpiecznie niszczona (`RemoveItem`), chroniąc ekwipunek przed zapchaniem.

2. **Napełnianie u Alchemika (Yang Sink):**
   - Podczas wizyty w mieście u Alchemika (NPC 20001), bot sprawdza puste flaszki.
   - Jeśli bota stać i potrzebuje zapasu: płaci równowartość mikstur u Handlarki (4 Yang / SP, 2 Yang / HP; np. 400 000 Yang za 100k PE) i flaszka zostaje napełniona (`socket1 = 0`).
   - Jeśli bota nie stać lub ma już pełne eliksiry: pusta butelka jest usuwana z ekwipunku.

3. **Wycena i wystawianie na tobołkach:**
   - Nadmiarowe pełne autopotki są wystawiane na tobołku z marżą 25% (np. 500 000 Yang za Eliksir Księżyca M).
   - Aktywne lub częściowo zużyte autopotki nigdy nie trafiają na handel.

4. **Wygasanie niesprzedanych autopotek (Shelf Life / TTL):**
   - Jeśli autopotka stoi na tobołku dłużej niż `PLAYERBOT_RARE_GOODS_MERCHANT_AFTER_MS` (~24h), bot ściąga ją ze stoiska i usuwa, zwalniając miejsce na nowe towary.

5. **Skupowanie przez inne boty:**
   - Boty expiące na mapach bez dropu skrzynek, które nie mają żadnej autopotki, a mają wystarczająco Yang, przeszukują stoiska i odkupują pełne eliksiry od graczy oraz innych botów.

---

## 📂 Zmodyfikowane Pliki
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_consumables.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_town.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_economy.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_market.h`
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_market.h`
- `Server/linux-port/docker/game/Dockerfile` (dodanie brakujących sygnatur questowych `mes.get_arguments`, `pc.is_premium_subscription`)
