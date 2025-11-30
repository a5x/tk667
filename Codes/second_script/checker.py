# Codes/Scripts/tiktok_info.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone
import os
import re
import sys
from colorama import init, Fore, Style

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

init(autoreset=True)

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def format_number(value):
    value = float(value)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}m"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return str(int(value))

def display_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = r"""

"""
    print(Fore.WHITE + ascii_art)
    sep = "=" * 150
    print(Fore.WHITE + sep)
    print(
        Fore.GREEN + "  s/O Le Z t.me/@enabIe "
    )
    print(Fore.WHITE + sep + "\n")

def _load_userinfo_from_soup(soup: BeautifulSoup) -> dict:
    data = None

    s = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")
    if s and s.string:
        try:
            data = json.loads(s.string)
        except Exception:
            data = None

    if data is None:
        for script in soup.find_all("script"):
            st = getattr(script, "string", None) or ""
            if "userInfo" in st:
                try:
                    data = json.loads(st)
                    break
                except Exception:
                    start = st.find("{")
                    end = st.rfind("}")
                    if start != -1 and end != -1:
                        try:
                            data = json.loads(st[start:end+1])
                            break
                        except Exception:
                            continue

    if not isinstance(data, dict):
        return {}

    candidate_paths = [
        lambda d: d.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {}).get("userInfo", {}),
        lambda d: d.get("props", {}).get("pageProps", {}).get("userInfo", {}),
        lambda d: d.get("app", {}).get("userInfo", {}),
    ]

    for getter in candidate_paths:
        ui = getter(data) or {}
        if isinstance(ui, dict) and "user" in ui:
            return ui

    if "userInfo" in data and isinstance(data["userInfo"], dict):
        return data["userInfo"]

    return {}

def normalize_username(username: str) -> str:
    """
    Permet d'accepter :
    - @username
    - username
    - https://www.tiktok.com/@username
    - https://tiktok.com/@username
    """
    username = username.strip()

    # URL complète → extrait après le @
    if username.startswith("http://") or username.startswith("https://"):
        if "@" in username:
            username = username.split("@")[-1]

    # Commence par @ → on retire
    if username.startswith("@"):
        username = username[1:]

    return username

def get_info(username):
    username = normalize_username(username)

    headers = {
        "Host": "www.tiktok.com",
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"99\", \"Google Chrome\";v=\"99\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.0.0; Plume L2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en;q=0.9"
    }

    url = f'https://www.tiktok.com/@{username}'

    try:
        response = requests.get(url, headers=headers, timeout=15)
    except Exception as e:
        print(Fore.RED + f"[x] Requête échouée : {username} ({e})")
        return None

    if response.status_code != 200:
        print(Fore.RED + f"[x] Echec pour : {username} (HTTP {response.status_code})")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    user_info = _load_userinfo_from_soup(soup)

    if not user_info:
        print(Fore.RED + f"[x] Pas de données pour : {username}")
        return None

    user = user_info.get('user', {}) if isinstance(user_info, dict) else {}

    region = (
        user.get('region')
        or user.get('regionCode')
        or user.get('country')
        or user.get('location')
        or (user.get('locale', '').split('_')[-1] if user.get('locale') else None)
        or "N/A"
    )

    try:
        create_time_unix = int(user.get('createTime', 0)) if user.get('createTime') else 0
    except Exception:
        create_time_unix = 0

    create_date = (
        datetime.fromtimestamp(create_time_unix, timezone.utc).strftime('%Y-%m-%d')
        if create_time_unix else 'N/A'
    )

    return {
        "region": region if region else "N/A",
        "create_date": create_date
    }

def extract_username_from_line(line):
    """
    Permet de détecter automatiquement :
    - username
    - @username
    - URL TikTok
    """
    line = line.strip()

    # URL → extrait username après @
    if line.startswith("http://") or line.startswith("https://"):
        if "@" in line:
            return line.split("@")[-1]

    # @username
    if line.startswith("@"):
        return line[1:]

    # username simple
    if " " not in line:
        return line

    # autres formats : recherche d'un token qui commence par @
    for token in line.split():
        if token.startswith('@') and len(token) > 1:
            return token[1:]

    return None

def strip_existing_date_country(parts):
    if len(parts) >= 2 and DATE_RE.match(parts[-2]):
        return parts[:-2]
    return parts

if __name__ == '__main__':
    display_banner()
    input_file = 'txt_files/usernames.txt'

    if not os.path.exists(input_file):
        print(Fore.RED + f"[x] Fichier introuvable : {input_file}")
        raise SystemExit(1)

    with open(input_file, 'r', encoding='utf-8') as f:
        original_lines = [ln.rstrip('\n') for ln in f if ln.strip()]

    updated_lines = []

    for line in original_lines:
        username = extract_username_from_line(line)
        if not username:
            print(Fore.YELLOW + f"[!] Ignoré (username introuvable) : {line}")
            updated_lines.append(line)
            continue

        print(Fore.WHITE + f"[->] Traitement de : @{username}")
        info = get_info(username)

        parts = line.split()
        parts = strip_existing_date_country(parts)

        if info:
            parts.extend([info.get("create_date", "N/A"), info.get("region", "N/A")])
        else:
            parts.extend(["N/A", "N/A"])

        updated_lines.append(" ".join(parts))

    with open(input_file, 'w', encoding='utf-8') as f:
        for ln in updated_lines:
            f.write(ln + "\n")

    print(Fore.GREEN + f"\n[OK] Lignes mises à jour dans {input_file}")
