import os

# === Demande à l'utilisateur le hashtag et le nom du fichier ===
hashtag = input("Quel hashtag veux-tu crée en scraper ? (ex: love, pourtoi, trend): ").strip().lower()
filename = input("Nom du fichier à générer (sans le .py) : ").strip().lower()

if not hashtag or not filename:
    print("❌ Hashtag et nom de fichier requis.")
    exit()

# === Construction de l'URL et du chemin complet ===
url = f"https://www.tiktok.com/tag/{hashtag}"
output_path = os.path.join("Scripts", f"{filename}.py")

# === Crée le dossier Scripts si besoin ===
os.makedirs("Scripts", exist_ok=True)

# === Template du scraper (avec {URL}) ===
scraper_template = f'''from selenium import webdriver
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
        "cookies": "✅ Cookies acceptés",
        "login_clicked": "🔓 Bouton loginContainer cliqué.",
        "scroll_try": "🌀 Scroll #",
        "scroll_blocked": "⚠️ Scroll bloqué ({{}} fois)"
    }},
    "en": {{
        "start": "Starting profile collection...",
        "collected": "Collected:",
        "error": "Error retrieving links:",
        "done": "Total collected links:",
        "scroll_end": "End of scroll reached.",
        "cookies": "✅ Cookies accepted",
        "login_clicked": "🔓 loginContainer button clicked.",
        "scroll_try": "🌀 Scroll #",
        "scroll_blocked": "⚠️ Scroll blocked ({{}} times)"
    }},
    "ru": {{
        "start": "Начало сбора профилей...",
        "collected": "Собрано:",
        "error": "Ошибка при получении ссылок:",
        "done": "Всего собрано ссылок:",
        "scroll_end": "Достигнут конец прокрутки.",
        "cookies": "✅ Файлы cookie приняты",
        "login_clicked": "🔓 Кнопка loginContainer нажата.",
        "scroll_try": "🌀 Прокрутка #",
        "scroll_blocked": "⚠️ Прокрутка заблокирована ({{}} раз)"
    }}
}}[lang]

print(t["start"])

URL = "{url}"
SCROLL_PAUSE_TIME = 2
OUTPUT_FILE = "Scripts_info_extract/tiktok_profiles.txt"
CONFIG_FILE = "Settings/config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
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

WebDriverWait(driver, 10).until(
    lambda d: d.execute_script("return document.readyState") == "complete"
)
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
    print(f"❌ Cookies non cliqués : {{e}}")

for i in range(SCROLL_LIMIT):
    try:
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="main-content-homepage_hot"]/aside/div/div[2]/button'))
        ).click()
        time.sleep(1)
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
            WebDriverWait(driver, 10).until_not(
                EC.presence_of_element_located((By.ID, "loginContainer"))
            )
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main-content-homepage_hot"]/aside/div/div[2]/button'))
            )
            time.sleep(1)
            continue
        except Exception:
            pass

    try:
        elements = driver.find_elements(
            By.XPATH,
            '//*[@id="main-content-challenge"]//a[contains(@href, "@")]'
        )
        for el in elements:
            href = el.get_attribute("href")
            if href:
                if "/video/" in href:
                    continue
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

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for link in collected_links:
        f.write(link + "\\n")

print(f"{{t['done']}} {{len(collected_links)}}")
driver.quit()
'''

# === Écriture du fichier ===
with open(output_path, "w", encoding="utf-8") as f:
    f.write(scraper_template)

print(f"✅ Script généré : {output_path}")
