#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ndl_idiomas_originales.py · Harvester for National Diet Library (NDL) via SRU API
Collects all records between 1850-1920 without keyword filters.
"""

import argparse, os, re, time, xml.etree.ElementTree as ET, json, sys, io, datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── CONFIG ───────────────────────────────────────────────────
BASE_URL = "https://ndlsearch.ndl.go.jp/api/sru"
YEAR_MIN, YEAR_MAX = 1850, 1920
JSONL_OUTPUT = "ndl_idiomas_original_1.jsonl"
CHECKPOINT_FILE = "ndl_idiomas_checkpoint.json"
MAX_RECORDS_PER_FETCH = 200     # Máximo recomendado por NDL SRU
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
TIMEOUT = 120
DELAY = 2
# ─────────────────────────────────────────────────────────────

def banner(msg, quiet):
    if not quiet:
        print(msg, flush=True)

def save_checkpoint(start_record, total_saved):
    data = {
        "start_record": start_record,
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

def fetch_ndl(start_record, quiet):
    """Realiza la petición SRU a NDL."""
    # Query: buscar por rango de fecha de publicación sin keywords
    # En SRU NDL: 'from' y 'until' funcionan para fecha de publicación
    query = f"from={YEAR_MIN} AND until={YEAR_MAX}"
    
    params = {
        "operation": "searchRetrieve",
        "version": "1.2",
        "query": query,
        "startRecord": start_record,
        "maximumRecords": MAX_RECORDS_PER_FETCH,
        "recordSchema": "dcndl",
        "recordPacking": "string"
    }
    
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=2)))
    
    try:
        r = session.get(BASE_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return ET.fromstring(r.text)
    except Exception as e:
        banner(f"\n⚠️ Error en fetch: {e}", quiet)
        return None

def parse_record(record_xml):
    """Extrae metadatos del esquema dcndl."""
    # El esquema dcndl viene a veces dentro de un string en SRU
    # Pero aquí usamos recordPacking=string, el XML está embebido
    ns = {
        "sru": "http://www.loc.gov/zing/srw/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "dcndl": "http://ndl.go.jp/dcndl/terms/",
        "srw": "http://www.loc.gov/zing/srw/"
    }
    
    # Intentar encontrar el contenido del registro (embebido en <srw:recordData>)
    record_data = record_xml.find(".//srw:recordData", ns)
    if record_data is None: return None
    
    # El contenido es a menudo un string XML si recordPacking=string
    # Pero ET.fromstring ya se encarga si el servidor lo envia como XML estructurado
    # NDL suele enviar el fragmento XML dentro de recordData
    try:
        data_xml = ET.fromstring(record_data.text) if record_data.text else record_data[0]
    except:
        return None
        
    dc_ns = "{http://purl.org/dc/elements/1.1/}"
    dcndl_ns = "{http://ndl.go.jp/dcndl/terms/}"
    
    row = {
        "display_title":        "; ".join([el.text for el in data_xml.findall(f".//{dc_ns}title") if el.text]),
        "display_creator":      "; ".join([el.text for el in data_xml.findall(f".//{dc_ns}creator") if el.text]),
        "display_publisher":    "; ".join([el.text for el in data_xml.findall(f".//{dc_ns}publisher") if el.text]),
        "display_creationdate": "; ".join([el.text for el in data_xml.findall(f".//{dc_ns}date") if el.text]),
        "display_language":     "; ".join([el.text for el in data_xml.findall(f".//{dc_ns}language") if el.text]),
        "display_type":         "; ".join([el.text for el in data_xml.findall(f".//{dc_ns}type") if el.text]),
        "display_coverage":     "; ".join([el.text for el in data_xml.findall(f".//{dcndl_ns}publicationPlace") if el.text]),
        "display_identifier":   "; ".join([el.text for el in data_xml.findall(f".//{dc_ns}identifier") if el.text]),
        "source": "ndl_idiomas"
    }
    return row

def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("-q","--quiet", action="store_true")
    argp.add_argument("--new", action="store_true")
    args = argp.parse_args()
    quiet = args.quiet

    checkpoint = load_checkpoint() if not args.new else None
    
    if checkpoint:
        start_record = checkpoint["start_record"]
        total_saved = checkpoint["total_saved"]
        banner(f"🔄 Reanudando NDL desde registro {start_record}", quiet)
    else:
        start_record = 1
        total_saved = 0

    banner(f"🚀 Cosecha NDL ({YEAR_MIN}-{YEAR_MAX}) | Salida: {JSONL_OUTPUT}", quiet)
    start_time = time.time()
    
    ns_sru = {"sru": "http://www.loc.gov/zing/srw/"}

    try:
        while True:
            root = fetch_ndl(start_record, quiet)
            if root is None: break
            
            # Obtener número total de resultados
            total_records_el = root.find(".//sru:numberOfRecords", ns_sru)
            total_count = int(total_records_el.text) if total_records_el is not None else 0
            
            records = root.findall(".//sru:record", ns_sru)
            if not records:
                banner("\n🏁 No se encontraron más registros.", quiet)
                break
            
            for rec in records:
                row = parse_record(rec)
                if row:
                    with open(JSONL_OUTPUT, "a", encoding="utf-8") as f:
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    total_saved += 1
            
            next_record = start_record + len(records)
            save_checkpoint(next_record, total_saved)
            
            # Progreso y ETA
            elapsed = time.time() - start_time
            rate = (next_record - (checkpoint["start_record"] if checkpoint else 1)) / elapsed if elapsed > 0 else 0
            remaining = total_count - next_record
            eta_sec = remaining / rate if rate > 0 else 0
            eta_str = str(datetime.timedelta(seconds=int(eta_sec)))
            
            print(f"\r   [NDL] Procesados: {next_record}/{total_count} | Guardados: {total_valid if 'total_valid' in locals() else total_saved} | ETA: {eta_str}   ", end="", flush=True)
            
            if next_record > total_count:
                break
                
            start_record = next_record
            time.sleep(DELAY)

    except KeyboardInterrupt:
        banner("\n🛑 Pausado por el usuario. Checkpoint guardado.", quiet)
    except Exception as e:
        banner(f"\n❌ Error fatal: {e}", quiet)

    banner(f"\n✅ Finalizado. Total: {total_saved}", quiet)

if __name__ == "__main__":
    main()
