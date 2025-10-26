# main.py
import os
import sys
import json
import io
import zipfile
import shutil
import threading
import subprocess
import time
from pathlib import Path
import tempfile
import stat
import datetime

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

try:
    import requests
except Exception:
    requests = None

APP_TITLE = "667 SCRAPER"
APP_MIN_SIZE = (1024, 640)

LOCAL_VERSION = "2.5"
GITHUB_OWNER  = "a5x"
GITHUB_REPO   = "tk667"
GITHUB_BRANCH = "main"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/refs/heads/main/version.txt"
ZIP_URL = f"https://codeload.github.com/{GITHUB_OWNER}/{GITHUB_REPO}/zip/refs/heads/{GITHUB_BRANCH}"

PRESERVE_PATHS = [
    "Settings/lang_config.json",
    "Settings/config.json",
    "txt_files/",
]

translations = {
    "fr": {
    "menu_title": "★ Nouvelle version {version} ★",
        "option_1": "Démarrer : (collecte profils)",
        "option_2": "Démarrer : (check bio pour emails)",
        "option_3": "Lancer : Scripts Collect + emails",
        "option_4": "TikTok hashtag scraper",
        "option_v": "Scrap Blue Badge accounts",
        "option_i": "Tiktok Infos Finder",
        "option_t": "Comment utiliser le tool",
        "option_cc": "Nettoyer les fichiers",
        "option_c": "Changer la langue",
        "option_s": "Paramètre (nombre de scroll)",
        "option_l": "Changelogs",
        "option_q": "Fermer",
        "option_create": "Créer un scraper hashtag perso",
        "panel_header": "Scraper TikTok par hashtag",
        "panel_create_personal": "Créer perso",
        "return_menu": "Retour au menu",
        "invalid": "Option invalide.",
        "scraper_prompt": ">> ",
        "choose": "Choisissez : ",
        "bye": "Au revoir !",
        "submenu_1_title": "=========== Choissisez une option ===========",
        "submenu_2_title": "=========== Choissisez une option ===========",
        "submenu_3_title": "=========== Paramètres ===========",
        "btn_check_updates": "Vérifier les mises à jour",
        "lbl_console": "Console",
        "nav_home": "Accueil",
        "nav_scraping": "Scraping Tools",
        "nav_tiktok": "TikTok Tools",
        "nav_settings": "Paramètres",
        "nav_changelog": "Changelogs",
        "home_welcome": "Bienvenue ! Choisissez une section dans le menu de gauche.",
        "btn_send_telegram": "Envoyer le fichier sur Telegram",
        "btn_infinite_report": "Infinite Report @ [NOT FINISHED]",
        "btn_convert_cookies": "Convertir les cookies",
        "btn_save": "Sauvegarder",
        "tuto_title": "Tuto",
        "not_found_title": "Introuvable",
        "not_found_text": "Le script n'existe pas : {path}",
        "ok_title": "OK",
        "saved_param": "Paramètre sauvegardé.",
        "lang_title": "Langue",
        "lang_changed": "Langue modifiée. Certaines étiquettes changeront au prochain redémarrage.",
        "ask_custom_scraper_title": "Custom Scraper",
        "ask_custom_scraper_body": "Combien de liens veux-tu ?",
        "option_theme": "Thème (console)",
        "theme_system": "Système",
        "theme_light": "Clair",
        "theme_dark": "Sombre",
        "theme_saved": "Thème appliqué.",
        "option_logo": "Logo",
        "logo_saved": "Logo mis à jour.",
        "option_color": "Couleur (UI)",
        "color_sky": "Bleu ciel",
        "color_blue": "Bleu foncé",
        "color_red": "Rouge",
        "color_yellow": "Jaune",
        "color_green": "Vert",
        "color_pink": "Rose",
        "color_orange": "Orange",
        "color_violet": "Violet",
        "color_saved": "Couleur appliquée.",
        "option_console_preset": "Couleur de la console",
        "console_preset_default": "Par défaut",
        "console_preset_green": "Vert sur noir",
        "console_preset_amber": "Ambre sur noir",
        "console_preset_light": "Clair",
        "console_preset_saved": "Préréglage console appliqué.",
        "update_title": "Mise à jour disponible",
        "update_text": "Version {latest} disponible (actuelle {current}).\n\nClique sur « Télécharger et installer » pour mettre à jour l’application.",
        "btn_update_now": "Télécharger et installer",
        "status_checking": "Vérification…",
        "status_downloading": "Téléchargement… {pct}%",
        "status_extracting": "Extraction…",
        "status_applying": "Application de la mise à jour…",
        "status_done": "Mise à jour terminée.",
        "restart_prompt": "Mise à jour installée. Redémarrer maintenant ?",
        "error_update": "Échec de mise à jour : {err}",
        "blocked_until_update": "Mise à jour requise — les actions sont désactivées jusqu’à l’installation.",
        "nav_credits": "Crédits",
        "credits_title": "Crédits",
        "status_connected": "Connecté",
        "status_disconnected": "Compte : non connecté",
        "status_for": "depuis",
        "credits_lines": [
            "dev @enabIe idea from @repient RU translation s/O : @?????"
        ],
        "changelogs_title": "Changelogs",
        "changelogs_lines": [
            "",
            "Changelogs :",
            "2.4 : Fix updater (remplace main.py en premier, copie atomique, UI bloquée).",
            "2.3 : Couleurs d’interface (Bleu ciel, Bleu foncé, Rouge, Jaune, Vert, Rose, Orange, Violet).",
            "2.2 : Sélecteur thème console (clair/sombre).",
            "2.1 : Script nombre de comptes voulu.",
            "2.0 : Corrections et optimisations.",
            "1.9 : Telegram file sender.",
            "1.8 : Cleaner + comptes certif.",
            "1.7 : Scraper hashtag custom.",
            "1.6 : Scraper hashtag.",
            "1.5 : Rework Codes/Scripts.",
            "1.4 : UI Update.",
            "1.3 : Scripts chainés + TikTok info.",
            "1.2 : Choix de la langue.",
            "1.1 : Paramètres.",
            "1.0 : Initial."
        ],
    },
    "en": {
    "menu_title": "★ New Release {version} ★",
        "option_1": "Start : (collect profiles)",
        "option_2": "Start : (check about me for emails)",
        "option_3": "Run : Collect + emails",
        "option_4": "TikTok hashtag scraper",
        "option_v": "Scrap Blue Badge accounts",
        "option_i": "Tiktok Infos Finder",
        "option_t": "How to use tools",
        "option_cc": "Clean files",
        "option_c": "Change language",
        "option_s": "Setting (scroll count)",
        "option_l": "Changelogs",
        "option_q": "Close",
        "option_create": "Create custom hashtag scraper",
        "panel_header": "TikTok Hashtag Scraper",
        "panel_create_personal": "Create custom",
        "return_menu": "Return to menu",
        "invalid": "Invalid option.",
        "scraper_prompt": ">> ",
        "choose": "Choose: ",
        "bye": "Goodbye!",
        "submenu_1_title": "=========== Choose an option ===========",
        "submenu_2_title": "=========== Choose an option ===========",
        "submenu_3_title": "=========== Settings ===========",
        "btn_check_updates": "Check for updates",
        "lbl_console": "Console",
        "nav_home": "Home",
        "nav_scraping": "Scraping Tools",
        "nav_tiktok": "TikTok Tools",
        "nav_settings": "Settings",
        "nav_changelog": "Changelogs",
        "home_welcome": "Welcome! Pick a section from the left menu.",
        "btn_send_telegram": "Send file to Telegram",
        "btn_infinite_report": "Infinite Report @ [PAS FINI]",
        "btn_convert_cookies": "Convert Cookies",
        "btn_save": "Save",
        "tuto_title": "Tutorial",
        "not_found_title": "Not found",
        "not_found_text": "Script does not exist: {path}",
        "ok_title": "OK",
        "saved_param": "Setting saved.",
        "lang_title": "Language",
        "lang_changed": "Language changed. Some labels update on next restart.",
        "ask_custom_scraper_title": "Custom Scraper",
        "ask_custom_scraper_body": "How many links do you want?",
        "option_theme": "Theme (console)",
        "theme_system": "System",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "theme_saved": "Theme applied.",
        "option_logo": "Logo",
        "logo_saved": "Logo updated.",
        "option_color": "Color (UI)",
        "color_sky": "Sky blue",
        "color_blue": "Dark blue",
        "color_red": "Red",
        "color_yellow": "Yellow",
        "color_green": "Green",
        "color_pink": "Pink",
        "color_orange": "Orange",
        "color_violet": "Violet",
        "color_saved": "Color applied.",
        "option_console_preset": "Console Color",
        "console_preset_default": "Default",
        "console_preset_green": "Green on black",
        "console_preset_amber": "Amber on black",
        "console_preset_light": "Light",
        "console_preset_saved": "Console preset applied.",
        "update_title": "Update available",
        "update_text": "Version {latest} available (current {current}).\n \n Click “Download & install” to update.",
        "btn_update_now": "Download & install",
        "status_checking": "Checking…",
        "status_downloading": "Downloading… {pct}%",
        "status_extracting": "Extracting…",
        "status_applying": "Applying update…",
        "status_done": "Update complete.",
        "restart_prompt": "Update installed. Restart now?",
        "error_update": "Update failed: {err}",
        "blocked_until_update": "Update required — actions disabled until installation.",
        "nav_credits": "Credits",
        "status_connected": "Connected",
        "status_disconnected": "Not connected",
        "status_for": "for",
        "credits_title": "Credits",
        "credits_lines": [
            "dev @enabIe idea from @repient RU translation s/O : @?????"
        ],
        "changelogs_title": "Changelogs",
        "changelogs_lines": [
            "",
            "Changelogs :",
            "2.4 : Fix updater (replace main.py first, atomic copy, UI locked).",
            "2.3 : UI colors (Sky, Dark blue, Red, Yellow, Green, Pink, Orange, Violet).",
            "2.2 : Console theme selector (light/dark).",
            "2.1 : Script number of desired accounts.",
            "2.0 : Fixes and optimizations.",
            "1.9 : Telegram file sender.",
            "1.8 : Cleaner + verified accounts.",
            "1.7 : Custom hashtag scraper.",
            "1.6 : Hashtag scraper.",
            "1.5 : Rework Codes/Scripts.",
            "1.4 : UI Update.",
            "1.3 : Chained scripts + TikTok info.",
            "1.2 : Language choice.",
            "1.1 : Settings.",
            "1.0 : Initial."
        ],
    }
}

