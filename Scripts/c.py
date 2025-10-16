import subprocess
import sys
import os
import time
import re
from urllib.parse import urlparse, urlunparse
from colorama import Fore, Style, init
init(autoreset=True)

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
OUTPUT_FILE = os.path.join(BASE_DIR, "Scripts_info_extract", "tiktok_profiles.txt")
A_PY = os.path.join(SCRIPTS_DIR, "a.py")
B_PY = os.path.join(SCRIPTS_DIR, "b.py")


def normalize_url(u: str) -> str:
    """verif si ya pas des liens dupliquer et les degage."""
    u = (u or "").strip()
    if not u:
        return ""
    try:
        p = urlparse(u)
        scheme = (p.scheme or "https").lower()
        netloc = p.netloc.lower()
        path = p.path.rstrip("/")
        if not netloc and path.startswith("@"):
            return f"https://www.tiktok.com/{path}"
        return urlunparse((scheme, netloc, path, "", "", ""))
    except Exception:
        return u.rstrip("/")

def read_file_urls():
    """Lit les URLS presentes dans le fichier (si il existe)."""
    if not os.path.exists(OUTPUT_FILE):
        return []
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def write_urls(urls):
    """Ecrit la liste d'URLs dans le fichier"""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True
    )
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")

HTTP_RE = re.compile(r'(https?://\S+)', re.IGNORECASE)
def extract_url(line: str):
    m = HTTP_RE.search(line)
    if not m:
        return None
    return m.group(1).rstrip('.,;\'")]}')


def run_a_live_until(desired, cumulative_set, cumulative_list):
    """
    Lance a.py (stdout non bufferisé), lit en temps réel.
    Chaque URL trouvée est normalisée, dédupliquée, écrite sur disque.
    Si total >= desired -> on coupe a.py et on renvoie immédiatement.
    Retourne (ok, total).
    """
    print(Fore.MAGENTA + "Start a.py ..." + Style.RESET_ALL)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    proc = subprocess.Popen(
        [sys.executable, "-u", A_PY],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        text=True,
        encoding="utf-8",
        env=env
    )

    total = len(cumulative_list)

    try:
        for raw in iter(proc.stdout.readline, ''):
            line = raw.rstrip("\n")
            if not line:
                continue

            if ("Collecté" in line) or ("Collected" in line):
                print(Fore.CYAN + line + Style.RESET_ALL, flush=True)
            else:
                print(line, flush=True)

            url = extract_url(line)
            if url:
                nu = normalize_url(url)
                if nu and nu not in cumulative_set:
                    cumulative_set.add(nu)
                    cumulative_list.append(nu)
                    write_urls(cumulative_list)
                    total = len(cumulative_list)

                    if total >= desired:
                        print(Fore.GREEN + f"Requiered Links ✅ ({total} >= {desired}). STOP, Starting b.py." + Style.RESET_ALL)
                        try:
                            proc.terminate()
                        except Exception:
                            pass
                        break
    finally:
        try:
            proc.stdout.close()
        except Exception:
            pass
        try:
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    ok = (total >= desired) or (proc.returncode == 0)
    return ok, total

def run_b():
    print(Fore.YELLOW + "Start b.py ..." + Style.RESET_ALL)
    proc = subprocess.run([sys.executable, B_PY], cwd=BASE_DIR)
    return proc.returncode == 0

def ask_int(prompt, minimum=1):
    while True:
        val = input(Fore.GREEN + prompt + Style.RESET_ALL).strip()
        try:
            n = int(val)
            if n >= minimum:
                return n
        except ValueError:
            pass
        print(Fore.RED + f"Please an logic number >= {minimum}." + Style.RESET_ALL)


def main():
    print(Fore.MAGENTA + "======Custom Scraper=====" + Style.RESET_ALL)
    desired = ask_int("How Much Links you want ? ")

    if os.path.exists(OUTPUT_FILE):
        print(Fore.YELLOW + "Clean the existing file..." + Style.RESET_ALL)
        try:
            os.remove(OUTPUT_FILE)
        except OSError as e:
            print(Fore.RED + "Impossible to clean the file already empty : " + str(e) + Style.RESET_ALL)
        time.sleep(0.2)

    cumulative_set = set()
    cumulative_list = []
    write_urls([])

    MAX_ITERATIONS = 200 

    print(Fore.CYAN + f"Requiered Links : {desired} unique profiles.\n" + Style.RESET_ALL)

    for it in range(1, MAX_ITERATIONS + 1):
        print(Fore.MAGENTA + f"Attempt {it} ..." + Style.RESET_ALL)

        ok, total = run_a_live_until(desired, cumulative_set, cumulative_list)

        if total >= desired:
            run_b()
            return

        if not ok:
            print(Fore.RED + "a.py ERREUR ARRET / ERROR STOPING PROCESS." + Style.RESET_ALL)
            break

        print(Fore.YELLOW + f"Total actuel: {total}/{desired}. Nouvelle tentative..." + Style.RESET_ALL)

    print(Fore.RED + "Capped Attempts rushed, STOPING." + Style.RESET_ALL)
    print(Fore.YELLOW + "Starting b.py with profiles links collected." + Style.RESET_ALL)
    run_b()

if __name__ == '__main__':
    main()
# AJOUT DE FONCTIONNALITE DISCORD ET TELEGRAM