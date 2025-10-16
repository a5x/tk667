import os

# Liste des fichiers à nettoyer
FILES_TO_CLEAN = [
    "Scripts_info_extract/tiktok_profiles.txt",
    "Scripts_info_extract/profiles_with_email.txt",
    "Scripts_info_extract/info_accs.txt"
]

def clean_files(file_paths):
    for path in file_paths:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            print(f"[✓] Clean ! : {path}")
        except Exception as e:
            print(f"[×] Error {path} : {e}")

if __name__ == "__main__":
    clean_files(FILES_TO_CLEAN)
