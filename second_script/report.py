from playwright.sync_api import sync_playwright
import time
import json
import os

COOKIES_PATH = "Settings/converted_cookies.json"

def load_cookies():
    if not os.path.exists(COOKIES_PATH):
        return []
    with open(COOKIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def signaler(page, skip_button=False):
    try:
        if not skip_button:
            # clicker dès que possible, timeout très court, force pour bypass hover/etc.
            page.click(
                'xpath=//*[@id="main-content-others_homepage"]/div/div[1]/div[2]/div[2]/button[2]',
                timeout=3000,
                force=True
            )
            time.sleep(0.1)

        floating_ui_xpath = None
        for i in range(35, 100):
            xpath = f'//*[@id="floating-ui-{i}"]/div/div/div[1]'
            try:
                page.click(f'xpath={xpath}', timeout=200, force=True)
                floating_ui_xpath = xpath
                break
            except:
                continue
        if not floating_ui_xpath:
            return

        time.sleep(0.1)

        # On clique directement sans chercher l'iframe, Playwright gère le focus
        for sel in [
            'xpath=//*[@id="tux-portal-container"]/div/div[2]/div/div/div[2]/div/div/section/form/div[2]/label',
            'xpath=//*[@id="tux-portal-container"]/div/div[2]/div/div/div[2]/div/div/section/form/div[2]/label[3]'
        ]:
            page.click(sel, timeout=2000, force=True)
            time.sleep(0.1)

        page.click(
            'xpath=//*[@id="tux-portal-container"]/div/div[2]/div/div/div[2]/div/div/section/form/div[2]/div[3]/button',
            timeout=2000,
            force=True
        )
        time.sleep(0.1)

        page.click(
            'xpath=//*[@id="tux-portal-container"]/div/div[2]/div/div/div[2]/div/div/section/div/div/button',
            timeout=2000,
            force=True
        )
        time.sleep(0.1)

    except Exception:
        pass

def main():
    username = input("Entrez le @ TikTok à signaler (sans @) : ").strip()
    if not username:
        return

    url = f"https://www.tiktok.com/@{username}"

    with sync_playwright() as p:
        # Lancement optimisé
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
            ]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            bypass_csp=True,
            java_script_enabled=True,
        )

        # Blocage des ressources inutiles
        def _route(route, request):
            if request.resource_type in ["image", "stylesheet", "font", "media"]:
                return route.abort()
            return route.continue_()
        context.route("**/*", _route)

        # Cargement des cookies si dispo
        cookies = load_cookies()
        if cookies:
            try:
                context.add_cookies(cookies)
            except:
                pass

        page = context.new_page()
        # Timeouts plus courts
        page.set_default_navigation_timeout(10000)
        page.set_default_timeout(5000)

        # Chargements plus légers
        page.goto("https://www.tiktok.com", wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(1)

        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(1)

        # Gestion éventuelle du captcha
        try:
            captcha_btn = page.locator('//*[@id="captcha_close_button"]')
            captcha_btn.wait_for(state="visible", timeout=5000)
            captcha_btn.click()
            time.sleep(1)
        except:
            pass

        # Boucle de signalement
        first_run = True
        while True:
            signaler(page, skip_button=not first_run)
            first_run = False

            print(f"✅ Report Done for @{username}")
            print("➡️ Appuie sur Entrée pour stopper, ou attends la prochaine boucle.")
            if os.name == "nt":
                import msvcrt
                if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                    break
            else:
                import select, sys
                i, o, e = select.select([sys.stdin], [], [], 1)
                if i:
                    input()
                    break

        browser.close()

if __name__ == "__main__":
    main()
