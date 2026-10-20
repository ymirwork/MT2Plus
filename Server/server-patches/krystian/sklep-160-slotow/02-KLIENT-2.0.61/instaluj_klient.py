#!/usr/bin/env python3
"""Narrow root-pack patch for MT2009 Plus 2.0.61. Preserves unrelated entries."""
import argparse
import hashlib
from pathlib import Path
import shutil
import sys
import time
import zlib

from m2clientpack import eterpack

MARKER = 'PLAYER_SHOP_TWO_BLOCKS_KEYS2_V1'
NAMES = ('offlineshopui.py', 'offlineshopbuilder.py', 'offlineshopmanage.py')


def once(value, old, new, label):
    count = value.count(old)
    if count != 1:
        raise ValueError('%s: znaleziono %d pasujacych miejsc, oczekiwano 1' % (label, count))
    return value.replace(old, new, 1)


def method(value, start, end, body, label):
    if value.count(start) != 1:
        raise ValueError('Nieznana struktura: ' + label)
    a = value.index(start)
    b = value.find(end, a + len(start))
    if b < 0:
        raise ValueError('Nieznana struktura: ' + label)
    return value[:a] + body + value[b:]


def transform(name, raw):
    if MARKER.encode('ascii') in raw:
        return raw
    crlf = b'\r\n' in raw
    value = raw.decode('latin-1').replace('\r\n', '\n')
    if name == 'offlineshopui.py':
        value = once(value, 'import ui\n', 'import ui\nimport dualshop # '+MARKER+'\n', 'UI import')
        value = method(value, 'def IsInLockedArea(', 'def HasShopPremium(', '''def IsInLockedArea(slotIndex, unlockProgress=0):
\treturn dualshop.Locked(slotIndex, unlockProgress)

def IsInPremiumArea(slotIndex):
\treturn dualshop.Premium(slotIndex)

def CanPlaceItemOnShopSlot(slotIndex, itemHeight, unlockProgress, isPremium):
\tif not dualshop.Fits(slotIndex, itemHeight):
\t\treturn False
\tfor i in range(itemHeight):
\t\tslot = slotIndex + i * shop.SHOP_PLAYER_WIDTH
\t\tif IsInLockedArea(slot, unlockProgress) or (not isPremium and IsInPremiumArea(slot)):
\t\t\treturn False
\treturn True

''', 'UI area rules')
        value = once(value, '\t\tslotWnd = ui.GridSlotWindow()\n', '\t\tslotWnd = dualshop.DualGrid() if getattr(self, "_dualShop", False) else ui.GridSlotWindow()\n', 'UI grid')
        value = once(value, '\t\tslotWnd.ArrangeSlot(0, shop.SHOP_PLAYER_WIDTH, shop.SHOP_PLAYER_HEIGHT, 32, 32, 0, 0)\n', '\t\tif not getattr(self, "_dualShop", False):\n\t\t\tslotWnd.ArrangeSlot(0, shop.SHOP_PLAYER_WIDTH, shop.SHOP_PLAYER_HEIGHT, 32, 32, 0, 0)\n', 'UI grid arrange')
        value = method(value, '\tdef __CreateSlotCurtain(self):', '\tdef OnSlotCurtainMouseOverIn(self, index):', '''\tdef __CreateSlotCurtain(self):
\t\tself.slotCurtainItems = []
\t\tcount = shop.SHOP_PLAYER_HEIGHT + (16 if getattr(self, "_dualShop", False) else 0)
\t\tfor i in range(count):
\t\t\tcurtain = ui.ImageBox()
\t\t\tcurtain.SetParent(self.itemSlot)
\t\t\tpremium = i < shop.SHOP_PLAYER_HEIGHT and i >= shop.SHOP_PLAYER_PREMIUM_Y_START
\t\t\tcurtain.LoadImage(flamewindPath.GetPublic("shop_unlock_slot_premium" if premium else "shop_unlock_slot"))
\t\t\tif i < shop.SHOP_PLAYER_HEIGHT:
\t\t\t\tcurtain.SetPosition(5*32, 32*i)
\t\t\telse:
\t\t\t\tgroup = i - shop.SHOP_PLAYER_HEIGHT
\t\t\t\tcurtain.SetPosition((shop.SHOP_PLAYER_WIDTH + (group % 2)*5)*32, (group//2)*32)
\t\t\tcurtain.SAFE_SetStringEvent("MOUSE_OVER_IN", self.OnSlotCurtainMouseOverIn, i)
\t\t\tcurtain.SAFE_SetStringEvent("MOUSE_OVER_OUT", self.OnSlotCurtainMouseOverOut)
\t\t\tcurtain.Show()
\t\t\tself.slotCurtainItems.append(curtain)

\tdef UpdateSlotCurtain(self, unlockedNum, isPremium):
\t\tfor i, curtain in enumerate(self.slotCurtainItems):
\t\t\tif i >= shop.SHOP_PLAYER_HEIGHT:
\t\t\t\topened = i - shop.SHOP_PLAYER_HEIGHT < max(0, unlockedNum - dualshop.OLD_KEYS)
\t\t\telif i < shop.SHOP_PLAYER_PREMIUM_Y_START:
\t\t\t\topened = i < unlockedNum
\t\t\telse:
\t\t\t\topened = bool(isPremium)
\t\t\tif opened:
\t\t\t\tcurtain.Hide()
\t\t\telse:
\t\t\t\tcurtain.Show()

''', 'UI curtains')
        value = once(value, '\t\tShopSlotRenderer.__init__(self, slotWindow, bindInternalEvents, itemSlotParent)\n', '\t\tself._dualShop = True\n\t\tShopSlotRenderer.__init__(self, slotWindow, bindInternalEvents, itemSlotParent)\n', 'UI player shop')
        value = once(value, 'self.toolTipText.SetText(uiScriptLocale.SHOP_LOCKED_SLOT if index < shop.SHOP_PLAYER_PREMIUM_Y_START else uiScriptLocale.SHOP_PREMIUM_SLOT)', 'self.toolTipText.SetText("5 pol: 2 Drewniane Klucze" if index >= shop.SHOP_PLAYER_HEIGHT else (uiScriptLocale.SHOP_LOCKED_SLOT if index < shop.SHOP_PLAYER_PREMIUM_Y_START else uiScriptLocale.SHOP_PREMIUM_SLOT))', 'UI tooltip')
    elif name == 'offlineshopbuilder.py':
        value = once(value, 'import offlineshopui\n', 'import offlineshopui\nimport dualshop # '+MARKER+'\n', 'builder import')
        value = once(value, '\t\t\tself.itemSlot = self.shopSlotRenderer.itemSlot\n', '\t\t\tself.itemSlot = self.shopSlotRenderer.itemSlot\n\t\t\tdualshop.WidenBuilder(self)\n', 'builder width')
        value = once(value, 'for i in xrange(shop.SHOP_SLOT_COUNT):', 'for i in xrange(dualshop.PAGE * 2):', 'builder slots')
        value = once(value, '\tdef CanPlaceOnShopSlot(self, destSlotPos, itemHeight):\n', '\tdef CanPlaceOnShopSlot(self, destSlotPos, itemHeight):\n\t\tif self.selectedTimeOption == 0 and destSlotPos >= dualshop.PAGE:\n\t\t\treturn False\n', 'builder regular shop')
        value = once(value, '\tdef OnOk(self):\n', '\tdef OnOk(self):\n\t\tif len(self.itemStock) > shop.SHOP_PLAYER_WIDTH * shop.SHOP_PLAYER_HEIGHT:\n\t\t\tchat.AppendChat(chat.CHAT_TYPE_INFO, "Przy tworzeniu sklepu maksymalnie 80 przedmiotow. Reszte dodaj po otwarciu.")\n\t\t\treturn\n', 'builder creation limit')
    elif name == 'offlineshopmanage.py':
        value = once(value, '\tWINDOW_WIDTH = 344\n', '\tWINDOW_WIDTH = 664 # '+MARKER+'\n', 'manage width')
        value = once(value, 'for y in range(shop.SHOP_PLAYER_HEIGHT):', 'for y in range(shop.SHOP_PLAYER_HEIGHT * 2):', 'manage clear slots')
    else:
        raise ValueError(name)
    return (value.replace('\n', '\r\n') if crlf else value).encode('latin-1')


