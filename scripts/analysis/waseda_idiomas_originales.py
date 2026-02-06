#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
waseda_idiomas_originales.py  –  Primo VE harvester (Waseda)
All records between 1850-1920 with Resume & Progress tracking.
"""

import requests, time, os, re, json, sys, io, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ───────── CONFIGURACIÓN ─────────
YEAR_MIN, YEAR_MAX = 1850, 1920
JSONL_OUTPUT = "waseda_idiomas_original_1.jsonl"
CHECKPOINT_FILE = "waseda_idiomas_checkpoint.json"
LIMIT         = 50              
SHORT_DELAY   = 1               
TIMEOUT       = 60              
# ─────────────────────────────────

BASE = "https://waseda.primo.exlibrisgroup.com/primaws/rest/pub/pnxs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8"
}

retry_strategy = Retry(
    total            = 5,
    backoff_factor   = 2,
    status_forcelist = [429, 500, 502, 503, 504],
    allowed_methods  = ["GET"]
)
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

year_pattern = re.compile(r"\b(1[89]\d{2}|19\d{2}|20[0-2]\d)\b")

def save_checkpoint(offset, total_saved):
    data = {
        "offset": offset,
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
        except:
            return None
    return None

def fetch(offset: int) -> dict:
    params = {
        "q"     : "any,contains,*",
        "vid"   : "81SOKEI_WUNI:WINE",
        "lang"  : "en",
        "offset": offset,
        "limit" : LIMIT,
        "facet" : f"creationdate,between,{YEAR_MIN},{YEAR_MAX}"
    }
    r = session.get(BASE, params=params, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def year_ok(doc: dict) -> bool:
    pnx = doc.get("pnx", {})
    dates = pnx.get("display", {}).get("creationdate", [])
    for d in dates:
        for yr_str in year_pattern.findall(str(d)):
            if YEAR_MIN <= int(yr_str) <= YEAR_MAX:
                return True
    return False

def to_row(doc: dict) -> dict:
    pnx = doc.get("pnx", {})
    display = pnx.get("display", {})
    addata  = pnx.get("addata", {})
    
    row = {
        "display_title":        "; ".join(display.get("title", [])),
        "display_creator":      "; ".join(display.get("creator", [])),
        "display_publisher":    "; ".join(display.get("publisher", [])),
        "display_creationdate": "; ".join(display.get("creationdate", [])),
        "display_language":     "; ".join(display.get("language", [])),
        "display_type":         "; ".join(display.get("type", [])),
        "display_identifier":   "; ".join(display.get("identifier", [])),
        "display_coverage":    "; ".join(addata.get("cop", []) or addata.get("country", [])),
        "source": "waseda_idiomas"
    }
    return row

def append_to_jsonl(row: dict):
    with open(JSONL_OUTPUT, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def main():
    checkpoint = load_checkpoint()
    if checkpoint:
        print(f"🔄 Reanudando Waseda desde offset {checkpoint['offset']} ({checkpoint['timestamp']})")
        offset = checkpoint["offset"]
        total_saved = checkpoint["total_saved"]
    else:
        offset = 0
        total_saved = 0
    
    print(f"🚀 Cosecha: Waseda ({YEAR_MIN}-{YEAR_MAX}) | Salida: {JSONL_OUTPUT}")
    start_time = time.time()

    try:
        while True:
            js = fetch(offset)
            docs = js.get("docs", [])
            if not docs:
                if os.path.exists(CHECKPOINT_FILE):
                    os.remove(CHECKPOINT_FILE)
                print("\n🏁 No hay más documentos.")
                break
            
            total_in_server = js.get("info", {}).get("total", 0)
            
            for doc in docs:
                if year_ok(doc):
                    row = to_row(doc)
                    append_to_jsonl(row)
                    total_saved += 1
            
            offset += len(docs)
            save_checkpoint(offset, total_saved)

            # ETA calculation
            elapsed = time.time() - start_time
            rate = offset / elapsed if elapsed > 0 else 0
            remaining = int(total_in_server) - offset
            eta_sec = remaining / rate if rate > 0 else 0
            eta_str = str(datetime.timedelta(seconds=int(eta_sec)))

            print(f"\r   [Waseda] Vistos: {offset} / {total_in_server} | Válidos: {total_saved} | ETA: {eta_str}   ", end="", flush=True)
            
            time.sleep(SHORT_DELAY)

    except KeyboardInterrupt:
        print("\n🛑 Pausado. Checkpoint guardado.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
