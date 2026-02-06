import os
import requests
import json
import time
from collections import defaultdict

# --- CONFIGURACIÓN ---
BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
YEAR_MIN, YEAR_MAX = 1800, 1850
OUTPUT_DIR = os.path.join("univ_jp", "Edo")
REPORT_FILE = os.path.join(OUTPUT_DIR, "cinii_edo_traducciones.md")
DATA_FILE = os.path.join(OUTPUT_DIR, "cinii_edo_translation_data.json")

# Palabras clave para identificar traducciones en registros japoneses
KEYWORDS = [
    "訳",       # Yaku (Traducción / Traducido por)
    "翻訳",     # Honyaku (Traducción formal)
    "訳者",     # Yakusha (Traductor)
    "共訳",     # Kyōyaku (Cotraducción)
    "全訳",     # Zen'yaku (Traducción completa)
    "和訳",     # Wayaku (Traducción al japonés)
    "抄訳",     # Shōyaku (Traducción abreviada)
    "対訳"      # Taiyaku (Bilingüe / Traducción paralela)
]

QUERY_STR = " OR ".join(KEYWORDS)

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

def fetch_count(year_from, year_to, lang="jpn", q=None, appid=None):
    params = {
        "format": "json",
        "year_from": year_from,
        "year_to": year_to,
        "lang": lang,
        "count": 0,
        "type": "0"
    }
    if q: params["q"] = q
    if appid: params["appid"] = appid

    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

    try:
        r = session.get(BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        return int(data.get("@graph", [{}])[0].get("opensearch:totalResults", 0))
    except Exception as e:
        print(f"Error fetching {year_from}-{year_to} (Q: {q}): {e}")
        return 0

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    appid = get_appid()
    
    # stats[year] = {"total": X, "trans": Y}
    stats = {}
    
    print(f"Iniciando cuantificación de traducciones Edo (1800-1850)...")
    
    for year in range(YEAR_MIN, YEAR_MAX + 1):
        # Total JPN
        total_jpn = fetch_count(year, year, appid=appid)
        time.sleep(0.5)
        # Traducciones JPN
        trans_jpn = fetch_count(year, year, q=QUERY_STR, appid=appid)
        time.sleep(0.5)
        
        stats[year] = {
            "total_jpn": total_jpn,
            "translations": trans_jpn
        }
        print(f"Año {year}: {trans_jpn}/{total_jpn} traducciones")

    # Guardar JSON de respaldo
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    # Generar Markdown
    generate_report(stats)
    print(f"\n✅ Proceso completado. Informe generado en: {REPORT_FILE}")

def generate_report(stats):
    global_total = sum(s["total_jpn"] for s in stats.values())
    global_trans = sum(s["translations"] for s in stats.values())
    global_perc = (global_trans / global_total * 100) if global_total > 0 else 0
    
    decade_agg = defaultdict(lambda: {"total": 0, "trans": 0})
    for year, s in stats.items():
        decade = (int(year) // 10) * 10
        decade_agg[decade]["total"] += s["total_jpn"]
        decade_agg[decade]["trans"] += s["translations"]

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# Estudio de Traducciones en CiNii (Edo: 1800-1850)\n\n")
        
        f.write("## 1. Metodología de búsqueda\n")
        f.write("Se han identificado traducciones mediante la presencia de las siguientes palabras clave en registros en japonés:\n")
        f.write("- **訳** (Yaku): Traducción / Traducido por\n")
        f.write("- **翻訳** (Honyaku): Traducción formal\n")
        f.write("- **訳者** (Yakusha): Traductor\n")
        f.write("- **共訳** (Kyōyaku): Cotraducción\n")
        f.write("- **全訳** (Zen'yaku): Traducción completa\n")
        f.write("- **和訳** (Wayaku): Traducción al japonés\n")
        f.write("- **抄訳** (Shōyaku): Traducción abreviada\n")
        f.write("- **対訳** (Taiyaku): Edición bilingüe / paralela\n\n")

        f.write("## 2. Resumen Global (1800-1850)\n")
        f.write(f"- **Total de registros en Japonés:** {global_total:,}\n")
        f.write(f"- **Total de traducciones detectadas:** {global_trans:,}\n")
        f.write(f"- **Proporción de traducciones:** **{global_perc:.2f}%**\n\n")

        f.write("## 3. Resumen por Décadas\n\n")
        f.write("| Década | Total JPN | Traducciones | Porcentaje |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for dec in sorted(decade_agg.keys()):
            d_total = decade_agg[dec]["total"]
            d_trans = decade_agg[dec]["trans"]
            d_perc = (d_trans / d_total * 100) if d_total > 0 else 0
            f.write(f"| {dec}s | {d_total:,} | {d_trans:,} | {d_perc:.2f}% |\n")
        f.write("\n")

        f.write("## 4. Desglose Anual\n\n")
        f.write("| Año | Total JPN | Traducciones | Porcentaje |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for year in sorted(stats.keys()):
            s = stats[year]
            y_total = s["total_jpn"]
            y_trans = s["translations"]
            y_perc = (y_trans / y_total * 100) if y_total > 0 else 0
            f.write(f"| {year} | {y_total:,} | {y_trans:,} | {y_perc:.2f}% |\n")

if __name__ == "__main__":
    main()
