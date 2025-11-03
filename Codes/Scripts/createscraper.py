
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox

def load_language():
    try:
        with open("Settings/lang_config.json", "r", encoding="utf-8") as f:
            return json.load(f).get("lang", "fr")
    except Exception:
        return "fr"

lang = load_language()
T = {
    "fr": {
        "title": "Créer un scraper hashtag",
        "lbl_hashtag": "Hashtag (sans #) :",
        "lbl_filename": "Nom du fichier (sans .py) :",
        "btn_cancel": "Annuler",
        "btn_create": "Créer",
        "err_required": "Hashtag et nom de fichier requis.",
        "err_badfile": "Nom de fichier invalide.",
        "ok_created": "OK Script généré : {}",
        "btn_overwrite": "Le fichier existe. Écraser ?",
        "err_write": "Erreur d’écriture : {}",
    },
    "en": {
        "title": "Create hashtag scraper",
        "lbl_hashtag": "Hashtag (without #):",
        "lbl_filename": "File name (without .py):",
        "btn_cancel": "Cancel",
        "btn_create": "Create",
        "err_required": "Hashtag and file name are required.",
        "err_badfile": "Invalid file name.",
        "ok_created": "OK Script generated: {}",
        "btn_overwrite": "File already exists. Overwrite?",
        "err_write": "Write error: {}",
    },
    "ru": {
        "title": "Создать скрапер хэштега",
        "lbl_hashtag": "Хэштег (без #):",
        "lbl_filename": "Имя файла (без .py):",
        "btn_cancel": "Отмена",
        "btn_create": "Создать",
        "err_required": "Требуются хэштег и имя файла.",
        "err_badfile": "Недопустимое имя файла.",
        "ok_created": "OK Скрипт создан: {}",
        "btn_overwrite": "Файл существует. Перезаписать?",
        "err_write": "Ошибка записи: {}",
    },
}.get(lang, {})

def make_template(url: str) -> str:
    return f'''from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

def load_language():
    if os.path.exists("Settings/lang_config.json"):
        with open("Settings/lang_config.json", "r", encoding="utf-8") as f:
            return json.load(f).get("lang", "fr")
    return "fr"

lang = load_language()
t = {{
    "fr": {{
        "start": "Début de la collecte des profils...",
        "collected": "Collecté :",
        "error": "Erreur récupération liens :",
        "done": "Total liens collectés :",
        "scroll_end": "Fin du scroll atteinte.",
        "cookies": "OK Cookies acceptés",
        "login_clicked": "OK Bouton loginContainer cliqué.",
        "scroll_try": "OK Scroll #",
        "scroll_blocked": "! Scroll bloqué ({{}} fois)"
    }},
    "en": {{
        "start": "Starting profile collection...",
        "collected": "Collected:",
        "error": "Error retrieving links:",
        "done": "Total collected links:",
        "scroll_end": "End of scroll reached.",
        "cookies": "OK Cookies accepted",
        "login_clicked": "OK loginContainer button clicked.",
        "scroll_try": "OK Scroll #",
        "scroll_blocked": "! Scroll blocked ({{}} times)"
    }},
    "ru": {{
        "start": "Начало сбора профилей...",
        "collected": "Собрано:",
        "error": "Ошибка при получении ссылок:",
        "done": "Всего собрано ссылок:",
        "scroll_end": "Достигнут конец прокрутки.",
        "cookies": "OK Файлы cookie приняты",
        "login_clicked": "OK Кнопка loginContainer нажата.",
        "scroll_try": "OK Прокрутка #",
        "scroll_blocked": "! Прокрутка заблокирована ({{}} раз)"
    }}
}}[lang]

print(t["start"])

URL = "{url}"
SCROLL_PAUSE_TIME = 2
OUTPUT_FILE = "txt_files/tiktok_profiles.txt"
CONFIG_FILE = "Settings/config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {{}}
    return {{}}

config = load_config()
SCROLL_LIMIT = config.get("scrolls", 10)

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
driver.get(URL)

WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
time.sleep(1)

try:
    WebDriverWait(driver, 5).until(lambda d: d.execute_script(\"""
        const banner = document.querySelector('tiktok-cookie-banner');
        if (!banner || !banner.shadowRoot) return false;
        const btn = banner.shadowRoot.querySelector('button:nth-of-type(2)');
        if (!btn) return false;
        btn.click();
        return true;
    \"""))
    print(t["cookies"])
    time.sleep(1)
except Exception as e:
    print(f" Cookies non cliqués : {{e}}")

# petit déverrouillage UI côté droite (si présent)
for i in range(30):
    try:
        WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="main-content-homepage_hot"]/aside/div/div[2]/button'))
        ).click()
        time.sleep(0.5)
    except Exception:
        break

collected_links = set()
last_height = driver.execute_script("return document.body.scrollHeight")
login_clicked = False
blocked_scroll_count = 0

for scroll in range(SCROLL_LIMIT):
    print(f"{{t['scroll_try']}}{{scroll + 1}}")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)

    if not login_clicked:
        try:
            login_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="loginContainer"]/div/div/div[3]/div/button[1]'))
            )
            login_button.click()
            login_clicked = True
            print(t["login_clicked"])
            time.sleep(2)
            WebDriverWait(driver, 10).until_not(EC.presence_of_element_located((By.ID, "loginContainer")))
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="main-content-homepage_hot"]/aside/div/div[2]/button')))
            time.sleep(1)
            continue
        except Exception:
            pass

    try:
        elements = driver.find_elements(By.XPATH, '//*[@id="main-content-challenge"]//a[contains(@href, "@")]')
        for el in elements:
            href = el.get_attribute("href")
            if href and "/video/" not in href:
                href = href.split("?")[0]
                if href not in collected_links:
                    collected_links.add(href)
                    print(f"{{t['collected']}} {{href}}")
    except Exception as e:
        print(f"{{t['error']}} {{e}}")

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        blocked_scroll_count += 1
        print(t["scroll_blocked"].format(blocked_scroll_count))
        if blocked_scroll_count >= 3:
            print(t["scroll_end"])
            break
    else:
        blocked_scroll_count = 0
    last_height = new_height

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for link in collected_links:
        f.write(link + "\\n")

print(f"{{t['done']}} {{len(collected_links)}}")
driver.quit()
'''

