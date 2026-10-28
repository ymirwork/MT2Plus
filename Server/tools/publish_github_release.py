#!/usr/bin/env python3
"""
Publishes MT2Plus server and client update packages to GitHub Releases.
Complies with Project Rule 13 (Mandatory GitHub Release publication).
"""
import os
import sys
import subprocess
import json
import urllib.request
import urllib.error

def get_github_token():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        proc = subprocess.run(
            ['git', 'credential', 'fill'],
            input="protocol=https\nhost=github.com\n",
            capture_output=True,
            text=True,
            check=True
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception as e:
        print(f"Warning: could not get token from git credential helper: {e}")
    return None

def create_or_get_release(token, tag, name, body):
    api_url = "https://api.github.com/repos/ymirwork/MT2Plus/releases"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'MT2Plus-Release'
    }
    payload = {
        'tag_name': tag,
        'target_commitish': 'main',
        'name': name,
        'body': body,
        'draft': False,
        'prerelease': False
    }
    req = urllib.request.Request(api_url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 422:
            print(f"Release for {tag} already exists. Fetching existing release...")
            tag_url = f"https://api.github.com/repos/ymirwork/MT2Plus/releases/tags/{tag}"
            get_req = urllib.request.Request(tag_url, headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github+json',
                'User-Agent': 'MT2Plus-Release'
            })
            with urllib.request.urlopen(get_req) as resp:
                existing = json.loads(resp.read().decode('utf-8'))
            patch_url = f"https://api.github.com/repos/ymirwork/MT2Plus/releases/{existing['id']}"
            patch_data = json.dumps({"name": name, "body": body}).encode('utf-8')
            patch_req = urllib.request.Request(patch_url, data=patch_data, method='PATCH', headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github+json',
                'Content-Type': 'application/json; charset=utf-8',
                'User-Agent': 'MT2Plus-Release'
            })
            with urllib.request.urlopen(patch_req) as resp:
                return json.loads(resp.read().decode('utf-8'))
        else:
            err_msg = e.read().decode('utf-8', errors='ignore')
            print(f"HTTPError {e.code}: {err_msg}")
            raise

def delete_existing_asset_if_exists(token, release_id, asset_name, expected_size=None):
    url = f"https://api.github.com/repos/ymirwork/MT2Plus/releases/{release_id}/assets"
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'MT2Plus-Release'
    })
    try:
        with urllib.request.urlopen(req) as resp:
            assets = json.loads(resp.read().decode('utf-8'))
            for a in assets:
                if a.get('name') == asset_name:
                    if expected_size and a.get('state') == 'uploaded' and a.get('size') == expected_size:
                        print(f"Asset {asset_name} is already completely uploaded ({a.get('size')} bytes), keeping.")
                        return False
                    del_url = f"https://api.github.com/repos/ymirwork/MT2Plus/releases/assets/{a['id']}"
                    del_req = urllib.request.Request(del_url, method='DELETE', headers={
                        'Authorization': f'Bearer {token}',
                        'Accept': 'application/vnd.github+json',
                        'User-Agent': 'MT2Plus-Release'
                    })
                    with urllib.request.urlopen(del_req) as del_resp:
                        print(f"Deleted old/incomplete asset {asset_name} (id {a['id']}, state: {a.get('state')})")
    except Exception as e:
        print(f"Notice on asset check: {e}")
    return True

class ProgressFileReader:
    def __init__(self, filepath, block_size=1024 * 1024):
        self.f = open(filepath, 'rb')
        self.total = os.path.getsize(filepath)
        self.read_so_far = 0
        self.block_size = block_size
        self.last_pct = -1

    def read(self, size=-1):
        n = self.block_size if (size is None or size < 0) else size
        chunk = self.f.read(n)
        if chunk:
            self.read_so_far += len(chunk)
            pct = int(self.read_so_far * 100 / self.total)
            if pct != self.last_pct and pct % 10 == 0:
                print(f"  {pct}% ({self.read_so_far // 1048576} MB / {self.total // 1048576} MB)")
                self.last_pct = pct
        return chunk

    def close(self):
        self.f.close()

