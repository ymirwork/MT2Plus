"""
Patchuje binarkę metin2client.exe w folderze Klient, aby:
1. Przesunąć pozycję pionową cyfr w slotach o 3 px DO GÓRY (z -10 na -13).
   Dzięki temu pełna, duża czcionka 12 px (HD) mieści się idealnie wewnątrz slotu i nie wychodzi poza dolną ramkę.
2. Przesunąć pozycję poziomą cyfr o 2 px W PRAWO (z -4 na -2).
   Dzięki temu cyfry są idealnie wyrównane do prawej krawędzi slotu.
"""

import os
import shutil

def patch_exe():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
    exe_path = os.path.join(root_dir, 'Klient', 'metin2client.exe')
    if not os.path.exists(exe_path):
        exe_path = os.path.join(os.getcwd(), 'Klient', 'metin2client.exe')
    bak_path = os.path.join(root_dir, 'Klient', 'metin2client.exe.bak')

    if not os.path.exists(exe_path):
        print(f"Nie znaleziono pliku: {exe_path}")
        return False

    with open(exe_path, 'r+b') as f:
        pattern = bytes.fromhex('0fb64f418b4734c1e10583c1f603c10fb64f40508b4730c1e10583c1fc03c18bca50e8')
        already_patched = bytes.fromhex('0fb64f418b4734c1e10583c1f303c10fb64f40508b4730c1e10583c1fe03c18bca50e8')
        
        data = f.read()
        if already_patched in data:
            print("Plik metin2client.exe jest już pomyślnie spatchowany!")
            return True
            
        idx = data.find(pattern)
        if idx == -1:
            print("Nie znaleziono wzorca w metin2client.exe!")
            return False

        if not os.path.exists(bak_path):
            shutil.copy2(exe_path, bak_path)
            print(f"Utworzono kopię zapasową: {bak_path}")

        # Y offset: idx + 12 (0xF6 -> 0xF3: -10 -> -13, 3 px do góry)
        # X offset: idx + 28 (0xFC -> 0xFE: -4 -> -2, 2 px w prawo)
        f.seek(idx + 12)
        f.write(bytes([0xF3]))
        
        f.seek(idx + 28)
        f.write(bytes([0xFE]))

    print(f"Pomyślnie spatchowano pozycję slotów w: {exe_path} (offset 0x{idx:08X})")
    print("  - Przesunięcie w pionie: 3 px DO GÓRY (brak wychodzenia poza slot)")
    print("  - Przesunięcie w poziomie: 2 px W PRAWO (wyrównanie do prawej krawędzi)")
    return True

if __name__ == '__main__':
    patch_exe()
