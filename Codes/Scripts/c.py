# Codes/Scripts/c.py
import subprocess
import sys
import os
import time
import re
import argparse
from urllib.parse import urlparse, urlunparse
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

SCRIPTS_DIR = Path(__file__).resolve().parent
BASE_DIR    = SCRIPTS_DIR.parent.parent
OUTPUT_FILE = BASE_DIR / "txt_files" / "tiktok_profiles.txt"
A_PY        = SCRIPTS_DIR / "a.py"
B_PY        = SCRIPTS_DIR / "b.py"

def normalize_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return ""
    try:
        p = urlparse(u)
        scheme = (p.scheme or "https").lower()
        netloc = (p.netloc or "").lower()
        path = (p.path or "").rstrip("/")
        if not netloc and path.startswith("@"):
            return f"https://www.tiktok.com/{path}"
        return urlunparse((scheme, netloc, path, "", "", ""))
    except Exception:
        return u.rstrip("/")

def read_file_urls():
    if not OUTPUT_FILE.exists():
        return []
    return [line.strip() for line in OUTPUT_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

def write_urls(urls):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")

HTTP_RE = re.compile(r'(https?://\S+)', re.IGNORECASE)
def extract_url(line: str):
    m = HTTP_RE.search(line)
    if not m:
        return None
    return m.group(1).rstrip('.,;\'")]}')

def run_a_live_until(desired, cumulative_set, cumulative_list):
    print(Fore.MAGENTA + "Start a.py ..." + Style.RESET_ALL)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    proc = subprocess.Popen(
        [sys.executable, "-u", str(A_PY)],
        cwd=str(BASE_DIR),
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

                    if total >= (desired - 2):  # Marge d'erreur de 2 en dessous
                        print(Fore.GREEN + f"Required Links ({total} good {desired}. STOP, Starting b.py." + Style.RESET_ALL)
                        try:
                            proc.terminate()
                        except Exception:
                            pass
                        break
    finally:
        try:
            if proc.stdout:
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
    proc = subprocess.run([sys.executable, str(B_PY)], cwd=str(BASE_DIR))
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
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--desired", type=int, default=None, help="How many unique profile links to collect.")
    parser.add_argument("--no-clean", dest="no_clean", action="store_true", help="Do not delete existing output file before running.")
    args = parser.parse_args()


    print(Fore.MAGENTA + "====== Custom Scraper =====" + Style.RESET_ALL)
    desired = args.desired if (args.desired and args.desired >= 1) else None
    if desired is None:
        desired = ask_int("How Much Links you want ? ", minimum=1)

    if not args.no_clean and OUTPUT_FILE.exists():
        print(Fore.YELLOW + "Clean the existing file..." + Style.RESET_ALL)
        try:
            OUTPUT_FILE.unlink()
        except OSError as e:
            print(Fore.RED + "Impossible to clean the file (maybe already empty): " + str(e) + Style.RESET_ALL)
        time.sleep(0.2)

    cumulative_set = set()
    cumulative_list = []
    write_urls([])

    MAX_ITERATIONS = 200
    print(Fore.CYAN + f"Requiered Links : {desired} unique profiles.\n" + Style.RESET_ALL)

    for it in range(1, MAX_ITERATIONS + 1):
        print(Fore.MAGENTA + f"Attempt {it} ..." + Style.RESET_ALL)

        ok, total = run_a_live_until(desired, cumulative_set, cumulative_list)

        if total >= (desired - 2):  # Marge d'erreur de 2 en dessous
            run_b()
            return

        if not ok:
            print(Fore.RED + "a.py ERREUR ARRET / ERROR STOPPING PROCESS." + Style.RESET_ALL)
            break

        print(Fore.YELLOW + f"Total actuel: {total}/{desired}. Nouvelle tentative..." + Style.RESET_ALL)

    print(Fore.RED + "Capped Attempts reached, STOPPING." + Style.RESET_ALL)
    print(Fore.YELLOW + "Starting b.py with profiles links collected." + Style.RESET_ALL)
    run_b()

if __name__ == '__main__':
    main()
