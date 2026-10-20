#!/bin/sh
# Keep this script outside /opt/metin2/stack; the official updater replaces
# files inside that directory.
set -eu

mod=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${M2_SERVER_ROOT:-}" ]; then
    root=$M2_SERVER_ROOT
elif [ -f "$mod/../../VERSION" ]; then
    root=$(CDPATH= cd -- "$mod/../.." && pwd)
else
    root=/opt/metin2/stack
fi
test -f "$root/VERSION" || { echo "Brak VERSION w $root" >&2; exit 1; }
tracker="$mod/tracker_maintenance.py"
official="$root/linux-port/tools/update.sh"
items=$(dirname -- "$root")/mods/infinite-items/reapply-after-update.sh
if [ -f "$root/mods/infinite-items/reapply-after-update.sh" ]; then
    items=$root/mods/infinite-items/reapply-after-update.sh
fi

case "${1:-update}" in
    check)
        sh "$official" check
        python3 "$tracker" --server-root "$root" --check
        ;;
    repair)
        python3 "$tracker" --server-root "$root" --repair
        ;;
    update)
        sh "$official" check
        sh "$official"
        if [ -f "$items" ]; then
            sh "$items"
        fi
        python3 "$tracker" --server-root "$root" --repair
        ;;
    *)
        echo 'Uzycie: aktualizuj-serwer-z-trackerem.sh [check|repair|update]' >&2
        exit 2
        ;;
esac
