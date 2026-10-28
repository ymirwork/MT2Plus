# Powiadomienia o Skarbcu Gildii (MT2009_PLUS_GUILD_TREASURY_NOTIFY_V1)

## 📌 Opis Modyfikacji
Modyfikacja dodaje dwa zintegrowane systemy powiadomień na czacie gry związane ze Skarbcem Gildii i podatkiem odprowadzanym z ulepszania ekwipunku oraz przetapiania rud:

1. **Powiadomienie na żywo o zasileniu skarbca ze szczegółami przedmiotu (`char.cpp` / `char_item.cpp` - `PayRefineFee`):**
   * Za każdym razem, gdy jakikolwiek gracz lub bot (spoza danej gildii) ulepszy lub spali przedmiot u kowala gildyjnego lub wytopi przetop u alchemika gildyjnego, 15% opłaty odprowadzane jest do kasy gildii.
   * Wszyscy zalogowani członkowie gildii otrzymują na czacie gildyjnym komunikat w czasie rzeczywistym z podaniem nicku gracza/bota, nazwy przedmiotu, docelowego poziomu ulepszenia (+X), rodzaju rzemieślnika oraz kwoty zysku:
     * *Pomyślne ulepszenie:* `[Skarbiec Gildii] Postać <Nick> ulepszyła <Przedmiot> na +<Poziom> u <Kowala Broni / Płatnerza / Jubilera> (+<Kwota> Yang).`
       *(np. `[Skarbiec Gildii] Postać Krystian ulepszyła Miecz Bojowy na +9 u Kowala Broni (+75 000 Yang).`)*
     * *Spalenie przedmiotu:* `[Skarbiec Gildii] Postać <Nick> spaliła <Przedmiot> na +<Poziom> u <Kowala Broni / Płatnerza / Jubilera> (+<Kwota> Yang).`
       *(np. `[Skarbiec Gildii] Postać Krystian spaliła Miecz Bojowy na +9 u Kowala Broni (+75 000 Yang).`)*
     * *Przetop u Alchemika:* `[Skarbiec Gildii] Postać <Nick> przetopiła rudę u Alchemika (+<Kwota> Yang).`
   * Wiadomości są poprawnie sformatowane w kodowaniu CP1250 dla klienta gry (polskie znaki: ć, ł, ę).

2. **Powiadomienie o stanie skarbca przy logowaniu (`input_login.cpp` - `Entergame`):**
   * Przy każdym wejściu do gry gracza należącego do gildii, na czacie informacyjnym (`CHAT_TYPE_INFO`) pojawia się status majątku gildii.
   * Jeśli od ostatniego logowania do skarbca wpłynęły nowe środki (z kowala, alchemika lub zrzutek botów), system informuje gracza o dokładnej nadwyżce:
     * `[Skarbiec Gildii] Aktualny stan skarbca: 15 420 000 Yang (+2 100 000 Yang od Twojego ostatniego logowania).`
   * Jeśli stan skarbca nie uległ zmianie:
     * `[Skarbiec Gildii] Aktualny stan skarbca: 15 420 000 Yang.`
   * Zabezpieczenie przed spamem (throttle 60s): częste teleporty i zmiany map nie powielają komunikatu. Wartości zapamiętywane w quest flagach gracza (`gt.gold_lo`, `gt.gold_hi`, `gt.notice_time`).

---

## 🛠️ Zmodyfikowane Pliki
* `Server/linux-port/docker/game/src/server/game/src/char.h`
* `Server/linux-port/docker/game/src/server/game/src/char.cpp`
* `Server/linux-port/docker/game/src/server/game/src/char_item.cpp`
* `Server/linux-port/docker/game/src/server/game/src/input_login.cpp`

## 🚀 Instalacja
Uruchomienie skryptu:
```bash
python apply_guild_treasury_notify.py --server-dir ../../..
```
Następnie przebudowa kontenera `game` w Dockerze:
```bash
docker compose --project-directory Server/linux-port/docker build --pull=false game
docker compose --project-directory Server/linux-port/docker up -d game
```
