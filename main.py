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

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

try:
    import requests
except Exception:
    requests = None

APP_TITLE = "667 SCRAPER"
APP_MIN_SIZE = (1024, 640)

LOCAL_VERSION = "2.4"
GITHUB_OWNER  = "a5x"
GITHUB_REPO   = "tk667"
GITHUB_BRANCH = "main"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/main/version.txt"

PRESERVE_PATHS = [
    "Settings/lang_config.json",
    "Settings/config.json",
    "txt_files/",
]

translations = {
    "fr": {
        "menu_title": "========= New Release 2.1 =========",
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
        "option_logo": "Logo (PNG dans Settings)",
        "logo_saved": "Logo mis à jour.",
        "option_color": "Couleur (UI)",
        "color_sky": "Bleu ciel",
        "color_blue": "Bleu foncé",
        "color_red": "Rouge",
        "color_yellow": "Jaune",
        "color_green": "Vert",
        "color_saved": "Couleur appliquée."
    },
    "en": {
        "menu_title": "========= New Release 2.1 =========",
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
        "option_logo": "Logo (PNG in Settings)",
        "logo_saved": "Logo updated.",
        "option_color": "Color (UI)",
        "color_sky": "Sky blue",
        "color_blue": "Dark blue",
        "color_red": "Red",
        "color_yellow": "Yellow",
        "color_green": "Green",
        "color_saved": "Color applied."
    }
}

SETTINGS_DIR = Path("Settings")
SETTINGS_DIR.mkdir(exist_ok=True)
LANG_FILE = SETTINGS_DIR / "lang_config.json"
CONFIG_FILE = SETTINGS_DIR / "config.json"

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

