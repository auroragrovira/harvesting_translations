#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tokyo_idiomas.py · Harvester for UTokyo Repository (1850-1920)
All records in the time frame, focusing on title, author, language, publisher.
"""

import argparse, os, re, time, xml.etree.ElementTree as ET, json, sys, io, datetime
import requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── CONFIG ───────────────────────────────────────────────────
BASE   = "https://repository.dl.itc.u-tokyo.ac.jp/oai"
PREFIX = "oai_dc"
YEAR_MIN, YEAR_MAX = 1850, 1920
CHECKPOINT_FILE = "tokyo_idiomas_checkpoint.json"
HEADERS     = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/xml,application/xml,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
    "Connection": "keep-alive"
}
TIMEOUT     = 120
BACKOFF_ERR = 60
DELAY       = 2
MAX_ERR     = 5
# ─────────────────────────────────────────────────────────────

YEAR_RE = re.compile(r"\b(1[89]\d{2}|19\d{2}|20[0-2]\d)\b")

def banner(msg, quiet):
    if not quiet:
        print(msg, flush=True)

def append_to_jsonl(row, filename, quiet):
    """Añade una fila al archivo JSONL"""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return 1
    except Exception as e:
        banner(f"⚠️ Error escribiendo JSONL en {filename}: {e}", quiet)
        return 0

def save_checkpoint(token, filename, total_seen, total_valid):
    data = {
        "token": token,
        "filename": filename,
        "total_seen": total_seen,
        "total_valid": total_valid,
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

def harvest(quiet, starting_token=None):
    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("https://", HTTPAdapter(max_retries=Retry(total=0)))

    token, batch, err = starting_token, 0, 0
    ns = {"oai":"http://www.openarchives.org/OAI/2.0/"}

    while True:
        params = {"verb":"ListRecords", "metadataPrefix":PREFIX} if not token \
                 else {"verb":"ListRecords", "resumptionToken":token}
        try:
            r = session.get(BASE, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            if not r.text.lstrip().startswith("<?xml"):
                raise ValueError("Respuesta no-XML")
            root = ET.fromstring(r.text)
            err = 0                              # reset contador errores
        except Exception as e:
            err += 1
            banner(f"\n⚠️ {e}  ({err}/{MAX_ERR}) – espera {BACKOFF_ERR}s", quiet)
            if err >= MAX_ERR:
                raise RuntimeError("Demasiados errores consecutivos") from e
            time.sleep(BACKOFF_ERR)
            continue

        recs = root.findall(".//oai:record", ns)
        tok_el = root.find(".//oai:resumptionToken", ns)
        
        total_size = None
        if tok_el is not None:
            size_attr = tok_el.attrib.get("completeListSize")
            if size_attr:
                total_size = int(size_attr)
            token = tok_el.text.strip() if tok_el.text else None
        else:
            token = None

        yield recs, token, total_size

        if not token:
            break
        batch += 1
        time.sleep(DELAY)

def rec_to_text(rec):
    """Convierte el registro a texto plano para búsqueda de fechas."""
    return ET.tostring(rec, encoding="unicode", method="text")

def year_ok(text):
    """Comprueba si el texto contiene algún año en el rango permitido."""
    years = {int(y) for y in YEAR_RE.findall(text)}
    return any(YEAR_MIN <= y <= YEAR_MAX for y in years)

def to_row(rec):
    dc_ns = "{http://purl.org/dc/elements/1.1/}"
    dc = {}
    for el in rec.findall(f".//{dc_ns}*"):
        dc.setdefault(el.tag.replace(dc_ns, ""), []).append(el.text or "")
    
    # Intentar extraer país desde coverage o publisher si existe algo sospechoso
    # En oai_dc es difícil, pero mapeamos lo que hay
    row = {
        "display_title":        "; ".join(dc.get("title", [])),
        "display_creator":      "; ".join(dc.get("creator", [])),
        "display_publisher":    "; ".join(dc.get("publisher", [])),
        "display_creationdate": "; ".join(dc.get("date", [])),
        "display_language":     "; ".join(dc.get("language", [])),
        "display_type":         "; ".join(dc.get("type", [])),
        "display_identifier":   "; ".join(dc.get("identifier", [])),
        "display_coverage":     "; ".join(dc.get("coverage", [])), # A veces contiene país
        "source": "tokyo_idiomas"
    }
    return row

def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("-q","--quiet", action="store_true")
    argp.add_argument("-v","--verbose", action="store_true")
    argp.add_argument("--new", action="store_true", help="Ignorar checkpoint y empezar de cero")
    args   = argp.parse_args()
    quiet  = args.quiet and not args.verbose

    checkpoint = load_checkpoint() if not args.new else None
    
    # Nombre de archivo fijo según petición
    output_filename = "tokyo_idiomas_original_1.jsonl"
    
    if checkpoint:
        banner(f"🔄 Reanudando cosecha de IDIOMAS desde checkpoint ({checkpoint['timestamp']})", quiet)
        token = checkpoint["token"]
        # Mantener el nombre solicitado aunque vengamos de un checkpoint
        total_seen = checkpoint["total_seen"]
        total_valid = checkpoint["total_valid"]
    else:
        token = None
        total_seen = 0
        total_valid = 0
    
    banner(f"Archivo de salida: {output_filename}", quiet)
    banner(f"Franja temporal: {YEAR_MIN} - {YEAR_MAX}", quiet)
    start_time = time.time()

    try:
        for recs, next_token, total_count in harvest(quiet, starting_token=token):
            for rec in recs:
                total_seen += 1
                text_content = rec_to_text(rec)
                
                # Sin keywords, solo filtro de año
                if year_ok(text_content):
                    row = to_row(rec)
                    total_valid += append_to_jsonl(row, output_filename, quiet)
            
            # Guardar checkpoint después de cada lote
            if next_token:
                save_checkpoint(next_token, output_filename, total_seen, total_valid)
            else:
                if os.path.exists(CHECKPOINT_FILE):
                    os.remove(CHECKPOINT_FILE)

            # Progreso y ETA
            elapsed = time.time() - start_time
            rate = total_seen / elapsed if elapsed > 0 else 0
            
            progress_str = f"   [Idiomas] Vistos: {total_seen}"
            if total_count:
                remaining = total_count - total_seen
                eta_sec = remaining / rate if rate > 0 else 0
                eta_str = str(datetime.timedelta(seconds=int(eta_sec)))
                progress_str += f" / {total_count} ({remaining} rest.) | ETA: {eta_str}"
            else:
                progress_str += f" | Total: Desconocido"
            
            progress_str += f" | Válidos: {total_valid}   "
            print(f"\r{progress_str}", end="", flush=True)

    except KeyboardInterrupt:
        banner("\n🛑 Proceso de idiomas pausado. Checkpoint guardado.", quiet)
    except Exception as e:
        banner(f"\n❌ Error fatal en idiomas: {e}", quiet)

    banner(f"\n✅ Proceso de idiomas finalizado/pausado. Válidos: {total_valid} de {total_seen}", quiet)

if __name__ == "__main__":
    main()
