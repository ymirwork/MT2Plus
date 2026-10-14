# MT2009 Plus — aktualizacja trackera do serwera 2.33.0

Paczka zawiera część serwerową i kliencką. Sprawdzona na VPS z serwerem 2.33.0 oraz kliencie 2.0.64. Dotychczasowa poprawka źródeł 2.31.0 pasuje do nowego silnika; instalator sprawdza to przed zapisem, buduje grę i czeka na stan `healthy`.

- `INSTRUKCJA-VPS.md` — aktualizacja własnego serwera Linux/VPS.
- `INSTRUKCJA-PC.md` — aktualizacja własnego serwera Windows/PC.
- `INSTRUKCJA-GRACZE.md` — gracze korzystający z cudzego serwera.
- `server/` — kod i skrypt przywracający tracker po oficjalnej aktualizacji.
- `client/` — program trackera i wspólny plik `Aktualizuj-i-graj.bat`.

Skrypt BAT uruchamia oficjalny patcher, a po jego zamknięciu nakłada znalezione obok niego dodatki: `MT2009-Dodatek.exe`, `MT2009-Dopalacze.exe`, `MT2009-Tracker.exe` i `MT2009-Sklep.exe`. Nie trzeba instalować wszystkich czterech. Części serwerowe instaluje administrator własnego serwera.

Na VPS autora potwierdzono: tracker, teleport, nieskończoną pelerynę oraz obie Auto Mikstury. Panel dopalaczy i sklep przeszły kontrolę zgodności plików klienta 2.0.64, ale ich interfejsy nie były sprawdzane w grze na tym VPS.
