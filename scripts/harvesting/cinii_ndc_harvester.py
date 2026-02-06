import argparse, os, time, json, sys, io, datetime, random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configuración para evitar errores de encoding en Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── CONFIG ───────────────────────────────────────────────────
BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
YEAR_MIN, YEAR_MAX = 1850, 1920
RECORDS_PER_PAGE = 200
DELAY_BASE = 1.2  # Respetando límites de la API
OUTPUT_BASE_DIR = os.path.join("univ_jp", "3")
CHECKPOINT_FILE = os.path.join("univ_jp", "cinii_checkpoint_ndc.json")

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
LANG_LIST = [None, "jpn", "eng", "chi", "ger", "fre", "rus", "ita", "spa", "kor"]
NDC_LIST = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
# ─────────────────────────────────────────────────────────────

def read_api_key():
    path = os.path.join("api_keys")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if "cinii=" in line:
                        key = line.strip().split("=")[1]
                        if key and key != "TU_API_KEY_AQUI" and not line.startswith("#"):
                            return key
        except: pass
    return None

def save_checkpoint(year, lang_idx, ndc_idx, start_index, total_saved):
    data = {
        "year": year,
        "lang_idx": lang_idx,
        "ndc_idx": ndc_idx,
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

def fetch_cinii(year, start_index, lang=None, ndc=None, appid=None):
    params = {
        "format": "json",
        "year_from": year,
        "year_to": year,
        "p": (start_index // RECORDS_PER_PAGE) + 1,
        "count": RECORDS_PER_PAGE,
        "type": "0",
        "sortorder": "1" # Relevance/Default
    }
    if lang: params["lang"] = lang
    if ndc: params["clas"] = f"NDC{ndc}*"
    if appid: params["appid"] = appid

    headers = {
        "User-Agent": "NationalUniversityHarvester/3.0 (NDC Classification; contact: auroragrovira@github)",
        "Accept": "application/json"
    }

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=3, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        r = session.get(BASE_URL, params=params, headers=headers, timeout=60)
        if r.status_code == 400:
            return "LIMIT_REACHED"
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"\n⚠️ Error en conexión: {e}")
        return None

def process_item(item):
    if not item: return None
    return {
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

def main():
    if not os.path.exists(OUTPUT_BASE_DIR): os.makedirs(OUTPUT_BASE_DIR)
    
    appid = read_api_key()
    if appid: print(f"🔑 Usando CiNii AppID.")

    cp = load_checkpoint()
    if cp:
        start_year = cp["year"]
        start_l_idx = cp["lang_idx"]
        start_n_idx = cp["ndc_idx"]
        s_idx = cp["start_index"]
        total_saved = cp["total_saved"]
        print(f"🔄 Reanudando desde {start_year}, Lang {LANG_MAP[LANG_LIST[start_l_idx]]}, NDC {NDC_LIST[start_n_idx]}")
    else:
        start_year, start_l_idx, start_n_idx, s_idx, total_saved = YEAR_MIN, 0, 0, 1, 0

    try:
        for year in range(start_year, YEAR_MAX + 1):
            year_dir = os.path.join(OUTPUT_BASE_DIR, str(year))
            if not os.path.exists(year_dir): os.makedirs(year_dir)
            
            for l_idx in range(start_l_idx if year == start_year else 0, len(LANG_LIST)):
                lang_code = LANG_LIST[l_idx]
                lang_suffix = LANG_MAP[lang_code]
                
                for n_idx in range(start_n_idx if (year == start_year and l_idx == start_l_idx) else 0, len(NDC_LIST)):
                    ndc_code = NDC_LIST[n_idx]
                    output_file = os.path.join(year_dir, f"cinii_{lang_suffix}_{ndc_code}.jsonl")
                    
                    cur_s_idx = s_idx if (year == start_year and l_idx == start_l_idx and n_idx == start_n_idx) else 1
                    
                    print(f"\r📅 [{year}] Lang: {lang_suffix} | NDC: {ndc_code} | Iniciando en {cur_s_idx}...", end="", flush=True)
                    
                    while True:
                        data = fetch_cinii(year, cur_s_idx, lang=lang_code, ndc=ndc_code, appid=appid)
                        
                        if data == "LIMIT_REACHED":
                            print(f"\nℹ️ Límite API alcanzado para {year}/{lang_suffix}/{ndc_code}")
                            break
                        if not data:
                            print(f"\n⏸️ Error de red. Esperando 10s...")
                            time.sleep(10)
                            continue

                        graph = data.get("@graph", [{}])[0]
                        items = graph.get("items", [])
                        total_results = int(graph.get("opensearch:totalResults", 0))

                        if not items:
                            break

                        # Solo crear el archivo si hay resultados
                        with open(output_file, "a", encoding="utf-8") as f:
                            for item in items:
                                row = process_item(item)
                                if row:
                                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                                    total_saved += 1
                        
                        cur_s_idx += len(items)
                        save_checkpoint(year, l_idx, n_idx, cur_s_idx, total_saved)
                        
                        if cur_s_idx > total_results:
                            break
                        
                        time.sleep(DELAY_BASE + random.uniform(0, 0.3))
                    
                    # Reset s_idx para la siguiente combinación
                    s_idx = 1
                    
            print(f"\n✅ Año {year} completado.")

    except KeyboardInterrupt:
        print("\n🛑 Pausado por el usuario.")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n📊 Sesión terminada. Registros guardados: {total_saved}")

if __name__ == "__main__":
    main()
