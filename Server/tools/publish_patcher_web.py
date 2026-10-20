import os
import sys
import json
import shutil
import hashlib
import subprocess
import urllib.request
import urllib.error

def get_github_token():
    try:
        proc = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, _ = proc.communicate(input='protocol=https\nhost=github.com\n\n')
        for line in out.splitlines():
            if line.startswith('password='):
                return line.split('=', 1)[1]
    except Exception:
        pass
    return os.environ.get('GITHUB_TOKEN')

def md5_file(filepath):
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().upper()

def download_file(url, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'MT2Plus-Patcher-Sync'})
    with urllib.request.urlopen(req) as resp, open(dest_path, 'wb') as out:
        while chunk := resp.read(1024 * 1024):
            out.write(chunk)

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    klient_dir = os.path.join(repo_root, 'Klient')
    dist_dir = os.path.join(repo_root, 'dist')
    web_dir = os.path.join(dist_dir, 'patcher-web')
    files_dir = os.path.join(web_dir, 'patcher', 'files')
    os.makedirs(files_dir, exist_ok=True)

    print("=== MT2Plus: Budowanie i synchronizacja serwera Patchera ===")

    # 1. Pobierz bazowy patchlist.json z upstreamu
    upstream_patchlist_url = "http://141.94.100.53/patcher/patchlist.json"
    print(f"Pobieranie bazowej listy z {upstream_patchlist_url}...")
    req = urllib.request.Request(upstream_patchlist_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        patchlist = json.loads(resp.read().decode('utf-8'))
    print(f"Pobrano bazową listę: {len(patchlist)} plików.")

    # 2. Przygotuj nasze zmodyfikowane pliki
    overrides = {}

    # Guard: upewnij sie, ze Klient/pack/root zawiera AutoFishWindow
    root_hunt_py = os.path.join(klient_dir, 'pack', 'root', 'uiautohunt.py')
    patch_hunt_py = os.path.join(repo_root, 'Server', 'server-patches', 'krystian', 'autofish', 'client', 'root', 'uiautohunt.py')
    if os.path.exists(root_hunt_py) and os.path.exists(patch_hunt_py):
        with open(root_hunt_py, 'r', encoding='utf-8', errors='ignore') as f_h:
            if 'AutoFishWindow' not in f_h.read():
                print("[GUARD] Brak AutoFishWindow w Klient/pack/root/uiautohunt.py! Kopiuje z server-patches...")
                shutil.copy2(patch_hunt_py, root_hunt_py)
                print("[GUARD] Kompilacja paczki root.data...")
                subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File',
                               os.path.join(repo_root, 'Server', 'tools', 'Compile-ClientPack.ps1'),
                               '-PackName', 'root', '-ClientDir', klient_dir, '-NoBackup'], check=True)
    
    # root.data i root.index
    root_data = os.path.join(klient_dir, 'pack', 'root.data')
    root_index = os.path.join(klient_dir, 'pack', 'root.index')
    if os.path.exists(root_data):
        overrides['pack\\root.data'] = root_data
    if os.path.exists(root_index):
        overrides['pack\\root.index'] = root_index

    # gamedata.data i gamedata.index
    gamedata_data = os.path.join(klient_dir, 'pack', 'gamedata.data')
    gamedata_index = os.path.join(klient_dir, 'pack', 'gamedata.index')
    if os.path.exists(gamedata_data):
        overrides['pack\\gamedata.data'] = gamedata_data
    if os.path.exists(gamedata_index):
        overrides['pack\\gamedata.index'] = gamedata_index

    # CLIENT_VERSION
    client_version_path = os.path.join(klient_dir, 'CLIENT_VERSION')
    if os.path.exists(client_version_path):
        overrides['CLIENT_VERSION'] = client_version_path

    # MT2009-Patcher.exe.config
    patcher_config_path = os.path.join(klient_dir, 'MT2009-Patcher.exe.config')
    if os.path.exists(patcher_config_path):
        overrides['MT2009-Patcher.exe.config'] = patcher_config_path

    print(f"Zastępowanie plików autorskimi modyfikacjami MT2Plus ({len(overrides)} plików)...")
    
    # 3. Zaktualizuj wpisy w patchlist
    for item in patchlist:
        name = item.get('name')
        if name in overrides:
            local_file = overrides[name]
            size = os.path.getsize(local_file)
            md5_hash = md5_file(local_file)
            uid = md5_hash.lower()
            
            old_hash = item.get('md5')
            item['size'] = size
            item['md5'] = md5_hash.upper()
            item['uid'] = uid
            print(f"  [MT2Plus MOD] {name}: stary MD5={old_hash} -> nowy MD5={item['md5']} ({size} B)")
            
            # Skopiuj zmodyfikowany plik do files/<uid>
            dest_file = os.path.join(files_dir, uid)
            shutil.copy2(local_file, dest_file)

    # 4. Upewnij się, że wszystkie pozostałe pliki upstreamu istnieją w files/
    print("Weryfikacja/dociąganie pozostałych plików upstreamu...")
    total_items = len(patchlist)
    downloaded_count = 0
    skipped_count = 0

    for idx, item in enumerate(patchlist, 1):
        uid = item.get('uid')
        name = item.get('name')
        if not uid or item.get('delete', 0) > 0:
            continue
        dest_file = os.path.join(files_dir, uid)
        if not os.path.exists(dest_file) or os.path.getsize(dest_file) != item.get('size'):
            url = f"http://141.94.100.53/patcher/files/{uid}"
            print(f"  [{idx}/{total_items}] Pobieranie upstream: {name} ({item.get('size') // 1024} KB)...")
            try:
                download_file(url, dest_file)
                downloaded_count += 1
            except Exception as e:
                print(f"  BŁĄD pobierania {url}: {e}")
        else:
            skipped_count += 1

    print(f"Pliki gotowe: {downloaded_count} nowo pobranych, {skipped_count} z pamięci podręcznej/lokalnych.")

    # 5. Zapisz patchlist.json
    patchlist_out = os.path.join(web_dir, 'patcher', 'patchlist.json')
    with open(patchlist_out, 'w', encoding='utf-8') as f:
        json.dump(patchlist, f, indent=1, ensure_ascii=False)
    print(f"Zapisano: {patchlist_out}")

    # 6. Przygotuj news.json
    news_data = [
        {
            "newsType": 2,
            "topic": "MT2Plus 2.35.0-mod56",
            "creator": "16.10.2026",
            "threadUrl": "https://github.com/ymirwork/MT2Plus",
            "date": "2026-10-16",
            "message": "Autorskie modyfikacje MT2Plus: szybkie zbieranie, sklep 160 slotów, balans gospodarki i optymalizacje.",
            "avatarLink": ""
        },
        {
            "newsType": 2,
            "topic": "Klient 2.0.66",
            "creator": "16.10.2026",
            "threadUrl": "https://github.com/ymirwork/MT2Plus",
            "date": "2026-10-16",
            "message": "Zintegrowane modyfikacje klienta z nowościami oficjalnego wydania.",
            "avatarLink": ""
        },
        {
            "newsType": 1,
            "topic": "Serwer gry MT2Plus",
            "creator": "MT2Plus",
            "threadUrl": "https://github.com/ymirwork/MT2Plus",
            "date": "",
            "message": "Patcher automatycznie pobiera oficjalne pliki oraz autorskie modyfikacje projektu MT2Plus.",
            "avatarLink": ""
        }
    ]
    news_out = os.path.join(web_dir, 'patcher', 'news.json')
    with open(news_out, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, indent=1, ensure_ascii=False)
    print(f"Zapisano: {news_out}")

    # 7. Utwórz .nojekyll w katalogu głównym web
    nojekyll_path = os.path.join(web_dir, '.nojekyll')
    with open(nojekyll_path, 'w') as f:
        pass

    # Index landing page
    index_html = os.path.join(web_dir, 'index.html')
    with open(index_html, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><title>MT2Plus Patcher</title></head><body><h1>MT2Plus Patcher Server</h1><p>Serwer aktualizacji projektu MT2Plus.</p></body></html>")

    print("\nDrzewo patchera gotowe w:", web_dir)

    # 8. Publikacja na gałąź gh-pages
    publish_to_gh_pages(repo_root, web_dir)

def publish_to_gh_pages(repo_root, web_dir):
    token = get_github_token()
    print("\nPublikacja drzewa patchera na gałąź gh-pages...")

    gh_pages_git = os.path.join(web_dir, '.git')
    init_needed = not os.path.exists(gh_pages_git)

    if init_needed:
        subprocess.run(['git', 'init'], cwd=web_dir, check=True)
        subprocess.run(['git', 'config', 'user.name', 'MT2Plus Patcher Bot'], cwd=web_dir, check=True)
        subprocess.run(['git', 'config', 'user.email', 'patcher@mt2plus.local'], cwd=web_dir, check=True)
        subprocess.run(['git', 'checkout', '-b', 'gh-pages'], cwd=web_dir, check=True)
        subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/ymirwork/MT2Plus.git'], cwd=web_dir, check=True)

    subprocess.run(['git', 'add', '-A'], cwd=web_dir, check=True)
    subprocess.run(['git', 'commit', '-m', 'Deploy MT2Plus Patcher web files'], cwd=web_dir, capture_output=True)
    push_res = subprocess.run(['git', 'push', '-f', 'origin', 'gh-pages'], cwd=web_dir, capture_output=True, text=True)
    
    if push_res.returncode == 0:
        print("Wypchnięto pomyślnie na origin/gh-pages!")
    else:
        print(f"Błąd push do origin/gh-pages: {push_res.stderr.strip()}")
        return False

    # Włącz GitHub Pages jeśli nie było włączone
    if token:
        try:
            data = json.dumps({'source': {'branch': 'gh-pages', 'path': '/'}}).encode('utf-8')
            req = urllib.request.Request('https://api.github.com/repos/ymirwork/MT2Plus/pages', data=data, method='POST')
            req.add_header('Authorization', f'Bearer {token}')
            req.add_header('Accept', 'application/vnd.github+json')
            req.add_header('Content-Type', 'application/json')
            req.add_header('User-Agent', 'MT2Plus-Patcher')
            with urllib.request.urlopen(req) as resp:
                print("Włączono GitHub Pages dla repozytorium MT2Plus!")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            if 'already' in err_body or e.code == 409:
                print("GitHub Pages jest już aktywne.")
            else:
                print(f"Info GitHub Pages API ({e.code}): {err_body}")

    print("Publikacja zakończona sukcesem!")
    print("Adres Patchlisty: https://ymirwork.github.io/MT2Plus/patcher/patchlist.json")
    return True

if __name__ == '__main__':
    main()
