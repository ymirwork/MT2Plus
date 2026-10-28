#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_guild_window_payout.py
Dodaje pole podgladu 'Do wyplaty' w oknie informacji o gildii
oraz obsluge polecenia serwera 'GuildPayout <amount>' do synchronizacji
wyswietlania z biezacym stanem utargu gildyjnego.
Autor: Krystian (MT2Plus)
"""

import os
import sys

def patch_file(file_path, old_text, new_text, description):
    if not os.path.isfile(file_path):
        print(f"[!] Nie znaleziono pliku: {file_path}")
        return False

    with open(file_path, "rb") as f:
        raw_bytes = f.read()

    is_crlf = b"\r\n" in raw_bytes
    content = raw_bytes.decode("latin1")

    content_normalized = content.replace("\r\n", "\n")
    old_normalized = old_text.replace("\r\n", "\n")
    new_normalized = new_text.replace("\r\n", "\n")

    if new_normalized in content_normalized:
        print(f"[OK] {description} - juz zaaplikowane.")
        return True

    if old_normalized in content_normalized:
        content_normalized = content_normalized.replace(old_normalized, new_normalized, 1)
        if is_crlf:
            result_bytes = content_normalized.replace("\n", "\r\n").encode("latin1")
        else:
            result_bytes = content_normalized.encode("latin1")

        with open(file_path, "wb") as f:
            f.write(result_bytes)
        print(f"[+] Zastosowano: {description}")
        return True

    print(f"[!] Nie znaleziono oryginalnego fragmentu dla: {description}")
    return False

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    ui_script_file = os.path.join(root_dir, "Klient", "pack", "root", "uiscript", "guildwindow_guildinfopage.py")
    ui_guild_file = os.path.join(root_dir, "Klient", "pack", "root", "uiguild.py")
    interface_file = os.path.join(root_dir, "Klient", "pack", "root", "interfacemodule.py")
    game_file = os.path.join(root_dir, "Klient", "pack", "root", "game.py")

    # 1. guildwindow_guildinfopage.py: Dodanie GuildPayout w luce na y=217, przesuniecie Yang na y=237
    old_uiscript = """\t\t\t\t## GuildMoney
\t\t\t\t{
\t\t\t\t\t"name" : "GuildMoney", "type" : "text", "x" : 3, "y" : 233, "text" : uiScriptLocale.GUILD_MONEY,
\t\t\t\t\t"children" :
\t\t\t\t\t(
\t\t\t\t\t\t{
\t\t\t\t\t\t\t"name" : "GuildMoneySlot",
\t\t\t\t\t\t\t"type" : "image",
\t\t\t\t\t\t\t"x" : 70,
\t\t\t\t\t\t\t"y" : -2,
\t\t\t\t\t\t\t"image" : LARGE_VALUE_FILE,
\t\t\t\t\t\t\t"children" :
\t\t\t\t\t\t\t(
\t\t\t\t\t\t\t\t{"name" : "GuildMoneyValue", "type":"text", "text":"9999999", "x":0, "y":0, "all_align":"center"},
\t\t\t\t\t\t\t),
\t\t\t\t\t\t},
\t\t\t\t\t),
\t\t\t\t},"""

    new_uiscript = """\t\t\t\t## GuildPayout (MT2009_PLUS_CRAFTER_REVENUE_V1: podglad do wyplaty)
\t\t\t\t{
\t\t\t\t\t"name" : "GuildPayout", "type" : "text", "x" : 3, "y" : 217, "text" : "Do wyp\\xb3aty",
\t\t\t\t\t"children" :
\t\t\t\t\t(
\t\t\t\t\t\t{
\t\t\t\t\t\t\t"name" : "GuildPayoutSlot",
\t\t\t\t\t\t\t"type" : "image",
\t\t\t\t\t\t\t"x" : 70,
\t\t\t\t\t\t\t"y" : -2,
\t\t\t\t\t\t\t"image" : LARGE_VALUE_FILE,
\t\t\t\t\t\t\t"children" :
\t\t\t\t\t\t\t(
\t\t\t\t\t\t\t\t{"name" : "GuildPayoutValue", "type":"text", "text":"0", "x":0, "y":0, "all_align":"center"},
\t\t\t\t\t\t\t),
\t\t\t\t\t\t},
\t\t\t\t\t),
\t\t\t\t},

