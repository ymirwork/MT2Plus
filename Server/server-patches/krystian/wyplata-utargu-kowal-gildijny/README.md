# Wyplata Utargu z Ulepszen i Przetopow Rzemieslnikow Gildyjnych (MT2009_PLUS_CRAFTER_REVENUE_V1)

## 1. Opis i Zalozenia Biznesowe
Gdy gracze spoza gildii korzystaja z uslug rzemieslnikow gildyjnych (Kowal Broni, Platnerz, Jubiler, Alchemicy gildyjni):
- 15% oplaty za ulepszenie trafia do skarbca gildii oraz zwieksza licznik utargu (`guild_payout_<guild_id>`).
- Lider gildii moze w kazdej chwili wyplacic zebrany utarg bezposrednio do swojego ekwipunku:
  - Bezposrednio u rzemieslnika na ziemi gildii (np. **Stanley - Kowal Broni 20044**, **Platnerz 20045**, **Jubiler 20046**).
  - W miescie u **Straznika Wsi (11000, 11002, 11004)** (opcja dialogowa `Odbierz utarg gildii`).
- **Balans ekonomiczny (Gold Sink):**
  - Od kazdej wyplaty pobierany jest **15% podatek cesarski**, ktory jest bezpowrotnie niszczony przez silnik gry (usuwany z obiegu serwera).
  - O kazdej wyplacie czlonkowie gildii sa informowani komunikatem na czacie gildyjnym dla pelnej transparentnosci.
- **Podglad w Oknie Informacji o Gildii:**
  - W oknie gildii (skrot `Alt+G`) w wierszu `Do wyplaty` (nad skarbcem `Yang`) wyswietlana jest aktualna kwota zgromadzonego utargu.
  - Pula startuje od **0 Yang** i jest synchronizowana z serwerem za pomoca pakietu polecenia `GuildPayout <amount>`.

---

## 2. Architektura Rozwiazania i Baza Danych MySQL

### Baza Danych MySQL:
- Utworzona dedykowana tabela w bazie `player`:
```sql
CREATE TABLE IF NOT EXISTS player.guild_crafter_revenue (
    guild_id INT UNSIGNED NOT NULL PRIMARY KEY,
    payout_available BIGINT NOT NULL DEFAULT 0,
    total_earned BIGINT NOT NULL DEFAULT 0,
    total_withdrawn BIGINT NOT NULL DEFAULT 0,
    last_withdrawal_time DATETIME DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
```
- Inicjalizacja poprzez skrypt `Server/linux-port/docker/mariadb/initdb.d/30-guild-crafter-revenue.sql`.
- Kazde ulepszenie przez gracza z zewnatrz wykonuje zapytanie `INSERT ... ON DUPLICATE KEY UPDATE` zwiekszajac `payout_available` oraz `total_earned`.
- Kazda wyplata przez Lidera odejmuje z `payout_available`, zwieksza `total_withdrawn` i ustawia `last_withdrawal_time = NOW()`.
- Rownolegle stan jest synchronizowany z event flagami silnika `guild_payout_<guild_id>` w `player.quest` dla ultraszybkiej obslugi P2P w pamieci RAM miedzy rdzeniami.

### Silnik Gry (C++):
- `questlua_guild.cpp` (`guild_payout_withdraw` oraz `guild_treasury_withdraw`):
  - Uzycie natywnej metody `ch->ChangeGold(net_gold)` (zamiast `PointChange(POINT_GOLD)`), ktora natychmiastowo dodaje Yang do ekwipunku postaci i wysyla pakiet `TPacketGCGoldUpdate` do klienta.
  - Rejestracja w logach ekonomicznych poprzez `DBManager::instance().SendMoneyLog(MONEY_LOG_GUILD, ...)`.
  - Aktualizacja stanu w tabeli `player.guild_crafter_revenue`.
- `char.cpp` (`PayRefineFee`):
  - Inkrementuje flage eventowa `guild_payout_<guild_id>` o kwote prowizji `iFee`.
  - Inkrementuje `payout_available` i `total_earned` w tabeli `player.guild_crafter_revenue`.
  - Wolana metoda `pGuild->SendGuildPayout(curPayout)` rozglasza zaktualizowany stan do online czlonkow.
- `guild.h` / `guild.cpp`:
  - Dodana metoda `void SendGuildPayout(int amount)`.
  - W `SendGuildInfoPacket` wysylana jest komenda `GuildPayout <payout>` przy kazdym otwarciu/odswiezeniu okna gildii.
- `input_login.cpp` (`Entergame`):
  - Przy logowaniu gracza nalezacego do gildii serwer wysyla aktualna wartosc `GuildPayout <payout>`.

### Questy i NPC (Lua):
- `questlib.lua`:
  - `open_guild_payout_dialog(crafter_title)`: uniwersalny interfejs wyplaty z formatowaniem Yang, mozliwoscia wyplaty calosci lub dowolnej kwoty, opisem zasad oraz przyciskiem testowym dla GM.
- `guild_building_npc.quest` & obiekty `20044`, `20045`, `20046`:
  - Przechwytuje klikniecie (`.click`) na rzemieslnika i jesli postac to Lider gildii bedacy wlascicielem, oferuje menu:
    1. "Odbierz utarg ze skarbca" -> uruchamia `open_guild_payout_dialog`
    2. "Informacje o ulepszaniu" -> wyswietla oryginalny opis
    3. "Zamknij"
- `guild_crafter_revenue.quest`:
  - Rejestruje opcje `.chat` "Odbierz utarg gildii" u Straznikow Wsi (`11000`, `11002`, `11004`) dla Lidera w kazdym krolestwie.
  - Rejestruje opcje `.chat` u wszystkich rzemieslnikow i alchemikow gildyjnych.

### Klient Gry (Python):
- `uiscript/guildwindow_guildinfopage.py`:
  - Wiersz `GuildPayout` na pozycji `y = 217` z etykieta "Do wyplaty" oraz slotem domyslnie wyswietlajacym "0".
- `uiguild.py`:
  - Inicjalizacja `self.payoutAmount = 0`.
  - Metoda `SetGuildPayout(amount)` odswiezajaca pole po odebraniu pakietu.
  - `RefreshGuildInfoPage` wyswietla wartosc `payoutAmount` (startuje od 0).
- `interfacemodule.py` & `game.py`:
  - Przekierowanie i obsluga komendy `serverCommandList["GuildPayout"]`.
