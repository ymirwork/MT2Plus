# Poradnik Administratora VPS: Dystrybucja Modyfikacji Autołowów

## Informacje o Modyfikacji
Modyfikacja operuje w warstwie logiki klienta (`uiautohunt.py` w paczce `root`).
Wykorzystuje istniejącą już komendę serwerową `/pickup_nearby`, dzięki czemu nie wymaga zmian binarnych w silniku C++.

---

## Dystrybucja Aktualizacji dla Graczy

1. Na maszynie przygotowującej wydanie klienta:
   - Skopiuj `klient_pliki/root/uiautohunt.py` do rozpakowanego folderu `root`.
   - Zbuduj nowe pliki `root.data` i `root.index`.
2. Wgraj pliki na serwer aktualizacji / autopatcher.
3. Gracze po aktualizacji zyskują w pełni sprawne, natychmiastowe zbieranie dropu i bezawaryjne omijanie przeszkód w Autołowach.
