import os

FILES_TO_CLEAN = [
    "txt_files/tiktok_profiles.txt",
    "txt_files/profiles_with_email.txt",
    "txt_files/verified_profiles.txt",
    "txt_files/info_accs.txt"
]

def clean_files(file_paths):
    for path in file_paths:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            print(f"[OK] Clean ! : {path}")
        except Exception as e:
            print(f"[x] Error {path} : {e}")

if __name__ == "__main__":
    clean_files(FILES_TO_CLEAN)
