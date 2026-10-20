# Poradnik Instalacji na Serwerze Linux VPS: Wstawanie z 100% HP

## Wymagania Wstępne
- Uprawnienia użytkownika `root` lub `sudo`
- Zainstalowane środowisko Docker oraz Docker Compose
- Zainstalowany `python3` (`apt update && apt install -y python3`)

---

## Metoda 1: Automatyczna (Zalecana)

1. Prześlij folder paczki na serwer VPS (np. do `/tmp/Wstawanie_100_Procent_HP`).
2. Wejdź do katalogu i nadaj prawa wykonywalności instalatorowi:
   ```bash
   cd /tmp/Wstawanie_100_Procent_HP
   chmod +x install_vps.sh
   ./install_vps.sh /sciezka/do/Server
   ```
3. Potwierdź przebudowę i restart kontenera `game`.

---

## Metoda 2: Ręczna (Manual Patch)

1. Zaaplikuj patch bezpośrenio przez `patch` lub skrypt Pythona:
   ```bash
   python3 serwer_cpp/apply_revive_100_hp_server.py --server-dir /sciezka/do/Server
   ```
2. Przebuduj kontener gry:
   ```bash
   cd /sciezka/do/Server/linux-port/docker
   docker compose build game
   docker compose restart game
   ```
3. Zweryfikuj logi rdzeni:
   ```bash
   docker compose logs -f --tail=30 game
   ```
