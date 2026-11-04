---
name: mt2-cpp-syserr-debugger
description: >-
  Diagnose, trace, and debug errors, crashes, and packet desynchronizations in the
  MT2Plus C++20 game server core (MartySama r41023), client Python scripts, and MariaDB.
  Use when analyzing syserr logs, server panics, character null pointers, packet mismatches,
  or client runtime exceptions.
---

# MT2Plus C++ & Syserr Debugging Runbook

## 1. Primary Log Locations
Always start debugging by examining the relevant log file rather than guessing:
- **Server Game Core Syserr:** `Server/linux-port/docker/game/logs/syserr`
- **Server Game Core Syslog:** `Server/linux-port/docker/game/logs/syslog`
- **Client Runtime Syserr:** `Klient/syserr.txt`
- **Docker Container Logs:** `docker logs mt2dev-game-1` and `docker logs mt2dev-mariadb-1`

## 2. Common Metin2 Crash Signatures & Root Causes

### A. Null Character / Item Pointer Dereference (`LPCHARACTER`, `LPITEM`)
- **Symptom:** Segmentation Fault (`SIGSEGV`) or server crash upon combat, trading, warping, or logout.
- **Cause:** Using `ch->GetPlayerID()`, `ch->GetName()`, or `item->GetVnum()` without checking `if (!ch)` or `if (ch->IsDead())` or `if (!item)`.
- **Fix:** Guard pointers at the boundary of event handlers, timers, and packet handlers:
  ```cpp
  if (!ch || !ch->GetDesc())
      return;
  ```

### B. Packet Header or Size Mismatch (`CPacketInfo`, `TPacketCG / TPacketGC`)
- **Symptom:** Client disconnected immediately after action, or server log: `UNKNOWN HEADER ...` or packet buffer overflow.
- **Cause:** Struct definition discrepancy between client (`UserInterface / Packet.h`) and server (`game/src/packet.h`), or incorrect dynamic packet sizing.
- **Rule:** Every packet header must have matching ID, fixed size or accurate dynamic length counter in both client and server protocols.

### C. Client Python UI Runtime Exceptions
- **Symptom:** UI window freezes, button does not click, or game closes silently.
- **Log:** `Klient/syserr.txt` lines ending in `Traceback (most recent call last):`.
- **Fix:** Inspect the exact `.py` file (e.g. `root/uiInventory.py`, `root/uiTarget.py`), verify variable scopes, dict keys, and component bindings in `uiscript/`.

### D. MariaDB Schema & Proto Mismatches
- **Symptom:** Server hangs on boot at `AsyncSQL: connected` or fails loading `item_proto` / `mob_proto`.
- **Check:** Ensure column count and types in database tables match the `TABLE_POSTFIX` and C++ DB cache structs in `db/src/ProtoReader.cpp` and `ClientManagerBoot.cpp`.

## 3. Surgical Patch Discipline
- Always test reproduction on the `dev` branch with Docker (`mt2dev`).
- Do not rewrite whole functions or subsystems to fix a null check or typo.
- Save the fix in `Server/server-patches/krystian/<patch_name>/` if it represents a reusable mod or upstream fix.