def patch_pack(index, data, module):
    version, entries = eterpack.read_index_bytes(index)
    by_name = {entry.name: entry for entry in entries}
    missing = [name for name in NAMES if name not in by_name]
    if missing:
        raise ValueError('Brak modulow sklepu: ' + ', '.join(missing))
    if 'dualshop.py' in by_name:
        existing = eterpack.read_entry(data, by_name['dualshop.py'])
        if existing != module:
            raise ValueError('Istnieje inny dualshop.py; wymagana analiza reczna.')
    changes = {name: transform(name, eterpack.read_entry(data, by_name[name])) for name in NAMES}
    changes['dualshop.py'] = module
    out = bytearray()
    for entry in entries:
        if entry.name in changes:
            blob = eterpack.encode_entry(changes[entry.name], entry.ctype)
            size = (len(blob) + 255) // 256 * 256
            entry.size, entry.real, entry.dcrc = len(blob), size, zlib.crc32(blob) & 0xffffffff
            slot = blob + b'\0' * (size - len(blob))
        else:
            slot = data[entry.pos:entry.pos + entry.real]
            if len(slot) != entry.real:
                raise ValueError('Uszkodzony wpis: ' + entry.name)
        entry.pos = len(out)
        out.extend(slot)
    if 'dualshop.py' not in by_name:
        blob = eterpack.encode_entry(module, 2)
        size = (len(blob) + 255) // 256 * 256
        entry = eterpack.Entry(bytes(eterpack.ENTRY))
        entry.id = max(e.id for e in entries) + 1
        entry.name = 'dualshop.py'
        entry.fcrc = eterpack.name_crc(entry.name)
        entry.real, entry.size, entry.dcrc, entry.pos, entry.ctype = size, len(blob), zlib.crc32(blob) & 0xffffffff, len(out), 2
        entries.append(entry)
        out.extend(blob + b'\0' * (size - len(blob)))
    new_index, new_data = eterpack.write_index_bytes(version, entries), bytes(out)
    _, verified = eterpack.read_index_bytes(new_index)
    for entry in verified:
        if entry.name in changes and eterpack.read_entry(new_data, entry) != changes[entry.name]:
            raise ValueError('Blad odczytu po zapisie: ' + entry.name)
    return new_index, new_data, changes


