# MT2009 Plus — sklep 160 pól, odblokowanie kluczami

Paczka dla twórców serwerów MT2009 Plus. Baza: **serwer 2.30.0, klient 2.0.61**. Zawiera instalator części serwerowej oraz punktowy instalator klienta. Nie zawiera adresów IP, danych dostępowych, bazy danych ani kompletnego `root.data`/`root.index`.

## Co dodaje

- Dwa bloki sklepu offline po 80 pól. Pierwszy zachowuje dotychczasowe 40 pól zwykłych, 20 pól za klucze i 20 pól premium.
- W drugim bloku 80 pól odblokowywanych po pięć. Każdy nowy krok wymaga **2 Drewnianych Kluczy (VNUM 30376)**. Dotychczasowe cztery kroki pozostają po jednym kluczu.
- Łączny licznik odblokowania kończy się na 20. Istniejący postęp postaci zostaje zachowany; baza danych nie wymaga migracji.
- Przy zakładaniu sklepu można jednorazowo wystawić do 80 przedmiotów. Kolejne dodaje się z poziomu zarządzania otwartym sklepem.
- Drugi blok dotyczy sklepu offline; zwykły kram przy postaci go nie otrzymuje.

## Kolejność

1. Wybierz [instrukcję VPS](INSTRUKCJA-VPS.md) albo [instrukcję PC](INSTRUKCJA-PC.md).
2. Wgraj i zbuduj część serwerową.
3. Zainstaluj część klienta w **kopii aktualnego klienta** i sprawdź działanie.
4. Udostępnij zmienione pliki klienta dopiero po próbie na własnej kopii.

Instalator serwera sprawdza SHA256 plików bazowych i przerywa przed zmianami, jeśli wersja lub lokalne modyfikacje są inne. Nie wymuszaj instalacji po błędzie; dostosuj kod do swojej bazy. Instalator klienta zachowuje wszystkie pozostałe pliki w paczce `root`, dzięki czemu nie usuwa trackera, pelerynek, autopotek ani dopalaczy.

**Status weryfikacji:** klient 2.0.61 przeszedł kontrolę i instalację na kopii z trackerem, nieskończonymi przedmiotami i Panelem Dopalaczy. Serwerowy instalator przeszedł kontrolę i instalację na izolowanej kopii źródeł 2.30.0. Sklep nie został wdrożony na działającym serwerze ani przetestowany w grze jako komplet. Przed udostępnieniem innym przeprowadź próbę według sekcji testów.


