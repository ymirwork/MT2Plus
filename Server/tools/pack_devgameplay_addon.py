import os
import zipfile

addon_name = 'MT2009-PLUS-DEV-GAMEPLAY-V1'
out_dir = os.path.join('Server', 'server-patches', 'krystian', 'devgameplay')
os.makedirs(out_dir, exist_ok=True)
zip_path = os.path.join(out_dir, f'{addon_name}.zip')

files_to_pack = [
    ('Server/server-patches/devgameplay/edits.json', 'server-patch/edits.json'),
    ('Server/server-patches/devgameplay/apply_devgameplay.py', 'server-patch/apply_devgameplay.py'),
    ('Server/server-patches/devgameplay/Apply-DevGameplayPatch.ps1', 'server-patch/Apply-DevGameplayPatch.ps1'),
    ('Server/server-patches/devgameplay/README.md', 'server-patch/README.md'),
    ('Server/linux-port/docker/game/quest/tp_bookmarks.quest', 'quest/tp_bookmarks.quest'),
    ('Server/client-patches/client-2.0.30/root/uicommon.py', 'client/root/uicommon.py'),
    ('Server/client-patches/client-2.0.30/root/uiexchange.py', 'client/root/uiexchange.py'),
    ('Server/client-patches/client-2.0.30/root/uipickmoney.py', 'client/root/uipickmoney.py'),
    ('Server/client-patches/client-2.0.30/root/uiscript/pickmoneydialog.py', 'client/root/uiscript/pickmoneydialog.py'),
    ('Server/client-patches/client-2.0.30/root/uiscript/pickmoneydialog_cheque.py', 'client/root/uiscript/pickmoneydialog_cheque.py'),
]

readme_content = """# Addon: MT2009-PLUS-DEV-GAMEPLAY-V1
Pakiet 6 modyfikacji deweloperskich serwera i klienta:
1. Czytanie KU bez wymaganego EXPa (char_skill.cpp)
2. Zdjecie limiterow Movement Speed, Attack Speed, Damage, usuniecie SpeedHack check/disconnect (char.cpp, battle.cpp, input_main.cpp, char_battle.cpp)
3. Natychmiastowe ulepszanie u kowala bez 1-sekundowego opoznienia 'Odczekaj przed nastepnym ulepszaniem' (input_main.cpp)
4. Zapis lochow w Zwoju Powrotu (V1/V2/V3/Malpy/Grota) ze sprawdzaniem przepustek i VIPa oraz naprawa czystego zwoju (tp_bookmarks.quest, char_item.cpp)
5. Wprowadzanie Yang k/kk/kkk w oknach dialogowych (uipickmoney.py, uicommon.py, uiexchange.py, pickmoneydialog.py, pickmoneydialog_cheque.py)
6. Bonus PvP +5% obrazen za znajomosc jezyka obcego krolestwa na poziomie M+ (char_battle.cpp)
"""

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for src, dst in files_to_pack:
        if os.path.exists(src):
            zf.write(src, dst)
            print(f'Packed: {src} -> {dst}')
        else:
            print(f'WARNING: Missing {src}')
    zf.writestr('README.md', readme_content)

print(f'Created {zip_path} successfully. Size: {os.path.getsize(zip_path)} bytes')