def main():
    ap = argparse.ArgumentParser(description='MT2009 Plus: klient sklepu 160 pol')
    ap.add_argument('--client', required=True, type=Path, help='folder klienta z CLIENT_VERSION i pack')
    action = ap.add_mutually_exclusive_group(required=True)
    action.add_argument('--check', action='store_true')
    action.add_argument('--install', action='store_true')
    args = ap.parse_args()
    client = args.client.resolve()
    version = (client / 'CLIENT_VERSION').read_text(encoding='ascii').strip()
    if version != '2.0.61':
        raise SystemExit('Wymagany klient 2.0.61; znaleziono ' + version)
    index_path, data_path = client / 'pack/root.index', client / 'pack/root.data'
    index, data = index_path.read_bytes(), data_path.read_bytes()
    module = (Path(__file__).resolve().parent / 'dualshop.py').read_bytes()
    new_index, new_data, changes = patch_pack(index, data, module)
    print('KONTROLA OK. Wpisy po instalacji:', len(eterpack.read_index_bytes(new_index)[1]))
    print('Zmiany:', ', '.join(changes))
    if args.check or (new_index == index and new_data == data):
        if args.install:
            print('JUZ ZAINSTALOWANE')
        return
    # Do not replace pack files while the process can hold them open.
    if sys.platform == 'win32':
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq metin2client.exe', '/NH'], capture_output=True, text=True)
        if 'metin2client.exe' in result.stdout.lower():
            raise SystemExit('Zamknij gre i patcher przed instalacja.')
    backup = client / ('backup-sklep-160-' + time.strftime('%Y%m%d-%H%M%S'))
    backup.mkdir()
    shutil.copy2(index_path, backup / 'root.index')
    shutil.copy2(data_path, backup / 'root.data')
    try:
        for target, content in ((data_path, new_data), (index_path, new_index)):
            temporary = target.with_name(target.name + '.shop160-new')
            temporary.write_bytes(content)
            temporary.replace(target)
        if hashlib.sha256(index_path.read_bytes()).digest() != hashlib.sha256(new_index).digest() or hashlib.sha256(data_path.read_bytes()).digest() != hashlib.sha256(new_data).digest():
            raise IOError('Blad weryfikacji plikow klienta')
    except Exception:
        shutil.copy2(backup / 'root.index', index_path)
        shutil.copy2(backup / 'root.data', data_path)
        raise
    print('ZAINSTALOWANO. Kopia:', backup)


if __name__ == '__main__':
    main()
