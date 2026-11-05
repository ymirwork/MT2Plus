# Balans Sekcji Za Smocze Znaki (SZ / Dragon Mark)

**Autor:** Krystian  
**Data:** 2026-11-05  
**Wersja:** 1.0.0 (dla MT2Plus v2.40.0+)  
**Status:** Aktywny  

---

## 1. Cel Modyfikacji

1. **Reaktywacja programu lojalnościowego Smoczych Znaków (SZ):**
   - Rozszerzenie oferty ze starych 11 pozycji do **30 zbalansowanych, przydatnych pozycji** (od 15 SZ do 120 SZ).
   - Likwidacja absurdalnych cen (np. Rada Pustelnika: z 599 SZ za 1 szt. na 50 SZ za 2 szt.; Magiczny Metal: z 599 SZ na 120 SZ; mikstury Boga Smoków z 249 SZ na 30 SZ).
   - Dodanie do oferty lojalnościowej: Peleryn Męstwa (x50 / x200), Fasolek Zen (x5), Zwojów Egzo (x5), Cor Draconis (x5), Zielonych Fasoli (x3), Pereł (Biała, Niebieska, Krwawa), Pierścieni Exp oraz Rękawic Złodzieja.
2. **Pozostałe kategorie sklepu (SM):**
   - Pozostawione w 100% w oryginalnym stanie sprzed zmian (1486 pozycji).
3. **Zabezpieczenie silnika gry:**
   - W `CItemShopManager::CanSendItem` dodano bezpiecznik `if (!pkItemTable) return false;` eliminujący jakiekolwiek crashe przy otwieraniu sklepu.
