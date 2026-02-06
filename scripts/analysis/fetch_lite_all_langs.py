import os
import requests
import json
import time
from collections import defaultdict

# --- CONFIGURACIÓN ---
BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
OUTPUT_DIR = os.path.join("univ_jp", "lite")
REPORT_FILE = os.path.join(OUTPUT_DIR, "analisis_literatura_multilingue.md")
DATA_FILE = os.path.join(OUTPUT_DIR, "literatura_multilingue_data.json")

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

# Idiomas principales a rastrear
MAJOR_LANGS = {
    "jpn": "Japonés",
    "eng": "Inglés",
    "chi": "Chino",
    "ger": "Alemán",
    "fre": "Francés",
    "rus": "Ruso",
    "dut": "Holandés",
    "spa": "Español",
    "ita": "Italiano"
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

def fetch_count(year_from, year_to, ndc, lang=None, appid=None):
    params = {
        "format": "json",
        "year_from": year_from,
        "year_to": year_to,
        "clas": f"{ndc}*",
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
        print(f"Error fetching {year_from}-{year_to} (NDC: {ndc}, Lang: {lang}): {e}")
        return 0

def main():
    appid = get_appid()
    results = {
        "global_1800_1850": {},
        "global_1850_1920": {},
        "decades": {}
    }

    # Definir periodos y décadas
    periods = [
        ("global_1800_1850", 1800, 1850),
        ("global_1850_1920", 1850, 1920)
    ]
    decades = [
        (1800, 1809), (1810, 1819), (1820, 1829), (1830, 1839), (1840, 1849),
        (1850, 1859), (1860, 1869), (1870, 1879), (1880, 1889), (1890, 1899),
        (1900, 1909), (1910, 1920)
    ]

    all_tasks = periods + [(f"{s}s", s, e) for s, e in decades]

    print("Iniciando análisis multilingüe de subcategorías de Literatura (NDC 9)...")

    for task_id, start, end in all_tasks:
        print(f"Procesando periodo: {task_id} ({start}-{end})...")
        task_data = {}
        
        for ndc_code, ndc_name in LITE_NDC.items():
            # 1. Total absoluto para este NDC (todos los idiomas)
            total_ndc = fetch_count(start, end, ndc_code, appid=appid)
            time.sleep(0.4)
            
            if total_ndc == 0:
                task_data[ndc_code] = {"total": 0, "langs": {}}
                continue
            
            # 2. Desglose por idiomas principales
            lang_counts = {}
            sum_major = 0
            for l_code, l_label in MAJOR_LANGS.items():
                c = fetch_count(start, end, ndc_code, lang=l_code, appid=appid)
                lang_counts[l_code] = c
                sum_major += c
                time.sleep(0.4)
            
            # 3. Otros / Sin clasificar
            # Nota: Algunos pueden ser multilingües, pero el resto aproximado es Total - Suma(Langs)
            # Si la suma es mayor al total, es por solapamiento multilingüe.
            diff = total_ndc - sum_major
            others = max(0, diff)
            lang_counts["others"] = others
            
            task_data[ndc_code] = {
                "total": total_ndc,
                "langs": lang_counts
            }
            print(f"  NDC {ndc_code} ({ndc_name}): {total_ndc} registros")

        if "global" in task_id:
            results[task_id] = task_data
        else:
            results["decades"][task_id] = task_data

    # Guardar JSON
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    # Generar Markdown
    generate_markdown(results)
    print(f"Análisis completado. Informe generado en: {REPORT_FILE}")

def generate_markdown(results):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# Análisis Multilingüe de Literatura (NDC 9: 1800-1920)\n\n")
        f.write("Este informe analiza la composición idiomática dentro de cada subcategoría de Literatura. Permite distinguir entre obras originales (en el idioma fuente) y el esfuerzo de traducción o estudio (en japonés u otros idiomas).\n\n")

        # Secciones Globales
        for key, label in [("global_1800_1850", "Periodo Edo (1800-1850)"), ("global_1850_1920", "Periodo Moderno (1850-1920)")]:
            f.write(f"## {label}\n\n")
            data = results[key]
            for ndc_code in sorted(data.keys()):
                ndc_info = data[ndc_code]
                total = ndc_info["total"]
                f.write(f"### NDC {ndc_code}: {LITE_NDC[ndc_code]}\n")
                f.write(f"- **Total registros:** {total:,}\n\n")
                
                if total > 0:
                    f.write("| Idioma | Cantidad | Porcentaje |\n")
                    f.write("| :--- | :---: | :---: |\n")
                    
                    # Ordenar idiomas por cantidad
                    langs_to_show = list(MAJOR_LANGS.items()) + [("others", "Otros / Sin clasificar")]
                    sorted_langs = sorted(langs_to_show, key=lambda x: ndc_info["langs"].get(x[0], 0), reverse=True)
                    
                    for l_code, l_label in sorted_langs:
                        count = ndc_info["langs"].get(l_code, 0)
                        if count > 0:
                            perc = (count / total * 100)
                            f.write(f"| {l_label} | {count:,} | {perc:.2f}% |\n")
                    f.write("\n")
                else:
                    f.write("*Sin registros identificados en esta categoría.*\n\n")

        f.write("## Evolución por Décadas\n\n")
        for dec_label in sorted(results["decades"].keys()):
            f.write(f"### Década {dec_label}\n\n")
            data = results["decades"][dec_label]
            for ndc_code in sorted(data.keys()):
                ndc_info = data[ndc_code]
                total = ndc_info["total"]
                if total > 0:
                    f.write(f"#### {ndc_code} - {LITE_NDC[ndc_code]} ({total:,} registros)\n")
                    f.write("| Idioma | Cantidad | % |\n")
                    f.write("| :--- | :---: | :---: |\n")
                    langs_to_show = list(MAJOR_LANGS.items()) + [("others", "Otros")]
                    sorted_langs = sorted(langs_to_show, key=lambda x: ndc_info["langs"].get(x[0], 0), reverse=True)
                    for l_code, l_label in sorted_langs:
                        count = ndc_info["langs"].get(l_code, 0)
                        if count > 0:
                            f.write(f"| {l_label} | {count:,} | {(count/total*100):.1f}% |\n")
                    f.write("\n")

if __name__ == "__main__":
    main()
