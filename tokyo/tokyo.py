#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tokyo.py · UTokyo Repository harvester (stream-save)

• KEYWORDS se buscan en TODO el texto del <record>.
• Un año cualquiera 1850-1920 en el XML → OK.
• Cada lote válido se vuelca enseguida a merged_waseda_ndl.xlsx
  (crea el archivo y respeta cabeceras). Bandera -q / -v mantenida.
"""

import argparse, os, re, time, xml.etree.ElementTree as ET
import pandas as pd, requests
from openpyxl import load_workbook
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── CONFIG ───────────────────────────────────────────────────
BASE   = "https://repository.dl.itc.u-tokyo.ac.jp/oai"
PREFIX = "oai_dc"
KEYWORDS = ["traductor", "translator", "翻訳", "번역자", "translation"]
YEAR_MIN, YEAR_MAX = 1850, 1920
EXCEL  = "merged_waseda_ndl.xlsx"
BATCH_WRITE = 100            # escribe cada N filas válidas
USER_AGENT  = {"User-Agent": "Mozilla/5.0"}
TIMEOUT     = 120
BACKOFF_ERR = 60
DELAY       = 2
MAX_ERR     = 5
# ─────────────────────────────────────────────────────────────

KW_RE   = re.compile(r"\b(" + "|".join(map(re.escape, KEYWORDS)) + r")\b", re.I)
YEAR_RE = re.compile(r"\b(1[89]\d{2}|19\d{2}|20[0-2]\d)\b")

def banner(msg, quiet):
    if not quiet:
        print(msg, flush=True)

def save_batch(df, cols, first_write):
    """Añade df al Excel inmediatamente."""
    mode = "a" if os.path.exists(EXCEL) else "w"
    startrow = load_workbook(EXCEL).active.max_row if mode == "a" else 0
    with pd.ExcelWriter(EXCEL, engine="openpyxl", mode=mode,
                        if_sheet_exists="overlay") as wr:
        df.to_excel(wr, index=False,
                    header=first_write and startrow == 0,
                    startrow=startrow)

def harvest(quiet):
    session = requests.Session()
    session.headers.update(USER_AGENT)
    session.mount("https://",
        HTTPAdapter(max_retries=Retry(total=0)))

    token, batch, err = None, 0, 0
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
            banner(f"⚠️ {e}  ({err}/{MAX_ERR}) – espera {BACKOFF_ERR}s", quiet)
            if err >= MAX_ERR:
                raise RuntimeError("Demasiados errores consecutivos") from e
            time.sleep(BACKOFF_ERR)
            continue

        recs = root.findall(".//oai:record", ns)
        banner(f"📥 Lote {batch+1}: {len(recs)} registros", quiet)
        for rec in recs:
            yield rec
        tok = root.find(".//oai:resumptionToken", ns)
        token = tok.text.strip() if tok is not None and tok.text else None
        if not token:
            banner("🏁 Fin de lotes.", quiet)
            break
        batch += 1
        time.sleep(DELAY)

def keyword_ok(rec):
    return bool(KW_RE.search(ET.tostring(rec, encoding="unicode", method="text")))

def year_ok(rec):
    years = {int(y) for y in YEAR_RE.findall(
             ET.tostring(rec, encoding="unicode", method="text"))}
    return any(YEAR_MIN <= y <= YEAR_MAX for y in years)

def to_row(rec, cols):
    dc_ns = "{http://purl.org/dc/elements/1.1/}"
    dc = {}
    for el in rec.findall(f".//{dc_ns}*"):
        dc.setdefault(el.tag.replace(dc_ns, ""), []).append(el.text or "")
    row = {c:"" for c in cols}
    row.update({
        "display_title":        "; ".join(dc.get("title", [])),
        "display_creator":      "; ".join(dc.get("creator", [])),
        "display_publisher":    "; ".join(dc.get("publisher", [])),
        "display_creationdate": "; ".join(dc.get("date", [])),
        "display_language":     "; ".join(dc.get("language", [])),
        "display_identifier":   "; ".join(dc.get("identifier", [])),
    })
    return row

def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("-q","--quiet", action="store_true")
    argp.add_argument("-v","--verbose", action="store_true")
    args   = argp.parse_args()
    quiet  = args.quiet and not args.verbose

    base_cols = ["display_title","display_creator","display_publisher",
                 "display_creationdate","display_language","display_identifier"]
    if not os.path.exists(EXCEL):
        pd.DataFrame(columns=base_cols).to_excel(EXCEL, index=False)
    first_write = False     # controla cabeceras solo la 1.ª vez
    buffer_rows, total_valid, total_seen = [], 0, 0

    banner(f"🚀 Palabras: {', '.join(KEYWORDS)}", quiet)

    for rec in harvest(quiet):
        total_seen += 1
        if keyword_ok(rec) and year_ok(rec):
            buffer_rows.append(to_row(rec, base_cols))
            total_valid += 1

        # Escribe cuando junta BATCH_WRITE filas válidas
        if len(buffer_rows) >= BATCH_WRITE:
            save_batch(pd.DataFrame(buffer_rows, columns=base_cols),
                       base_cols, first_write)
            first_write = True
            banner(f"💾 Guardadas {len(buffer_rows)} filas (acum {total_valid})", quiet)
            buffer_rows.clear()

        if not quiet and total_seen % 100 == 0:
            print(f"   Revisados {total_seen} – Válidos {total_valid}")

    # Guarda las filas restantes
    if buffer_rows:
        save_batch(pd.DataFrame(buffer_rows, columns=base_cols),
                   base_cols, first_write)

    banner(f"✅ Terminado: {total_valid} válidos de {total_seen}.", quiet)

if __name__ == "__main__":
    main()
