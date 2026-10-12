#!/usr/bin/env bash
set -e

echo "==============================================================================="
echo "   INSTALATOR LINUX VPS: SZYBKIE ZBIERANIE W AUTOLOWACH + FIX (KLIENT)"
echo "==============================================================================="

CLIENT_DIR="${1:-}"

if [ -z "$CLIENT_DIR" ]; then
    if [ -d "../../Klient" ]; then
        CLIENT_DIR="../../Klient"
    elif [ -d "../Klient" ]; then
        CLIENT_DIR="../Klient"
    elif [ -d "Klient" ]; then
        CLIENT_DIR="Klient"
    fi
fi

if [ -z "$CLIENT_DIR" ]; then
    echo "[!] Ta modyfikacja dotyczy wylacznie plikow klienta (pack/root/uiautohunt.py)."
    echo "    Na serwerze VPS przygotuj zaktualizowana paczke root.data i root.index do patchera."
    exit 0
fi

if [ -f "klient_pliki/root/uiautohunt.py" ] && [ -d "$CLIENT_DIR/pack/root" ]; then
    cp -f klient_pliki/root/uiautohunt.py "$CLIENT_DIR/pack/root/uiautohunt.py"
    echo "[+] Skopiowano uiautohunt.py do $CLIENT_DIR/pack/root/uiautohunt.py"
fi

echo "[SUKCES] Gotowe. Przepakuj paczke root w panelu Seban (m2clientpack) lub za pomoca PackMakerLite."
