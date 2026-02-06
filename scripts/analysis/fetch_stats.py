import requests
import json
import time

BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
YEAR_MIN, YEAR_MAX = 1850, 1920
LANGUAGES = [None, "jpn", "eng", "chi", "ger", "fre", "rus", "ita", "spa", "kor"]
LANG_MAP = {
    None: "TOTAL (ALL)",
    "jpn": "Japonés (JP)",
    "eng": "Inglés (EN)",
    "chi": "Chino (ZH)",
    "ger": "Alemán (DE)",
    "fre": "Francés (FR)",
    "rus": "Ruso (RU)",
    "ita": "Italiano (IT)",
    "spa": "Español (ES)",
    "kor": "Coreano (KO)"
}

results = {}

import sys
sys.stdout.reconfigure(line_buffering=True)
print(f"Obteniendo estadísticas de {YEAR_MIN} a {YEAR_MAX}...", flush=True)

for year in range(YEAR_MIN, YEAR_MAX + 1):
    year_stats = {}
    for lang in LANGUAGES:
        params = {
            "format": "json",
            "year_from": year,
            "year_to": year,
            "count": 1,
            "type": "0"
        }
        if lang: params["lang"] = lang
        
        try:
            r = requests.get(BASE_URL, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                total = int(data.get("@graph", [{}])[0].get("opensearch:totalResults", 0))
                year_stats[LANG_MAP[lang]] = total
            else:
                year_stats[LANG_MAP[lang]] = "Error"
        except:
            year_stats[LANG_MAP[lang]] = "Error"
        
        time.sleep(0.1) # Muy breve para no ser lento pero no saturar
    
    results[year] = year_stats
    print(f"Año {year} procesado.", flush=True)

with open("cinii_full_stats.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("Estadísticas completadas y guardadas en cinii_full_stats.json")
