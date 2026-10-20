# Instalacja lokalna na Windows — MT2009 Plus 2.30.0

Przykład używa `C:\Games\metin2mod` jako katalogu **serwera**. U Ciebie może być `C:\METIN2MOD\mt2009 plus serwer` albo inna ścieżka. Wskaż katalog z `MOD_VERSION` lub `VERSION` oraz `linux-port`. Folder klienta jest osobny.

## 1. Przygotowanie

Zrób kopię katalogu serwera i bazy danych. Zamknij grę, patcher i sklep. Wypakuj paczkę do dowolnego miejsca, np. `C:\Games\MT2009-PLUS-SKLEP-160-SLOTOW-KLUCZE-2.30.0`. Wymagane są Python 3, Docker Desktop oraz działające `docker compose`. W PowerShell:

```powershell
Get-Content "C:\Games\metin2mod\MOD_VERSION"
Get-Content "C:\SCIEZKA\DO\KLIENTA\CLIENT_VERSION"
```

Jeśli nie ma `MOD_VERSION`, odczytaj `VERSION` w tym samym katalogu. Oczekiwane wersje: serwer `2.30.0`, klient `2.0.61`.

## 2. Kontrola i instalacja serwera

```powershell
Set-Location "C:\Games\MT2009-PLUS-SKLEP-160-SLOTOW-KLUCZE-2.30.0"
py -3 .\01-SERWER-2.30.0\instaluj_serwer.py --server-root "C:\Games\metin2mod" --check
py -3 .\01-SERWER-2.30.0\instaluj_serwer.py --server-root "C:\Games\metin2mod" --install
```

Zamień obie ścieżki na własne. Jeśli nie masz polecenia `py -3`, użyj `python` po zainstalowaniu Python 3. **Najpierw sprawdź wynik `--check`**. Przy `WERSJA NIEZGODNA` nie uruchamiaj `--install`; Twoje źródła wymagają ręcznego dopasowania. Skrypt zachowuje kopię zmienionych plików w katalogu serwera `backup-sklep-160-DATA`.

## 3. Budowanie i start całego środowiska

```powershell
Set-Location "C:\Games\metin2mod"
docker compose --project-directory .\linux-port\docker build game
docker compose --project-directory .\linux-port\docker up -d
docker compose --project-directory .\linux-port\docker ps
```

Poczekaj na `Built`. Komendy uruchamiaj w katalogu serwera, a nie klienta. `up -d` uruchamia cały zestaw usług, w tym panel administracyjny. **Nie ograniczaj się do `up game`**: to był powód, dla którego na jednej lokalnej instalacji nie działały panele mimo poprawnej gry. Jeśli panele nadal są niedostępne, sprawdź `docker compose ... ps` i logi usług, które nie są `Up`.

## 4. Klient

Pracuj na kopii aktualnego klienta. Z folderu wypakowanej paczki:

```powershell
py -3 .\02-KLIENT-2.0.61\instaluj_klient.py --client "C:\SCIEZKA\DO\KLIENTA" --check
py -3 .\02-KLIENT-2.0.61\instaluj_klient.py --client "C:\SCIEZKA\DO\KLIENTA" --install
```

Patcher i gra muszą być zamknięte. Skrypt aktualizuje `pack/root.data` i `pack/root.index`, zachowuje pozostałe skrypty klienta i robi kopię obu plików. Własny aktualizator może rozsyłać tę parę. `Aktualizuj-i-graj.bat` od trackera sam nie instaluje sklepu.

## 5. Sprawdzenie

Zaloguj postać, otwórz sklep offline i sprawdź oba bloki. Przetestuj stary klucz, nowy koszt dwóch kluczy, zakup i odzyskanie przedmiotu z drugiego bloku oraz zapis po ponownym logowaniu. Sprawdź dotychczasowe modyfikacje klienta oraz dostęp do paneli. Gdy wszystko działa, dopiero wtedy opublikuj klienta dla innych.

## Cofnięcie

Przywróć oryginalne pliki serwera i klienta z folderów `backup-sklep-160-DATA`, przebuduj obraz `game`, uruchom cały stos. Przed cofnięciem wycofaj towary z dodatkowych pól sklepu.


