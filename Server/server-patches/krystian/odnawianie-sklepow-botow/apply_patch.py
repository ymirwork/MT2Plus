#!/usr/bin/env python3
"""
Modyfikacja: Odnawianie Sklepów Botów (4 strony / 320 slotów)
Autor: Krystian
Data: 2026-10-24

Opis:
Usuwa błąd logiczny w silniku C++, który uniemożliwiał botom wznawianie wygasłych
sklepów offline (IkarusShop). Po wprowadzeniu 4 stron sklepu dla botów (320 slotów)
w aktualizacji 2.36.0, funkcja wznawiania (RecvShopReopenClientPacket) wciąż
weryfikowała przedmioty za pomocą CanPlaceItemOnShopSlot(), który wymuszał limity
zwykłego gracza (max 160 slotów, kłódki oraz strefę premium).
W rezultacie sklepy botów po 8 godzinach wygasały z błędem slots_ok=0 / SHOP_NO_PREMIUM
i nie mogły się odnowić, co prowadziło do stopniowego wymierania handlu.
"""

import sys
from pathlib import Path

def patch_file(path: Path):
    if not path.is_file():
        print(f"[!] Plik nie istnieje: {path}")
        return False

    content = path.read_text(encoding="utf-8")
    original = content
    filename = path.name

    if filename == "char_shop.cpp":
        # Patch CanPlaceOnShopSlot
        target_on = "bool CHARACTER::CanPlaceOnShopSlot(BYTE slot)\n{\n"
        replacement_on = (
            "bool CHARACTER::CanPlaceOnShopSlot(BYTE slot)\n"
            "{\n"
            "\t// MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1: bot shops are not subject to player lock or premium restrictions\n"
            "\tif (GetDesc() && GetDesc()->IsBot())\n"
            "\t\treturn true;\n"
        )
        if "MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1" not in content:
            if target_on in content:
                content = content.replace(target_on, replacement_on, 1)
            else:
                # Try CRLF
                target_on_crlf = target_on.replace("\n", "\r\n")
                replacement_on_crlf = replacement_on.replace("\n", "\r\n")
                if target_on_crlf in content:
                    content = content.replace(target_on_crlf, replacement_on_crlf, 1)

        # Patch CanPlaceItemOnShopSlot
        target_item = "bool CHARACTER::CanPlaceItemOnShopSlot(BYTE slot, BYTE itemHeight)\n{\n"
        replacement_item = (
            "bool CHARACTER::CanPlaceItemOnShopSlot(BYTE slot, BYTE itemHeight)\n"
            "{\n"
            "\t// MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1: bot shops have up to 4 pages (BOT_SHOP_PAGES) without human limits\n"
            "\tif (GetDesc() && GetDesc()->IsBot())\n"
            "\t\treturn true;\n"
        )
        if "MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1: bot shops have up to 4 pages" not in content:
            if target_item in content:
                content = content.replace(target_item, replacement_item, 1)
            else:
                target_item_crlf = target_item.replace("\n", "\r\n")
                replacement_item_crlf = replacement_item.replace("\n", "\r\n")
                if target_item_crlf in content:
                    content = content.replace(target_item_crlf, replacement_item_crlf, 1)

    elif filename == "ikarus_shop_manager.cpp":
        target = "if (!ch->CanPlaceItemOnShopSlot(itemHandle->GetInfo().pos, itemHandle->GetTable()->bSize))"
        replacement = "// MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1: bot shops are not subject to player lock or premium restrictions\n\t\t\t\tif (!(ch->GetDesc() && ch->GetDesc()->IsBot()) && !ch->CanPlaceItemOnShopSlot(itemHandle->GetInfo().pos, itemHandle->GetTable()->bSize))"
        if target in content and "MT2009_PLUS_FIX_BOT_SHOP_REOPEN_V1" not in content:
            content = content.replace(target, replacement, 1)

    elif filename == "playerbot_offline_shop.h":
        target = "!ch->CanPlaceItemOnShopSlot((BYTE)line->GetInfo().pos, (BYTE)line->GetTable()->bSize)"
        replacement = "!(ch->GetDesc() && ch->GetDesc()->IsBot()) && !ch->CanPlaceItemOnShopSlot((BYTE)line->GetInfo().pos, (BYTE)line->GetTable()->bSize)"
        if target in content and "!(ch->GetDesc() && ch->GetDesc()->IsBot())" not in content:
            content = content.replace(target, replacement, 1)

    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"[OK] Zaktualizowano: {path}")
        return True
    else:
        print(f"[--] Brak zmian lub juz zaaplikowane: {path}")
        return True

def main():
    repo_root = Path(__file__).resolve().parents[4]
    files = [
        repo_root / "Server/linux-port/overlays/playerbot/src/game/src/char_shop.cpp",
        repo_root / "Server/linux-port/docker/game/src/server/game/src/char_shop.cpp",
        repo_root / "Server/linux-port/overlays/playerbot/src/game/src/ikarus_shop_manager.cpp",
        repo_root / "Server/linux-port/docker/game/src/server/game/src/ikarus_shop_manager.cpp",
        repo_root / "Server/linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h",
        repo_root / "Server/linux-port/docker/game/src/server/game/src/playerbot_offline_shop.h",
    ]

    success = True
    for f in files:
        if not patch_file(f):
            success = False

    if success:
        print("\n[SUKCES] Wszystkie pliki silnika gry zostaly pomyslnie zaktualizowane.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
