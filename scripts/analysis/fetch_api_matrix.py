import os
import requests
import json
import time
from collections import defaultdict

BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
YEAR_MIN, YEAR_MAX = 1850, 1920

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

def fetch_count(year_from, year_to, lang=None, ndc=None, appid=None):
    params = {
        "format": "json",
        "year_from": year_from,
        "year_to": year_to,
        "count": 0,
        "type": "0"
    }
    if lang: params["lang"] = lang
    if ndc: params["clas"] = f"NDC{ndc}*"
    if appid: params["appid"] = appid

    try:
        r = requests.get(BASE_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return int(data.get("@graph", [{}])[0].get("opensearch:totalResults", 0))
    except Exception as e:
        return None

def main():
    appid = get_appid()
    # matrix[ndc][lang] = count
    matrix = defaultdict(lambda: defaultdict(int))
    
    print(f"Iniciando descarga de matriz global NDC x Idioma (1850-1920)...")
    
    for ndc_code in NDC_NAMES.keys():
        print(f"Procesando NDC {ndc_code} ({NDC_NAMES[ndc_code]})...")
        
        # 1. Total por NDC
        total_ndc = fetch_count(YEAR_MIN, YEAR_MAX, ndc=ndc_code, appid=appid)
        matrix[ndc_code]["TOTAL"] = total_ndc
        time.sleep(0.5)
        
        if total_ndc and total_ndc > 0:
            for lang_code, lang_short in LANG_MAP.items():
                count = fetch_count(YEAR_MIN, YEAR_MAX, lang=lang_code, ndc=ndc_code, appid=appid)
                matrix[ndc_code][lang_short] = count
                print(f"  {lang_short}: {count}")
                time.sleep(0.5)
        else:
            print("  Sin registros.")

    # Guardar JSON
    with open("cinii_api_matrix_ndc_lang.json", "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=4)

    # Generar Markdown
    with open("cinii_api_resumen_matriz.md", "w", encoding="utf-8") as f:
        f.write("# Matriz Global de Materia e Idioma (API CiNii 1850-1920)\n\n")
        f.write("Este informe muestra el desglose real y total por idiomas para cada materia NDC en la base de datos nacional japonesa.\n\n")
        
        for ndc_code in sorted(NDC_NAMES.keys()):
            name = NDC_NAMES[ndc_code]
            total = matrix[ndc_code]["TOTAL"]
            
            f.write(f"### NDC {ndc_code}: {name}\n")
            f.write(f"- **Total oficial en API:** {total:,}\n\n")
            
            if total > 0:
                f.write("| Idioma | Cantidad | Porcentaje |\n")
                f.write("| :--- | :---: | :---: |\n")
                
                # Ordenar idiomas por cantidad
                langs = sorted(
                    [(l, c) for l, c in matrix[ndc_code].items() if l != "TOTAL"],
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for l_short, count in langs:
                    if count > 0:
                        perc = (count / total) * 100
                        f.write(f"| {l_short} | {count:,} | {perc:.2f}% |\n")
                f.write("\n")
            else:
                f.write("*No hay registros clasificados con este código en CiNii para este periodo.*\n\n")

    print("Proceso completado.")

if __name__ == "__main__":
    main()