def main():
    root = tk.Tk()
    root.withdraw()

    win = tk.Toplevel(root)
    win.title(T.get("title", "Créer un scraper hashtag"))
    win.geometry("400x220")
    win.resizable(False, False)
    win.grab_set()
    win.attributes("-topmost", True)

    container = ttk.Frame(win)
    container.pack(fill="both", expand=True)
    canvas = tk.Canvas(container, borderwidth=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)
    scroll_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    hashtag_var = tk.StringVar()
    file_var = tk.StringVar()

    ttk.Label(scroll_frame, text=T.get("lbl_hashtag")).pack(anchor="w", pady=(10, 4), padx=12)
    ttk.Entry(scroll_frame, textvariable=hashtag_var, width=36).pack(padx=12, fill="x")

    ttk.Label(scroll_frame, text=T.get("lbl_filename")).pack(anchor="w", pady=(12, 4), padx=12)
    ttk.Entry(scroll_frame, textvariable=file_var, width=36).pack(padx=12, fill="x")

    btns = ttk.Frame(scroll_frame)
    btns.pack(anchor="e", pady=16, padx=12)

    def cancel():
        win.destroy()
        root.destroy()

    def valid_filename(name: str) -> bool:
        bad = set('\\/:*?"<>|')
        return bool(name) and not any(ch in bad for ch in name)

    def create():
        hashtag = hashtag_var.get().strip().lstrip("#").lower()
        filename = file_var.get().strip().lower()

        if not hashtag or not filename:
            messagebox.showerror("Error", T.get("err_required"))
            return
        if not valid_filename(filename):
            messagebox.showerror("Error", T.get("err_badfile"))
            return

        url = f"https://www.tiktok.com/tag/{hashtag}"
        os.makedirs("Codes/Scripts/hashtag/", exist_ok=True)
        output_path = os.path.join("Codes", "Scripts", "hashtag", f"{filename}.py")

        if os.path.exists(output_path):
            if not messagebox.askyesno("Overwrite", T.get("btn_overwrite")):
                return

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(make_template(url))
        except Exception as e:
            messagebox.showerror("Error", T.get("err_write").format(e))
            print(T.get("err_write").format(e))
            return

        messagebox.showinfo("OK", T.get("ok_created").format(output_path))
        print(T.get("ok_created").format(output_path))
        win.destroy()
        root.destroy()

    ttk.Button(btns, text=T.get("btn_cancel"), command=cancel).pack(side="right", padx=6)
    ttk.Button(btns, text=T.get("btn_create"), command=create).pack(side="right")

    root.mainloop()

if __name__ == "__main__":
    main()
