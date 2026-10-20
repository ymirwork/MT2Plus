# Tracker — aktualizacja własnego serwera PC do 2.33.0

Dotyczy osób prowadzących lokalny serwer w Docker Desktop. Wymagane są Python 3, Git for Windows i działające `docker compose`. Zrób kopię serwera i świata. Zaktualizuj serwer oficjalnym launcherem do 2.33.0.

Zamknij grę i patcher. Skopiuj **zawartość** katalogu `client` z paczki do folderu klienta, obok `metin2client.exe`; zastąp stary `Aktualizuj-i-graj.bat` i folder `Tracker-Serwer`. Zachowaj inne programy dodatków obecne w folderze.

Jeśli ten klient nie był wcześniej powiązany z lokalnym serwerem, uruchom raz `Ustaw-serwer-PC.bat` i wskaż **główny folder serwera**, zawierający `VERSION` oraz `linux-port` (np. `C:\Games\metin2mod`).

Uruchom `Aktualizuj-i-graj.bat`. Po pobraniu aktualizacji zamknij oficjalny patcher bez klikania „GRAJ”. Skrypt sprawdzi źródła lokalnego serwera, nałoży tracker, przebuduje `game`, uruchomi kontener i poczeka na `TRACKER_READY`. Pierwsza kompilacja może potrwać kilka minut. Potem nałoży dostępne dodatki klienta i uruchomi grę.

Po kolejnej oficjalnej aktualizacji serwera i klienta uruchamiaj ten sam BAT. Jeśli zobaczysz `NIEZGODNA AKTUALIZACJA`, prześlij komunikat i numer z `VERSION`; skrypt nie wymusza niepasującej poprawki. Części serwerowe sklepu oraz nieskończonych przedmiotów mają własne instrukcje.

Ręczna kontrola, gdy gra nie wystartuje (PowerShell, zamień ścieżkę na własną):

```powershell
Get-Content 'C:\Games\metin2mod\VERSION'
docker compose --project-directory 'C:\Games\metin2mod\linux-port\docker' ps
```

Kontener `game` powinien być `healthy`. Aby uruchomić również panele, użyj `docker compose --project-directory 'C:\Games\metin2mod\linux-port\docker' up -d`.
