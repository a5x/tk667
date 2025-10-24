import os
import sys
import json
import random
import time
import io
import zipfile
import shutil
import requests
from colorama import Fore, Style, init
from ascii_styles import ascii_styles

init(autoreset=True)

if os.name == 'nt':
    try:
        import ctypes
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        cols = min(240, screen_width // 8)
        lines = min(60, screen_height // 16)
        os.system(f'mode con: cols={cols} lines={lines}')
    except:
        pass

LOCAL_VERSION = "2.2"
GITHUB_OWNER  = "a5x"
GITHUB_REPO   = "tk667"
GITHUB_BRANCH = "main"

VERSION_URL = f"https://raw.githubusercontent.com/a5x/tk667/main/version.txt"

PRESERVE_PATHS = [
    "Settings/lang_config.json",
    "Settings/config.json",
    "Scripts_info_extract/",
]

def _parse_version(v: str):
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except Exception:
        return tuple(v.strip().split("."))

def _is_preserved(rel_path: str) -> bool:
    rel_path = rel_path.replace("\\", "/")
    for p in PRESERVE_PATHS:
        p = p.replace("\\", "/")
        if p.endswith("/"):
            if rel_path.startswith(p):
                return True
        else:
            if rel_path == p:
                return True
    return False


def _force_update_from_github():
    zip_url = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"
    print(Fore.CYAN + f"Téléchargement du ZIP depuis le github: {zip_url}" + Style.RESET_ALL)
    r = requests.get(zip_url, timeout=30)
    print(Fore.CYAN + f"HTTP {r.status_code}" + Style.RESET_ALL)
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        top = z.namelist()[0].split("/")[0]
        print(Fore.CYAN + f"Racine ZIP !: {top}" + Style.RESET_ALL)

        replaced, skipped = 0, 0
        for member in z.infolist():
            if member.is_dir():
                continue
            path_in_zip = member.filename
            if not path_in_zip.startswith(top + "/"):
                continue

            rel_path = path_in_zip[len(top) + 1:]
            if not rel_path or rel_path.endswith("/"):
                continue
            if _is_preserved(rel_path):
                skipped += 1
                continue

            target_path = os.path.join(os.getcwd(), rel_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with z.open(member, "r") as src, open(target_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
            replaced += 1

    print(Fore.GREEN + f"Fichiers remplacés : {replaced} ✅ | non modifiés: {skipped} ✅" + Style.RESET_ALL)
    print(Fore.GREEN + "Mise à jour installée ✅. Redémarrage..." + Style.RESET_ALL)
    time.sleep(0.5)
    os.execv(sys.executable, [sys.executable] + sys.argv)

def check_and_force_update():
    try:
        print(Fore.CYAN + f"Vérification de la version: {VERSION_URL}" + Style.RESET_ALL)
        resp = requests.get(VERSION_URL, timeout=8)
        print(Fore.CYAN + f"HTTP {resp.status_code}" + Style.RESET_ALL)

        if resp.status_code != 200:
            print(Fore.YELLOW + "Impossible de vérifier la version sur le github.\n" + Style.RESET_ALL)
            return

        latest = resp.text.strip()
        print(Fore.CYAN + f"Distante: {latest} | Locale: {LOCAL_VERSION}" + Style.RESET_ALL)

        if _parse_version(latest) > _parse_version(LOCAL_VERSION):
            msg1 = f" Nouvelle version détectée : {latest} "
            msg2 = f" Version actuelle : {LOCAL_VERSION} "
            msg3 = " Appuie sur Entrée pour télécharger et installer la mise à jour "
            bar_len = max(len(msg1), len(msg2), len(msg3)) + 4

            print(Fore.RED + "█" * bar_len)
            print(Fore.RED +"█ " + msg1.ljust(bar_len - 3) + "█")
            print(Fore.RED +"█ " + msg2.ljust(bar_len - 3) + "█")
            print(Fore.RED +"█ " + msg3.ljust(bar_len - 3) + "█")
            print(Fore.RED +"█" * bar_len + Style.RESET_ALL + "\n")

            input(Fore.YELLOW + "Appuie sur Entrée pour installer..." + Style.RESET_ALL)
            _force_update_from_github()
        else:
            print(Fore.GREEN + f"Version à jour ({LOCAL_VERSION}).\n" + Style.RESET_ALL)

    except Exception as e:
        print(Fore.YELLOW + f"Vérification de la mise à jour échouée : {e}\n" + Style.RESET_ALL)

translations = {
    "fr": {
        "menu_title": "========= New Release 2.1 =========",
        "option_1": "Démarrer le script de collecte d'@",
        "option_2": "Démarrer le script de vérification des bio",
        "option_3": "Lancer le script au complet",
        "option_4": "Tiktok hashtag scraper",
        "option_v": "Recupérer les comptes avec la certif",
        "option_i": "Tiktok Infos Finder",
        "option_t": "Comment utiliser le tool pour les nuls",
        "option_cc": "Nettoie les fichiers textes",
        "option_c": "Changer la langue du tool",
        "option_s": "Paramètres (nombre de scroll)",
        "option_l": "Changelogs",
        "option_q": "Fermer le Tool",
        "option_create": "Créer un scraper hashtag personnalisé",
        "panel_header": "Scraper TikTok par hashtag",
        "return_menu": "Retour au menu",
        "invalid": "Option invalide.",
        "scraper_prompt": ">> ",
        "choose": "Choisissez une option : ",
        "bye": "Au revoir !",
        "choose_submenu_option": "Choisissez une option (ou [b] pour revenir) : ",
        "submenu_1_title": "=============== Choissisez une option ===============",
        "submenu_2_title": "=============== Choissisez une option ===============",
        "submenu_3_title": "=========== Paramètres ==========="
    },
    "en": {
        "menu_title": "========= New Release 2.1 =========",
        "option_1": "Start script : (collect profiles)",
        "option_2": "Start script : (check about me for emails)",
        "option_3": "Start script : Run Compiled Scripts Collect + emails",
        "option_4": "Start script : TikTok hashtag scraper",
        "option_v": "Start script : Scrap Blue Badge accounts",
        "option_i": "Tiktok Infos Finder",
        "option_t": "How to use tools for noobie",
        "option_cc": "Clean save files",
        "option_c": "Change language",
        "option_s": "Settings (Scroll for scrapping)",
        "option_l": "Changelogs",
        "option_q": "Quit/Close",
        "option_create": "Create a custom hashtag scraper",
        "panel_header": "TikTok Hashtag Scraper",
        "return_menu": "Return to menu",
        "invalid": "Invalid option.",
        "scraper_prompt": ">> ",
        "choose": "Choose an option: ",
        "bye": "Goodbye !",
        "choose_submenu_option": "Choose an option (or [b] to go back): ",
        "submenu_1_title": "=========== Choose an option ===========",
        "submenu_2_title": "=========== Choose an option ===========",
        "submenu_3_title": "=========== Settings ==========="
    },
    "ru": {
        "menu_title": "========= New Release 2.1 =========",
        "option_1": "Запуск скрипта A (сбор имен пользователей)",
        "option_2": "Запуск скрипта B (проверка био на email)",
        "option_3": "Запустить Скрипт A, затем Скрипт B автоматически",
        "option_4": "TikTok скрапер по хэштегу",
        "option_v": "Скрап Blue Badge",
        "option_i": "Инфо (tiktok_info.py)",
        "option_t": "Обучение (как использовать инструмент)",
        "option_cc": "Очистить сохранённые файлы",
        "option_c": "Изменить язык",
        "option_s": "Настройки",
        "option_l": "Changelogs",
        "option_q": "Выход",
        "bye": "Bye",
        "option_create": "Создать пользовательский скрапер по хэштегу",
        "panel_header": "Скрапер TikTok по хэштегу",
        "return_menu": "Вернуться в меню",
        "invalid": "Неверная опция.",
        "scraper_prompt": ">> ",
        "choose_submenu_option": "Выберите опцию (или [b] для возврата): ",
        "submenu_1_title": "=========== Инструменты сбора данных ===========",
        "submenu_2_title": "=========== Вторые скрипты ===========",
        "submenu_3_title": "=========== Настройки ==========="
    }
}

def load_language():
    if os.path.exists("Settings/lang_config.json"):
        with open("Settings/lang_config.json", "r", encoding="utf-8") as f:
            return json.load(f).get("lang", "fr")
    return "fr"

def save_language(lang):
    with open("Settings/lang_config.json", "w", encoding="utf-8") as f:
        json.dump({"lang": lang}, f)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def horizontal_gradient_text(text):
    return ''.join(Fore.LIGHTGREEN_EX + char if char != ' ' else char for char in text) + Style.RESET_ALL

def print_banner():
    banner_lines = random.choice(list(ascii_styles.values()))
    for line in banner_lines:
        print(horizontal_gradient_text(line))

def menu():
    lang = load_language()
    t = translations[lang]
    clear_console()
    print_banner()
    margin = " " * 50
    print("\n" + margin + Fore.WHITE + Style.BRIGHT + t["menu_title"])
    print()
    print(margin + Fore.GREEN + "[1]" + Fore.RED + " Tools for Scraping")
    print(margin + Fore.GREEN + "[2]" + Fore.RED + " Tools for Tiktok")
    print(margin + Fore.YELLOW + "[3]" + Fore.RED + " Settings")
    print(margin + Fore.YELLOW + "[4]" + Fore.RED + " Soon Change Region")
    print(margin + Fore.RED + "[Q]" + Fore.RED + " " + t["option_q"])
    print()

def scraps_tools_menu():
    lang = load_language()
    t = translations[lang]
    clear_console()
    print_banner()
    margin = " " * 50
    print("\n" + margin + Fore.CYAN + Style.BRIGHT + t["submenu_1_title"] + Style.RESET_ALL)
    print(margin + Fore.GREEN + "[1]" + Fore.RED + f" {t['option_1']}")
    print(margin + Fore.GREEN + "[2]" + Fore.RED + f" {t['option_2']}")
    print(margin + Fore.GREEN + "[3]" + Fore.RED + f" {t['option_3']}")
    print(margin + Fore.GREEN + "[4]" + Fore.RED + f" {t['option_4']}")
    print(margin + Fore.GREEN + "[5]" + Fore.RED + " Start script : (Collect Profiles + emails + acc's info's)")
    print(margin + Fore.GREEN + "[v]" + Fore.RED + f" {t['option_v']}")
    print(margin + Fore.YELLOW + "[b]" + Fore.RED + f" {t['return_menu']}")
    print()

def second_scripts_menu():
    lang = load_language()
    t = translations[lang]
    clear_console()
    print_banner()
    margin = " " * 50
    print("\n" + margin + Fore.CYAN + Style.BRIGHT + t["submenu_2_title"] + Style.RESET_ALL)
    print(margin + Fore.MAGENTA + "[t]" + Fore.RED + f" {t['option_t']}")
    print(margin + Fore.MAGENTA + "[tl]" + Fore.RED + " Send file to telegram chat")
    print(margin + Fore.MAGENTA + "[r]" + Fore.RED + " Infinite Report @")
    print(margin + Fore.MAGENTA + "[cc]" + Fore.RED + f" {t['option_cc']}")
    print(margin + Fore.MAGENTA + "[ck]" + Fore.RED + " Convert Cookies")
    print(margin + Fore.YELLOW + "[b]" + Fore.RED + f" {t['return_menu']}")
    print()

def settings_menu():
    lang = load_language()
    t = translations[lang]
    clear_console()
    print_banner()
    margin = " " * 50
    print("\n" + margin + Fore.CYAN + Style.BRIGHT + t["submenu_3_title"] + Style.RESET_ALL)
    print(margin + Fore.YELLOW + "[S]" + Fore.RED + f" {t['option_s']}")
    print(margin + Fore.YELLOW + "[C]" + Fore.RED + f" {t['option_c']}")
    print(margin + Fore.BLUE + "[L]" + Fore.RED + f" {t['option_l']}")
    print(margin + Fore.RED + "[Q]" + Fore.RED + f" {t['option_q']}")
    print(margin + Fore.GREEN + "[T]" + Fore.RED + f" {t['option_t']}")
    print(margin + Fore.YELLOW + "[b]" + Fore.RED + f" {t['return_menu']}")
    print()

def run_script(script_name):
    print(Fore.YELLOW + f"Lancement de {script_name}...\n" + Style.RESET_ALL)
    exit_code = os.system(f"{sys.executable} {script_name}")
    if exit_code != 0:
        print(Fore.RED + f"Erreur lors de l'exécution de {script_name} (code {exit_code})" + Style.RESET_ALL)

def run_scripts_automatic():
    run_script("Scripts/a.py")
    run_script("Scripts/b.py")

def choose_language():
    clear_console()
    print("🌐 Choisissez une langue / Choose a language / Выберите язык:\n")
    print("[1] Français")
    print("[2] English")
    print("[3] Русский")
    choice = input("\n>> ").strip()
    if choice == '1':
        save_language("fr")
    elif choice == '2':
        save_language("en")
    elif choice == '3':
        save_language("ru")
    else:
        print("Choix invalide.")
        input("\nAppuyez sur Entrée pour revenir au menu...")
        return
    input("\nAppuyez sur Entrée pour revenir au menu...")

def settings():
    CONFIG_FILE = "Settings/config.json"
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                config = json.load(f)
            except:
                pass
    scrolls = config.get("scrolls", 10)
    print(f"Nombre actuel de scrolls pour a.py : {scrolls}")
    try:
        new_scrolls = int(input("Entrez le nouveau nombre de scrolls (entier > 0) : "))
        if new_scrolls > 0:
            config["scrolls"] = new_scrolls
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
            print("Paramètre sauvegardé.")
        else:
            print("Nombre invalide, aucune modification effectuée.")
    except ValueError:
        print("Entrée invalide, aucune modification effectuée.")
    input("Appuyez sur Entrée pour revenir au menu...")

def tuto():
    clear_console()
    print_banner()
    print(Fore.CYAN + "=== Tuto Tiktok Scrapper + checker ===" + Style.RESET_ALL)
    print("""
Ce script se compose de deux parties principales :

1/ Script 1 (collecte usernames)
   - Accède à la page TikTok Explore avec Selenium.
   - Fait défiler la page plusieurs fois pour extraire des liens de profils TikTok.
   - Enregistre les liens dans le fichier : tiktok_profiles.txt

2// Script 2 (filtrage emails)
   - Récupère les liens dans tiktok_profiles.txt
   - Ouvre chaque profil TikTok.
   - Cherche des adresses email dans la bio.
   - Enregistre les résultats dans : profiles_with_email.txt

3// Script 3 (complet)
   - Lance les deux script en un pour faire une vérification complète

4// Script 4 (Scrap #)
   - Permet de scrap des bio depuis des # spécifique comme ex : #foryou etc

5// Script 5 (Scrap Blue Badge) 
   - Permet de récupèrer les utilisateurs possèdant le badge de certification

6// Script (Tiktok info)
   - Récupère le fichier profiles_with_email.txt et ouvre le fichier
   - Vérifie le fichier et donne les informations publique de l'api tiktok de tout les @ présent dans le fichier et les renvoie dans info_accs.txt

7// Script Nettoyage
   - Permet simplement de clean les fichier txt

8// Paramètres
   - changer la langue du tool
   - modifier le nombre de scroll sur les pages
   - Changelog ici les mises a jours du tool son noté
""")
    input(Fore.YELLOW + "\nAppuyez sur Entrée pour revenir au menu..." + Style.RESET_ALL)

def changelog():
    clear_console()
    print_banner()
    print(Fore.CYAN + "========================== Changelogs ==========================".center(140) + Style.RESET_ALL)
    changelog_lines = [
        "",
        "Changelogs :",
        "2.1 : Ajout d'un new script qui permet de choisir le nombre de compte voulu par exemple si vous mettez 154 il recupera 154 comptes et passe a l'étape suivante"
        "2.0 : Corrections des fautes, améliorations de la vitesse pour signaler un @, amélioration de la vitesse pour recupérer les bio Changement de textes pour les titres pour etre plus clair sur la fonction,"
        " modification du script 3 qui permet de faire marcher le 1 et 2 en meme temps plus besoin d'appuyer sur entrer pour commener la seconde étape",
        "1.9 : Ajout de Telegram file sender",
        "1.8 : Ajout de [cc] pour clean les fichiers, ajout de [v] permet de scrap les comptes certif, et modification du système de sauvegarde des fichiers les anciennes lignes ne sont plus supprimé",
        "1.7 : Ajout du script permettant la création de scraper hashtag custom",
        "1.6 : Ajout du script scraper hashtag",
        "1.5 : Scripts rework, Dynamic UI ASCII",
        "1.4 : UI Update, Files directory Update",
        "1.3 : Ajout du script complet + TikTok info",
        "1.2 : Choix de la langue",
        "1.1 : Ajout des paramètres",
        "1.0 : Version initiale"
    ]
    for line in changelog_lines:
        print(line.center(140))
    input(Fore.YELLOW + "\nAppuyez sur Entrée pour revenir au menu...".center(100) + Style.RESET_ALL)

def launch_foryou_panel():
    clear_console()
    print_banner()
    lang = load_language()
    t = translations[lang]

    header = f"========== {t['panel_header']} =========="
    print(Fore.CYAN + header.center(140) + Style.RESET_ALL)
    print()

    options = [
        "[1] #fyp",
        "[2] #trend",
        "[3] #foryou",
        "[4] #famous",
        "[5] #love",
        "[6] #mood",
        "[7] #pourtoi",
        f"[create] {t['option_create']}",
        f"[Q] {t['return_menu']}"
    ]

    longest = max(len(line) for line in options)
    margin = (140 - longest) // 2

    for line in options:
        print(" " * margin + line)

    print()
    choice = input(t["scraper_prompt"].rjust(70)).strip().lower()

    scripts = {
        '1': "Scripts/fyp.py",
        '2': "Scripts/trend.py",
        '3': "Scripts/foryou.py",
        '4': "Scripts/famous.py",
        '5': "Scripts/love.py",
        '6': "Scripts/mood.py",
        '7': "Scripts/pourtoi.py",
        'create': "Scripts/createscraper.py"
    }

    if choice in scripts:
        run_script(scripts[choice])
    elif choice == 'q':
        return
    else:
        print(t.get("invalid_option", t.get("invalid", "Option invalide.")).center(140))
        input(f"{t['return_menu']}...".center(140))

def main():
    check_and_force_update()

    while True:
        lang = load_language()
        t = translations[lang]
        menu()
        choice = input(t["choose"]).strip().lower()
        if choice == '1':
            while True:
                scraps_tools_menu()
                c = input(translations[lang]["choose_submenu_option"]).strip().lower()
                if c == '1':
                    run_script("Scripts/a.py")
                elif c == '2':
                    run_script("Scripts/b.py")
                elif c == '3':
                    run_scripts_automatic()
                elif c == '4':
                    launch_foryou_panel()
                elif c == '5':
                    run_script("Scripts/c.py")
                elif c == 'v':
                    run_script("Scripts/check_verified.py")
                elif c == 'b':
                    break
                else:
                    print(Fore.RED + t["invalid"] + Style.RESET_ALL)
                    input("Appuyez sur Entrée pour continuer...")
        elif choice == '2':
            while True:
                second_scripts_menu()
                c = input(translations[lang]["choose_submenu_option"]).strip().lower()
                if c == 't':
                    tuto()
                elif c == 'tl':
                    run_script("second_script/telegram_sender.py")
                elif c == 'r':
                    run_script("second_script/tiktok_info.py")
                elif c == 'cc':
                    run_script("second_script/cleaner.py")
                elif c == 'ck':
                    run_script("second_script/cc.py")
                elif c == 'b':
                    break
                else:
                    print(Fore.RED + t["invalid"] + Style.RESET_ALL)
                    input("Appuyez sur Entrée pour continuer...")
        elif choice == '3':
            while True:
                settings_menu()
                c = input(translations[lang]["choose_submenu_option"]).strip().lower()
                if c == 's':
                    settings()
                elif c == 'c':
                    choose_language()
                elif c == 'l':
                    changelog()
                elif c == 'q':
                    print(Fore.MAGENTA + t["bye"] + Style.RESET_ALL)
                    sys.exit(0)
                elif c == 't':
                    tuto()
                elif c == 'b':
                    break
                else:
                    print(Fore.RED + t["invalid"] + Style.RESET_ALL)
                    input("Appuyez sur Entrée pour continuer...")
        elif choice == 'q':
            print(Fore.MAGENTA + t["bye"] + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + t["invalid"] + Style.RESET_ALL)
            input("Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()