SETTINGS_DIR = Path("Settings")
SETTINGS_DIR.mkdir(exist_ok=True)
LANG_FILE = SETTINGS_DIR / "lang_config.json"
CONFIG_FILE = SETTINGS_DIR / "config.json"
SESSION_STATUS_FILE = SETTINGS_DIR / "session_status.json"  # <-- ajouté

def load_language() -> str:
    if LANG_FILE.exists():
        try:
            return json.loads(LANG_FILE.read_text(encoding="utf-8")).get("lang", "fr")
        except Exception:
            return "fr"
    return "fr"

def save_language(lang: str):
    LANG_FILE.write_text(json.dumps({"lang": lang}, ensure_ascii=False), encoding="utf-8")

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")

def list_settings_pngs():
    try:
        return [p.name for p in SETTINGS_DIR.glob("*.png")]
    except Exception:
        return []

def get_logo_path_from_config(cfg=None):
    if cfg is None:
        cfg = load_config()
    logo = cfg.get("logo_png")
    if not logo:
        return None
    p = SETTINGS_DIR / logo
    return str(p) if p.exists() else None

def _parse_version(v: str):
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except Exception:
        return tuple(v.strip().split("."))

def _is_newer(latest: str, current: str) -> bool:
    return _parse_version(latest) > _parse_version(current)

def _path_is_preserved(rel_path: str) -> bool:
    rel = rel_path.replace("\\", "/")
    for p in PRESERVE_PATHS:
        p = p.rstrip("/")
        if p == "":
            continue
        if not p.endswith("/") and rel == p:
            return True
        if p.endswith("/") and (rel == p[:-1] or rel.startswith(p)):
            return True
    return False

