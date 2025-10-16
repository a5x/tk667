import os
import json
import requests

CONFIG_PATH = "Settings/telegram_config.json"
FICHIER_PATHS = [
    'Scripts_info_extract/profiles_with_email.txt',
    'Scripts_info_extract/info_accs.txt'
]

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_config(token, chat_id):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump({"token": token, "chat_id": chat_id}, f, indent=4)

def get_credentials():
    config = load_config()
    if not config.get("token") or not config.get("chat_id"):
        print("🔑 Configuration Telegram manquante.")
        token = input("👉 Entrez le TOKEN du bot : ").strip()
        chat_id = input("👉 Entrez l'ID du groupe (ex: -1001234567890) : ").strip()
        save_config(token, chat_id)
    else:
        token = config["token"]
        chat_id = config["chat_id"]
    return token, chat_id

def send_files(token, chat_id):
    url = f'https://api.telegram.org/bot{token}/sendDocument'
    for file_path in FICHIER_PATHS:
        if os.path.exists(file_path):
            print(f"📤 Envoi de {file_path}...")
            with open(file_path, 'rb') as file:
                response = requests.post(url, data={'chat_id': chat_id}, files={'document': file})
            print(f"✅ {file_path} envoyé (code {response.status_code})")
        else:
            print(f"❌ Fichier introuvable : {file_path}")

if __name__ == "__main__":
    token, chat_id = get_credentials()
    send_files(token, chat_id)
