#!/usr/bin/env bash
set -e

echo "==============================================================================="
echo "   INSTALATOR LINUX VPS: WSTAWANIE ZE 100% HP PO SMIERCI"
echo "==============================================================================="

if ! command -v python3 &> /dev/null; then
    echo "[!] Nie znaleziono python3. Zainstaluj poleceniem: apt update && apt install -y python3"
    exit 1
fi

SERVER_DIR="${1:-}"

if [ -z "$SERVER_DIR" ]; then
    if [ -d "../../linux-port" ]; then
        SERVER_DIR="../.."
    elif [ -d "../linux-port" ]; then
        SERVER_DIR=".."
    elif [ -d "Server/linux-port" ]; then
        SERVER_DIR="Server"
    elif [ -d "/opt/mt2009/Server" ]; then
        SERVER_DIR="/opt/mt2009/Server"
    fi
fi

if [ -z "$SERVER_DIR" ]; then
    read -rp "Podaj sciezke do katalogu Server: " SERVER_DIR
fi

echo "[*] Uzywam sciezki serwera: $SERVER_DIR"

echo "[1/2] Aplikowanie zmian w kodzie C++..."
python3 serwer_cpp/apply_revive_100_hp_server.py --server-dir "$SERVER_DIR"

echo "[2/2] Pytanie o przebudowe kontenera..."
read -rp "Czy chcesz przebudowac kontener game w Dockerze teraz? (t/n): " BUILD_NOW
if [ "$BUILD_NOW" = "t" ] || [ "$BUILD_NOW" = "T" ]; then
    docker compose --project-directory "$SERVER_DIR/linux-port/docker" build game
    echo "[*] Kontener zostal pomyslnie przebudowany. Restartowanie uslugi game..."
    docker compose --project-directory "$SERVER_DIR/linux-port/docker" restart game
fi

echo "==============================================================================="
echo "[SUKCES] Instalacja zakonczona pomyslnie!"
echo "==============================================================================="
