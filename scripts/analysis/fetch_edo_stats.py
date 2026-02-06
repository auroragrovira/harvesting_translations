import os
import requests
import json
import time
from collections import defaultdict

# --- CONFIGURACIÓN ---
BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
YEAR_MIN, YEAR_MAX = 1800, 1850
OUTPUT_DIR = os.path.join("univ_jp", "Edo")
DATA_FILE = os.path.join(OUTPUT_DIR, "cinii_edo_full_stats.json")
REPORT_FILE = os.path.join(OUTPUT_DIR, "cinii_edo_resumen.md")

LANG_MAP = {
    "jpn": "Japonés (JP)",
    "eng": "Inglés (EN)",
    "chi": "Chino (ZH)",
    "ger": "Alemán (DE)",
    "fre": "Francés (FR)",
    "dut": "Holandés (NL)",  # Corregido de 'nld' a 'dut'
    "rus": "Ruso (RU)",
    "ita": "Italiano (IT)",
    "spa": "Español (ES)",
    "kor": "Coreano (KO)",
    "lat": "Latín (LA)"      # Útil para obras académicas antiguas
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

def fetch_count(year_from, year_to, lang=None, appid=None):
    params = {
        "format": "json",
        "year_from": year_from,
        "year_to": year_to,
        "count": 0,
        "type": "0"
    }
    if lang: params["lang"] = lang
    if appid: params["appid"] = appid

    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

    try:
        r = session.get(BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        return int(data.get("@graph", [{}])[0].get("opensearch:totalResults", 0))
    except Exception as e:
        print(f"Error fetching {year_from}-{year_to} (Lang: {lang}): {e}")
        return 0

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    appid = get_appid()
    
    # stats[year][lang_code] = count
    stats = {}
    
    print(f"Iniciando cosecha de estadísticas Edo (1800-1850) con Holandés (DUT) y Latín...")
    
    for year in range(YEAR_MIN, YEAR_MAX + 1):
        y_str = str(year)
        stats[y_str] = {}
        
        # Total anual
        total_yr = fetch_count(year, year, appid=appid)
        stats[y_str]["TOTAL"] = total_yr
        time.sleep(0.4)
        
        print(f"Año {year}: Total {total_yr}")
        
        if total_yr > 0:
            for l_code, l_name in LANG_MAP.items():
                count = fetch_count(year, year, lang=l_code, appid=appid)
                stats[y_str][l_code] = count
                time.sleep(0.4)
        else:
            for l_code in LANG_MAP:
                stats[y_str][l_code] = 0

    # Guardar JSON
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

    # Generar Markdown
    generate_markdown(stats)
    print(f"Proceso completado. Archivos actualizados en {OUTPUT_DIR}")

def generate_markdown(stats):
    global_total = sum(s["TOTAL"] for s in stats.values())
    global_langs = defaultdict(int)
    decade_stats = defaultdict(lambda: {"total": 0, "langs": defaultdict(int)})
    
    for y_str, s in stats.items():
        year = int(y_str)
        decade = (year // 10) * 10
        decade_stats[decade]["total"] += s["TOTAL"]
        for l_code in LANG_MAP:
            global_langs[l_code] += s.get(l_code, 0)
            decade_stats[decade]["langs"][l_code] += s.get(l_code, 0)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# Resumen Estadístico de CiNii (Edo: {YEAR_MIN}-{YEAR_MAX})\n\n")
        
        f.write("## 1. Resumen Global\n")
        f.write(f"- **Total de registros únicos:** {global_total:,}\n\n")
        write_table(f, global_total, global_langs)

        f.write("## 2. Resumen por Décadas\n\n")
        for decade in sorted(decade_stats.keys()):
            d_total = decade_stats[decade]["total"]
            f.write(f"### Década de {decade}\n")
            f.write(f"- **Total registros únicos:** {d_total:,}\n\n")
            
            if d_total > 0:
                write_table(f, d_total, decade_stats[decade]["langs"])
            else:
                f.write("*Sin registros*\n\n")

        f.write("## 3. Desglose Anual Detallado\n\n")
        for y_str in sorted(stats.keys()):
            y_total = stats[y_str]["TOTAL"]
            f.write(f"### Año {y_str}\n")
            f.write(f"- **Total registros únicos:** {y_total:,}\n\n")
            
            if y_total > 0:
                write_table(f, y_total, stats[y_str])
            else:
                f.write("*Sin registros*\n\n")

def write_table(f, total_count, lang_counts):
    f.write("| Idioma | Cantidad | Porcentaje |\n")
    f.write("| :--- | :---: | :---: |\n")
    
    sum_langs = 0
    sorted_langs = sorted(LANG_MAP.items(), key=lambda x: lang_counts.get(x[0], 0), reverse=True)
    
    for l_code, l_name in sorted_langs:
        count = lang_counts.get(l_code, 0)
        if count > 0:
            perc = (count / total_count) * 100
            f.write(f"| {l_name} | {count:,} | {perc:.2f}% |\n")
            sum_langs += count
            
    # Gestión del Excedente o Resto
    diff = sum_langs - total_count
    
    if diff > 0:
        # Existe solapamiento (libros multilingües)
        f.write(f"| *Excedente (Multilingüismo)* | +{diff:,} | +{(diff/total_count*100):.2f}% |\n")
    elif diff < 0:
        # Faltan idiomas por clasificar
        rest = abs(diff)
        f.write(f"| *Otros / No clasificados* | {rest:,} | {(rest/total_count*100):.2f}% |\n")
    
    f.write("\n")
    f.write(f"**Total acumulado por categorías:** {sum_langs:,} (sobre {total_count:,} registros base)\n\n")

if __name__ == "__main__":
    main()
