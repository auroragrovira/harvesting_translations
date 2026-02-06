import os
import requests
import json
import time
from collections import defaultdict

BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
OUTPUT_FILE = os.path.join("univ_jp", "cinii_translation_stats.jsonl")
YEAR_MIN, YEAR_MAX = 1850, 1920

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

NDC_LIST = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

def get_appid():
    path = "api_keys"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "cinii=" in line and not line.strip().startswith("#"):
                    return line.strip().split("=")[1]
    return None

def fetch_count(year_from, year_to, lang="jpn", q=None, ndc=None, appid=None):
    params = {
        "format": "json",
        "year_from": year_from,
        "year_to": year_to,
        "lang": lang,
        "count": 0,
        "type": "0"
    }
    if q: params["q"] = q
    if ndc: params["clas"] = f"NDC{ndc}*"
    if appid: params["appid"] = appid

    try:
        r = requests.get(BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        return int(data.get("@graph", [{}])[0].get("opensearch:totalResults", 0))
    except Exception as e:
        print(f"Error fetching {year_from}-{year_to} (Q: {q}, NDC: {ndc}): {e}")
        return 0

def main():
    appid = get_appid()
    if not os.path.exists("univ_jp"): os.makedirs("univ_jp")
    
    # Abrir archivo para escribir resultados en tiempo real
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        # 1. Metadatos iniciales
        meta = {
            "type": "metadata",
            "keywords_used": {
                "訳": "Traducción / Traducido por",
                "翻訳": "Traducción (término formal)",
                "訳者": "Traductor",
                "共訳": "Cotraducción",
                "全訳": "Traducción completa",
                "和訳": "Traducción al japonés",
                "抄訳": "Traducción abreviada",
                "対訳": "Edición bilingüe / paralela"
            },
            "period": f"{YEAR_MIN}-{YEAR_MAX}",
            "language_filter": "jpn (Japonés)",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        out.write(json.dumps(meta, ensure_ascii=False) + "\n")

        yearly_data = []
        decade_agg = defaultdict(lambda: {"total": 0, "trans": 0})
        
        print(f"--- Iniciando cuantificación anual (1850-1920) ---")
        for year in range(YEAR_MIN, YEAR_MAX + 1):
            # Total registros en Japonés
            total_jpn = fetch_count(year, year, appid=appid)
            time.sleep(0.5)
            # Registros en Japonés con palabras clave de traducción
            trans_jpn = fetch_count(year, year, q=QUERY_STR, appid=appid)
            time.sleep(0.5)
            
            originals = total_jpn - trans_jpn
            p_trans = (trans_jpn / total_jpn * 100) if total_jpn > 0 else 0
            
            row = {
                "type": "yearly_stat",
                "year": year,
                "total_jpn": total_jpn,
                "translations": trans_jpn,
                "originals": max(0, originals),
                "percent_translations": round(p_trans, 2)
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            yearly_data.append(row)
            
            # Acumular para décadas
            decade = (year // 10) * 10
            decade_agg[decade]["total"] += total_jpn
            decade_agg[decade]["trans"] += trans_jpn
            
            print(f"Año {year}: {trans_jpn}/{total_jpn} traducciones ({p_trans:.2f}%)")

        print(f"\n--- Procesando resúmenes por décadas ---")
        for dec in sorted(decade_agg.keys()):
            d_total = decade_agg[dec]["total"]
            d_trans = decade_agg[dec]["trans"]
            d_originals = d_total - d_trans
            d_perc = (d_trans / d_total * 100) if d_total > 0 else 0
            
            row_dec = {
                "type": "decade_stat",
                "decade": f"{dec}s",
                "total_jpn": d_total,
                "translations": d_trans,
                "originals": max(0, d_originals),
                "percent_translations": round(d_perc, 2)
            }
            out.write(json.dumps(row_dec, ensure_ascii=False) + "\n")

        print(f"\n--- Procesando desglose por Materia (NDC) y Década ---")
        for dec in sorted(decade_agg.keys()):
            y_start = dec
            y_end = dec + 9 if dec < 1920 else 1920
            
            print(f"Década {dec}s...")
            for ndc in NDC_LIST:
                t_ndc = fetch_count(y_start, y_end, ndc=ndc, appid=appid)
                time.sleep(0.4)
                tr_ndc = fetch_count(y_start, y_end, q=QUERY_STR, ndc=ndc, appid=appid)
                time.sleep(0.4)
                
                p_ndc = (tr_ndc / t_ndc * 100) if t_ndc > 0 else 0
                
                ndc_row = {
                    "type": "ndc_decade_stat",
                    "decade": f"{dec}s",
                    "ndc": ndc,
                    "total_jpn": t_ndc,
                    "translations": tr_ndc,
                    "percent_translations": round(p_ndc, 2)
                }
                out.write(json.dumps(ndc_row, ensure_ascii=False) + "\n")

    print(f"\n✅ Análisis completado. Resultados en: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
