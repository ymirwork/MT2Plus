import os
import sys
import shutil
import urllib.request
import zipfile
import hashlib

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().upper()

def download_with_progress(url, dest_path):
    print(f"Downloading {url} -> {dest_path}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp, open(dest_path, 'wb') as out:
        total = int(resp.headers.get('Content-Length', 0))
        downloaded = 0
        last_pct = -1
        while chunk := resp.read(1024 * 1024):
            out.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                pct = int(downloaded * 100 / total)
                if pct != last_pct and pct % 20 == 0:
                    print(f"  {pct}% ({downloaded // (1024*1024)} MB / {total // (1024*1024)} MB)")
                    last_pct = pct
    print(f"Downloaded {dest_path} ({os.path.getsize(dest_path)} bytes)")

def build_server_package(repo_root, dist_dir):
    server_root = os.path.join(repo_root, 'Server')
    base_zip = os.path.join(dist_dir, 'base_server.zip')
    url = 'https://github.com/zaxerrrr-dot/mt2009-sp-plus/releases/download/v2.35.0/metin2-server-update-2.35.0.zip'
    
    if not os.path.exists(base_zip):
        download_with_progress(url, base_zip)

    target_zip = os.path.join(dist_dir, 'metin2-server-update-2.35.0.zip')
    temp_dir = os.path.join(dist_dir, 'server_extracted')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    print("Extracting base server package...")
    with zipfile.ZipFile(base_zip, 'r') as zf:
        zf.extractall(temp_dir)

    print("Injecting MT2Plus modifications into server package...")
    # 1. Addons (opcjonalne/archiwalne)
    addons_src = os.path.join(server_root, 'addons')
    if os.path.exists(addons_src):
        addons_dst = os.path.join(temp_dir, 'addons')
        os.makedirs(addons_dst, exist_ok=True)
        for addon_file in os.listdir(addons_src):
            src = os.path.join(addons_src, addon_file)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(addons_dst, addon_file))

    # 2. Server patches
    patches_dst = os.path.join(temp_dir, 'server-patches')
    if os.path.exists(os.path.join(server_root, 'server-patches')):
        shutil.copytree(os.path.join(server_root, 'server-patches'), patches_dst, dirs_exist_ok=True)

    # 3. Quest tp_bookmarks
    quest_dst = os.path.join(temp_dir, 'linux-port', 'docker', 'game', 'quest')
    os.makedirs(quest_dst, exist_ok=True)
    shutil.copy2(os.path.join(server_root, 'linux-port', 'docker', 'game', 'quest', 'tp_bookmarks.quest'), quest_dst)

    # 4. Engine C++ source files
    engine_src = os.path.join(server_root, 'linux-port', 'docker', 'game', 'src', 'server', 'game', 'src')
    engine_dst = os.path.join(temp_dir, 'linux-port', 'docker', 'game', 'src', 'server', 'game', 'src')
    if os.path.exists(engine_src):
        os.makedirs(engine_dst, exist_ok=True)
        for f in ['char_skill.cpp', 'char.cpp', 'battle.cpp', 'input_main.cpp', 'char_battle.cpp', 'char_item.cpp']:
            src_f = os.path.join(engine_src, f)
            if os.path.exists(src_f):
                shutil.copy2(src_f, engine_dst)

    # 5. Overlays (playerbot + seban-panel)
    pb_dst = os.path.join(temp_dir, 'linux-port', 'overlays', 'playerbot', 'src', 'game', 'src')
    os.makedirs(pb_dst, exist_ok=True)
    shutil.copy2(os.path.join(server_root, 'linux-port', 'overlays', 'playerbot', 'src', 'game', 'src', 'playerbot_bonus.h'), pb_dst)

    seban_src = os.path.join(server_root, 'linux-port', 'overlays', 'seban-panel')
    seban_dst = os.path.join(temp_dir, 'linux-port', 'overlays', 'seban-panel')
    if os.path.exists(seban_src):
        shutil.copytree(seban_src, seban_dst, dirs_exist_ok=True)
    # Also in docker/seban-panel
    seban_docker_src = os.path.join(server_root, 'linux-port', 'docker', 'seban-panel')
    seban_docker_dst = os.path.join(temp_dir, 'linux-port', 'docker', 'seban-panel')
    if os.path.exists(seban_docker_src):
        shutil.copytree(seban_docker_src, seban_docker_dst, dirs_exist_ok=True)

    # 6. Client patches directory
    cp_src = os.path.join(server_root, 'client-patches')
    cp_dst = os.path.join(temp_dir, 'client-patches')
    if os.path.exists(cp_src):
        shutil.copytree(cp_src, cp_dst, dirs_exist_ok=True)

    # 7. Root info files
    for rf in ['VERSION', 'MOD_VERSION', 'CLIENT_VERSION', 'CHANGELOG.md', 'update-manifest-mt2009.json']:
        shutil.copy2(os.path.join(server_root, rf), temp_dir)

    # Pack into target zip
    print(f"Compressing {target_zip}...")
    if os.path.exists(target_zip):
        os.remove(target_zip)
    
    with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, temp_dir)
                zf.write(full_path, rel_path)

    shutil.rmtree(temp_dir)
    hash_val = sha256_file(target_zip)
    size_val = os.path.getsize(target_zip)
    print(f"Built {target_zip}: size={size_val}, sha256={hash_val}")
    return target_zip, size_val, hash_val

