import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from colorama import Fore, Style, init
import json
import os
import subprocess
import sys

def load_language():
    if os.path.exists("Settings/lang_config.json"):
        try:
            with open("Settings/lang_config.json", "r", encoding="utf-8") as f:
                return json.load(f).get("lang", "fr")
        except Exception:
            return "fr"
    return "fr"

lang = load_language()

messages = {
    "fr": {
        "start": "Vérifie si un compte a un email...",
        "failed_retrieve": "[×] Échec de récupération des données pour l'utilisateur : {}",
        "no_user_data": "[×] Pas de données utilisateur trouvées pour : {}",
        "json_error": "[×] Erreur décodage JSON pour {} : {}",
        "processing_error": "[×] Erreur lors du traitement des données pour {} : {}",
        "email_found": "[+] Email(s) trouvé(s) dans la bio de @{} : {}",
        "email_not_found": "[-] Pas d'email dans la bio de @{}",
        "username_extract_fail": "Impossible d'extraire le nom d'utilisateur de {}",
        "profiles_saved": "\n{} profils avec email enregistrés dans {}",
        "next_script": "\nExécution du script suivant : Codes/second_script/tiktok_info.py\n",
        "missing_script": "\n[×] Script introuvable : {}",
        "file_cleaned": "Fichier nettoyé : {}",
        "input_missing": "[×] Fichier introuvable : {}"
    },
    "en": {
        "start": "Verify if an account has an email...",
        "failed_retrieve": "[×] Failed to retrieve data for username: {}",
        "no_user_data": "[×] No user data found for username: {}",
        "json_error": "[×] JSON decoding error for {}: {}",
        "processing_error": "[×] Error while processing data for {}: {}",
        "email_found": "[+] Email(s) found in bio of @{}: {}",
        "email_not_found": "[-] No email found in bio of @{}",
        "username_extract_fail": "Cannot extract username from {}",
        "profiles_saved": "\n{} profiles with email saved in {}",
        "next_script": "\nLaunching next script: Codes/second_script/tiktok_info.py\n",
        "missing_script": "\n[×] Script not found: {}",
        "file_cleaned": "File cleaned: {}",
        "input_missing": "[×] Missing file: {}"
    }
}

t = messages.get(lang, messages["fr"])

init(autoreset=True)

INPUT_FILE = "txt_files/tiktok_profiles.txt"
OUTPUT_FILE = "txt_files/profiles_with_email.txt"

email_pattern = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', re.IGNORECASE)

def format_number(value):
    try:
        value = float(value)
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}m"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}k"
        return str(int(value))
    except Exception:
        return str(value)

def get_info(username: str):
    headers = {
        "Host": "www.tiktok.com",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.0.0; Plume L2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
        "accept-language": "en-US,en;q=0.9,fr;q=0.8",
    }

    try:
        response = requests.get(f"https://www.tiktok.com/@{username}", headers=headers, timeout=10)
    except Exception as e:
        print(Fore.RED + t["failed_retrieve"].format(username))
        return None

    if response.status_code != 200:
        print(Fore.RED + t["failed_retrieve"].format(username))
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    try:
        state_tag = soup.find("script", id="SIGI_STATE")
        if state_tag and state_tag.string:
            try:
                state = json.loads(state_tag.string)
            except json.JSONDecodeError as e:
                print(Fore.RED + t["json_error"].format(username, e))
                state = None

            if state:
                um = state.get("UserModule", {})
                users = um.get("users") or um.get("user") or {}
                user_obj = users.get(username) or {}
                bio = user_obj.get("signature", "") or user_obj.get("bio", "")
                if bio is not None:
                    return {"username": username, "bio": bio}
    except Exception as e:
        pass

    try:
        m = re.search(r'"signature"\s*:\s*"([^"]*)"', response.text)
        if m:
            return {"username": username, "bio": m.group(1)}
    except Exception:
        pass

    print(Fore.BLUE + t["no_user_data"].format(username))
    return None

def extract_username_from_url(url: str):
    if "@" in url:
        return url.split("@")[-1].split("?")[0].strip("/")
    return None

def main():
    print(Fore.CYAN + t["start"])

    if not os.path.exists(INPUT_FILE):
        print(Fore.RED + t["input_missing"].format(INPUT_FILE))
        return

    try:
        if os.path.exists(OUTPUT_FILE):
            open(OUTPUT_FILE, "w", encoding="utf-8").close()
            print(Fore.YELLOW + t["file_cleaned"].format(OUTPUT_FILE))
    except Exception:
        pass

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        profile_urls = [line.strip() for line in f if line.strip()]

    matching_profiles = []
    for url in profile_urls:
        username = extract_username_from_url(url)
        if not username:
            print(Fore.YELLOW + t["username_extract_fail"].format(url))
            continue

        info = get_info(username)
        if not info:
            continue

        bio = info["bio"] if isinstance(info, dict) else ""
        emails_found = email_pattern.findall(bio or "")

        gmail_found = [mail for mail in emails_found if mail.lower().endswith("@gmail.com")]

        if gmail_found:
            emails_str = " ".join(sorted(set(gmail_found)))
            print(Fore.GREEN + t["email_found"].format(username, emails_str))
            matching_profiles.append(f"@{username} {emails_str}")
        else:
            print(Fore.RED + t["email_not_found"].format(username))

    try:
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            for line in matching_profiles:
                f.write(line + "\n")
        print(Fore.MAGENTA + t["profiles_saved"].format(len(matching_profiles), OUTPUT_FILE))
    except Exception as e:
        print(Fore.RED + t["processing_error"].format("write_output", e))

    script_path = os.path.join("Codes", "second_script", "tiktok_info.py")
    if os.path.exists(script_path):
        print(Fore.CYAN + t["next_script"])
        try:
            subprocess.run([sys.executable, script_path], check=False)
        except Exception as e:
            print(Fore.YELLOW + f"[!] Next script failed but continuing: {e}")
    else:
        print(Fore.RED + t["missing_script"].format(script_path))

if __name__ == "__main__":
    main()
