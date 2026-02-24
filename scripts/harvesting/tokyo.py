#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tokyo.py · UTokyo Repository harvester (stream-save) with Resume & Progress tracking
"""

import argparse, os, re, time, xml.etree.ElementTree as ET, json, sys, io, datetime
import requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── CONFIG ───────────────────────────────────────────────────
BASE   = "https://repository.dl.itc.u-tokyo.ac.jp/oai"
PREFIX = "oai_dc"
KEYWORDS = ["traductor", "translator", "翻訳", "번역자", "translation", "翻译者"]
YEAR_MIN, YEAR_MAX = 1850, 1920
CHECKPOINT_FILE = "tokyo_checkpoint.json"
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
    return ET.tostring(rec, encoding="unicode", method="text")

def keyword_matches(text):
    found = []
    for kw in KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", text, re.I):
            found.append(kw)
    return found

def year_ok(text):
    years = {int(y) for y in YEAR_RE.findall(text)}
    return any(YEAR_MIN <= y <= YEAR_MAX for y in years)

def to_row(rec, kw):
    dc_ns = "{http://purl.org/dc/elements/1.1/}"
    dc = {}
    for el in rec.findall(f".//{dc_ns}*"):
        dc.setdefault(el.tag.replace(dc_ns, ""), []).append(el.text or "")
    row = {
        "display_title":        "; ".join(dc.get("title", [])),
        "display_creator":      "; ".join(dc.get("creator", [])),
        "display_publisher":    "; ".join(dc.get("publisher", [])),
        "display_creationdate": "; ".join(dc.get("date", [])),
        "display_language":     "; ".join(dc.get("language", [])),
        "display_identifier":   "; ".join(dc.get("identifier", [])),
        "matched_keyword": kw,
        "source": "tokyo"
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
    
    if checkpoint:
        banner(f"🔄 Reanudando desde checkpoint ({checkpoint['timestamp']})", quiet)
        token = checkpoint["token"]
        output_filename = checkpoint["filename"]
        total_seen = checkpoint["total_seen"]
        total_valid = checkpoint["total_valid"]
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = os.path.join("data", "tokyo", f"tokyo_results_{timestamp}.jsonl")
        token = None
        total_seen = 0
        total_valid = 0
    
    banner(f"Archivo de salida: {output_filename}", quiet)
    start_time = time.time()

    try:
        for recs, next_token, total_count in harvest(quiet, starting_token=token):
            for rec in recs:
                total_seen += 1
                text_content = rec_to_text(rec)
                
                if year_ok(text_content):
                    matches = keyword_matches(text_content)
                    if matches:
                        for kw in matches:
                            row = to_row(rec, kw)
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
            
            progress_str = f"   [Progreso] Vistos: {total_seen}"
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
        banner("\n🛑 Proceso pausado por el usuario. Checkpoint guardado.", quiet)
    except Exception as e:
        banner(f"\n❌ Error fatal: {e}", quiet)

    banner(f"\n✅ Proceso finalizado/pausado. Válidos: {total_valid} de {total_seen}", quiet)

if __name__ == "__main__":
    main()
