# Drop Zielonej Siły i Zielonego Czaru w M1/M2, Priorytet Botów i Wymiana Pozwoleń

## Opis Modyfikacji
Modyfikacja gospodarczo-rozwojowa wspierająca wczesną fazę rozgrywki (early-game) dla graczy i botów w klimacie serwera Hard:
1. **Drop Zielonej Siły i Zielonego Czaru w M1 i M2:**
   - **Metiny M1** (Cierpienia, Walki, Bitwy, Chciwości – VNUM 8001–8004): **5% szansy** na drop Zielonego Czaru (`71151`) lub Zielonej Siły (`71152`) (losowanie 50/50).
   - **Metiny M2** (Czerni, Ciemności, Zazdrości – VNUM 8005–8007): **8% szansy** na drop Zielonego Czaru lub Zielonej Siły.
   - **Bossy M1/M2** (Lykos, Scrofa, Bera, Tigris, Mi-Jung, Eun-Jung, Se-Rang, Jin-Hee, Mahon, Bo, Goo-Pae, Chuong, Best. Kapitan): **dokładnie 15% szansy** na drop Zielonego Czaru lub Zielonej Siły (zgodnie z zaleceniem operatora – brak gwarantowanego 100%, zachowany styl Hard).
   - Drop trafia zarówno do graczy (wyrzucany ze znacznikiem na ziemię), jak i botów (bezpośrednio do inwentarza z kontrolą wolnych slotów).
   - Zintegrowano z podglądem celu (`MobPreview`) oraz Drop Wiki (`/drop_wiki`).
2. **Zaawansowane Priorytety Celowania Botów (Targeting):**
   - Boty poszukujące bonusów do 40 poziomu traktują Metiny M1/M2 z podwyższonym priorytetem (`+500 000` punktów wagowych).
   - Bossy M1/M2 zyskują priorytet `+800 000` punktów wagowych dla botów <= 40 poziomu (`+500 000` dla poziomów 41–45), co powoduje, że boty aktywnie polują na bossy w celu zdobycia zielonych kamieni do rozwijania własnego uzbrojenia.
3. **Automatyczna Wymiana i Gospodarka Pozwoleń (30370 / 30368 / 30369):**
   - Wprowadzono procedurę `ManagePlayerBotPermitExchange`: boty automatycznie wymieniają dropnięte Pozwolenia na Zaczarowanie (`30370`) na zbywalne Zaczarowanie Przedmiotu (`71284`), a Pozwolenia na Wzmocnienie (`30368`, `30369`) na Wzmocnienie Przedmiotu (`71285`).
   - Następnie w pętli decyzyjnej bot w pierwszej kolejności wykorzystuje otrzymane Zaczarowania/Wzmocnienia do dopalenia własnego ekwipunku, a cały nadmiar natychmiast wystawia w tobołku offline (Ikarus) po cenach rynkowych (1.38M / 5M Yang), zasilając rynek dla innych graczy.
4. **Wycena Katalogowa:**
   - Dodano Pozwolenia (`30368`, `30369`, `30370`) do tabel cenowych `playerbot_price_tables.h`.

## Dotknięte Pliki
- `Server/linux-port/docker/game/src/server/game/src/item_manager.cpp` (Drop, MobPreview, DropWiki)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_targeting.h` (Priorytety Metinów i Bossów M1/M2)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_bonus.h` (`ManagePlayerBotPermitExchange`, integracja w `ManagePlayerBotBonusReroll`)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_town.h` (Wymiana przed zebraniem towarów na sklep)
- `Server/linux-port/overlays/playerbot/src/game/src/playerbot_price_tables.h` (Wyceny pozwoleń)
