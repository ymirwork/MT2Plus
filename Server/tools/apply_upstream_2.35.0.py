import os
import subprocess
import shutil

def get_upstream_file(git_path):
    res = subprocess.run(['git', 'show', f'upstream/main:{git_path}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to get {git_path} from upstream/main: {res.stderr.decode('utf-8', errors='ignore')}")
    return res.stdout

def write_file(dest_path, content):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'wb') as f:
        f.write(content)
    print(f"Updated: {dest_path}")

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    server_root = os.path.join(repo_root, 'Server')
    klient_root = os.path.join(repo_root, 'Klient')

    # 1. Root server version and info files
    for fname in ['VERSION', 'MOD_VERSION', 'CLIENT_VERSION', 'CHANGELOG.md', 'client-files.json', 'update-manifest-mt2009.json']:
        content = get_upstream_file(fname)
        write_file(os.path.join(server_root, fname), content)

    # Update Klient/CLIENT_VERSION
    write_file(os.path.join(klient_root, 'CLIENT_VERSION'), get_upstream_file('CLIENT_VERSION'))

    # 2. Quests
    quests = [
        'linux-port/docker/game/quest/biblioteka_wiedzy.quest',
        'linux-port/docker/game/quest/ruiny_skorpiona.quest',
        'linux-port/docker/game/quest/starozytna_dzungla.quest',
        'linux-port/docker/game/quest/wzgorze_wukonga.quest',
    ]
    for q in quests:
        write_file(os.path.join(server_root, q), get_upstream_file(q))

    # 3. Panel & Seban-Panel files
    seban_files = [
        'linux-port/docker/panel/app/admin_panel.py',
        'linux-port/docker/seban-panel/VERSION',
        'linux-port/docker/seban-panel/env_editor.py',
        'linux-port/docker/seban-panel/env_schema.py',
        'linux-port/docker/seban-panel/market_preview/sheet.py',
        'linux-port/docker/seban-panel/templates/server_env.html',
        'linux-port/docker/seban-panel/test_env_editor.py',
    ]
    for sf in seban_files:
        write_file(os.path.join(server_root, sf), get_upstream_file(sf))

    # Also mirror into overlays/seban-panel where appropriate
    for overlay_rel in [
        'env_editor.py',
        'env_schema.py',
        'test_env_editor.py',
        'templates/server_env.html',
        'market_preview/sheet.py',
    ]:
        src = os.path.join(server_root, 'linux-port/docker/seban-panel', overlay_rel)
        dst = os.path.join(server_root, 'linux-port/overlays/seban-panel', overlay_rel)
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"Mirrored overlay: {dst}")

    # 4. Tools
    tools_files = [
        'linux-port/tools/test_update_autostart.py',
        'linux-port/tools/update.sh',
        'start-server.ps1',
    ]
    for tf in tools_files:
        write_file(os.path.join(server_root, tf), get_upstream_file(tf))

    # 5. Client patches
    client_patch_files = [
        'client-patches/client-2.0.30/root/uiingameevent.py',
        'client-patches/client-2.0.30/root/uipickupfilter.py',
        'client-patches/client-2.0.30/root/uipickupfilterrules.py',
    ]
    for cpf in client_patch_files:
        content = get_upstream_file(cpf)
        write_file(os.path.join(server_root, cpf), content)
        # Also copy directly into Klient/pack/root
        base_name = os.path.basename(cpf)
        klient_dest = os.path.join(klient_root, 'pack', 'root', base_name)
        if os.path.exists(os.path.dirname(klient_dest)):
            write_file(klient_dest, content)

    # 6. Playerbot header files (22 files)
    pb_headers = [
        'linux-port/overlays/playerbot/src/game/src/playerbot_activities.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_demon_tower.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_economy.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_explain_rules.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_gear.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_herbalism.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_loot.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_market_life.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_movement.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_navigation.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_offline_market.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_offline_policy.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_offline_shop.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_party_dungeon.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_price_tables.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_priorities.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_sidekick.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_targeting.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_town.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_travel.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_types.h',
        'linux-port/overlays/playerbot/src/game/src/playerbot_world_memory.h',
    ]
    for pbh in pb_headers:
        write_file(os.path.join(server_root, pbh), get_upstream_file(pbh))

    # 7. Merge playerbot_bonus.h (upstream + YmirWork modification)
    bonus_content = get_upstream_file('linux-port/overlays/playerbot/src/game/src/playerbot_bonus.h').decode('utf-8')
    
    # Extract our YmirWork block from current Server/linux-port/overlays/playerbot/src/game/src/playerbot_bonus.h
    current_bonus_path = os.path.join(server_root, 'linux-port/overlays/playerbot/src/game/src/playerbot_bonus.h')
    with open(current_bonus_path, 'r', encoding='utf-8') as f:
        curr_lines = f.read()
    
    ymir_marker = '// MT2009_PLUS_BOT_M1M2_LIQUIDATION_V2 (Autor: YmirWork / Krystian):'
    ymir_end_marker = 'bool ManagePlayerBotBonusReroll(LPCHARACTER ch, TPlayerBotAIState& state, DWORD dwNow)'
    
    ymir_start = curr_lines.find(ymir_marker)
    ymir_end = curr_lines.find(ymir_end_marker)
    if ymir_start == -1 or ymir_end == -1:
        raise RuntimeError("Could not find YmirWork block in existing playerbot_bonus.h")
    
    ymir_block = curr_lines[ymir_start:ymir_end]
    
    # In upstream bonus_content, find ManagePlayerBotBonusReroll
    target_pos = bonus_content.find(ymir_end_marker)
    if target_pos == -1:
        raise RuntimeError("Could not find ManagePlayerBotBonusReroll in upstream playerbot_bonus.h")
    
    merged_bonus = bonus_content[:target_pos] + "\t" + ymir_block.strip() + "\n\n\t" + bonus_content[target_pos:]
    
    # Now in ManagePlayerBotBonusReroll, make sure ManagePlayerBotLiquidationM1M2(ch); is called
    reroll_call = "ManagePlayerBotLiquidationM1M2(ch);"
    if reroll_call not in merged_bonus:
        anchor = "ManagePlayerBotRefinerExchange(ch);"
        anchor_pos = merged_bonus.find(anchor)
        if anchor_pos == -1:
            raise RuntimeError("Could not find ManagePlayerBotRefinerExchange in ManagePlayerBotBonusReroll")
        merged_bonus = merged_bonus[:anchor_pos + len(anchor)] + "\n\t\t" + reroll_call + merged_bonus[anchor_pos + len(anchor):]
    
    write_file(current_bonus_path, merged_bonus.encode('utf-8'))
    print("playerbot_bonus.h merged with YmirWork liquidation successfully.")

if __name__ == '__main__':
    main()
