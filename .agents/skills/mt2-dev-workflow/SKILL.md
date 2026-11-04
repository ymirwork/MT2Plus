---
name: mt2-dev-workflow
description: >-
  Standard operating procedures and strict safety gates for MT2Plus development:
  5-step upstream merge cycle, patch registry maintenance in Server/server-patches/krystian/,
  audit gating with audit_mods.py, client pack compilation, patcher web publishing,
  and mandatory in-game test checklist before any git commit or push.
---

# MT2Plus Development & Release Workflow

## 1. Safety Gates & Golden Rules
1. **Zero Unconfirmed Pushes:** NEVER commit or push to Git, never publish GitHub Releases or patcher updates until the user has tested the change in-game and explicitly confirmed that everything works.
2. **Surgical Patches:** When adding new features or fixes, write modular code in `Server/server-patches/krystian/<mod_name>/` and register it in `PROJECT_CONTEXT.md` (Section 5.1).
3. **Mandatory Audit:** Before building docker containers after modifications or upstream merge, always run:
   ```bash
   python Server/tools/audit_mods.py
   ```
   All active mods must pass with 0 errors.
4. **Database Safety:** Always take a dump of the MariaDB database to `Server/backups/` before applying SQL migrations or destructive server changes.

## 2. 5-Step Upstream Merge Procedure (`[AKTUALIZUJ]` / `[UPSTREAM]`)
When merging upstream changes from `https://github.com/zaxerrrr-dot/mt2009-sp-plus`:
1. **Krok 1 (Fetch & Diff):** `git fetch upstream` on `dev`. Compare diff with the upstream release tag.
2. **Krok 2 (Apply Upstream):** Apply core engine, script, panel, and manifest updates to `dev`. Bump version identifiers in `Server/VERSION`, `Server/MOD_VERSION`, `Klient/CLIENT_VERSION`.
3. **Krok 3 (Reapply Custom Patches):** Sequentially re-apply all active modules from `Server/server-patches/krystian/`. Run `python Server/tools/patch_dockerfile.py` to ensure custom Lua functions and quests are registered. Run `python Server/tools/audit_mods.py`.
4. **Krok 4 (Resolve Collisions & Build Dev):** Resolve any C++/Lua/Python collisions keeping upstream intact. Rebuild containers in `mt2dev`:
   ```bash
   docker compose build game panel seban-panel
   ```
   Verify 0 compilation errors. Stop containers cleanly: `docker compose down`.
5. **Krok 5 (Test & Release Gate):** Issue Checklist (Szablon C). Wait for user confirmation. Only then commit to `dev`, merge to `main`, push tags, build client packs, publish CDN patcher (`publish_patcher_web.py`), and create GitHub Release with ready-to-play archives.

## 3. Client Packaging & Patcher Web Publishing (`[CLIENT]` / `[PACK]`)
- Packaging: Run `Klient/Kompiluj-Paczki.bat` or `Klient/Compile-ClientPack.ps1` (PackMakerLite-RS).
- CDN Patcher sync (only after test confirmation):
  ```bash
  python Server/tools/publish_patcher_web.py
  ```
- No server downtime required for client-only Python UI or asset changes.

## 4. End-of-Task Verification Checklist (Szablon C)
Always conclude technical tasks with:
```markdown
### 📋 Co należy przetestować (Checklist Weryfikacyjny):
1. [ ] **Krok 1 (Przygotowanie / Wejście):** [Np. Zaloguj się, otwórz okno X]
2. [ ] **Krok 2 (Akcja testowa):** [Np. Kliknij przycisk Y, kup przedmiot Z]
3. [ ] **Oczekiwany rezultat:** [Dokładny opis poprawnego zachowania]
4. [ ] **Weryfikacja logów:** Brak błędów w `Klient/syserr.txt` oraz `Server/linux-port/docker/game/logs/syserr`

> ⚠️ **Status Git:** Zmiany czekają lokalnie. Upload na GitHub nastąpi dopiero po Twoim pomyślnym przetestowaniu i potwierdzeniu!
```
