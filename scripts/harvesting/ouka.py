#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ouka.py · Osaka University OAI-PMH harvester (palabras múltiples + fecha global)

• KEYWORDS: lista fija → basta que UNA aparezca en cualquier parte del <record>.
• YEAR check: escanea TODO el texto XML; si algún año ∈ [YEAR_MIN, YEAR_MAX] se acepta.
• Añade filas al Excel maestro (crea si no existe).
"""

import argparse, os, re, time, xml.etree.ElementTree as ET, json, sys, io
import requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ─── CONFIG ──────────────────────────────────────────────────
BASE   = "https://ir.library.osaka-u.ac.jp/repo/mmd_api/oai-pmh/"
PREFIX = "oai_dc"
KEYWORDS = ["traductor", "translator", "翻訳", "번역자", "translation", "翻译者"]
YEAR_MIN, YEAR_MAX = 1850, 1920
JSONL_OUTPUT = os.path.join("data", "osaka", "osaka_results.jsonl")
DELAY_LOT, DELAY_ERR = 2, 30
HEADERS = {"User-Agent": "Mozilla/5.0"}
# ─────────────────────────────────────────────────────────────

YEAR_RE = re.compile(r"\b(1[89]\d{2}|19\d{2}|20[0-2]\d)\b")

def banner(msg, quiet):
    if not quiet:
        print(msg, flush=True)

def harvest(quiet):
    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("https://",
        HTTPAdapter(max_retries=Retry(total=3, backoff_factor=3)))

    ns = {"oai": "http://www.openarchives.org/OAI/2.0/"}
    token, batch = None, 0

    while True:
        params = {"verb":"ListRecords", "metadataPrefix":PREFIX} if not token \
                 else {"verb":"ListRecords", "resumptionToken":token}
        r = session.get(BASE, params=params, timeout=60)

        # Garantiza XML válido; reintento si devuelve HTML
        if not r.text.lstrip().startswith("<?xml"):
            banner(f"⚠️ HTML/ERROR {r.status_code}. Espera {DELAY_ERR}s…", quiet)
            time.sleep(DELAY_ERR); continue

        root = ET.fromstring(r.text)
        recs = root.findall(".//oai:record", ns)
        banner(f"Lote {batch+1}: {len(recs)} registros", quiet)

        for rec in recs:
            yield rec

        token_elem = root.find(".//oai:resumptionToken", ns)
        token = token_elem.text.strip() if token_elem is not None and token_elem.text else None
        if not token:
            banner("🏁 Fin de lotes.", quiet); break
        batch += 1
        time.sleep(DELAY_LOT)

def keyword_ok(rec, kw):
    return bool(re.search(r"\b" + re.escape(kw) + r"\b", ET.tostring(rec, encoding="unicode", method="text"), re.I))

def year_ok(rec):
    years = {int(y) for y in YEAR_RE.findall(
             ET.tostring(rec, encoding="unicode", method="text"))}
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
        "source": "osaka"
    }
    return row

def append_to_jsonl(row, quiet):
    """Añade una fila al archivo JSONL"""
    try:
        with open(JSONL_OUTPUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return 1
    except Exception as e:
        banner(f"⚠️ Error escribiendo JSONL: {e}", quiet)
        return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-q","--quiet",   action="store_true", help="silencioso")
    ap.add_argument("-v","--verbose", action="store_true", help="verboso")
    args, quiet = ap.parse_args(), None
    quiet = args.quiet and not args.verbose

    # Limpiar archivo JSONL anterior si existe
    if os.path.exists(JSONL_OUTPUT):
        os.remove(JSONL_OUTPUT)
    
    total_vistos, total_añadidos = 0, 0
    banner(f"Guardando en: {JSONL_OUTPUT}", quiet)

    for kw in KEYWORDS:
        banner(f"\n--- Buscando palabra clave: {kw} ---", quiet)
        vistos, añadidos = 0, 0
        for rec in harvest(quiet):
            vistos += 1
            if keyword_ok(rec, kw) and year_ok(rec):
                row = to_row(rec, kw)
                añadidos += append_to_jsonl(row, quiet)
            if not quiet and vistos % 100 == 0:
                print(f"   [{kw}] Revisados {vistos} – Válidos {añadidos}")
        
        banner(f"Fin palabra '{kw}': {añadidos} añadidos de {vistos}.", quiet)
        total_vistos += vistos
        total_añadidos += añadidos

    banner(f"✅ Proceso completo: {total_añadidos} totales (de {total_vistos}) en {JSONL_OUTPUT}", quiet)

if __name__ == "__main__":
    main()
