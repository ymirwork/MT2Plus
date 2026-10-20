#!/usr/bin/env bash
set -e

echo "==============================================================================="
echo "   INSTALATOR LINUX VPS: UKRYCIE WARTOSCI LICZBOWEJ HP CELU (KLIENT)"
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
    echo "[!] Ta modyfikacja dotyczy wylacznie plikow klienta (pack/root/uitarget.py)."
    echo "    Na serwerze VPS przygotuj gotowa paczke root.data i root.index do patchera."
    exit 0
fi

if [ -f "klient_pliki/root/uitarget.py" ] && [ -d "$CLIENT_DIR/pack/root" ]; then
    cp -f klient_pliki/root/uitarget.py "$CLIENT_DIR/pack/root/uitarget.py"
    echo "[+] Skopiowano uitarget.py do $CLIENT_DIR/pack/root/uitarget.py"
fi

echo "[SUKCES] Gotowe. Przepakuj paczke root w panelu Seban (m2clientpack) lub za pomoca PackMakerLite."
