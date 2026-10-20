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

    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        return res

def upload_asset(token, upload_url, file_path, name):
    base_upload_url = upload_url.split('{')[0]
    target_url = f"{base_upload_url}?name={name}"
    print(f"Uploading asset {name} ({os.path.getsize(file_path)} bytes)...")
    
    file_size = os.path.getsize(file_path)
    with open(file_path, 'rb') as f:
        file_data = f.read()

    req = urllib.request.Request(target_url, data=file_data, method='POST')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/vnd.github+json')
    req.add_header('Content-Type', 'application/zip')
    req.add_header('User-Agent', 'MT2Plus-Release')

    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print(f"Uploaded successfully: {res['name']} ({res['size']} bytes)")
        return res

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dist_dir = os.path.join(repo_root, 'dist')
    
    srv_zip = os.path.join(dist_dir, 'metin2-server-update-2.35.0.zip')
    cli_zip = os.path.join(dist_dir, 'metin2-client-update-2.0.66.zip')

    if not os.path.exists(srv_zip) or not os.path.exists(cli_zip):
        print(f"ERROR: Missing release zip files in {dist_dir}")
        sys.exit(1)

    token = get_github_token()
    print("GitHub token acquired successfully.")

    tag = "v2.35.0-mod56"
    release_name = "MT2009 PLUS v2.35.0-mod56 - Serwer 2.35.0 & Klient 2.0.66"

    body = """# 📦 MT2Plus Wydanie v2.35.0-mod56

Oficjalne wydanie zintegrowanych paczek instalacyjnych i aktualizacyjnych **MT2009 PLUS** (Serwer 2.35.0, mod-56 oraz Klient 2.0.66).

---

### 🎮 Autorskie Systemy Rozgrywki MT2Plus (Dev Gameplay V1)
• **Czytanie KU bez wymogu EXPa:** Zniesiono blokadę czytania Ksiąg Umiejętności przy braku punktów doświadczenia w `char_skill.cpp`.
• **Zdjęcie limiterów Movement Speed & Attack Speed:** Usunięto sztuczne ograniczenia prędkości poruszania się i ataku, odblokowano limit obrażeń (damage cap) oraz usunięto rozłączanie i cofki gracza przez antyhack.
• **Błyskawiczne ulepszanie u Kowala:** Całkowicie wyeliminowano 1-sekundowy komunikat "Odczekaj przed następnym ulepszaniem", co pozwala na natychmiastowe i płynne potwierdzanie ulepszania enterem.
• **Zapisywanie Lochów w Zwoju Powrotu:** Odblokowano możliwość zapisu i teleportacji do Lochów Pająków (V1/V2/V3), Lochów Małp oraz Groty Wygnańców przy posiadaniu statusu VIP lub odpowiedniej Przepustki; naprawiono również zapis ze zwojów czystych.
• **Wprowadzanie kwot Yang ze skrótami (k, kk, kkk):** W oknach wprowadzania waluty (handel, tobołek, wyrzucanie) wpisanie np. `1kk` automatycznie uzupełnia wartość `1.000.000`.
• **Bonus PvP za znajomość języków obcych:** Atakując gracza z wrogiego królestwa, zadajemy o 5% wyższe obrażenia, jeśli posiadamy język danej nacji rozwinięty na poziomie minimum M1.

### 🤖 Ekonomia i Porządek u Botów (Upstream 2.35.0)
• **Wartościowy sprzęt na straganach:** Boty wystawiają wyłącznie broń i zbroje z minimum 2 bonusami (lub 1 topowym); słabszy sprzęt sprzedają u Handlarki lub Alchemika.
• **Magiczny Pył & Kamienie Duszy:** Boty niszczą nadmiarowe Kamienie Duszy +0..+2 u Alchemika (limit 3 szt. każdego rodzaju w tobołku) i wytwarzają z pyłu Zaczarowania/Wzmocnienia wyłącznie na własne uzbrojenie.
• **Optymalizacja ziół:** Boty trzymają w plecakach tylko zioła potrzebne na 2-3 warki, a nadwyżki wystawiają w pełnych stosach po 200 sztuk lub odkładają do Dozorcy.
• **Automatyczne pieczęcie w lochach:** W lochach Wzgórza Wukonga, Ruin Skorpiona, Starożytnej Dżungli i Biblioteki Wiedzy pieczęć bota aktywuje się samoczynnie po ok. 30 s.

### 💻 Klient Gry 2.0.66
• **Błyskawiczna synchronizacja Filtru Podnoszenia:** Reguły filtra docierają do serwera natychmiast po wejściu do gry i zmianie kanału.
• **Poprawka okna wydarzeń:** Wyeliminowano błąd rekurencji i zawieszania gry przy wielu równoczesnych eventach.
• **Ready-to-Play:** Gotowy, odchudzony klient ze zintegrowanymi skryptami UI i zaktualizowanym `pack/root`.

---

### 📦 Sumy kontrolne załączonych archiwów (SHA-256)
- **`metin2-server-update-2.35.0.zip`** (137 649 387 bytes)
  `SHA-256: B4B30A5BBD01699D47E189C05221455EFFF0C1E856808994A65B2C8A0943ADF8`
- **`metin2-client-update-2.0.66.zip`** (620 499 956 bytes)
  `SHA-256: 48DD3CDA1612ECECE86B377C54DAAA475964F207DDA683E5D17421D943203524`

---

📥 **Instrukcja Uruchomienia (Ready-to-Play):**
1. Pobierz paczkę serwera `metin2-server-update-2.35.0.zip` oraz klienta `metin2-client-update-2.0.66.zip`.
2. Wypakuj serwer i uruchom `start.bat` (wymagany Docker Desktop).
3. Wypakuj klienta i uruchom grę przez `metin2client.exe`.
"""

    print("Creating release on GitHub...")
    rel = create_release(token, tag, release_name, body)
    rel_id = rel['id']
    upload_url = rel['upload_url']
    html_url = rel['html_url']
    print(f"Created release {rel_id}: {html_url}")

    upload_asset(token, upload_url, srv_zip, "metin2-server-update-2.35.0.zip")
    upload_asset(token, upload_url, cli_zip, "metin2-client-update-2.0.66.zip")

    print(f"\nSUCCESS! Release published at: {html_url}")

if __name__ == '__main__':
    main()
