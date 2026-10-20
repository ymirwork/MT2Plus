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

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dist_dir = os.path.join(repo_root, 'dist')
    
    srv_zip = os.path.join(dist_dir, 'metin2-server-update-2.36.0.zip')
    cli_zip = os.path.join(dist_dir, 'metin2-client-update-2.0.67.zip')

    if not os.path.exists(srv_zip) or not os.path.exists(cli_zip):
        print(f"ERROR: Missing release zip files in {dist_dir}")
        sys.exit(1)

    token = get_github_token()
    print("GitHub token acquired successfully.")

    tag = "v2.36.0-mod57"
    release_name = "MT2009 PLUS v2.36.0-mod57 - Serwer 2.36.0 & Klient 2.0.67"

    body = """# 📦 MT2Plus Wydanie v2.36.0-mod57

Oficjalne wydanie zintegrowanych paczek instalacyjnych i aktualizacyjnych **MT2009 PLUS** (Serwer 2.36.0, mod-57 oraz Klient 2.0.67) z pełnym zachowaniem autorskich rozszerzeń (YmirWork / Krystian).

---

### 🛡️ Autorskie Modyfikacje i Systemy MT2Plus
• **Optymalizacja Autołowów (Lochy Małp & Zabezpieczenie Ścian):** Wbudowany filtr osiągalności celów `CPlayerBotManager::IsHumanTargetReachable` (`playerbot_manager.cpp`, `playerbot_manager.h`), eliminujący wybieranie potworów za ścianami w odciętych komnatach.
• **Sklepy Offline 160 Slotów z Drewnianymi Kluczami:** Pełna obsługa 2-stronicowych magazynów i sklepów offline gracza (kompatybilność z drewnianymi kluczami `shop_unlock_slots.quest`, `ikarus_shop_manager.cpp` oraz `offlineshopmanage.py`).
• **Seban Panel – Rozszerzona Ekonomia V2 & Caching:** Zachowano zaawansowany moduł `/economy` (analiza rynku, transakcje, doradca rotacji emerytur botów, statystyki M1/M2 i cache wydajnościowy paneli).
• **Zarządzanie Czasem Amuletów i Stackowaniem:** 30-dniowe amulety i pierścienie z ItemShopu oraz stackowanie wybranych ulepszaczy i ksiąg do 200 sztuk (`apply.sh`).
• **Autorskie Zadania Gry:** Kompilacja `recykling_bonusow.quest`, `shop_unlock_slots.quest` oraz `tp_bookmarks.quest`.

---

### 🤖 Nowości i Usprawnienia Upstream (2.36.0 / mod-57)
• **Zabezpieczenie celów w lochach (Dungeon Target Respawn):** W 10 lochach (m.in. Wieża Demonów, Katakumby, Razador, Nemere, Wukong, Ruiny Skorpiona, Dżungla) utracony cel powraca samoczynnie – żaden etap lochu nie zamyka się przez zagubienie moba (`MT2009_PLUS_DUNGEON_TARGET_RESPAWN_V1`).
• **Sklepy Botów do 4 Stron (320 pól):** Boty mogą teraz zarządzać sklepami o pojemności do 4 stron (`MT2009_PLUS_BOT_SHOP_PAGES4_V1`), oferując większą płynność handlu.
• **Przenoszenie ksiąg między kanałami:** Boty z CH2 transportują cenne księgi na stragany na CH1 (`MT2009_PLUS_BOT_BOOK_STACKS_V1`).
• **Zarządzanie Kamieniami Duszy +4:** Zaawansowana logika rynku i osadzania kamieni dusz +4 u botów (`playerbot_stone4.h`, `AI_STONE4_KEYS`).
• **Biolog 70 lvl (Konar Zelkova):** Konar Zelkova (30165) stackuje się do 200 sztuk i dropi niezależnie od stanu ekwipunku (`collect_quest_lv70.quest`).
• **Retencja Logów Bazy Danych:** Seban Panel otrzymał narzędzie retencji logów oraz ochronę zapytań `db_block` (`log_maintenance.py`, `db_logs.html`).
• **Autołowy bez odwetu (No Revenge):** Natychmiastowe zatrzymanie flagi walki po wyłączeniu autołowów (`/autohunt_stop`).

---

### 💻 Klient Gry 2.0.67
• **Pełna obsługa 4-stronicowych sklepów botów:** Skalowanie siatki okna gościa w `offlineshopguest.py`.
• **Naprawa Smoczej Alchemii w Sklepach Offline:** Poprawka typu slotu myszy (`SLOT_TYPE_DRAGON_SOUL_INVENTORY`) w `offlineshopmanage.py`.
• **Zatrzymywanie Autołowów:** Wysłanie pakietu `/autohunt_stop` przy zatrzymaniu polowania w `uiautohunt.py`.
• **Zsynchronizowany Patcher Web CDN:** Aktualizacja sum MD5/SHA256 na GitHub Pages.

---

### 📦 Sumy kontrolne załączonych archiwów (SHA-256)
- **`metin2-server-update-2.36.0.zip`** (138 643 364 bytes)
  `SHA-256: C40A196E97C418C4E3B42C8312C809947E3BF5767C074E5BC03AE8103A331A6C`
- **`metin2-client-update-2.0.67.zip`** (620 662 105 bytes)
  `SHA-256: D1F3B99190B25714E0AA1F32074F22EE277037F2AB76B453FFFAD7E5A4A4D7D8`

---

📥 **Instrukcja Uruchomienia (Ready-to-Play):**
1. Pobierz paczkę serwera `metin2-server-update-2.36.0.zip` oraz klienta `metin2-client-update-2.0.67.zip`.
2. Wypakuj serwer i uruchom `start.bat` (wymagany Docker Desktop).
3. Wypakuj klienta i uruchom grę przez `metin2client.exe` (lub zaktualizuj automatycznie przez `MT2009-Patcher.exe`).
"""

    print("Creating release on GitHub...")
    rel = create_release(token, tag, release_name, body)
    rel_id = rel['id']
    upload_url = rel['upload_url']
    html_url = rel['html_url']
    print(f"Created release {rel_id}: {html_url}")

    upload_asset_curl(token, upload_url, srv_zip, "metin2-server-update-2.36.0.zip")
    upload_asset_curl(token, upload_url, cli_zip, "metin2-client-update-2.0.67.zip")

    print(f"\nSUCCESS! Release published at: {html_url}")

if __name__ == '__main__':
    main()
