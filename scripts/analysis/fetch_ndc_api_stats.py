import os
import json
import time
import requests
from collections import defaultdict

BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
YEAR_MIN, YEAR_MAX = 1850, 1920
DELAY = 0.5  # Slightly faster since we only fetch counts
DATA_FILE = "cinii_ndc_api_counts.json"
REPORT_FILE = "cinii_resumen_ndc_api.md"

LANG_MAP = {
    "jpn": "JP",
    "eng": "EN",
    "chi": "ZH",
    "ger": "DE",
    "fre": "FR",
    "rus": "RU",
    "ita": "IT",
    "spa": "ES",
    "kor": "KO"
}

NDC_LIST = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
NDC_NAMES = {
    "0": "Generalidades",
    "1": "Filosofía",
    "2": "Historia",
    "3": "Ciencias Sociales",
    "4": "Ciencias Naturales",
    "5": "Tecnología",
    "6": "Industria",
    "7": "Artes",
    "8": "Lenguaje",
    "9": "Literatura"
}

def get_appid():
    path = "api_keys"
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if "cinii=" in line and not line.strip().startswith("#"):
                    return line.strip().split("=")[1]
    return None

def fetch_count(year, lang=None, ndc=None, appid=None):
    params = {
        "format": "json",
        "year_from": year,
        "year_to": year,
        "count": 0,  # We just want the metadata including totalResults
        "type": "0"
    }
    if lang: params["lang"] = lang
    if ndc: params["clas"] = f"NDC{ndc}*"
    if appid: params["appid"] = appid

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return int(data.get("@graph", [{}])[0].get("opensearch:totalResults", 0))
    except Exception as e:
        print(f"\nError fetching {year} {lang} {ndc}: {e}")
        return None

def main():
    appid = get_appid()
    if appid: print(f"Using AppID: {appid}")

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_counts = json.load(f)
    else:
        all_counts = {}

    try:
        for year in range(YEAR_MIN, YEAR_MAX + 1):
            y_str = str(year)
            if y_str not in all_counts:
                all_counts[y_str] = {}
            
            print(f"Processing Year {year}...")
            
            for ndc in NDC_LIST:
                if ndc not in all_counts[y_str]:
                    all_counts[y_str][ndc] = {}
                
                # Check total for this NDC first
                if "TOTAL" not in all_counts[y_str][ndc]:
                    count = fetch_count(year, ndc=ndc, appid=appid)
                    if count is None: continue
                    all_counts[y_str][ndc]["TOTAL"] = count
                    time.sleep(DELAY)
                
                total_for_ndc = all_counts[y_str][ndc]["TOTAL"]
                
                if total_for_ndc > 0:
                    for l_code, l_short in LANG_MAP.items():
                        if l_short not in all_counts[y_str][ndc]:
                            count = fetch_count(year, lang=l_code, ndc=ndc, appid=appid)
                            if count is None: continue
                            all_counts[y_str][ndc][l_short] = count
                            time.sleep(DELAY)
                else:
                    # Skip languages if total is 0
                    pass
            
            # Save every year to avoid data loss
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(all_counts, f, indent=4)

    except KeyboardInterrupt:
        print("\nStopped by user.")

    # Generate Report
    print("Generating report...")
    generate_markdown(all_counts)

def generate_markdown(all_counts):
    global_ndc = defaultdict(lambda: defaultdict(int))
    decade_ndc = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    years = sorted(all_counts.keys())
    
    for year_str in years:
        year = int(year_str)
        decade = (year // 10) * 10
        for ndc, langs in all_counts[year_str].items():
            for lang, count in langs.items():
                if lang == "TOTAL":
                    global_ndc[ndc]["TOTAL"] += count
                    decade_ndc[decade][ndc]["TOTAL"] += count
                else:
                    global_ndc[ndc][lang] += count
                    decade_ndc[decade][ndc][lang] += count

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# Resumen Estadístico por Materia (NDC) - API CiNii (1850-1920)\n\n")
        f.write("*Nota: Datos obtenidos directamente de la API de CiNii (opensearch:totalResults)*\n\n")
        
        f.write("## Resumen Global por Materia\n\n")
        for ndc in sorted(NDC_LIST):
            name = NDC_NAMES[ndc]
            total = global_ndc[ndc]["TOTAL"]
            f.write(f"### NDC {ndc}: {name}\n")
            f.write(f"- **Total de registros:** {total:,}\n\n")
            if total > 0:
                f.write("| Idioma | Cantidad | Porcentaje |\n")
                f.write("| :--- | :---: | :---: |\n")
                langs = sorted([(l, c) for l, c in global_ndc[ndc].items() if l != "TOTAL" and c > 0], key=lambda x: x[1], reverse=True)
                for l_short, count in langs:
                    perc = (count / total) * 100
                    f.write(f"| {l_short} | {count:,} | {perc:.2f}% |\n")
                f.write("\n")
            else:
                f.write("*Sin registros*\n\n")

        f.write("## Resumen por Décadas\n\n")
        for decade in sorted(decade_ndc.keys()):
            f.write(f"### Década de {decade}\n")
            total_dec = sum(decade_ndc[decade][n]["TOTAL"] for n in NDC_LIST)
            f.write(f"- **Total de registros:** {total_dec:,}\n\n")
            f.write("| NDC | Materia | Idioma | Cantidad | % |\n")
            f.write("| :---: | :--- | :--- | :---: | :---: |\n")
            for ndc in sorted(NDC_LIST):
                total_ndc_dec = decade_ndc[decade][ndc]["TOTAL"]
                if total_ndc_dec > 0:
                    langs = sorted([(l, c) for l, c in decade_ndc[decade][ndc].items() if l != "TOTAL" and c > 0], key=lambda x: x[1], reverse=True)
                    for i, (l_short, count) in enumerate(langs):
                        perc = (count / total_ndc_dec) * 100
                        n_code = ndc if i == 0 else ""
                        n_name = NDC_NAMES[ndc] if i == 0 else ""
                        f.write(f"| {n_code} | {n_name} | {l_short} | {count:,} | {perc:.2f}% |\n")
            f.write("\n")

        f.write("## Desglose por Años\n\n")
        for year_str in years:
            f.write(f"### Año {year_str}\n")
            year_total = sum(all_counts[year_str][n].get("TOTAL", 0) for n in NDC_LIST)
            f.write(f"- **Total del año:** {year_total:,}\n\n")
            f.write("| NDC | Materia | Idioma | Cantidad | % |\n")
            f.write("| :---: | :--- | :--- | :---: | :---: |\n")
            for ndc in sorted(NDC_LIST):
                total_ndc_yr = all_counts[year_str][ndc].get("TOTAL", 0)
                if total_ndc_yr > 0:
                    langs = sorted([(l, c) for l, c in all_counts[year_str][ndc].items() if l != "TOTAL" and c > 0], key=lambda x: x[1], reverse=True)
                    for i, (l_short, count) in enumerate(langs):
                        perc = (count / total_ndc_yr) * 100
                        n_code = ndc if i == 0 else ""
                        n_name = NDC_NAMES[ndc] if i == 0 else ""
                        f.write(f"| {n_code} | {n_name} | {l_short} | {count:,} | {perc:.2f}% |\n")
            f.write("\n")

if __name__ == "__main__":
    main()
