import subprocess
import sys

required_packages = [
    "selenium",
    "requests",
    "beautifulsoup4",
    "colorama"
]

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in required_packages:
    try:
        print(f"Installation de {pkg}...")
        install(pkg)
    except Exception as e:
        print(f"Erreur lors de l'installation de {pkg} : {e}")

print("✅ Installation terminée.")