def build_client_package(repo_root, dist_dir):
    klient_root = os.path.join(repo_root, 'Klient')
    base_zip = os.path.join(dist_dir, 'base_client.zip')
    url = 'https://github.com/zaxerrrr-dot/mt2009-sp-plus/releases/download/klient-v2.0.66/metin2-client-update-2.0.66.zip'
    
    if not os.path.exists(base_zip):
        download_with_progress(url, base_zip)

    target_zip = os.path.join(dist_dir, 'metin2-client-update-2.0.66.zip')
    temp_dir = os.path.join(dist_dir, 'client_extracted')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    print("Extracting base client package...")
    with zipfile.ZipFile(base_zip, 'r') as zf:
        zf.extractall(temp_dir)

    print("Injecting MT2Plus modifications into client package...")
    # Inject root.data and root.index
    pack_dst = os.path.join(temp_dir, 'pack')
    os.makedirs(pack_dst, exist_ok=True)
    shutil.copy2(os.path.join(klient_root, 'pack', 'root.data'), os.path.join(pack_dst, 'root.data'))
    shutil.copy2(os.path.join(klient_root, 'pack', 'root.index'), os.path.join(pack_dst, 'root.index'))

    # Inject CLIENT_VERSION
    shutil.copy2(os.path.join(klient_root, 'CLIENT_VERSION'), os.path.join(temp_dir, 'CLIENT_VERSION'))

    # Clean any unwanted bak or syserr files
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            if f.endswith('.bak') or f in ['syserr.txt', 'syslog.txt']:
                try:
                    os.remove(os.path.join(root, f))
                except Exception:
                    pass

    print(f"Compressing {target_zip}...")
    if os.path.exists(target_zip):
        os.remove(target_zip)

    with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, temp_dir)
                zf.write(full_path, rel_path)

    shutil.rmtree(temp_dir)
    hash_val = sha256_file(target_zip)
    size_val = os.path.getsize(target_zip)
    print(f"Built {target_zip}: size={size_val}, sha256={hash_val}")
    return target_zip, size_val, hash_val

if __name__ == '__main__':
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dist_dir = os.path.join(repo_root, 'dist')
    os.makedirs(dist_dir, exist_ok=True)

    print("Building server release package...")
    srv_file, srv_size, srv_hash = build_server_package(repo_root, dist_dir)

    print("Building client release package...")
    cli_file, cli_size, cli_hash = build_client_package(repo_root, dist_dir)

    print("\n--- SUMMARY ---")
    print(f"Server: {srv_file} ({srv_size} bytes) SHA-256: {srv_hash}")
    print(f"Client: {cli_file} ({cli_size} bytes) SHA-256: {cli_hash}")
