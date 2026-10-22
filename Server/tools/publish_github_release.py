import os
import sys
import subprocess
import urllib.request
import json

def get_github_token():
    proc = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, _ = proc.communicate(input='protocol=https\nhost=github.com\n\n')
    for line in out.splitlines():
        if line.startswith('password='):
            return line.split('=', 1)[1]
    raise RuntimeError("Could not find GitHub token via git credential fill")

def create_release(token, tag, name, body):
    url = "https://api.github.com/repos/ymirwork/MT2Plus/releases"
    payload = {
        "tag_name": tag,
        "target_commitish": "main",
        "name": name,
        "body": body,
        "draft": False,
        "prerelease": False
    }
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('User-Agent', 'MT2Plus-Release')

    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            return res
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='ignore')
        print(f"HTTPError {e.code}: {err_msg}")
        raise

def upload_asset_curl(token, upload_url, file_path, name):
    base_upload_url = upload_url.split('{')[0]
    target_url = f"{base_upload_url}?name={name}"
    print(f"Uploading asset {name} ({os.path.getsize(file_path)} bytes) via streaming curl...")

    cmd = [
        'curl.exe', '-S', '-s',
        '-X', 'POST',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Accept: application/vnd.github+json',
        '-H', 'Content-Type: application/zip',
        '--data-binary', f'@{file_path}',
        target_url
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"curl upload failed with code {res.returncode}: {res.stderr}")
    
    try:
        resp_json = json.loads(res.stdout)
        if 'id' in resp_json:
            print(f"Uploaded successfully: {resp_json.get('name')} ({resp_json.get('size')} bytes)")
            return resp_json
        else:
            print(f"Response: {res.stdout[:400]}")
            return resp_json
    except Exception as e:
        print(f"Response parse error: {e}, raw: {res.stdout[:200]}")
        return None

