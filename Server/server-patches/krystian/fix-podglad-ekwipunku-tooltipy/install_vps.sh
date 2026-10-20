#!/usr/bin/env bash
set -e

echo "======================================================================"
echo "   FIX PODGLĄDU EKWIPUNKU I DYMKÓW PRZEDMIOTÓW (SEBAN PANEL)"
echo "   Autor: Krystian | MT2Plus Community Fix"
echo "======================================================================"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATIC_SRC="${DIR}/pliki_panelu/static/player-profile.css"
TEMPLATE_SRC="${DIR}/pliki_panelu/templates/player.html"

if [ ! -f "${STATIC_SRC}" ] || [ ! -f "${TEMPLATE_SRC}" ]; then
    echo "[BŁĄD] Brak wymaganych plików w katalogu pliki_panelu/!"
    exit 1
fi

CONTAINER=$(docker ps --filter "name=seban-panel" --format "{{.Names}}" | head -n 1 || true)

if [ -n "${CONTAINER}" ]; then
    echo "[1/2] Wykryto kontener Docker: ${CONTAINER}"
    echo "Kopiowanie plików do kontenera..."
    docker cp "${STATIC_SRC}" "${CONTAINER}:/app/static/player-profile.css"
    docker cp "${TEMPLATE_SRC}" "${CONTAINER}:/app/templates/player.html"
    echo "Restartowanie kontenera..."
    docker restart "${CONTAINER}" >/dev/null
    echo "[OK] Zaktualizowano pomyślnie w kontenerze Docker (${CONTAINER})!"
else
    echo "[2/2] Brak aktywnego kontenera Docker. Sprawdzanie ścieżek lokalnych..."
    CANDIDATES=(
        "${DIR}/../../linux-port/docker/seban-panel"
        "/opt/seban-panel"
        "/var/www/seban-panel"
        "./seban-panel"
    )
    INSTALLED=0
    for TARGET in "${CANDIDATES[@]}"; do
        if [ -d "${TARGET}/static" ] && [ -d "${TARGET}/templates" ]; then
            echo "Kopiowanie do ${TARGET}..."
            cp -f "${STATIC_SRC}" "${TARGET}/static/player-profile.css"
            cp -f "${TEMPLATE_SRC}" "${TARGET}/templates/player.html"
            INSTALLED=1
            echo "[OK] Skopiowano pomyślnie do ${TARGET}."
            break
        fi
    done

    if [ "${INSTALLED}" -eq 0 ]; then
        echo "[UWAGA] Nie znaleziono domyślnej ścieżki panelu. Skopiuj pliki ręcznie:"
        echo "  - pliki_panelu/static/player-profile.css  -> <twoj_panel>/static/"
        echo "  - pliki_panelu/templates/player.html      -> <twoj_panel>/templates/"
    fi
fi

echo "======================================================================"
echo "Gotowe! W przeglądarce odśwież stronę z użyciem [Ctrl + F5]."
echo "======================================================================"
