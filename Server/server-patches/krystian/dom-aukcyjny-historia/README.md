# Dom Aukcyjny – Historia Handlu i Zakupów (AH_V2)

## Opis Modułu
Autorskie rozszerzenie Domu Aukcyjnego w MT2Plus o pełną historię zakupów i handlu:
- Przycisk **"Historia"** na belce tytułowej okna obok przycisku `[Reset]`.
- Dedykowane okno `AuctionHistoryDialog` (`574 x 420 px`) z podsumowaniem transakcji, łączną sumą wydanych Yang oraz przewijaną listą zakupów (obsługa kółka myszy).
- Każdy wpis w historii wyświetla:
  - Ikonę przedmiotu ze skalowaniem i obsługą ksiąg oraz marmurów.
  - Pełną nazwę przedmiotu (z poziomem ulepszenia `+`, nazwą umiejętności lub potwora).
  - Ilość zakupionych sztuk.
  - Cenę łączną (oraz stawkę za sztukę w przypadku pakietów).
  - Sprzedawcę / nazwę tobołka.
  - Datę i godzinę zakupu (`DD.MM.YYYY HH:MM`).
- **Pełny podgląd przedmiotu (Item Tooltip):** Po najechaniu myszką na wiersz wyświetla się oryginalny dymek Metin2 z włożonymi KD i bonusami 1-5 dokładnie takimi, jakie miał kupiony przedmiot.
- **Szukaj w AH (1-klik):** Dwuklik na pozycji lub zaznaczenie i kliknięcie przycisku "Szukaj w AH" natychmiast wyszukuje dany przedmiot w Domu Aukcyjnym.
- **Czyszczenie historii:** Przycisk "Wyczyść historię" z potwierdzeniem dialogowym.
- **Trwałość danych:** Zapis do pliku `cache/ah_history_<nazwa_postaci>.json` (osobna historia dla każdej postaci, bufor do ostatnich 200 transakcji).

## Zmodyfikowane Pliki
- `Klient/pack/root/uiauctionhouse.py`
- `Server/client-patches/client-2.0.30/root/uiauctionhouse.py`
