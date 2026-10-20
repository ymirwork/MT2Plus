# Tracker — aktualizacja własnego VPS do 2.33.0

Jeśli prowadzisz własny serwer, najpierw dokończ jego oficjalną aktualizację do 2.33.0 i zrób kopię świata. Poniższy przykład używa katalogu `/opt/metin2/stack`. Przy innym katalogu zastąp go własną ścieżką do folderu z `VERSION` i `linux-port`.

Prześlij **zawartość** katalogu `server` z tej paczki do `/opt/metin2/mods/boss-tracker/` (albo do własnego trwałego katalogu poza folderem aktualizowanym przez MT2009 Plus). Zachowaj oba dołączone pliki `.patch`.

Kontrola bez zmian:

```sh
cat /opt/metin2/stack/VERSION
python3 /opt/metin2/mods/boss-tracker/tracker_maintenance.py --server-root /opt/metin2/stack --check
```

Przy wyniku `PATCH_COMPATIBLE` albo `ALREADY_INSTALLED` przywróć lub potwierdź działającą wersję gry:

```sh
sh /opt/metin2/mods/boss-tracker/aktualizuj-serwer-z-trackerem.sh repair
docker compose --project-directory /opt/metin2/stack/linux-port/docker ps game
```

Poczekaj na `TRACKER_READY` oraz `healthy`. Przebudowa na chwilę restartuje grę. Jeśli kontrola pokaże `NIEZGODNA AKTUALIZACJA`, nie wymuszaj instalacji: ta baza wymaga osobnej poprawki.

Przy **kolejnej** oficjalnej aktualizacji możesz wykonać całość jedną komendą:

```sh
sh /opt/metin2/mods/boss-tracker/aktualizuj-serwer-z-trackerem.sh update
```

Skrypt uruchamia oficjalny aktualizator, następnie skrypt nieskończonych przedmiotów, jeśli jest obecny, i naprawę trackera. Zatrzyma się przy niezgodnym przyszłym wydaniu zamiast wgrać niepasującą poprawkę.

Przykład niestandardowej instalacji `/opt/mt2009plus`: umieść pliki w `/opt/mt2009plus/mods/boss-tracker/`, a kontrolę uruchom z `--server-root /opt/mt2009plus`. Skrypt `aktualizuj-serwer-z-trackerem.sh` sam rozpozna tę ścieżkę; można ją też podać jawnie: `M2_SERVER_ROOT=/opt/mt2009plus sh /opt/mt2009plus/mods/boss-tracker/aktualizuj-serwer-z-trackerem.sh repair`.

Gracze, którzy mają już klienta z trackerem i plik BAT, korzystają z instrukcji `INSTRUKCJA-GRACZE.md`. Nie kopiują plików serwera do klienta.