\t\t\t\t## GuildMoney
\t\t\t\t{
\t\t\t\t\t"name" : "GuildMoney", "type" : "text", "x" : 3, "y" : 237, "text" : uiScriptLocale.GUILD_MONEY,
\t\t\t\t\t"children" :
\t\t\t\t\t(
\t\t\t\t\t\t{
\t\t\t\t\t\t\t"name" : "GuildMoneySlot",
\t\t\t\t\t\t\t"type" : "image",
\t\t\t\t\t\t\t"x" : 70,
\t\t\t\t\t\t\t"y" : -2,
\t\t\t\t\t\t\t"image" : LARGE_VALUE_FILE,
\t\t\t\t\t\t\t"children" :
\t\t\t\t\t\t\t(
\t\t\t\t\t\t\t\t{"name" : "GuildMoneyValue", "type":"text", "text":"9999999", "x":0, "y":0, "all_align":"center"},
\t\t\t\t\t\t\t),
\t\t\t\t\t\t},
\t\t\t\t\t),
\t\t\t\t},"""

    patch_file(ui_script_file, old_uiscript, new_uiscript, "guildwindow_guildinfopage.py: Dodanie GuildPayout")

    # 2. uiguild.py: Inicjalizacja page.guildPayoutSlot
    old_child_get = """\t\t\ttry:
\t\t\t\tpage.guildMoneySlot = page.GetChild("GuildMoneyValue")
\t\t\texcept KeyError:
\t\t\t\tpage.guildMoneySlot = None"""

    new_child_get = """\t\t\ttry:
\t\t\t\tpage.guildMoneySlot = page.GetChild("GuildMoneyValue")
\t\t\texcept KeyError:
\t\t\t\tpage.guildMoneySlot = None

\t\t\ttry:
\t\t\t\tpage.guildPayoutSlot = page.GetChild("GuildPayoutValue")
\t\t\texcept KeyError:
\t\t\t\tpage.guildPayoutSlot = None"""

    patch_file(ui_guild_file, old_child_get, new_child_get, "uiguild.py: Inicjalizacja page.guildPayoutSlot")

    # 3. uiguild.py: SetGuildPayout metoda
    old_open = """\tdef Open(self):
\t\tself.Show()
\t\tself.SetTop()"""

    new_open = """\tdef SetGuildPayout(self, amount):
\t\ttry:
\t\t\tself.payoutAmount = int(amount)
\t\texcept:
\t\t\tself.payoutAmount = 0
\t\tif self.IsShow() and getattr(self, "isLoaded", 0) and hasattr(self, "pageWindow") and "GUILD_INFO" in self.pageWindow:
\t\t\tpage = self.pageWindow["GUILD_INFO"]
\t\t\tif getattr(page, "guildPayoutSlot", None):
\t\t\t\tpage.guildPayoutSlot.SetText(str(self.payoutAmount))

\tdef Open(self):
\t\tself.Show()
\t\tself.SetTop()"""

    patch_file(ui_guild_file, old_open, new_open, "uiguild.py: Metoda SetGuildPayout")

    # 4. uiguild.py: odswiezanie slotu "Do wyplaty" ze zmiennej self.payoutAmount (start od 0)
    old_refresh_calc = """\t\tif getattr(page, "guildPayoutSlot", None):
\t\t\tcurMoney = guild.GetGuildMoney()
\t\t\ttry:
\t\t\t\tpayout = long(curMoney) * 85 / 100
\t\t\texcept:
\t\t\t\tpayout = int(curMoney * 0.85)
\t\t\tpage.guildPayoutSlot.SetText(str(payout))"""

    new_refresh_calc = """\t\tif getattr(page, "guildPayoutSlot", None):
\t\t\tpage.guildPayoutSlot.SetText(str(getattr(self, "payoutAmount", 0)))"""

    patch_file(ui_guild_file, old_refresh_calc, new_refresh_calc, "uiguild.py: RefreshGuildInfoPage - uzycie payoutAmount (domyslnie 0)")

    # 5. interfacemodule.py: dodanie metody SetGuildPayout
    old_toggle_guild = """\tdef ToggleGuildWindow(self):"""
    new_toggle_guild = """\tdef SetGuildPayout(self, amount):
\t\tif hasattr(self, "wndGuild") and self.wndGuild:
\t\t\tself.wndGuild.SetGuildPayout(amount)

\tdef ToggleGuildWindow(self):"""

    patch_file(interface_file, old_toggle_guild, new_toggle_guild, "interfacemodule.py: Metoda SetGuildPayout")

    # 6. game.py: dodanie obslugi polecenia "GuildPayout"
    old_cmd = """\t\tserverCommandList={"""
    new_cmd = """\t\tserverCommandList={
\t\t\t"GuildPayout": self.__GuildPayout,"""

    patch_file(game_file, old_cmd, new_cmd, "game.py: serverCommandList['GuildPayout']")

    old_pickup_sound = """\tdef __OnPickupSound(self, vnum="0", *rest):"""
    new_pickup_sound = """\tdef __GuildPayout(self, amount="0", *args):
\t\tif hasattr(self, "interface") and self.interface:
\t\t\tself.interface.SetGuildPayout(amount)

\tdef __OnPickupSound(self, vnum="0", *rest):"""

    patch_file(game_file, old_pickup_sound, new_pickup_sound, "game.py: Handler __GuildPayout")

if __name__ == "__main__":
    main()
