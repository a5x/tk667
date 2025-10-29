import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from colorama import Fore, Style, init
import json
import os
import subprocess
import sys
import re


def load_language():
    if os.path.exists("Settings/lang_config.json"):
        with open("Settings/lang_config.json", "r", encoding="utf-8") as f:
            return json.load(f).get("lang", "fr")
    return "fr"

lang = load_language()

messages = {
    "fr": {
        "start": "Virifie si un compte a un email...",
        "failed_retrieve": "[×] Échec de récupération des données pour l'utilisateur : {}",
        "no_user_data": "[×] Pas de données utilisateur trouvées pour : {}",
        "json_error": "[×] Erreur décodage JSON pour {} : {}",
        "processing_error": "[×] Erreur lors du traitement des données pour {} : {}",
        "email_found": "[+] Email(s) trouvé(s) dans la bio de @{} : {}",
        "email_not_found": "[-] Pas d'email dans la bio de @{}",
        "username_extract_fail": "Impossible d'extraire le nom d'utilisateur de {}",
        "profiles_saved": "\n{} profils avec email enregistrés dans {}",
        "next_script": "\n Exécution du script suivant : Codes/Scripts/tiktok_info.py\n",
        "missing_script": "\n[×] Script introuvable : {}",
        "file_cleaned": "Fichier nettoyé : {}"
    },
    "en": {
        "start": "Verify if an account have an email...",
        "failed_retrieve": "[×] Failed to retrieve data for username: {}",
        "no_user_data": "[×] No user data found for username: {}",
        "json_error": "[×] JSON decoding error for {}: {}",
        "processing_error": "[×] Error while processing data for {}: {}",
        "email_found": "[+] Email(s) found in bio of @{}: {}",
        "email_not_found": "[-] No email found in bio of @{}",
        "username_extract_fail": "Cannot extract username from {}",
        "profiles_saved": "\n{} profiles with email saved in {}",
        "next_script": "\n Launching next script: Codes/Scripts/tiktok_info.py\n",
        "missing_script": "\n[×] Script not found: {}",
        "file_cleaned": " File cleaned : {}"
    }
}

t = messages.get(lang, messages["fr"])

init(autoreset=True)

INPUT_FILE = "txt_files/tiktok_profiles.txt"
OUTPUT_FILE = "txt_files/profiles_with_email.txt"


email_pattern = re.compile(r'[\w\.-]+@(?:gmail\.com|hotmail\.com)', re.IGNORECASE)


def format_number(value):
    value = float(value)
    if value >= 1000000:
        return f"{value / 1000000:.1f}m"
    elif value >= 1000:
        return f"{value / 1000:.1f}k"
    return str(int(value))


def get_info(username):
    headers = {
        "Host": "www.tiktok.com",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.0.0; Plume L2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
    }

    response = requests.get(f'https://www.tiktok.com/@{username}', headers=headers)
    if response.status_code != 200:
        print(Fore.RED + t["failed_retrieve"].format(username))
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    user_data_script = None
    for script in soup.find_all('script'):
        if 'userInfo' in script.text:
            user_data_script = script.string
            break

    if not user_data_script:
        print(Fore.BLUE + t["no_user_data"].format(username))
        return None

    try:
        user_data_json = json.loads(user_data_script)
        user_info = user_data_json.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {}).get('userInfo', {})
        user = user_info.get('user', {})

        return {
            "username": username,
            "bio": user.get('signature', 'N/A')
        }

    except json.JSONDecodeError as e:
        print(Fore.RED + t["json_error"].format(username, e))
        return None
    except Exception as e:
        print(Fore.RED + t["processing_error"].format(username, e))
        return None


def extract_username_from_url(url):
    if '@' in url:
        return url.split('@')[-1].split('?')[0].strip('/')
    return None


def main():
    print(Fore.CYAN + t["start"])

    if os.path.exists(OUTPUT_FILE):
        open(OUTPUT_FILE, "w", encoding="utf-8").close()
        print(Fore.YELLOW + t["file_cleaned"].format(OUTPUT_FILE))


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

        bio = info["bio"]
        emails_found = email_pattern.findall(bio)
        if emails_found:
            emails_str = ' '.join(set(emails_found))
            print(Fore.GREEN + t["email_found"].format(username, emails_str))
            matching_profiles.append(f"@{username} {emails_str}")
        else:
            print(Fore.RED + t["email_not_found"].format(username))

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for line in matching_profiles:
            f.write(line + "\n")

    print(Fore.MAGENTA + t["profiles_saved"].format(len(matching_profiles), OUTPUT_FILE))


    script_path = os.path.join("Codes/second_script", "tiktok_info.py")
    if os.path.exists(script_path):
        print(Fore.CYAN + t["next_script"])
        subprocess.run([sys.executable, script_path], check=True)
    else:
        print(Fore.RED + t["missing_script"].format(script_path))


if __name__ == "__main__":
    main()
