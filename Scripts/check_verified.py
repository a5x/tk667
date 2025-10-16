import os
import json
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from colorama import Fore, Style, init

init(autoreset=True)

CONFIG_FILE = "Settings/config.json"
OUTPUT_FILE = "Scripts_info_extract/verified_profiles.txt"
TIKTOK_EXPLORE_URL = "https://www.tiktok.com/explore"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
}

def load_scroll_count():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                return max(int(config.get("scrolls", 10)), 1)
        except:
            pass
    return 10

def create_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1200, 800)
    return driver

def is_verified_profile(username):
    try:
        response = requests.get(f"https://www.tiktok.com/@{username}", headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return False
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup.find_all('script'):
            if 'userInfo' in script.text:
                data = json.loads(script.string)
                user_info = data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {}).get('userInfo', {})
                return user_info.get('user', {}).get('verified', False)
    except Exception:
        return False
    return False

def scroll_and_check(driver, max_scrolls, existing):
    verified_profiles = set()
    seen_usernames = set()

    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/@')]")
        for el in links:
            href = el.get_attribute("href")
            if not href:
                continue
            username = href.split("/@")[-1].split("?")[0].split("/")[0].strip().lower()
            if not username or username in seen_usernames:
                continue
            seen_usernames.add(username)

            # Vérification sans afficher les tests
            if is_verified_profile(username):
                if f"@{username}" not in existing and f"@{username}" not in verified_profiles:
                    print(Fore.GREEN + f"[✓] @{username} est certifié.")
                    verified_profiles.add(f"@{username}")
                    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                        f.write(f"@{username}\n")

    return verified_profiles


def main():
    print(Fore.CYAN + "[...] Détection des comptes certifiés TikTok en temps réel.")

    scrolls = load_scroll_count()
    print(Fore.CYAN + f"[i] Nombre de scrolls configuré : {scrolls}")

    existing = set()
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing = set(line.strip() for line in f)

    driver = create_driver(headless=True)
    driver.get(TIKTOK_EXPLORE_URL)
    time.sleep(5)

    verified = scroll_and_check(driver, scrolls, existing)

    driver.quit()
    print(Fore.CYAN + f"\n[✓] {len(verified)} nouveaux comptes certifiés ajoutés à {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
