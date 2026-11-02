# Wytwarzanie Cor Draconis u NPC Mistrz (Opcja A - 3:1)

Autorska modyfikacja systemu wytwarzania przedmiotA3w (Cube) na serwerze MT2Plus.

## Opis Funkcji
U NPC **Mistrz (VNUM 20082)**, znajduj.cego siT obok Kowala w M1 oraz M3 kadego krA3lestwa, dodano osobn. opcjT dialogow.:
**"Wytwarzanie Cor Draconis"**.

### Czysty Podzia, Okna Craftingu (Category Filter):
DziTki dedykowanemu filtrowi w kliencie (`CubeCategory`):
- WybA3r **"Wytwarzanie pasA3w"** otwiera okno wytwarzania wy,.cznie z pasami.
- WybA3r **"Wytwarzanie Cor Draconis"** otwiera okno wytwarzania wy,.cznie z Corami Draconis.

### Zbalansowane Proporcje (Opcja A - 3 do 1):
- **3x Cor Draconis (Surowy)** (50255) $\rightarrow$ **1x Cor Draconis (szlif.)** (50256)
- **3x Cor Draconis (szlif.)** (50256) $\rightarrow$ **1x Cor Draconis (rzadkie)** (50257)
- **3x Cor Draconis (rzadkie)** (50257) $\rightarrow$ **1x Cor Draconis (antyczne)** (50258)
- **3x Cor Draconis (antyczne)** (50258) $\rightarrow$ **1x Cor Draconis (legend.)** (50259)

* Szansa powodzenia: **100%**
* Koszt: **0 Yang** (wymiana w oparciu o zebrane Cory)

---

## Zmodyfikowane Pliki:
1. `Server/linux-port/docker/game/cube.pasy.txt` - dodanie 4 sekcji receptur dla NPC 20082.
2. `Server/linux-port/docker/game/Dockerfile` - aktualizacja asercji z 9 do 13 receptur u Mistrza.
3. `Server/linux-port/docker/game/quest/pasy.quest` - dodanie opcji dialogowej `Wytwarzanie Cor Draconis` z komend. `cmdchat("CubeCategory cors")`.
4. `Klient/pack/root/game.py` - obs,uga komendy `CubeCategory`, filtrowanie wy>wietlanych receptur w oknie cube.
5. `Klient/pack/root/uicube.py` - bezpieczne czyszczenie s,ownika materia,A3w przy zmianie listy (`ClearCubeResultItem`).
