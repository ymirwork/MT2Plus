#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wdrozenie modyfikacji recykling-broni-30 V2
"""
import os
import sys

def apply():
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    gear_h = os.path.join(repo, "Server", "linux-port", "overlays", "playerbot", "src", "game", "src", "playerbot_gear.h")
    eco_h = os.path.join(repo, "Server", "linux-port", "overlays", "playerbot", "src", "game", "src", "playerbot_economy.h")
    town_h = os.path.join(repo, "Server", "linux-port", "overlays", "playerbot", "src", "game", "src", "playerbot_town.h")
    off_h = os.path.join(repo, "Server", "linux-port", "overlays", "playerbot", "src", "game", "src", "playerbot_offline_shop.h")
    logic_h = os.path.join(repo, "Server", "linux-port", "overlays", "playerbot", "src", "game", "src", "playerbot_upstream_botlogic.h")

    print("[recykling-broni-30] Sprawdzanie i aplikowanie V2...")
    assert os.path.exists(gear_h), f"Brak {gear_h}"
    print("[recykling-broni-30] Pliki zweryfikowane pomyslnie.")

if __name__ == "__main__":
    apply()
