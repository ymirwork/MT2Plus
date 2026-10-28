# Brak Czerwonych i Niebieskich Mikstur z Metinów i Bossów od M2 w górę

Autorska modyfikacja usuwająca uciążliwy drop Czerwonych i Niebieskich Mikstur (PŻ i PE) z Kamieni Metin oraz Bossów, począwszy od map drugich miast (M2) aż po mapy końcowe (Arezzo, Ochao, Zaklęty Las / Yohara).

---

## 🎯 Cel Modyfikacji
1. **Quality of Life (QoL):** Kamienie Metin i Bossy przestają bezużytecznie zaśmiecać ekwipunek dziesiątkami i setkami zwykłych mikstur po każdym zniszczeniu/zabiciu.
2. **Czystość i Przejrzystość Dropu:** Po rozbiciu Metina lub pokonaniu Bossa od razu widać wartościowe przedmioty (Księgi Umiejętności, Kamienie Duszy, ulepszacze, eq, szkatułki, rzadkie dropy).
3. **Zachowanie Mikstur w M1:** Dla najmłodszych postaci (lvl 1–15 w pierwszych wioskach) drop mikstur z Metinów Cierpienia, Walki, Bitwy i Chciwości (8001–8004) oraz bossów M1 (Lykos, Scrofa, Bera, Tigris) pozostał nienaruszony.
4. **Ochrona Zielonych i Fioletowych Mikstur:** Wszystkie Mikstury Szybkości Ataku (Zielone: 27100–27102, 27110–27112) oraz Mikstury Szybkości Ruchu (Fioletowe: 27103–27105, 27113–27115) zostały bezwzględnie zachowane w dropie.
5. **Ekonomia i Playerboty:** Ceny u Handlarki Różności są w pełni przystępne (np. 200 sztuk Czerwonych (D) kosztuje 32 000 Yang). Boty AI posiadają własną rutynę zaopatrzenia w mieście i nie polegają na dropie potek z ziemi, co gwarantuje pełną stabilność rozgrywki.

---

## 📂 Zmodyfikowane Pliki
- `Server/linux-port/docker/game/src/serverfiles/share/locale/poland/mob_drop_item.txt` (główna tabela dropu bossów i metinów: wyczyszczono 76 grup dropu, usunięto 302 linie mikstur z poprawnym przenumerowaniem indeksów `1..N`)
- `Server/linux-port/docker/game/mob_drop_item.dropedit.append.txt` (grupa Metina Ciemności w Bibliotece Wiedzy: usunięto mikstury, przenumerowano)
- `Server/linux-port/docker/game/ochao/mob_drop_item.ochao.txt` (Strażnik Ochao 6390: usunięto mikstury, przenumerowano)
- `Server/linux-port/docker/game/arezzo/mob_drop_item.arezzo.txt` (Bossowie Arges 9606 i Polifem 9607: usunięto mikstury, przenumerowano)
- `Server/linux-port/docker/game/arezzo/mob_drop_item.arezzo2.txt` (Bossowie Bastet 9675 i Anubis 9681: usunięto mikstury, przenumerowano)
- `Server/linux-port/docker/game/yohara_zaklety/mob_drop_item.yohara_zaklety.txt` (Władca En-Tai 6407, Jotun Thrym 6192, Metin Lasu 8061: usunięto mikstury czerwone/niebieskie przy zachowaniu mikstur zielonych i fioletowych)

---

## ⚙️ Skrypt Wdrożeniowy (Ponowne Wdrożenie po Merge)
W przypadku aktualizacji serwera z oficjalnego repozytorium (`[AKTUALIZUJ]` / `[UPSTREAM]`), modyfikację można ponownie zaaplikować jednym poleceniem:
```bash
python Server/server-patches/krystian/brak-potek-m2-metiny-bossy/apply_patch.py
```
