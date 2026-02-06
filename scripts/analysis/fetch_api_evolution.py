import os
import requests
import json
import time
from collections import defaultdict

BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
DECADES = [
    (1850, 1859), (1860, 1869), (1870, 1879), (1880, 1889),
    (1890, 1899), (1900, 1909), (1910, 1919), (1920, 1920)
]

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
    # stats[decade][ndc][lang] = count
    stats = {}

    print(f"Obteniendo evolución por décadas (API CiNii)...")
    
    for start, end in DECADES:
        label = f"{start}s" if start != end else str(start)
        print(f"Procesando {label}...")
        stats[label] = {"TOTAL": 0, "BY_LANG": {}, "BY_NDC": {}, "MATRIX": {}}
        
        # 1. Total década
        total_dec = fetch_count(start, end, appid=appid)
        stats[label]["TOTAL"] = total_dec
        time.sleep(0.4)
        
        # 2. Por idioma
        for l_code, l_short in LANG_MAP.items():
            c = fetch_count(start, end, lang=l_code, appid=appid)
            stats[label]["BY_LANG"][l_short] = c
            time.sleep(0.4)
            
        # 3. Por materia e idioma (Matriz)
        for ndc in NDC_LIST:
            # Primero total por NDC en la década
            c_ndc = fetch_count(start, end, ndc=ndc, appid=appid)
            stats[label]["BY_NDC"][ndc] = c_ndc
            time.sleep(0.4)
            
            if c_ndc and c_ndc > 0:
                stats[label]["MATRIX"][ndc] = {}
                for l_code, l_short in LANG_MAP.items():
                    c_nl = fetch_count(start, end, lang=l_code, ndc=ndc, appid=appid)
                    stats[label]["MATRIX"][ndc][l_short] = c_nl
                    time.sleep(0.4)
        
        # Guardar progreso parcial
        with open("cinii_api_evolution_data.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4)

    print("Extracción completada. Generando informe...")
    generate_report(stats)

def generate_report(stats):
    with open("cinii_evolucion_proporciones.md", "w", encoding="utf-8") as f:
        f.write("# Evolución Temporal de Proporciones - API CiNii (1850-1920)\n\n")
        
        f.write("## 1. Evolución por Idiomas\n\n")
        f.write("| Década | JP % | EN % | DE % | FR % | ZH % | Otros % |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        
        for dec in sorted(stats.keys()):
            total = stats[dec]["TOTAL"]
            if not total: continue
            
            def get_p(lang):
                return (stats[dec]["BY_LANG"].get(lang, 0) / total) * 100
            
            p_jp = get_p("JP")
            p_en = get_p("EN")
            p_de = get_p("DE")
            p_fr = get_p("FR")
            p_zh = get_p("ZH")
            others = 100 - (p_jp + p_en + p_de + p_fr + p_zh)
            
            f.write(f"| {dec} | {p_jp:.1f}% | {p_en:.1f}% | {p_de:.1f}% | {p_fr:.1f}% | {p_zh:.1f}% | {others:.1f}% |\n")
        f.write("\n")

        f.write("## 2. Evolución por Materias (NDC)\n\n")
        f.write("| Década | NDC 1 (Filo) | NDC 6 (Ind) | NDC 8 (Lang) | NDC 9 (Lit) | Otros |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        
        for dec in sorted(stats.keys()):
            total_classified = sum(stats[dec]["BY_NDC"].values())
            if not total_classified:
                f.write(f"| {dec} | - | - | - | - | - |\n")
                continue
            
            def get_p_ndc(n):
                return (stats[dec]["BY_NDC"].get(n, 0) / total_classified) * 100
            
            f.write(f"| {dec} | {get_p_ndc('1'):.1f}% | {get_p_ndc('6'):.1f}% | {get_p_ndc('8'):.1f}% | {get_p_ndc('9'):.1f}% | {get_p_ndc('7'):.1f}% |\n")
        f.write("\n")

        f.write("## 3. Evolución Cruzada (Materia + Idioma)\n")
        f.write("Se analiza el idioma dominante dentro de cada materia a través de las décadas.\n\n")
        
        for ndc_code in ["1", "6", "8", "9"]:
            name = NDC_NAMES[ndc_code]
            f.write(f"### Evolución en {name} (NDC {ndc_code})\n")
            f.write("| Década | Idioma Principal | % en Materia | 2º Idioma | % en Materia |\n")
            f.write("| :--- | :--- | :---: | :--- | :---: |\n")
            
            for dec in sorted(stats.keys()):
                m = stats[dec]["MATRIX"].get(ndc_code)
                if not m:
                    f.write(f"| {dec} | - | - | - | - |\n")
                    continue
                
                total_m = stats[dec]["BY_NDC"][ndc_code]
                sorted_l = sorted(m.items(), key=lambda x: x[1], reverse=True)
                
                l1, c1 = sorted_l[0]
                l2, c2 = sorted_l[1] if len(sorted_l) > 1 else ("-", 0)
                
                p1 = (c1 / total_m) * 100
                p2 = (c2 / total_m) * 100 if c2 else 0
                
                f.write(f"| {dec} | {l1} | {p1:.1f}% | {l2} | {p2:.1f}% |\n")
            f.write("\n")

if __name__ == "__main__":
    main()