def check_update_gui(root: tk.Tk, console_append):
    if not requests:
        return
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
        except Exception as e:
            console_append(f"Update checking failed : {e}\n")
    threading.Thread(target=task, daemon=True).start()

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
        self.current_theme = cfg.get("theme", "dark")
        self.current_color = cfg.get("color_theme", "sky")

        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(top, text=APP_TITLE, font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=10, pady=6)
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

        self.logo_panel = ttk.Frame(self.content, width=280)
        self.logo_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.logo_panel.pack_propagate(False)
        self._logo_img = None
        self.logo_label = ttk.Label(self.logo_panel)
        self.logo_label.pack(anchor="ne", padx=8, pady=8)
        ttk.Label(self.logo_panel, text="(Place PNGs in Settings/ and choose one in Settings)").pack(anchor="ne")
        try: self.refresh_logo()
        except Exception: pass

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

        self.apply_theme(self.current_theme)
        self.apply_color_theme(self.current_color)

        self.show_home()
        self.after(800, lambda: check_update_gui(self, self.console_append))

    def is_dark(self) -> bool:
        return load_config().get("theme", "dark") == "dark"

    def _refresh_console_colors(self):
        if self.is_dark():
            self.console.configure(bg="#000000", fg="#e6e6e6", insertbackground="#e6e6e6")
        else:
            self.console.configure(bg="#ffffff", fg="#222222", insertbackground="#222222")

    def apply_theme(self, pref: str):
        try:
            self.style.theme_use("sun-valley-light")
        except Exception:
            pass
        self._refresh_console_colors()
        cfg = load_config()
        cfg["theme"] = pref
        save_config(cfg)

    def apply_color_theme(self, name: str):
        """
        Accent color for the whole UI (buttons/frames/labels/hover).
        Options: 'sky', 'blue', 'red', 'yellow', 'green'
        """
        palette = {
            "sky":    {"accent": "#32A9E0", "accent_fg": "#ffffff", "bg": "#F4F6F8"},
            "blue":   {"accent": "#0B61A4", "accent_fg": "#ffffff", "bg": "#F3F5F8"},
            "red":    {"accent": "#D94343", "accent_fg": "#ffffff", "bg": "#F8F3F3"},
            "yellow": {"accent": "#E0B000", "accent_fg": "#111111", "bg": "#F8F6EE"},
            "green":  {"accent": "#2E7D32", "accent_fg": "#ffffff", "bg": "#F1F7F2"},
        }
        if name not in palette:
            name = "sky"
        acc  = palette[name]["accent"]
        acc_fg = palette[name]["accent_fg"]
        bg   = palette[name]["bg"]

        def darken(hex_color, factor=0.85):
            c = hex_color.lstrip("#")
            r = int(c[0:2], 16); g = int(c[2:4], 16); b = int(c[4:6], 16)
            r = max(0, min(255, int(r*factor)))
            g = max(0, min(255, int(g*factor)))
            b = max(0, min(255, int(b*factor)))
            return f"#{r:02x}{g:02x}{b:02x}"

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

        cfg = load_config()
        cfg["color_theme"] = name
        save_config(cfg)

    def console_append(self, text: str):
        self.console.configure(state=tk.NORMAL)
        self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.console.configure(state=tk.NORMAL)

    def refresh_logo(self):
        from tkinter import PhotoImage
        self._logo_img = None
        logo_path = get_logo_path_from_config()
        try:
            self.logo_label.configure(image="", text="")
        except Exception:
            pass
        if not logo_path:
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
            self.logo_label.configure(image=self._logo_img)
        except Exception:
            self.logo_label.configure(text=str(logo_path))

    def clear_content(self):
        for w in self.content_left.winfo_children():
            w.destroy()

    def show_home(self):
        self.clear_content()
        frm = ttk.Frame(self.content_left)
        frm.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        center = ttk.Frame(frm)
        center.place(relx=0.5, rely=0.3, anchor="center")
        lang = load_language(); t = translations.get(lang, translations["fr"])
        ttk.Label(center, text=t["menu_title"], font=("Segoe UI", 16, "bold")).pack(anchor="center")
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

        row3 = ttk.Frame(frm); row3.pack(anchor="w", pady=8)
        ttk.Label(row3, text=t["option_theme"]).pack(side=tk.LEFT)
        theme_map = {t["theme_system"]: "system", t["theme_light"]: "light", t["theme_dark"]: "dark"}
        inv_theme_map = {v: k for k, v in theme_map.items()}
        theme_var = tk.StringVar(value=inv_theme_map.get(cfg.get("theme","dark"), t["theme_dark"]))
        ttk.Combobox(row3, textvariable=theme_var, values=list(theme_map.keys()), width=12, state="readonly").pack(side=tk.LEFT, padx=8)
        ttk.Button(row3, text=translations[load_language()]["btn_save"], command=lambda: self._save_theme(theme_map.get(theme_var.get(),"dark"))).pack(side=tk.LEFT)

        row4 = ttk.Frame(frm); row4.pack(anchor="w", pady=8)
        ttk.Label(row4, text=t["option_color"]).pack(side=tk.LEFT)
        color_labels = [t["color_sky"], t["color_blue"], t["color_red"], t["color_yellow"], t["color_green"]]
        color_map = {
            t["color_sky"]: "sky",
            t["color_blue"]: "blue",
            t["color_red"]: "red",
            t["color_yellow"]: "yellow",
            t["color_green"]: "green",
        }
        inv_color_map = {v: k for k, v in color_map.items()}
        color_var = tk.StringVar(value=inv_color_map.get(cfg.get("color_theme","sky"), t["color_sky"]))
        ttk.Combobox(row4, textvariable=color_var, values=color_labels, width=16, state="readonly").pack(side=tk.LEFT, padx=8)
        ttk.Button(row4, text=translations[load_language()]["btn_save"], command=lambda: self._save_color_theme(color_map[color_var.get()])).pack(side=tk.LEFT)

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
        ttk.Label(frm, text="Changelogs", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        txt = tk.Text(frm, height=18, wrap="word"); txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", "\n".join([
            "", "Changelogs :", "2.3 : Couleurs d’interface (Bleu ciel, Bleu foncé, Rouge, Jaune, Vert).",
            "2.2 : Sélecteur thème console (clair/sombre).", "2.1 : Script nombre de comptes voulu.",
            "2.0 : Corrections et optimisations.", "1.9 : Telegram file sender.",
            "1.8 : Cleaner + comptes certif.", "1.7 : Scraper hashtag custom.",
            "1.6 : Scraper hashtag.", "1.5 : Rework Codes/Scripts.",
            "1.4 : UI Update.", "1.3 : Scripts chainés + TikTok info.",
            "1.2 : Choix de la langue.", "1.1 : Paramètres.", "1.0 : Initial."
        ]))
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

    def _save_theme(self, pref: str):
        self.apply_theme(pref)
        messagebox.showinfo(translations[load_language()]["ok_title"], translations[load_language()]["theme_saved"])

    def _save_color_theme(self, name: str):
        self.apply_color_theme(name)
        messagebox.showinfo(translations[load_language()]["ok_title"], translations[load_language()]["color_saved"])

if __name__ == "__main__":
    app = App()
    app.mainloop()