def _ensure_writable(path: Path):
    try:
        if not path.exists():
            return
        mode = path.stat().st_mode
        if not (mode & stat.S_IWRITE):
            path.chmod(mode | stat.S_IWRITE)
    except Exception:
        pass

def _atomic_copy(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    _ensure_writable(dst)
    with open(src, "rb") as fsrc:
        tmp = dst.with_suffix(dst.suffix + ".updtmp")
        with open(tmp, "wb") as fdst:
            shutil.copyfileobj(fsrc, fdst, length=1024*1024)
        os.replace(tmp, dst)

def check_update_gui(root: tk.Tk, console_append):
    if not requests:
        return
    lang = load_language(); t = translations.get(lang, translations["fr"])

    def task():
        try:
            console_append(f"Checking update version : {VERSION_URL}\n")
            r = requests.get(VERSION_URL, timeout=8)
            console_append(f"HTTP {r.status_code}\n")
            if r.status_code != 200:
                console_append("Error can't find the version on the github page.\n")
                return
            latest = r.text.strip()
            console_append(f"Last Released Update : {latest} | Your Update Version : {LOCAL_VERSION}\n")
            if _is_newer(latest, LOCAL_VERSION):
                root.after(0, lambda: _show_update_modal(root, latest, console_append))
        except Exception as e:
            console_append(f"Update checking failed : {e}\n")
    threading.Thread(target=task, daemon=True).start()

def _collect_all_buttons(widget):
    buttons = []
    try:
        if isinstance(widget, ttk.Button):
            buttons.append(widget)
    except Exception:
        pass
    for child in widget.winfo_children():
        buttons.extend(_collect_all_buttons(child))
    return buttons

def _set_all_buttons_state(root, state: str):
    for btn in _collect_all_buttons(root):
        try:
            btn.state([state] if state == "disabled" else ["!disabled"])
        except Exception:
            try:
                btn.configure(state=state)
            except Exception:
                pass

def _show_update_modal(root: tk.Tk, latest: str, console_append):
    lang = load_language(); t = translations.get(lang, translations["fr"])

    _set_all_buttons_state(root, "disabled")
    try:
        root.attributes("-disabled", True)
    except Exception:
        pass

    win = tk.Toplevel(root)
    win.title(t["update_title"])
    win.geometry("480x240")
    win.transient(root)
    win.grab_set()

    def _deny_close():
        pass
    win.protocol("WM_DELETE_WINDOW", _deny_close)

    frm = ttk.Frame(win, padding=16); frm.pack(fill=tk.BOTH, expand=True)
    msg = t["update_text"].format(latest=latest, current=LOCAL_VERSION)
    ttk.Label(frm, text=msg, justify="left", wraplength=440).pack(anchor="w")

    prog = ttk.Progressbar(frm, orient="horizontal", mode="determinate", maximum=100, length=440)
    prog.pack(pady=(12, 6))
    status_var = tk.StringVar(value=t["status_checking"])
    ttk.Label(frm, textvariable=status_var).pack(anchor="w")

    btn = ttk.Button(frm, text=t["btn_update_now"],
                     command=lambda: _start_update_thread(win, prog, status_var, latest, console_append, root))
    btn.pack(pady=(10, 0))

def _start_update_thread(win: tk.Toplevel, prog: ttk.Progressbar, status_var: tk.StringVar,
                         latest: str, console_append, root):
    threading.Thread(
        target=_perform_update,
        args=(win, prog, status_var, latest, console_append, root),
        daemon=True
    ).start()

def _perform_update(win: tk.Toplevel, prog: ttk.Progressbar, status_var: tk.StringVar,
                    latest: str, console_append, root):
    lang = load_language(); t = translations.get(lang, translations["fr"])
    base_dir = Path.cwd()

    try:
        status_var.set(t["status_downloading"].format(pct=0))
        prog["value"] = 0
        with requests.get(ZIP_URL, stream=True, timeout=20) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0)) or None
            tmp_zip = Path(tempfile.gettempdir()) / f"{GITHUB_REPO}-{GITHUB_BRANCH}.zip"
            with open(tmp_zip, "wb") as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
                        if total:
                            downloaded += len(chunk)
                            pct = int(downloaded * 100 / total)
                            prog["value"] = pct
                            status_var.set(t["status_downloading"].format(pct=pct))
        console_append(f"\nZIP downloaded to: {tmp_zip}\n")
    except Exception as e:
        messagebox.showerror(translations[load_language()]["update_title"], t["error_update"].format(err=str(e)))
        return

    try:
        status_var.set(t["status_extracting"])
        prog["value"] = 0
        extract_dir = Path(tempfile.mkdtemp(prefix="update_"))
        with zipfile.ZipFile(tmp_zip, "r") as z:
            z.extractall(extract_dir)
        src_root = next(extract_dir.iterdir())
        console_append(f"Extracted to: {src_root}\n")
    except Exception as e:
        messagebox.showerror(translations[load_language()]["update_title"], t["error_update"].format(err=str(e)))
        return

    try:
        status_var.set(t["status_applying"])

        files_to_copy = []
        for p in src_root.rglob("*"):
            if p.is_dir():
                continue
            rel = str(p.relative_to(src_root)).replace("\\", "/")
            if _path_is_preserved(rel):
                continue
            files_to_copy.append((rel, p, base_dir / rel))

        files_to_copy.sort(key=lambda t: (t[0] != "main.py", t[0]))

        total = len(files_to_copy) or 1
        for i, (rel, src, dst) in enumerate(files_to_copy, 1):
            try:
                _atomic_copy(src, dst)
            except PermissionError:
                try:
                    if dst.exists():
                        _ensure_writable(dst)
                        dst.unlink()
                    _atomic_copy(src, dst)
                except Exception as e:
                    console_append(f"[WARN] Could not replace {rel}: {e}\n")
                    raise
            pct = int(i * 100 / total)
            prog["value"] = pct

        status_var.set(t["status_done"])
    except Exception as e:
        messagebox.showerror(translations[load_language()]["update_title"], t["error_update"].format(err=str(e)))
        return

    try:
        try:
            root.attributes("-disabled", False)
        except Exception:
            pass

        if messagebox.askyesno(APP_TITLE, t["restart_prompt"], parent=win):
            python = sys.executable
            os.execl(python, python, *sys.argv)
        else:
            try:
                win.destroy()
            except Exception:
                pass
            _set_all_buttons_state(root, "!disabled")
    except Exception:
        try:
            win.destroy()
        except Exception:
            pass
        _set_all_buttons_state(root, "!disabled")

