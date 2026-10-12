# Poradnik Administratora VPS: Dystrybucja Ukrycia HP Celu

## Charakterystyka Modyfikacji
Modyfikacja dotyczy wyłącznie warstwy wizualnej klienta gry (`uitarget.py` w paczce `root`).
Nie wymaga żadnych zmian w kodzie C++ serwera ani w bazie MariaDB.

---

## Przygotowanie Dystrybucji na Autopatcher Graczy

1. Na maszynie roboczej (lub na VPS, jeżeli używasz modułu `m2clientpack` w panelu Seban):
   - Zamień plik `pack/root/uitarget.py` na plik z paczki dodatku.
   - Skompiluj paczkę `root` do plików binarnych `root.data` oraz `root.index`.
2. Umieść zaktualizowane pliki `root.data` i `root.index` na serwerze aktualizacji (autopatcherze HTTP / manifest).
3. Gracze po pobraniu aktualizacji natychmiast zobaczą czysty pasek HP bez wartości liczbowych.