def upload_asset(token, upload_url, file_path, name):
    base_upload_url = upload_url.split('{')[0]
    target_url = f"{base_upload_url}?name={name}"
    total_size = os.path.getsize(file_path)
    print(f"Uploading asset {name} ({total_size} bytes)...")

    # Try streaming upload with Python OpenSSL first
    try:
        reader = ProgressFileReader(file_path)
        req = urllib.request.Request(
            target_url,
            data=reader,
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'application/vnd.github+json',
                'Content-Type': 'application/zip',
                'Content-Length': str(total_size),
                'User-Agent': 'MT2Plus-Release'
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=1800) as resp:
            resp_data = json.loads(resp.read().decode('utf-8'))
            print(f"Uploaded successfully: {resp_data.get('name')} ({resp_data.get('size')} bytes)")
            reader.close()
            return resp_data
    except Exception as e:
        print(f"Python stream upload notice: {e}. Falling back to curl with --http1.1...")
        reader.close()

    cmd = [
        'curl.exe', '-S', '-s',
        '--http1.1',
        '--retry', '3',
        '--retry-delay', '5',
        '--keepalive-time', '30',
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
    
    srv_zip = os.path.join(dist_dir, 'metin2-server-update-2.39.0.zip')
    cli_zip = os.path.join(dist_dir, 'metin2-client-update-2.0.70.zip')

    if not os.path.exists(srv_zip) or not os.path.exists(cli_zip):
        print(f"ERROR: Missing release zip files in {dist_dir}")
        sys.exit(1)

    token = get_github_token()
    print("GitHub token acquired successfully.")

    tag = "v2.39.0-mod60"
    release_name = "MT2009 PLUS v2.39.0-mod60 - Serwer 2.39.0 & Klient 2.0.70"

    body = f"""# 📦 MT2Plus Wydanie v2.39.0-mod60

Oficjalne wydanie zintegrowanych paczek instalacyjnych i aktualizacyjnych **MT2009 PLUS** (Serwer 2.39.0, mod-60 oraz Klient 2.0.70) z pełnym zachowaniem autorskich rozszerzeń (YmirWork / Krystian).

---

### 🛡️ Sumy Kontrolne SHA-256 i Rozmiary Paczek

| Paczka | Nazwa Pliku | Rozmiar (bajty) | Suma kontrolna SHA-256 |
| :--- | :--- | :--- | :--- |
| **Serwer MT2Plus** | `metin2-server-update-2.39.0.zip` | `{srv_size:,} B` | `{srv_hash}` |
| **Klient MT2Plus** | `metin2-client-update-2.0.70.zip` | `{cli_size:,} B` | `{cli_hash}` |

---

### 🌟 Najważniejsze Zmiany i Autorskie Modyfikacje (MT2Plus):

1. **Baza Upstream v2.39.0 (mod-60, Klient 2.0.70):**
   - **Event Halloween:** NPC Jack Pumpkin, dynie, różdżki, maski dyniowe i latające miotły (`event_halloween_hair.quest`, dedykowany drop i paczka `halloween` w kliencie).
   - **Poprawka Kamieni Przywołania:** Metiny przywołane ze specjalnych kamieni znikają automatycznie po 15 minutach (`MT2009_PLUS_SUMMON_STONE_V1` w `char_item.cpp`).
   - **Playerbot Engine:** Nowe reguły doboru broni, zaktualizowane statystyki pancerzy botów i optymalizacje zachowań w walce.
   - **Klient 2.0.70:** Aktualizacja modeli, tekstur i interfejsów eventowych.

2. **Autorskie Rozszerzenia MT2Plus (Wszystkie 24 w pełni zachowane i aktywne):**
   - **Ceny Bazowe Botów:** Nowy moduł konfiguracji i dynamicznego przeliczania cen skupu/sprzedaży botów w panelu (`/economy/bot-prices`).
   - **Emerytura Botów V3:** Inteligentna i płynna rotacja emerytalna botów zapobiegająca zastojom na mapach.
   - **ItemShop Panel:** Dedykowany moduł zarządzania ofertami i sklepem w panelu administracyjnym.
   - **Brak Potionów w M2:** Usunięcie zbędnych mikstur z metinów i bossów na mapach drugich miast.
   - **Sklep Offline 160 Slotów:** Zachowano rozszerzoną strukturę `offlineshopmanage.py` i `offlineshopguest.py` z obsługą drewnianych kluczy (`item_unlock_slots`) oraz naprawioną obsługą `destPos`.
   - **Filtr GM w Agregacji Ekonomii:** Wykluczenie postaci i kont GM ze statystyk bogactwa i rynków (`item_not_gm_scope_sql`).
   - **Ukrywanie Paska Życia Mobów/Bossów:** Zachowano celowe ukrycie wartości liczbowej i procentowej HP potworów w `uitarget.py`.
   - **System Szarf:** Zachowano ukrywanie szarf w podglądzie kostiumów oraz dedykowany tooltip szansy na ulepszenie.
   - **Ekonomia & Przedmioty:** Stackowanie kluczowych przedmiotów do 200, pierścienie i amulety z czasem 30 dni czasu noszenia (`limittype0=9`), 92 oferty błyskawiczne w ItemShopie.
   - **Wstawanie 100% HP:** Pełne odrodzenie życia po śmierci postaci.

---

📥 **Instrukcja Uruchomienia (Ready-to-Play):**
1. Pobierz paczkę serwera `metin2-server-update-2.39.0.zip` oraz klienta `metin2-client-update-2.0.70.zip`.
2. Wypakuj serwer i uruchom `start.bat` (wymagany Docker Desktop).
3. Wypakuj klienta i uruchom grę przez `metin2client.exe` (lub zaktualizuj automatycznie przez `MT2009-Patcher.exe`).
"""

    print("Creating or updating release on GitHub...")
    rel = create_or_get_release(token, tag, release_name, body)
    rel_id = rel['id']
    upload_url = rel['upload_url']
    html_url = rel['html_url']
    print(f"Release {rel_id}: {html_url}")

    if delete_existing_asset_if_exists(token, rel_id, "metin2-server-update-2.39.0.zip", srv_size):
        upload_asset(token, upload_url, srv_zip, "metin2-server-update-2.39.0.zip")
    if delete_existing_asset_if_exists(token, rel_id, "metin2-client-update-2.0.70.zip", cli_size):
        upload_asset(token, upload_url, cli_zip, "metin2-client-update-2.0.70.zip")

    print(f"\nSUCCESS! Release updated at: {html_url}")
    return html_url

if __name__ == '__main__':
    if len(sys.argv) >= 5:
        publish_release(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), sys.argv[4])
    else:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        dist_dir = os.path.join(repo_root, 'dist')
        srv_zip = os.path.join(dist_dir, 'metin2-server-update-2.39.0.zip')
        cli_zip = os.path.join(dist_dir, 'metin2-client-update-2.0.70.zip')
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
