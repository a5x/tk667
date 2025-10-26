import os, sys, json, ast, re, time, glob
from pathlib import Path
from typing import List, Dict, Any, Optional
import threading
import subprocess

import tkinter as tk
from tkinter import ttk, messagebox

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

BASE_URL = "https://www.tiktok.com/"
SETTINGS_DIR = "Settings"
COOKIE_DIR = os.path.join("acc", "cookies")
STATUS_PATH = Path(SETTINGS_DIR) / "session_status.json"
USER_MAP_PATH = Path(SETTINGS_DIR) / "cookie_user_map.json"

TXT_DIR = Path("txt_files")
OUTPUT_FILE = TXT_DIR / "tiktok_profiles.txt"

def ensure_dirs():
    Path(SETTINGS_DIR).mkdir(exist_ok=True)
    TXT_DIR.mkdir(parents=True, exist_ok=True)

def find_cookie_files() -> List[str]:
    if not os.path.isdir(COOKIE_DIR):
        return []
    patterns = ["frenchacc_*.json","frenchacc_*.txt","*.json","*.txt"]
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(COOKIE_DIR, p)))
    return sorted(dict.fromkeys(files))

def _to_cookie_list(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict):
        return [{"name": k, "value": v, "domain": ".tiktok.com", "path": "/"} for k, v in obj.items()]
    if isinstance(obj, list):
        out = []
        for item in obj:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("key") or item.get("cookie")
            value = item.get("value") or item.get("val")
            if not name or value is None:
                continue
            c = {
                "name": name,
                "value": value,
                "domain": item.get("domain") or item.get("host") or ".tiktok.com",
                "path": item.get("path", "/")
            }
            for k in ("expiry","expires","expirationDate"):
                if item.get(k) is not None:
                    try:
                        c["expiry"] = int(float(item[k])); break
                    except Exception:
                        pass
            if "httpOnly" in item: c["httpOnly"] = bool(item["httpOnly"])
            if "secure"   in item: c["secure"]   = bool(item["secure"])
            out.append(c)
        return out
    return []

def load_cookies_from_file(path: str) -> List[Dict[str, Any]]:
    text = Path(path).read_text(encoding="utf-8", errors="ignore").strip()
    try:
        data = json.loads(text)
        cookies = _to_cookie_list(data)
        if cookies: return cookies
    except Exception:
        pass

    parts = re.split(r"\]\s*\[\s*", text)
    if len(parts) > 1:
        merged = []
        for i, part in enumerate(parts):
            chunk = (("[" if i>0 else "") + part + ("]" if i < len(parts)-1 else ""))
            try:
                data = json.loads(chunk); merged.extend(_to_cookie_list(data))
            except Exception:
                pass
        if merged: return merged
    try:
        data = ast.literal_eval(text); cookies = _to_cookie_list(data)
        if cookies: return cookies
    except Exception:
        pass
    cookies = []
    for line in [l.strip() for l in text.splitlines() if l.strip()]:
        if "=" in line:
            name, value = line.split("=", 1)
            cookies.append({"name": name.strip(), "value": value.strip(), "domain": ".tiktok.com", "path": "/"})
    return cookies

def conv_path_for_cookie_file(cookie_file_path: str) -> str:
    stem = Path(cookie_file_path).stem
    safe = re.sub(r"[^A-Za-z0-9_\-]+", "_", stem)
    return str(Path(SETTINGS_DIR) / f"converted_cookies_{safe}.json")

