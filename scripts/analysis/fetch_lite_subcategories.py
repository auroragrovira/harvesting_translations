import os
import requests
import json
import time
from collections import defaultdict

# --- CONFIGURACIÓN ---
BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
OUTPUT_DIR = os.path.join("univ_jp", "lite")
REPORT_FILE = os.path.join(OUTPUT_DIR, "analisis_literatura.md")
DATA_FILE = os.path.join(OUTPUT_DIR, "literatura_data.json")

# Subcategorías NDC de Literatura (900)
LITE_NDC = {
    "91": "Literatura Japonesa",
    "92": "Literatura China / Oriental",
    "93": "Literatura Inglesa / Americana",
    "94": "Literatura Alemana",
    "95": "Literatura Francesa",
    "96": "Literatura Española",
    "97": "Literatura Italiana",
    "98": "Literatura Rusa / Soviética",
    "99": "Otras Literaturas"
}

def get_appid():
    path = "api_keys"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if "cinii=" in line and not line.strip().startswith("#"):
                        return line.strip().split("=")[1]
        except: pass
    return None

def fetch_count(year_from, year_to, ndc, appid=None):
    params = {
        "format": "json",
        "year_from": year_from,
        "year_to": year_to,
        "lang": "jpn",
        "clas": f"{ndc}*", # Eliminado el prefijo 'NDC'
        "count": 0,
        "type": "0"
    }
    if appid: params["appid"] = appid

    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

    try:
        r = session.get(BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        return int(data.get("@graph", [{}])[0].get("opensearch:totalResults", 0))
    except Exception as e:
        print(f"Error fetching {year_from}-{year_to} (NDC: {ndc}): {e}")
        return 0

def main():
    appid = get_appid()
    results = {
        "global_1800_1850": {},
        "global_1850_1920": {},
        "decades": {}
    }

    periods = [
        ("global_1800_1850", 1800, 1850),
        ("global_1850_1920", 1850, 1920)
    ]

    print("Iniciando análisis de subcategorías de Literatura (NDC 9)...")

    # 1. Cálculos Globales
    for key, start, end in periods:
        print(f"Calculando periodo {start}-{end}...")
        period_data = {}
        total_lite = 0
        for code, name in LITE_NDC.items():
            count = fetch_count(start, end, code, appid)
            period_data[code] = count
            total_lite += count
            time.sleep(0.4)
        results[key] = {"counts": period_data, "total": total_lite}

    # 2. Desglose por Décadas
    decades = [
        (1800, 1809), (1810, 1819), (1820, 1829), (1830, 1839), (1840, 1849),
        (1850, 1859), (1860, 1869), (1870, 1879), (1880, 1889), (1890, 1899),
        (1900, 1909), (1910, 1920) # 1920 incluido en la última tanda
    ]

    for start, end in decades:
        label = f"{start}s"
        print(f"Procesando década {label}...")
        dec_data = {}
        total_dec = 0
        for code, name in LITE_NDC.items():
            count = fetch_count(start, end, code, appid)
            dec_data[code] = count
            total_dec += count
            time.sleep(0.4)
        results["decades"][label] = {"counts": dec_data, "total": total_dec}

    # Guardar JSON
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    # Generar Markdown
    generate_markdown(results)
    print(f"Análisis completado. Resultados en: {REPORT_FILE}")

def generate_markdown(results):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# Análisis de Subcategorías de Literatura en Japonés (NDC 9: 1800-1920)\n\n")
        f.write("Este informe analiza la composición de la categoría 'Literatura' del catálogo CiNii Books, filtrando exclusivamente registros en idioma japonés (`lang:jpn`). El objetivo es observar qué literaturas extranjeras fueron más traducidas o adaptadas.\n\n")

        # Secciones Globales
        for key, label in [("global_1800_1850", "Periodo Edo (1800-1850)"), ("global_1850_1920", "Periodo Moderno (1850-1920)")]:
            data = results[key]
            total = data["total"]
            f.write(f"## {label}\n")
            f.write(f"- **Total de registros de Literatura con NDC identificado:** {total:,}\n\n")
            
            if total > 0:
                f.write("| Código | Subcategoría | Cantidad | Porcentaje |\n")
                f.write("| :--- | :--- | :---: | :---: |\n")
                sorted_codes = sorted(LITE_NDC.keys(), key=lambda x: data["counts"][x], reverse=True)
                for code in sorted_codes:
                    count = data["counts"][code]
                    perc = (count / total * 100)
                    f.write(f"| {code} | {LITE_NDC[code]} | {count:,} | {perc:.2f}% |\n")
            f.write("\n")

        f.write("## Evolución por Décadas\n\n")
        for dec_label in sorted(results["decades"].keys()):
            data = results["decades"][dec_label]
            total = data["total"]
            f.write(f"### Década {dec_label}\n")
            f.write(f"- **Total registros:** {total:,}\n\n")
            
            if total > 0:
                f.write("| Código | Subcategoría | Cantidad | Porcentaje |\n")
                f.write("| :--- | :--- | :---: | :---: |\n")
                sorted_codes = sorted(LITE_NDC.keys(), key=lambda x: data["counts"][x], reverse=True)
                for code in sorted_codes:
                    count = data["counts"][code]
                    perc = (count / total * 100)
                    f.write(f"| {code} | {LITE_NDC[code]} | {count:,} | {perc:.2f}% |\n")
            f.write("\n")

if __name__ == "__main__":
    main()
