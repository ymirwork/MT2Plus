# Modyfikacja: Duże i czytelne czcionki Skilli oraz Ilości Przedmiotów (HD Slot Numbers)

## Opis działania
Modyfikacja powiększa miniaturowe (domyślnie 5x7 px) cyfry i litery wyświetlane na ikonach przedmiotów oraz umiejętności:
- **Ilość przedmiotów w stacku:** czytelne, powiększone cyfry (np. `200`, `50`) w prawym dolnym rogu slotu w ekwipunku, magazynie i na pasku szybkiego dostępu.
- **Poziom umiejętności:** powiększone cyfry (`1` do `20`) oraz stopnie umiejętności: `M1`–`M10`, `G1`–`G10`, `P` w oknie postaci (`V`), w drzewku umiejętności i na pasku skrótów.

## Cechy techniczne
- Nowa rozdzielczość glifów: wysokość **12 px** (zamiast 7 px – wzrost o ponad 71% w pionie i ponad 2-krotny wzrost powierzchni).
- Glify pogrubione (**Bold**) z precyzyjnym 1-pikselowym czarnym obrysem (outline), gwarantującym 100% czytelności na każdym tle (jasne perły, ciemne zbroje, kolorowe mikstury).
- Składowane w atlasie `d:/ymir work/ui/TaskBar.tga` oraz zmapowane w `.sub` w `d:/ymir work/ui/game/taskbar/`.
- Pełna zgodność z silnikiem gry bez modyfikacji binarnej `metin2client.exe`.

## Instalacja
Uruchom skrypt `INSTALUJ_AUTOMATYCZNIE.bat` lub spakuj paczkę `etc` poleceniem:
```powershell
powershell -ExecutionPolicy Bypass -File Klient\Compile-ClientPack.ps1 etc pack
```
