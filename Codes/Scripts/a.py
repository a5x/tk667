from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import time
import json
import os

def load_language():
    if os.path.exists("Settings/lang_config.json"):
        with open("Settings/lang_config.json", "r", encoding="utf-8") as f:
            return json.load(f).get("lang", "fr")
    return "fr"

lang = load_language()
t = {
    "fr": {
        "start": "Lance el scrap pour les bio...",
        "collected": "Collecté :",
        "error": "Erreur récupération liens :",
        "done": "Total liens collectés :",
        "scroll_end": "Fin du scroll atteinte."
    },
    "en": {
        "start": "Start Scrap about me...",
        "collected": "Collected:",
        "error": "Error retrieving links:",
        "done": "Total collected links:",
        "scroll_end": "End of scroll reached."
    },
    "ru": {
        "start": "Начало сбора профилей...",
        "collected": "Собрано:",
        "error": "Ошибка при получении ссылок:",
        "done": "Всего собрано ссылок:",
        "scroll_end": "Достигнут конец прокрутки."
    }
}[lang]

print(t["start"])

URL = "https://www.tiktok.com/explore"
SCROLL_PAUSE_TIME = 1
OUTPUT_FILE = "txt_files/tiktok_profiles.txt"
CONFIG_FILE = "Settings/config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

config = load_config()
SCROLL_LIMIT = config.get("scrolls", 10)

options = Options()
options.page_load_strategy = 'eager'
options.add_argument("--disable-gpu")
options.add_argument("--headless-new")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")

service = Service(log_path=os.devnull)

if os.name == 'nt':
    service.creationflags = subprocess.CREATE_NO_WINDOW

driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(10)
driver.set_page_load_timeout(30)

driver.get(URL)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "main-content-explore_page"))
)

collected_links = set()
last_height = driver.execute_script("return document.body.scrollHeight")

for scroll in range(SCROLL_LIMIT):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)

    try:
        elements = driver.find_elements(By.XPATH, '//*[@id="main-content-explore_page"]//a[2]')
        for el in elements:
            href = el.get_attribute("href")
            if href and href not in collected_links:
                collected_links.add(href)
                print(f"{t['collected']} {href}")
    except Exception as e:
        print(f"{t['error']} {e}")

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        print(t["scroll_end"])
        break
    last_height = new_height

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for link in collected_links:
        f.write(link + "\n")

print(f"{t['done']} {len(collected_links)}")
driver.quit()

