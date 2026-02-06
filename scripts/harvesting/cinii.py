#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cinii.py · National University Catalog Harvester (Japan)
Granular Deep Harvest Edition: Segments by Year and Language into separate files.
"""

import argparse, os, time, json, sys, io, datetime, random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuración de salida para consola (evitar errores de encoding en Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── CONFIG ───────────────────────────────────────────────────
BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
YEAR_MIN, YEAR_MAX = 1850, 1920
RECORDS_PER_PAGE = 200
DELAY_BASE = 1.0
CHECKPOINT_FILE = os.path.join("univ_jp", "cinii_checkpoint_v2.json")
OUTPUT_DIR = os.path.join("univ_jp", "2")

# Mapeo de códigos de idioma para nombres de archivo (ISO 639-2/B)
LANG_MAP = {
    None: "ALL",
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
LANGUAGES = [None, "jpn", "eng", "chi", "ger", "fre", "rus", "ita", "spa", "kor"]
# ─────────────────────────────────────────────────────────────

def read_api_key():
    possible_paths = [
        "api_keys",
        os.path.join("..", "api_keys"),
        os.path.join(os.path.dirname(__file__), "..", "api_keys")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("cinii="):
                            key = line.strip().split("=")[1]
                            if key and key != "TU_API_KEY_AQUI" and not key.startswith("#"):
                                return key
            except: pass
    return None

def banner(msg):
    print(msg, flush=True)

def save_checkpoint(year, lang_idx, start_index, total_saved):
    data = {
        "current_year": year,
        "lang_idx": lang_idx,
        "start_index": start_index,
        "total_saved": total_saved,
        "timestamp": datetime.datetime.now().isoformat()
    }
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return None
    return None

def fetch_cinii(year, start_index, lang=None, sort=2, appid=None):
    # Sort=2 es Title Asc, más estable para paginación profunda
    params = {
        "format": "json",
        "year_from": year,
        "year_to": year,
        "p": (start_index // RECORDS_PER_PAGE) + 1,
        "count": RECORDS_PER_PAGE,
        "type": "0",
        "sortorder": sort
    }
    if lang: params["lang"] = lang
    if appid: params["appid"] = appid

    headers = {
        "User-Agent": "NationalUniversityHarvester/2.6 (Deep Harvest; contact: auroragrovira@github)",
        "Accept": "application/json"
    }

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        r = session.get(BASE_URL, params=params, headers=headers, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            banner(f"\nℹ️ Límite de paginación alcanzado (Año {year}, Start {start_index}, Lang {lang}).")
            return "LIMIT_REACHED"
        banner(f"\n⚠️ Error HTTP (Año {year}, Start {start_index}, Lang {lang}): {e}")
        return None
    except Exception as e:
        banner(f"\n⚠️ Error en conexión (Año {year}, Start {start_index}, Lang {lang}): {e}")
        return None

def process_item(item):
    if not item: return None
    row = {
        "display_title":        item.get("title", ""),
        "display_creator":      item.get("dc:creator", ""),
        "display_publisher":    item.get("dc:publisher", ""),
        "display_publicationplace": item.get("dc:publicationPlace", ""),
        "display_creationdate": item.get("dc:date", ""),
        "display_language":     item.get("dc:language", ""),
        "display_type":         item.get("dc:type", "Book/Journal"),
        "display_identifier":   item.get("@id", ""),
        "source": "cinii_national"
    }
    if isinstance(row["display_creator"], list):
        row["display_creator"] = "; ".join([str(c) for c in row["display_creator"]])
    if isinstance(row["display_publisher"], list):
        row["display_publisher"] = "; ".join([str(p) for p in row["display_publisher"]])
    return row

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    argp = argparse.ArgumentParser()
    argp.add_argument("--appid", help="CiNii Application ID")
    argp.add_argument("--new", action="store_true", help="Ignorar checkpoint")
    args = argp.parse_args()

    appid = args.appid if args.appid else read_api_key()
    if appid: banner(f"🔑 Usando CiNii Application ID.")

    checkpoint = load_checkpoint() if not args.new else None
    
    if checkpoint:
        current_year = checkpoint.get("current_year", YEAR_MIN)
        c_lang_idx = checkpoint.get("lang_idx", 0)
        start_index = checkpoint.get("start_index", 1)
        total_saved = checkpoint.get("total_saved", 0)
        banner(f"🔄 Reanudando desde {current_year}, IDIOMA: {LANG_MAP[LANGUAGES[c_lang_idx]]}, Index {start_index}")
    else:
        current_year, c_lang_idx, start_index, total_saved = YEAR_MIN, 0, 1, 0

    banner(f"🚀 Iniciando Cosecha Profunda CiNii ({YEAR_MIN}-{YEAR_MAX})")
    start_time = time.time()

    try:
        for year in range(current_year, YEAR_MAX + 1):
            
            # Decidir qué idiomas procesar para este año
            # Si el total es pequeño, podemos hacer solo ALL. Si es grande, segmentamos.
            # No obstante, el usuario quiere clasificación, así que haremos siempre la lista si llega al límite.
            
            # Primero obtenemos el total para decidir la estrategia
            data_init = fetch_cinii(year, 1, appid=appid)
            if not data_init:
                banner(f"❌ Error al conectar para el año {year}. Saltando.")
                continue
            
            graph_node_init = data_init.get("@graph", [{}])[0]
            total_year = int(graph_node_init.get("opensearch:totalResults", 0))
            banner(f"\n📅 Año {year}: {total_year} registros totales en CiNii.")

            # Estrategia: Si hay más de 10,000, intentamos segmentar por idiomas principales
            # para que el usuario tenga los archivos clasificados. 
            # El resto (o todo si el usuario quiere) va en el archivo ALL.
            
            langs_to_process = LANGUAGES # Siempre procesamos la lista para asegurar clasificación
            
            for l_idx in range(c_lang_idx, len(langs_to_process)):
                lang_code = LANGUAGES[l_idx]
                lang_suffix = LANG_MAP[lang_code]
                output_file = os.path.join(OUTPUT_DIR, f"cinii_{year}_{lang_suffix}.jsonl")
                
                s_idx = start_index if (year == current_year and l_idx == c_lang_idx) else 1
                
                # Para evitar duplicados en el mismo archivo si hay reintentos
                existing_ids = set()
                if os.path.exists(output_file) and s_idx > 1:
                    with open(output_file, "r", encoding="utf-8") as rf:
                        for line in rf:
                            try:
                                itm = json.loads(line)
                                if "display_identifier" in itm: existing_ids.add(itm["display_identifier"])
                            except: pass

                banner(f"  📂 Procesando {lang_suffix} (Lang: {lang_code})...")
                
                while True:
                    data = fetch_cinii(year, s_idx, lang=lang_code, appid=appid)
                    if data == "LIMIT_REACHED":
                        break
                    if not data:
                        banner(f"⏸️ Error de red. Pausando. Ejecute de nuevo para continuar.")
                        return

                    graph_node = data.get("@graph", [{}])[0]
                    search_results = graph_node.get("items", [])
                    total_sub = int(graph_node.get("opensearch:totalResults", 0))
                    
                    if s_idx == 1:
                        banner(f"    Subtotal para {lang_suffix}: {total_sub}")

                    if not search_results: break
                    
                    with open(output_file, "a", encoding="utf-8") as f:
                        for item in search_results:
                            row = process_item(item)
                            if row and row["display_identifier"] not in existing_ids:
                                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                                existing_ids.add(row["display_identifier"])
                                total_saved += 1

                    elapsed = time.time() - start_time
                    rate = total_saved / elapsed if elapsed > 0 else 0
                    print(f"\r   [{year}|{lang_suffix}] Progreso: {s_idx}/{total_sub} | Sesión: {total_saved} ", end="", flush=True)

                    s_idx += len(search_results)
                    save_checkpoint(year, l_idx, s_idx, total_saved)
                    
                    if s_idx > total_sub: break
                    # Pequeño delay para no saturar
                    time.sleep(DELAY_BASE + random.uniform(0, 0.5))
                
                print() # Nueva línea al terminar idioma
                start_index = 1 # Reset para el siguiente idioma
            
            c_lang_idx = 0 # Reset para el siguiente año
            banner(f"✅ Año {year} completado.")

    except KeyboardInterrupt:
        banner("\n🛑 Pausado por usuario.")
    except Exception as e:
        banner(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()

    banner(f"📊 Sesión terminada. Guardados: {total_saved}")

if __name__ == "__main__":
    main()

