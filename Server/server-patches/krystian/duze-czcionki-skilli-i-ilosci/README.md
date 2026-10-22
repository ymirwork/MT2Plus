# Modyfikacja: Duże i czytelne czcionki Skilli oraz Ilości Przedmiotów (HD Slot Numbers)

## Opis działania
Modyfikacja powiększa miniaturowe (domyślnie 5x7 px) cyfry i litery wyświetlane na ikonach przedmiotów oraz umiejętności:
- **Ilość przedmiotów w stacku:** duże, masywne, pogrubione cyfry (np. `200`, `50`) w prawym dolnym rogu slotu w ekwipunku, magazynie i na pasku szybkiego dostępu.
- **Poziom umiejętności:** duże, pogrubione cyfry (`1` do `20`) oraz stopnie umiejętności: `M1`–`M10`, `G1`–`G10`, `P` w oknie postaci (`V`), w drzewku umiejętności i na pasku skrótów.

## Cechy techniczne
- Nowa rozdzielczość glifów: pełna wysokość **12 px** (wzrost o ponad 71% w pionie i ponad 2-krotny wzrost powierzchni).
- Glify pogrubione (**Bold**) z precyzyjnym 1-pikselowym czarnym obrysem (outline), gwarantującym 100% czytelności na każdym tle.
- Pełna masywność: oryginalne, grube trzonki 2 px z pełnymi daszkami.
- Precyzyjne spasowanie slotów w silniku (`PATCH_METIN2CLIENT.py`):
  - Przesunięcie o **3 px do góry** w pionie (z -10 na -13), co sprawia, że duża czcionka 12 px w 100% mieści się wewnątrz slotu i nie wychodzi poza dolną krawędź.
  - Przesunięcie o **2 px w prawo** w poziomie (z -4 na -2), co zapewnia idealne wyrównanie do prawej krawędzi slotu.
- Składowane w atlasie `d:/ymir work/ui/TaskBar.tga` oraz zmapowane w `.sub` w `d:/ymir work/ui/game/taskbar/`.

## Instalacja
Uruchom skrypt `INSTALUJ_AUTOMATYCZNIE.bat` lub:
1. Spakuj paczkę `etc`:
```powershell
powershell -ExecutionPolicy Bypass -File Klient\Compile-ClientPack.ps1 etc pack
```
2. Zastosuj patch pozycji w `metin2client.exe`:
```cmd
python Server\server-patches\krystian\duze-czcionki-skilli-i-ilosci\PATCH_METIN2CLIENT.py
```