def publish_release(srv_size, srv_hash, cli_size, cli_hash):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dist_dir = os.path.join(repo_root, 'dist')
    
    srv_zip = os.path.join(dist_dir, 'metin2-server-update-2.37.0.zip')
    cli_zip = os.path.join(dist_dir, 'metin2-client-update-2.0.68.zip')

    if not os.path.exists(srv_zip) or not os.path.exists(cli_zip):
        print(f"ERROR: Missing release zip files in {dist_dir}")
        sys.exit(1)

    token = get_github_token()
    print("GitHub token acquired successfully.")

    tag = "v2.37.0-mod58"
    release_name = "MT2009 PLUS v2.37.0-mod58 - Serwer 2.37.0 & Klient 2.0.68"

    body = f"""# 📦 MT2Plus Wydanie v2.37.0-mod58

Oficjalne wydanie zintegrowanych paczek instalacyjnych i aktualizacyjnych **MT2009 PLUS** (Serwer 2.37.0, mod-58 oraz Klient 2.0.68) z pełnym zachowaniem autorskich rozszerzeń (YmirWork / Krystian).

---

### 🛡️ Autorskie Modyfikacje i Systemy MT2Plus
• **Optymalizacja Autołowów (Lochy Małp & Zabezpieczenie Ścian):** Wbudowany filtr osiągalności celów `CPlayerBotManager::IsHumanTargetReachable` (`playerbot_manager.cpp`, `playerbot_manager.h`), eliminujący wybieranie potworów za ścianami w odciętych komnatach.
• **Sklepy Offline 160 Slotów z Drewnianymi Kluczami:** Pełna obsługa 2-stronicowych magazynów i sklepów offline gracza (kompatybilność z drewnianymi kluczami `shop_unlock_slots.quest`, `ikarus_shop_manager.cpp` oraz `offlineshopmanage.py`).
• **Seban Panel – Rozszerzona Ekonomia V2 & Caching:** Zachowano zaawansowany moduł `/economy` (analiza rynku, transakcje, doradca rotacji emerytur botów, statystyki M1/M2 i cache wydajnościowy paneli).
• **Zarządzanie Czasem Amuletów i Stackowaniem:** 30-dniowe amulety i pierścienie z ItemShopu oraz stackowanie wybranych ulepszaczy i ksiąg do 200 sztuk (`apply.sh`).
• **Autorskie Zadania Gry:** Kompilacja `recykling_bonusow.quest`, `shop_unlock_slots.quest` oraz `tp_bookmarks.quest`.

---

### 🌳 Nowości i Usprawnienia Upstream (2.37.0 / mod-58)
• **Zaklęty Las (map 353) & Mapy 90+ (301-304):** Pełna integracja nowych lokacji wysokopoziomowych, mobów i bossów (En-Tai, Bagjanamu, Cape Dragon Head, Yohara mobs).
• **Czwarty Rdzeń Mapowy (game3):** Wydzielenie mapy 353 i map 301-304 na dedykowany proces `ch1-game3` na porcie 13003 dla maksymalnej płynności i stabilności.
• **Aktualizacja Portów:** Zakres portów gier rozszerzony do 13000-13003 w Docker Compose i konfiguracji `.env`.
• **Flagi M2_BONUS_MODE & PLAYERBOT_HANDOVER:** Nowe dyrektywy silnika gry dla optymalizacji systemów bonusów oraz przekazywania sterowania botami.
• **Pełna kompatybilność z mod-58:** Wszystkie schematy bazy danych i procedury mariadb zaktualizowane do najnowszego standardu.

---

### 💻 Klient Gry 2.0.68
• **Pełna obsługa nowych lokacji i assetów:** Kompatybilność z Zaklętym Lasem, mapami 90+ i nowymi modelami potworów.
• **Zabezpieczenie AutoFish Guard:** Spójność pakietów i zabezpieczenie modułów wędkarskich.
• **Zsynchronizowany Patcher Web CDN:** Aktualizacja sum kontrolnych i plików patchera na GitHub Pages.

---

### 📦 Sumy kontrolne załączonych archiwów (SHA-256)
- **`metin2-server-update-2.37.0.zip`** ({srv_size:,} bytes)
  `SHA-256: {srv_hash}`
- **`metin2-client-update-2.0.68.zip`** ({cli_size:,} bytes)
  `SHA-256: {cli_hash}`

---

📥 **Instrukcja Uruchomienia (Ready-to-Play):**
1. Pobierz paczkę serwera `metin2-server-update-2.37.0.zip` oraz klienta `metin2-client-update-2.0.68.zip`.
2. Wypakuj serwer i uruchom `start.bat` (wymagany Docker Desktop).
3. Wypakuj klienta i uruchom grę przez `metin2client.exe` (lub zaktualizuj automatycznie przez `MT2009-Patcher.exe`).
"""

    print("Creating release on GitHub...")
    rel = create_release(token, tag, release_name, body)
    rel_id = rel['id']
    upload_url = rel['upload_url']
    html_url = rel['html_url']
    print(f"Created release {rel_id}: {html_url}")

    upload_asset_curl(token, upload_url, srv_zip, "metin2-server-update-2.37.0.zip")
    upload_asset_curl(token, upload_url, cli_zip, "metin2-client-update-2.0.68.zip")

    print(f"\nSUCCESS! Release published at: {html_url}")
    return html_url

if __name__ == '__main__':
    if len(sys.argv) >= 5:
        publish_release(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4])
    else:
        # Default placeholder / auto-calculate if files exist
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        dist_dir = os.path.join(repo_root, 'dist')
        srv_zip = os.path.join(dist_dir, 'metin2-server-update-2.37.0.zip')
        cli_zip = os.path.join(dist_dir, 'metin2-client-update-2.0.68.zip')
        import hashlib
        def h(p):
            x = hashlib.sha256()
            with open(p, 'rb') as f:
                while c := f.read(1024*1024):
                    x.update(c)
            return x.hexdigest().upper()
        if os.path.exists(srv_zip) and os.path.exists(cli_zip):
            publish_release(os.path.getsize(srv_zip), h(srv_zip), os.path.getsize(cli_zip), h(cli_zip))
        else:
            print("Usage: python publish_github_release.py <srv_size> <srv_hash> <cli_size> <cli_hash>")
