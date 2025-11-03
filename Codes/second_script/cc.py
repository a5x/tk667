import json
import os

input_path = "Settings/cookies.json"
output_path = "Settings/converted_cookies.json"

def convert_same_site(value):
    if value.lower() in ["lax", "lax_mode", "laxmode"]:
        return "Lax"
    elif value.lower() in ["strict"]:
        return "Strict"
    elif value.lower() in ["no_restriction", "none", "unspecified"]:
        return "None"
    return "Lax"

with open(input_path, "r", encoding="utf-8") as f:
    original = json.load(f)

converted = []
for c in original:
    new_cookie = {
        "name": c["name"],
        "value": c["value"],
        "domain": c["domain"],
        "path": c.get("path", "/"),
        "secure": c.get("secure", True),
        "httpOnly": c.get("httpOnly", False),
        "sameSite": convert_same_site(c.get("sameSite", "Lax"))
    }
    if "expirationDate" in c:
        new_cookie["expires"] = int(c["expirationDate"])
    converted.append(new_cookie)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(converted, f, indent=4)

print(f"OK Conversion terminée ! Fichier prêt pour Playwright : {output_path}")
