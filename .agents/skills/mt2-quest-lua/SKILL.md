---
name: mt2-quest-lua
description: >-
  Authoring, maintaining, and debugging Metin2 Lua quests, dungeon state machines,
  and event scripts. Covers qc quest compilation, flag management (pc.getqf, game.get_event_flag),
  server timers, dungeon instances, and exposing custom C++ functions to Lua.
---

# MT2Plus Quest & Lua Scripting Guide

## 1. Directory Structure & Compilation
- **Quest Directory:** `Server/linux-port/docker/game/quest/`
- **Quest List:** `quest_list` (lists all quests to be compiled by `qc`)
- **Compilation:** Quests are compiled into binary states via the `qc` compiler during container startup or manually inside the `game` container.
- **Custom Lua Functions:** Custom functions (`guild.payout_*`, `open_guild_payout_dialog`, `guild.treasury_withdraw`) are bound in `questlua_*.cpp` and preserved across Docker builds by `Server/tools/patch_dockerfile.py`.

## 2. Quest State Machine Anatomy
```lua
quest sample_event begin
    state start begin
        when login begin
            if pc.getqf("completed") == 1 then
                return
            end
            set_state(active)
        end
    end

    state active begin
        when 20001.chat."Zadanie" begin
            say_title("Alchemik:")
            say("Witaj w nowym evencie!")
            set_state(__COMPLETE__)
            pc.setqf("completed", 1)
        end
    end

    state __COMPLETE__ begin
    end
end
```

## 3. Best Practices & Pitfalls
1. **Never use infinite loops or heavy polling in Lua:** Lua runs on the main game server thread. A blocking loop freezes the entire channel/game process.
2. **Timers:** Use `server_timer("name", seconds, map_index)` for dungeons and global events; use `timer("name", seconds)` only for single-player session delays.
3. **Dungeon Scoping:** Always use `d.setf("flag", value)` and `d.getf("flag")` to ensure dungeon flags stay isolated to that specific dungeon map instance.
4. **Flag Hygiene:** Do not bloat player quest flags (`quest` SQL table). Clean up temporary flags with `pc.delqf("flag")` when quests finish.