def convert_to_selenium(cookies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Selenium attend des cookies avec (name, value, domain/path ou url). On ajoutera via driver.add_cookie().
    """
    out = []
    for c in cookies:
        name = c.get("name"); value = c.get("value")
        if not name or value is None: continue
        ck = {
            "name": str(name),
            "value": str(value),
            "path": c.get("path", "/")
        }
        dom = c.get("domain")
        if isinstance(dom, str):
            ck["domain"] = dom
        exp = c.get("expiry") or c.get("expires") or c.get("expirationDate")
        if exp is not None:
            try: ck["expiry"] = int(float(exp))
            except Exception: pass
        if c.get("secure") is True: ck["secure"] = True
        if c.get("httpOnly") is True: ck["httpOnly"] = True
        out.append(ck)
    return out

def save_converted(cookies: List[Dict[str, Any]], target_path: str):
    ensure_dirs()
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)

def choose_cookie_file(files: List[str], preselect: Optional[int]=None) -> Optional[str]:
    if not files:
        return None
    if preselect is not None and 1 <= preselect <= len(files):
        return files[preselect-1]
    print("=== Choisissez un fichier cookies ===")
    for i, f in enumerate(files, 1): print(f"{i}. {os.path.basename(f)}")
    while True:
        s = input("Numéro: ").strip()
        if s.isdigit():
            idx = int(s)
            if 1 <= idx <= len(files):
                return files[idx-1]


def load_user_map() -> Dict[str, str]:
    try:
        if USER_MAP_PATH.exists():
            return json.loads(USER_MAP_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def save_user_map(d: Dict[str, str]):
    try:
        ensure_dirs()
        USER_MAP_PATH.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def write_status(connected: bool, username: Optional[str], when_ts: Optional[int], source_cookie: Optional[str]):
    ensure_dirs()
    now = int(time.time())
    payload = {
        "connected": bool(connected),
        "username": (username or None),
        "when": (int(when_ts) if (when_ts is not None and connected) else None),
        "elapsed_seconds": (now - int(when_ts)) if (connected and when_ts) else None,
        "source_file": os.path.basename(source_cookie) if source_cookie else None,
    }
    try:
        STATUS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def ask_number_with_tk(initial=10) -> Optional[int]:
    result = {"value": None}
    def on_ok():
        v = entry.get().strip()
        try:
            n = int(v)
            if n >= 1:
                result["value"] = n
                root.destroy()
            else:
                messagebox.showerror("Erreur", "Entier >= 1 requis.")
        except Exception:
            messagebox.showerror("Erreur", "Entier invalide.")
    def on_cancel():
        root.destroy()

    root = tk.Tk()
    root.title("Combien de liens ?")
    root.geometry("320x110")
    root.resizable(False, False)

    try:
        root.attributes("-topmost", True)
        root.lift()
        root.focus_force()
        root.after(500, lambda: root.attributes("-topmost", False))
    except Exception:
        pass

    frm = ttk.Frame(root, padding=10); frm.pack(expand=True, fill="both")
    ttk.Label(frm, text="Combien de liens veux-tu collecter ?").pack(pady=(0,6))
    entry = ttk.Entry(frm); entry.insert(0, str(initial)); entry.pack(fill="x", padx=10)

    btns = ttk.Frame(frm); btns.pack(pady=8)
    ttk.Button(btns, text="OK", command=on_ok).pack(side="left", padx=6)
    ttk.Button(btns, text="Annuler", command=on_cancel).pack(side="left", padx=6)

    try: root.eval('tk::PlaceWindow . center')
    except Exception: pass

    root.mainloop()
    return result["value"]


def build_driver(headless: bool=False, user_agent: Optional[str]=None):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--start-maximized")
    if user_agent:
        opts.add_argument(f"--user-agent={user_agent}")

    opts.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])

    service = Service()
    try:
        if os.name == "nt":
            service.creationflags = subprocess.CREATE_NO_WINDOW
    except Exception:
        pass

    driver = webdriver.Chrome(service=service, options=opts)
    driver.implicitly_wait(5)
    return driver

def inject_cookies_and_open(driver, selenium_cookies: List[Dict[str, Any]]):
    driver.get(BASE_URL)
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except TimeoutException:
        pass

    for c in selenium_cookies:
        try:
            driver.add_cookie(c)
        except Exception:
            pass

    driver.get(BASE_URL)
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except TimeoutException:
        pass

def is_connected(driver) -> bool:
    try:
        cookies = driver.get_cookies()
        names = {c.get("name","") for c in cookies}
        return any(n.lower().startswith("sessionid") or n.lower() in ("sid_tt","sessionid_ss") for n in names)
    except WebDriverException:
        return False

def extract_username_via_href(driver) -> Optional[str]:
    """
    NE TOUCHE PAS la logique métier : on extrait le @ via href
    - a[data-e2e="nav-profile"] si dispo
    - sinon on scanne les anchors
    - sinon on tente og:url / canonical
    """
    def pick_from_href(href: Optional[str]) -> Optional[str]:
        if not href: return None
        try:
            if re.match(r"^https?://", href, re.I):
                url = href
            else:
                url = f"https://www.tiktok.com/{href.lstrip('/')}"
            m = re.search(r"/@([^/?#]+)", url)
            return m.group(1) if m else None
        except Exception:
            return None

    try:
        a = driver.find_element(By.CSS_SELECTOR, 'a[data-e2e="nav-profile"]')
        u = pick_from_href(a.get_attribute("href"))
        if u: return u
    except Exception:
        pass

    try:
        hrefs = driver.execute_script("""
            const out = [];
            const as = document.querySelectorAll('a[href]');
            as.forEach(a => out.push(a.getAttribute('href')));
            return out;
        """)
        if isinstance(hrefs, list):
            for href in hrefs:
                if href and "/@" in href:
                    u = pick_from_href(href)
                    if u: return u
    except Exception:
        pass

    try:
        u = pick_from_href(driver.current_url)
        if u: return u
    except Exception:
        pass
    try:
        og = driver.execute_script("""
            const m = document.querySelector('meta[property="og:url"]');
            return m ? m.content : null;
        """)
        u = pick_from_href(og)
        if u: return u
    except Exception:
        pass
    try:
        canon = driver.execute_script("""
            const lk = document.querySelector('link[rel="canonical"]');
            return lk ? lk.href : null;
        """)
        u = pick_from_href(canon)
        if u: return u
    except Exception:
        pass

    return None

def extract_username_fallback_state(driver) -> Optional[str]:
    """
    Fallback comme avant (SIGI_STATE etc.) via JS exécuté par Selenium.
    """
    try:
        got = driver.execute_script("""
        try {
            const fromState = (st) => {
              if (!st) return null;
              if (st.UserModule && st.UserModule.users) {
                const ids = Object.keys(st.UserModule.users);
                for (const id of ids) {
                  const u = st.UserModule.users[id];
                  if (u && (u.uniqueId || u.nickname)) return u.uniqueId || u.nickname;
                }
              }
              if (st.AppContext && st.AppContext.appContext && st.AppContext.appContext.user) {
                const u = st.AppContext.appContext.user;
                if (u && (u.uniqueId || u.nickname)) return u.uniqueId || u.nickname;
              }
              return null;
            };
            let name = null;
            if (typeof window.SIGI_STATE !== 'undefined') name = fromState(window.SIGI_STATE);
            if (!name && typeof window.__UNIVERSAL_DATA__ !== 'undefined') name = fromState(window.__UNIVERSAL_DATA__);
            if (!name && typeof window.__INIT_PROPS__ !== 'undefined') name = fromState(window.__INIT_PROPS__);
            return name || null;
        } catch(e){ return null; }
        """)
        if isinstance(got, str) and got.strip():
            return got.strip()
    except Exception:
        pass
    return None


def collect_profiles_with_driver(driver, desired_links: int) -> List[str]:
    collected, seen = [], set()
    try:
        driver.get("https://www.tiktok.com/explore")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
        time.sleep(0.6)
    except Exception:
        pass

    last_height = None
    for _ in range(10000):
        try:
            anchors = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/@"]')
            for el in anchors[:1000]:
                try:
                    href = el.get_attribute("href")
                    if not href: continue
                    m = re.search(r"/@([^/?#]+)", href)
                    if not m: continue
                    username = m.group(1)
                    url = f"https://www.tiktok.com/@{username}"
                    if url not in seen:
                        seen.add(url); collected.append(url)
                        if len(collected) >= desired_links:
                            raise StopIteration
                except Exception:
                    continue
        except StopIteration:
            break
        except Exception:
            pass


        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception:
            pass
        time.sleep(1.0)

        try:
            new_h = driver.execute_script("return document.body.scrollHeight")
            if last_height is not None and new_h == last_height:
                time.sleep(0.8)
                nh2 = driver.execute_script("return document.body.scrollHeight")
                if nh2 == last_height:
                    break
                last_height = nh2
            else:
                last_height = new_h
        except Exception:
            pass

        if len(collected) >= desired_links:
            break

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for u in collected:
                f.write(u + "\n")
    except Exception:
        pass
    return collected


def run_selenium(converted_path: str, user_agent: Optional[str], headless: bool):
    source_cookie_name = None
    try:
        bn = os.path.basename(converted_path)
        if bn.startswith("converted_cookies_"):
            source_cookie_name = bn.replace("converted_cookies_", "", 1)
    except Exception:
        pass

    write_status(False, None, None, source_cookie_name)

    cookies = []
    try:
        cookies = json.loads(Path(converted_path).read_text(encoding="utf-8"))
    except Exception:
        cookies = []

    driver = build_driver(headless=headless, user_agent=user_agent)
    disconnected_evt = threading.Event()

    def mark_disconnected():
        if not disconnected_evt.is_set():
            disconnected_evt.set()
            write_status(False, None, None, source_cookie_name)

    try:
        inject_cookies_and_open(driver, cookies)

        connected = is_connected(driver)
        username = None
        when_ts = None

        if connected:
            when_ts = int(time.time())

            username_extracted = None
            try:
                username_extracted = extract_username_via_href(driver)
            except Exception:
                username_extracted = None

            if not username_extracted:
                username_extracted = extract_username_fallback_state(driver)

            try:
                user_map = load_user_map()
                if source_cookie_name:
                    mapped = user_map.get(source_cookie_name)
                    if mapped:
                        username = mapped
                    else:
                        username = username_extracted
                        if username:
                            user_map[source_cookie_name] = username
                            save_user_map(user_map)
                else:
                    username = username_extracted
            except Exception:
                username = username_extracted

        write_status(connected, username, when_ts, source_cookie_name)

        if connected:
            def ticker():
                while not disconnected_evt.is_set():
                    write_status(True, username, when_ts, source_cookie_name)
                    time.sleep(1)
            threading.Thread(target=ticker, daemon=True).start()

        if connected:
            time.sleep(10)
            desired = ask_number_with_tk(initial=10)
            if desired is not None:
                _ = collect_profiles_with_driver(driver, desired_links=desired)
                b_path = os.path.join("Codes", "Scripts", "b.py")
                if not os.path.exists(b_path):
                    b_path = "b.py"
                if os.path.exists(b_path):
                    try:
                        subprocess.run([sys.executable, b_path], check=False)
                    except Exception:
                        pass

        try:
            while True:
                time.sleep(0.5)
                _ = driver.window_handles
        except WebDriverException:
            pass
        finally:
            mark_disconnected()

    finally:
        try:
            driver.quit()
        except Exception:
            pass


def run(preselect_index: Optional[int]=None, cookie_path: Optional[str]=None, user_agent: Optional[str]=None, headless: bool=False):
    ensure_dirs()
    files = find_cookie_files()
    if cookie_path:
        if not os.path.isabs(cookie_path):
            alt = os.path.join(COOKIE_DIR, cookie_path)
            cookie_path = alt if os.path.exists(alt) else cookie_path
        if not os.path.exists(cookie_path):
            return
    else:
        cookie_path = choose_cookie_file(files, preselect=preselect_index)
        if not cookie_path: return

    converted_path = conv_path_for_cookie_file(cookie_path)
    raw = load_cookies_from_file(cookie_path)
    if not raw:
        return
    selenium_cookies = convert_to_selenium(raw)
    save_converted(selenium_cookies, converted_path)

    run_selenium(converted_path=converted_path, user_agent=user_agent, headless=headless)

def parse_args():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--index", type=int, default=None, help="Sélection du fichier cookies par index (1..N)")
    p.add_argument("--cookie", type=str, default=None, help="Chemin d'un fichier cookies spécifique")
    p.add_argument("--ua", type=str, default=None, help="User-Agent custom")
    p.add_argument("--headless", action="store_true", help="Lancer Chrome en headless")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run(preselect_index=args.index, cookie_path=args.cookie, user_agent=args.ua, headless=args.headless)