class ProcessRunner:
    def __init__(self, console_append):
        self.proc = None
        self.console_append = console_append
        self.lock = threading.Lock()
    def run(self, cmd, cwd=None):
        with self.lock:
            if self.proc and self.proc.poll() is None:
                self.console_append("Un script est déjà en cours.\n")
                return
            try:
                self.console_append(f"\n$ {' '.join(cmd)}\n")
                self.proc = subprocess.Popen(
                    cmd, cwd=cwd, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, bufsize=1
                )
            except FileNotFoundError:
                self.console_append("Python ou le script est introuvable.\n")
                return
        def reader():
            try:
                for line in self.proc.stdout:
                    self.console_append(line)
            finally:
                rc = self.proc.poll()
                self.console_append(f"\n[Process terminé] Code: {rc}\n")
        threading.Thread(target=reader, daemon=True).start()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(*APP_MIN_SIZE)
        self.geometry("1100x700")

        self.style = ttk.Style(self)
        try:
            self.call("source", "sun-valley.tcl")
            self.style.theme_use("sun-valley-light")
        except Exception:
            try: self.style.theme_use("clam")
            except Exception: pass

        cfg = load_config()
        self.current_color = cfg.get("color_theme", "sky")

        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X)

        from tkinter import PhotoImage
        self._logo_small_ref = None
        self.logo_label = None
        logo_path = get_logo_path_from_config()
        if logo_path:
            try:
                img = PhotoImage(file=logo_path)
                w, h = img.width(), img.height()
                sx = max(1, int(w / 50)) if w > 50 else 1
                sy = max(1, int(h / 50)) if h > 50 else 1
                if sx > 1 or sy > 1:
                    img = img.subsample(sx, sy)
                self._logo_small_ref = img
                self.logo_label = ttk.Label(top, image=self._logo_small_ref)
                self.logo_label.pack(side=tk.LEFT, padx=10, pady=6)
            except Exception:
                self.logo_label = ttk.Label(top, text="667 SCRAPER", font=("Segoe UI", 14, "bold"))
                self.logo_label.pack(side=tk.LEFT, padx=10, pady=6)
        else:
            self.logo_label = ttk.Label(top, text="667 SCRAPER", font=("Segoe UI", 14, "bold"))
            self.logo_label.pack(side=tk.LEFT, padx=10, pady=6)

        center = ttk.Frame(top)
        center.pack(side=tk.LEFT, expand=True)

        self.session_dot = ttk.Label(center, text="●", font=("Segoe UI", 12, "bold"))
        self.session_dot.pack(anchor="center")
        self.session_var = tk.StringVar(value=translations[load_language()]["status_disconnected"])
        self.session_label = ttk.Label(center, textvariable=self.session_var, font=("Segoe UI", 11, "bold"))
        self.session_label.pack(anchor="center")

        ttk.Button(top, text=translations[load_language()]["btn_check_updates"],
                   command=lambda: check_update_gui(self, self.console_append)).pack(side=tk.RIGHT, padx=6)

        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True)

        nav = ttk.Frame(body)
        nav.pack(side=tk.LEFT, fill=tk.Y)

        self.content = ttk.Frame(body)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.content_left = ttk.Frame(self.content)
        self.content_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        console_frame = ttk.LabelFrame(self, text=translations[load_language()]["lbl_console"])
        console_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=8)
        self.console = tk.Text(console_frame, height=12, wrap="word")
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(console_frame, command=self.console.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.configure(yscrollcommand=sb.set)

        self.runner = ProcessRunner(self.console_append)

        ttk.Button(nav, text=translations[load_language()]["nav_home"], command=self.show_home).pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(nav, text=translations[load_language()]["nav_scraping"], command=self.show_scraping).pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(nav, text=translations[load_language()]["nav_tiktok"], command=self.show_tiktok).pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(nav, text=translations[load_language()]["nav_settings"], command=self.show_settings).pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(nav, text=translations[load_language()]["nav_changelog"], command=self.show_changelog).pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(nav, text=translations[load_language()]["nav_credits"], command=self.show_credits).pack(fill=tk.X, padx=6, pady=4)

        ttk.Button(nav, text="Region Changer", command=self.show_region_changer).pack(fill=tk.X, padx=6, pady=4)

        self.apply_color_theme(self.current_color)

        self._reset_session_status_on_start()

        self.show_home()
        self.after(800, lambda: check_update_gui(self, self.console_append))

        self._schedule_session_refresh()


    def _reset_session_status_on_start(self):
        try:
            payload = {"connected": False, "username": None, "when": None}
            SESSION_STATUS_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            self.session_var.set(translations[load_language()]["status_disconnected"])
            try: self.session_dot.configure(foreground="#c0392b")
            except Exception: pass
        except Exception:
            pass



    def _refresh_console_colors(self):
        cfg = load_config()
        color = cfg.get("color_theme", getattr(self, "current_color", "sky"))
        is_dark = cfg.get("theme", "dark") == "dark"

        console_bg = "#000000" if is_dark else "#ffffff"
        console_fg = "#e6e6e6" if is_dark else "#222222"
        insert = console_fg

        try:
            cols = getattr(self, "_console_colors", None)
            if cols and color in cols:
                variant = "dark" if is_dark else "light"
                console_bg = cols[color][variant]["bg"]
                console_fg = cols[color][variant]["fg"]
                insert = cols[color][variant].get("insert", console_fg)
        except Exception:
            pass

        try:
            preset = cfg.get("console_preset", "default")
            if preset and preset != "default":
                presets = {
                    "green": {"bg": "#001100", "fg": "#00ff55", "insert": "#00ff55"},
                    "amber": {"bg": "#0b0b00", "fg": "#ffcc66", "insert": "#ffcc66"},
                    "light": {"bg": "#ffffff", "fg": "#222222", "insert": "#000000"},
                }
                p = presets.get(preset)
                if p:
                    console_bg = p["bg"]
                    console_fg = p["fg"]
                    insert = p.get("insert", console_fg)
        except Exception:
            pass

        try:
            self.console.configure(bg=console_bg, fg=console_fg, insertbackground=insert)
        except Exception:
            if is_dark:
                self.console.configure(bg="#000000", fg="#e6e6e6", insertbackground="#e6e6e6")
            else:
                self.console.configure(bg="#ffffff", fg="#222222", insertbackground="#222222")

    def apply_color_theme(self, name: str):
        palette = {
            "sky":    {"accent": "#32A9E0", "accent_fg": "#ffffff", "bg": "#F4F6F8"},
            "blue":   {"accent": "#0B61A4", "accent_fg": "#ffffff", "bg": "#F3F5F8"},
            "red":    {"accent": "#D94343", "accent_fg": "#ffffff", "bg": "#F8F3F3"},
            "yellow": {"accent": "#E0B000", "accent_fg": "#111111", "bg": "#F8F6EE"},
            "pink":   {"accent": "#C671CE", "accent_fg": "#ffffff", "bg": "#FFF6FB"},
                "orange": {"accent": "#F57C00", "accent_fg": "#ffffff", "bg": "#FFF7ED"},
                "violet": {"accent": "#6A1B9A", "accent_fg": "#ffffff", "bg": "#F6F0FB"},
            "green":  {"accent": "#2E7D32", "accent_fg": "#ffffff", "bg": "#F1F7F2"},
        }
        if name not in palette:
            name = "sky"

        def darken(hex_color, factor=0.85):
            c = hex_color.lstrip("#")
            r = int(c[0:2], 16); g = int(c[2:4], 16); b = int(c[4:6], 16)
            r = max(0, min(255, int(r*factor)))
            g = max(0, min(255, int(g*factor)))
            b = max(0, min(255, int(b*factor)))
            return f"#{r:02x}{g:02x}{b:02x}"

        acc = palette[name]["accent"]
        acc_fg = palette[name]["accent_fg"]
        bg = palette[name]["bg"]

        hover = darken(acc, 0.9)
        active = darken(acc, 0.8)

        try:
            self.configure(bg=bg)
        except Exception:
            pass

        for sty in ("TFrame", "TLabelframe", "TLabel"):
            try:
                self.style.configure(sty, background=bg)
            except Exception:
                pass
        try:
            self.style.configure("TButton", background=acc, foreground=acc_fg, borderwidth=1, focusthickness=3, focuscolor=acc)
            self.style.map("TButton",
                           background=[("active", hover), ("pressed", active)],
                           foreground=[("disabled", "#888888")])
        except Exception:
            pass
        try:
            self.style.configure("TLabelframe.Label", background=bg, foreground=darken(acc, 0.7), font=("Segoe UI", 10, "bold"))
        except Exception:
            pass

        console_colors = {}
        for nm, p in palette.items():
            try:
                a = p["accent"]
                light_bg = p.get("bg", "#ffffff")
                light_fg = "#222222"
                dark_bg = darken(a, 0.12)
                dark_fg = "#e6e6e6"
                console_colors[nm] = {
                    "light": {"bg": light_bg, "fg": light_fg, "insert": a},
                    "dark":  {"bg": dark_bg,  "fg": dark_fg,  "insert": a},
                }
            except Exception:
                console_colors[nm] = {
                    "light": {"bg": "#ffffff", "fg": "#222222", "insert": "#000000"},
                    "dark":  {"bg": "#000000", "fg": "#e6e6e6", "insert": "#ffffff"},
                }

        self._console_colors = console_colors

        cfg = load_config()
        cfg["color_theme"] = name
        save_config(cfg)

        self.current_color = name
        try:
            self._refresh_console_colors()
        except Exception:
            pass

    def console_append(self, text: str):
        self.console.configure(state=tk.NORMAL)
        self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.console.configure(state=tk.NORMAL)

    def refresh_logo(self):
        from tkinter import PhotoImage
        self._logo_img = None
        logo_path = get_logo_path_from_config()
        if not self.logo_label:
            return
        try:
            self.logo_label.configure(image="", text="")
        except Exception:
            pass
        if not logo_path:
            try:
                self.logo_label.configure(text="667 SCRAPER")
            except Exception:
                pass
            return
        try:
            img = PhotoImage(file=logo_path)
            w, h = img.width(), img.height()
            max_w, max_h = 260, 260
            sx = max(1, (w + max_w - 1) // max_w) if w > max_w else 1
            sy = max(1, (h + max_h - 1) // max_h) if h > max_h else 1
            if sx > 1 or sy > 1:
                img = img.subsample(sx, sy)
            self._logo_img = img
            self.logo_label.configure(image=self._logo_img, text="")
        except Exception:
            self.logo_label.configure(text=str(logo_path))

    def clear_content(self):
        for w in self.content_left.winfo_children():
            w.destroy()

  
    def _read_session_status(self):
        """Lit Settings/session_status.json et retourne (connected: bool, username: str|None, when: int|None)."""
        try:
            if not SESSION_STATUS_FILE.exists():
                return False, None, None
            data = json.loads(SESSION_STATUS_FILE.read_text(encoding="utf-8"))
            return bool(data.get("connected")), data.get("username"), int(data.get("when") or 0)
        except Exception:
            return False, None, None
    def _fmt_duration(self, secs: int) -> str:
        secs = max(0, int(secs))
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"


    def _refresh_session_badge(self):
        lang = load_language()
        t = translations.get(lang, translations["fr"])
        connected, username, when = self._read_session_status()

        GREEN = "#27ae60"
        RED   = "#c0392b"

        if connected:
            elapsed_txt = ""
            if isinstance(when, int) and when > 0:
                elapsed = int(time.time()) - when
                elapsed_txt = f"  •  {t['status_for']} {self._fmt_duration(elapsed)}"
            name = f"@{username}" if username else t["status_connected"].lower()
            self.session_var.set(f"{t['status_connected']} : {name}{elapsed_txt}")
            try: self.session_dot.configure(foreground=GREEN)
            except Exception: pass
        else:
            self.session_var.set(t["status_disconnected"])
            try: self.session_dot.configure(foreground=RED)
            except Exception: pass


    def _schedule_session_refresh(self):
        """Rafraîchit l'état toutes les 3 secondes."""
        try:
            self._refresh_session_badge()
        finally:
            self.after(3000, self._schedule_session_refresh)

    def show_home(self):
        self.clear_content()
        frm = ttk.Frame(self.content_left)
        frm.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        center = ttk.Frame(frm)
        center.place(relx=0.5, rely=0.3, anchor="center")
        lang = load_language(); t = translations.get(lang, translations["fr"])
        title = t.get("menu_title", "★ New Release {version} ★").format(version=LOCAL_VERSION)
        ttk.Label(center, text=title, font=("Segoe UI", 18, "bold")).pack(anchor="center")
        ttk.Label(center, text=t["home_welcome"]).pack(anchor="center", pady=(6, 0))

    def show_scraping(self):
        self.clear_content()
        base = ttk.Frame(self.content_left); base.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        frm = ttk.Frame(base); frm.pack(expand=True)
        lang = load_language(); t = translations.get(lang, translations["fr"])
        ttk.Label(frm, text=t["submenu_1_title"], font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        buttons = [
            (t["option_1"], "Codes/Scripts/a.py"),
            (t["option_2"], "Codes/Scripts/b.py"),
            (t["option_3"], None),
            (t["option_4"], "__OPEN_PANEL__"),
            ("Start script : (Collect Profiles + emails + acc's info's)", "__RUN_C__"),
            (t["option_v"], "Codes/Scripts/check_verified.py"),
        ]
        for i, (label, target) in enumerate(buttons, start=1):
            def make_cmd(target=target):
                if target == "__OPEN_PANEL__": return self.open_hashtag_panel
                elif target == "__RUN_C__":     return self.run_c_with_desired
                elif target is None:            return self.run_Scripts_automatic
                else:                           return lambda: self.run_script(target)
            ttk.Button(frm, text=label, command=make_cmd()).grid(row=i, column=0, sticky="w", pady=4)
        ttk.Button(frm, text=translations[load_language()]["return_menu"], command=self.show_home).grid(row=len(buttons)+1, column=0, pady=(12,0), sticky="w")

    def show_tiktok(self):
        self.clear_content()
        base = ttk.Frame(self.content_left); base.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        frm = ttk.Frame(base); frm.pack(expand=True)
        lang = load_language(); t = translations.get(lang, translations["fr"])
        ttk.Label(frm, text=t["submenu_2_title"], font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Button(frm, text=t["option_t"], command=self.show_tuto).grid(row=1, column=0, sticky="w", pady=4)
        ttk.Button(frm, text=translations[load_language()]["btn_send_telegram"], command=lambda: self.run_script("Codes/second_script/telegram_sender.py")).grid(row=2, column=0, sticky="w", pady=4)
        ttk.Button(frm, text=translations[load_language()]["btn_infinite_report"], command=lambda: self.run_script("Codes/second_script/tiktok_info.py")).grid(row=3, column=0, sticky="w", pady=4)
        ttk.Button(frm, text=t["option_cc"], command=lambda: self.run_script("Codes/second_script/cleaner.py")).grid(row=4, column=0, sticky="w", pady=4)
        ttk.Button(frm, text=translations[load_language()]["btn_convert_cookies"], command=lambda: self.run_script("Codes/second_script/cc.py")).grid(row=5, column=0, sticky="w", pady=4)
        ttk.Button(frm, text=t["return_menu"], command=self.show_home).grid(row=6, column=0, pady=(12,0), sticky="w")

    def show_settings(self):
        self.clear_content()
        outer = ttk.Frame(self.content_left); outer.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        frm = ttk.Frame(outer); frm.pack(expand=True, anchor="w")
        lang = load_language(); t = translations.get(lang, translations["fr"])
        ttk.Label(frm, text=t["submenu_3_title"], font=("Segoe UI", 14, "bold")).pack(anchor="w")

        cfg = load_config()

        row1 = ttk.Frame(frm); row1.pack(anchor="w", pady=8)
        ttk.Label(row1, text=t["option_s"]).pack(side=tk.LEFT)
        scroll_var = tk.IntVar(value=int(cfg.get("scrolls", 10)))
        ttk.Spinbox(row1, from_=1, to=10000, width=8, textvariable=scroll_var).pack(side=tk.LEFT, padx=8)
        ttk.Button(row1, text=translations[load_language()]["btn_save"], command=lambda: self._save_scrolls(scroll_var.get())).pack(side=tk.LEFT)

        row2 = ttk.Frame(frm); row2.pack(anchor="w", pady=8)
        ttk.Label(row2, text=t["option_c"]).pack(side=tk.LEFT)
        lang_var = tk.StringVar(value=lang)
        for code, label in [("fr", "Français"), ("en", "English")]:
            ttk.Radiobutton(row2, text=label, value=code, variable=lang_var, command=lambda lv=lang_var: self._change_lang(lv.get())).pack(side=tk.LEFT, padx=6)


        row4 = ttk.Frame(frm); row4.pack(anchor="w", pady=8)
        ttk.Label(row4, text=t["option_color"]).pack(side=tk.LEFT)
        color_labels = [t["color_sky"], t["color_blue"], t["color_red"], t["color_yellow"], t["color_pink"], t["color_orange"], t["color_violet"], t["color_green"]]
        color_map = {
            t["color_sky"]: "sky",
            t["color_blue"]: "blue",
            t["color_red"]: "red",
            t["color_yellow"]: "yellow",
            t["color_pink"]: "pink",
            t["color_orange"]: "orange",
            t["color_violet"]: "violet",
            t["color_green"]: "green",
        }
        inv_color_map = {v: k for k, v in color_map.items()}
        color_var = tk.StringVar(value=inv_color_map.get(cfg.get("color_theme","sky"), t["color_sky"]))
        ttk.Combobox(row4, textvariable=color_var, values=color_labels, width=16, state="readonly").pack(side=tk.LEFT, padx=8)
        ttk.Button(row4, text=translations[load_language()]["btn_save"], command=lambda: self._save_color_theme(color_map[color_var.get()])).pack(side=tk.LEFT)

        row4b = ttk.Frame(frm); row4b.pack(anchor="w", pady=8)
        ttk.Label(row4b, text=t["option_console_preset"]).pack(side=tk.LEFT)
        preset_labels = [t["console_preset_default"], t["console_preset_green"], t["console_preset_amber"], t["console_preset_light"]]
        preset_map = {
            t["console_preset_default"]: "default",
            t["console_preset_green"]: "green",
            t["console_preset_amber"]: "amber",
            t["console_preset_light"]: "light",
        }
        inv_preset_map = {v: k for k, v in preset_map.items()}
        console_preset_var = tk.StringVar(value=inv_preset_map.get(cfg.get("console_preset","default"), t["console_preset_default"]))
        ttk.Combobox(row4b, textvariable=console_preset_var, values=preset_labels, width=18, state="readonly").pack(side=tk.LEFT, padx=8)
        ttk.Button(row4b, text=translations[load_language()]["btn_save"], command=lambda: self._save_console_preset(preset_map[console_preset_var.get()])).pack(side=tk.LEFT)

        row5 = ttk.Frame(frm); row5.pack(anchor="w", pady=8)
        ttk.Label(row5, text=t["option_logo"]).pack(side=tk.LEFT)
        pngs = list_settings_pngs()
        logo_var = tk.StringVar(value=cfg.get("logo_png", ""))
        ttk.Combobox(row5, textvariable=logo_var, values=pngs, state="readonly", width=28).pack(side=tk.LEFT, padx=8)
        ttk.Button(row5, text=translations[load_language()]["btn_save"], command=lambda: self._save_logo_png(logo_var.get())).pack(side=tk.LEFT)

        ttk.Button(frm, text=t["option_l"], command=self.show_changelog).pack(anchor="w", pady=(10,0))

    def show_changelog(self):
        self.clear_content()
        frm = ttk.Frame(self.content_left); frm.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        lang = load_language(); t = translations.get(lang, translations["fr"])
        ttk.Label(frm, text=t.get("changelogs_title", "Changelogs"), font=("Segoe UI", 14, "bold")).pack(anchor="w")
        txt = tk.Text(frm, height=18, wrap="word"); txt.pack(fill=tk.BOTH, expand=True)
        lines = t.get("changelogs_lines", ["", "Changelogs :", "No entries."])
        txt.insert("1.0", "\n".join(lines))
        txt.configure(state=tk.DISABLED)

    def show_credits(self):
        self.clear_content()
        frm = ttk.Frame(self.content_left); frm.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        lang = load_language(); t = translations.get(lang, translations["fr"])
        ttk.Label(frm, text=t.get("credits_title", "Credits"), font=("Segoe UI", 14, "bold")).pack(anchor="w")
        txt = tk.Text(frm, height=8, wrap="word"); txt.pack(fill=tk.BOTH, expand=True)
        lines = t.get("credits_lines", ["dev @enabIe idea from @repient RU translation s/O : @?????"])
        txt.insert("1.0", "\n".join(lines))
        txt.configure(state=tk.DISABLED)

    def show_tuto(self):
        top = tk.Toplevel(self); top.title(translations[load_language()]["tuto_title"]); top.geometry("700x600")
        msg = ("=== Tuto Tiktok Scrapper + checker ===\n\n"
               "1/ Collecte de profils → tiktok_profiles.txt\n"
               "2/ Filtrage emails dans la bio → profiles_with_email.txt\n"
               "3/ Mode complet : enchaîne 1 puis 2\n"
               "4/ Hashtag scraper (#foryou, #trend, ...)\n"
               "5/ Comptes certifiés\n"
               "6/ Infos publiques API\n"
               "7/ Nettoyage fichiers .txt\n"
               "8/ Paramètres : langue, scroll, thème, couleur, logo\n")
        t = tk.Text(top, wrap="word"); t.pack(fill=tk.BOTH, expand=True); t.insert("1.0", msg); t.configure(state=tk.DISABLED)

    def run_script(self, script_path: str):
        if not Path(script_path).exists():
            messagebox.showerror(translations[load_language()]["not_found_title"], translations[load_language()]["not_found_text"].format(path=script_path))
            return
        ProcessRunner(self.console_append).run([sys.executable, script_path])

    def run_Scripts_automatic(self):
        seq = ["Codes/Scripts/a.py", "Codes/Scripts/b.py"]
        def run_next(i=0):
            if i >= len(seq): return
            path = seq[i]
            if not Path(path).exists():
                self.console_append(f"Introuvable: {path}")
                run_next(i+1); return
            runner = ProcessRunner(self.console_append)
            runner.run([sys.executable, path])
            def waiter():
                while runner.proc and runner.proc.poll() is None:
                    time.sleep(0.2)
                run_next(i+1)
            threading.Thread(target=waiter, daemon=True).start()
        run_next(0)

    def run_c_with_desired(self):
        try:
            desired = simpledialog.askinteger(
                translations[load_language()]["ask_custom_scraper_title"],
                translations[load_language()]["ask_custom_scraper_body"],
                minvalue=1, initialvalue=150, parent=self)
        except Exception:
            desired = None
        if desired is None: return
        script_path = "Codes/Scripts/c.py"
        if not Path(script_path).exists():
            messagebox.showerror("Introuvable", f"Le script n'existe pas : {script_path}"); return
        ProcessRunner(self.console_append).run([sys.executable, script_path, "--desired", str(desired)])


    def open_hashtag_panel(self):
        lang = load_language(); t = translations.get(lang, translations["fr"])
        top = tk.Toplevel(self); top.title(t["panel_header"]); top.geometry("420x420")
        scripts = {
            '#fyp': "Codes/Scripts/fyp.py",
            '#trend': "Codes/Scripts/trend.py",
            '#foryou': "Codes/Scripts/foryou.py",
            '#famous': "Codes/Scripts/famous.py",
            '#love': "Codes/Scripts/love.py",
            '#mood': "Codes/Scripts/mood.py",
            '#pourtoi': "Codes/Scripts/pourtoi.py",
            translations[load_language()]["panel_create_personal"]: "Codes/Scripts/createscraper.py",
        }
        for tag, path in scripts.items():
            ttk.Button(top, text=tag, command=(lambda p=path: self.run_script(p))).pack(fill=tk.X, padx=12, pady=6)

    def _save_scrolls(self, value: int):
        cfg = load_config(); cfg["scrolls"] = int(value); save_config(cfg)
        messagebox.showinfo(translations[load_language()]["ok_title"], translations[load_language()]["saved_param"])

    def _change_lang(self, lang_code: str):
        save_language(lang_code)
        messagebox.showinfo(translations[load_language()]["lang_title"], translations[load_language()]["lang_changed"])

    def _save_logo_png(self, filename: str):
        cfg = load_config()
        if filename: cfg["logo_png"] = filename
        else: cfg.pop("logo_png", None)
        save_config(cfg)
        messagebox.showinfo(translations[load_language()]["ok_title"], translations[load_language()]["logo_saved"])
        try: self.refresh_logo()
        except Exception: pass


    def _save_color_theme(self, name: str):
        self.apply_color_theme(name)
        messagebox.showinfo(translations[load_language()]["ok_title"], translations[load_language()]["color_saved"])

    def _save_console_preset(self, name: str):
        cfg = load_config()
        if name and name != "default":
            cfg["console_preset"] = name
        else:
            cfg.pop("console_preset", None)
        save_config(cfg)
        messagebox.showinfo(translations[load_language()]["ok_title"], translations[load_language()]["console_preset_saved"])
        try:
            self._refresh_console_colors()
        except Exception:
            pass

    def show_region_changer(self):
        """Show the Region Changer tab: lists cookie files in acc/cookies and allows launching ttkccfnf.py with the selection."""
        self.clear_content()
        frm = ttk.Frame(self.content_left); frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        ttk.Label(frm, text="Region Changer - acc/cookies", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0,8))

        list_frame = ttk.Frame(frm)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.rc_listbox = tk.Listbox(list_frame, height=12, selectmode=tk.SINGLE)
        self.rc_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lb_sb = ttk.Scrollbar(list_frame, command=self.rc_listbox.yview)
        lb_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.rc_listbox.configure(yscrollcommand=lb_sb.set)

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(anchor="w", pady=(8,0))

        ttk.Button(btn_frame, text="Refresh", command=self._rc_refresh_list).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Launch", command=self._rc_launch_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text=translations[load_language()]["return_menu"], command=self.show_home).pack(side=tk.LEFT, padx=12)

        self._rc_refresh_list()

    def _rc_cookie_files(self):
        """Return sorted list of cookie files found in acc/cookies/ (full paths)."""
        import glob
        search_dir = os.path.join("acc", "cookies")
        if not os.path.isdir(search_dir):
            return []
        patterns = ["frenchacc_*.txt", "frenchacc_*.json", "*.txt", "*.json"]
        files = []
        for p in patterns:
            files.extend(glob.glob(os.path.join(search_dir, p)))
        files = sorted(dict.fromkeys(files))
        return files

    def _rc_refresh_list(self):
        self.rc_listbox.delete(0, tk.END)
        files = self._rc_cookie_files()
        if not files:
            self.rc_listbox.insert(tk.END, "(no cookie files found in acc/cookies/)")
            return
        for f in files:
            self.rc_listbox.insert(tk.END, os.path.basename(f))

    def _rc_launch_selected(self):
        idx = self.rc_listbox.curselection()
        if not idx:
            messagebox.showerror("Selection requise", "Choisir un fichier cookie dans la liste.")
            return
        index = idx[0]
        files = self._rc_cookie_files()
        if index >= len(files):
            messagebox.showerror("Erreur", "Sélection invalide.")
            return
        cookie_path = files[index]
        threading.Thread(target=self._rc_run_ttkinject, args=(index, cookie_path, files), daemon=True).start()

    def _rc_run_ttkinject(self, index, cookie_path, files):
        """
        Launch ttkccfnf.py and automatically provide the chosen index.
        The ttkccfnf.py script prints the list then waits input("Choose an account by number...").
        We start it and immediately send the appropriate number (1-based).
        Stream output into the app console.
        """
        script = "ttkccfnf.py"
        if not Path(script).exists():
            alt1 = Path("Codes") / "tiktok_cookies_changer_for_new_fyp" / "ttkccfnf.py"
            alt2 = Path("Codes") / "ttkccfnf.py"
            if alt1.exists():
                script = str(alt1)
            elif alt2.exists():
                script = str(alt2)
            else:
                self.console_append(f"Script {script} introuvable.\n")
                return

        cmd = [sys.executable, script]
        try:
            self.console_append(f"\n$ {' '.join(cmd)}\n")
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        except Exception as e:
            self.console_append(f"Impossible de lancer le script: {e}\n")
            return

        def reader():
            try:
                for line in proc.stdout:
                    self.console_append(line)
            except Exception as e:
                self.console_append(f"[reader error] {e}\n")
            finally:
                rc = proc.poll()
                self.console_append(f"\n[Process terminé] Code: {rc}\n")

        threading.Thread(target=reader, daemon=True).start()

        try:
            to_send = f"{index+1}\n"
            proc.stdin.write(to_send)
            proc.stdin.flush()
        except Exception as e:
            self.console_append(f"Impossible d'envoyer la sélection au script: {e}\n")

        # ping le badge pendant/à la fin du script (ajouté)
        def ping_refresh():
            for _ in range(15):  # ~30s (2s * 15)
                if proc.poll() is not None:
                    break
                try:
                    self._refresh_session_badge()
                except Exception:
                    pass
                time.sleep(2)
            try:
                self._refresh_session_badge()
            except Exception:
                pass
        threading.Thread(target=ping_refresh, daemon=True).start()



    def show_changelog(self):
        self.clear_content()
        frm = ttk.Frame(self.content_left); frm.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        lang = load_language(); t = translations.get(lang, translations["fr"])
        ttk.Label(frm, text=t.get("changelogs_title", "Changelogs"), font=("Segoe UI", 14, "bold")).pack(anchor="w")
        txt = tk.Text(frm, height=18, wrap="word"); txt.pack(fill=tk.BOTH, expand=True)
        lines = t.get("changelogs_lines", ["", "Changelogs :", "No entries."])
        txt.insert("1.0", "\n".join(lines))
        txt.configure(state=tk.DISABLED)

if __name__ == "__main__":
    app = App()
    app.mainloop()



