# Instalacja na VPS — MT2009 Plus 2.30.0

W przykładach katalog serwera to `/opt/metin2/stack`. Jeżeli u Ciebie jest inny, zastąp go **w każdym poleceniu** własnym katalogiem zawierającym `VERSION` lub `MOD_VERSION` i `linux-port`. Nie wpisuj nigdzie swojego IP do paczki.

## 1. Przygotowanie

Zrób kopię serwera i bazy danych swoim dotychczasowym sposobem. Zaplanuj przerwę na przebudowę gry. Wypakuj archiwum na swoim komputerze, a cały wypakowany folder prześlij na VPS, np. do `/root/MT2009-PLUS-SKLEP-160-SLOTOW-KLUCZE-2.30.0`. Użyj własnego narzędzia SCP/SFTP i własnych danych połączenia. Nie wysyłaj archiwum do katalogu klienta.

Na VPS sprawdź wersję:

```bash
cat /opt/metin2/stack/VERSION
```

Oczekiwany wynik: `2.30.0`. Wymagany jest Python 3 oraz działające Docker Compose.

## 2. Kontrola i instalacja źródeł

```bash
cd /root/MT2009-PLUS-SKLEP-160-SLOTOW-KLUCZE-2.30.0
python3 01-SERWER-2.30.0/instaluj_serwer.py --server-root /opt/metin2/stack --check
```

Kontrola powinna zakończyć się tekstem `KONTROLA OK`. Jeśli pokaże `WERSJA NIEZGODNA`, **zatrzymaj się**: część źródeł jest już zmieniona albo ma inną wersję. Trzeba przenieść zmiany ręcznie do tej bazy, a nie nadpisywać jej całymi plikami.

```bash
python3 01-SERWER-2.30.0/instaluj_serwer.py --server-root /opt/metin2/stack --install
```

Skrypt robi kopię zmienianych plików w `/opt/metin2/stack/backup-sklep-160-DATA`. Kopia nie zawiera bazy danych.

## 3. Przebudowa i uruchomienie

```bash
cd /opt/metin2/stack/linux-port/docker
docker compose build game
```

Poczekaj na komunikat o poprawnym zbudowaniu obrazu `metin2/game:mt2009`. Jeśli kompilacja się nie powiedzie, nie restartuj gry. Po udanym buildzie:

```bash
docker compose stop -t 60 game
docker compose up -d --no-deps --force-recreate game
docker compose up -d
docker compose ps
```

Po wymianie gry sprawdź **cały stos**, również usługi panelu i bazy. Samo `up game` może pozostawić panele administracyjne niedostępne. Pokazane polecenia odtwarzają kontener gry i uruchamiają brakujące usługi bez wymuszania ponownego tworzenia działającej bazy.

## 4. Klient

Na swoim komputerze przygotuj **kopię aktualnego klienta 2.0.61**. Zamknij grę i patcher. Wypakowany folder paczki może leżeć gdziekolwiek. W PowerShell uruchom:

```powershell
py -3 .\02-KLIENT-2.0.61\instaluj_klient.py --client "C:\SCIEZKA\DO\KLIENTA" --check
py -3 .\02-KLIENT-2.0.61\instaluj_klient.py --client "C:\SCIEZKA\DO\KLIENTA" --install
```

Polecenia uruchom z katalogu wypakowanej paczki. Zamień ścieżkę w cudzysłowie na **folder klienta zawierający `CLIENT_VERSION` i `pack`**. Jeśli `py -3` nie działa, użyj `python` po zainstalowaniu Python 3. Skrypt sam tworzy folder `backup-sklep-160-DATA` obok klienta. Nie podmieniaj starymi plikami `root.data`/`root.index` z oryginalnej paczki kolegi.

Osoby korzystające z Twojego klienta potrzebują później zaktualizowanego `pack/root.data` i `pack/root.index`. Dodaj **oba wygenerowane pliki** do własnej dystrybucji klienta. Sam instalator nie zmienia patchera ani jego adresów. Nasz `Aktualizuj-i-graj.bat` obsługuje tracker, pelerynki, autopotki i dopalacze, ale **nie nakłada sklepu**.

## 5. Próba po instalacji

Sprawdź: otwarcie sklepu, istniejące pola i postęp, pierwszy stary krok za 1 klucz, nowy krok za 2 klucze, brak zużycia przy tylko jednym kluczu, przedmiot wysoki na granicy bloku, zakup i wycofanie przedmiotu z drugiego bloku, ponowne logowanie, restart gry, panele administracyjne. Potwierdź też działanie własnych wcześniejszych modyfikacji klienta.

## Cofnięcie

Zatrzymaj grę, przywróć zmienione pliki serwera z katalogu `backup-sklep-160-DATA` do odpowiadających im ścieżek w `/opt/metin2/stack`, przebuduj `game` i uruchom cały stos. W kliencie przywróć razem `root.data` i `root.index` z jego folderu `backup-sklep-160-DATA`. Gdy postacie zdążyły już użyć nowych pól, przed cofnięciem usuń z nich wystawione przedmioty.


