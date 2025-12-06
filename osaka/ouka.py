#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ouka.py · Osaka University OAI-PMH harvester (palabras múltiples + fecha global)

• KEYWORDS: lista fija → basta que UNA aparezca en cualquier parte del <record>.
• YEAR check: escanea TODO el texto XML; si algún año ∈ [YEAR_MIN, YEAR_MAX] se acepta.
• Añade filas al Excel maestro (crea si no existe).
"""

import argparse, os, re, time, xml.etree.ElementTree as ET
import pandas as pd, requests
from openpyxl import load_workbook
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ─── CONFIG ──────────────────────────────────────────────────
BASE   = "https://ir.library.osaka-u.ac.jp/repo/mmd_api/oai-pmh/"
PREFIX = "oai_dc"
KEYWORDS = ["traductor", "translator", "翻訳", "번역자", "translation"]
YEAR_MIN, YEAR_MAX = 1850, 1920
EXCEL  = "merged_waseda_ndl.xlsx"
DELAY_LOT, DELAY_ERR = 2, 30
HEADERS = {"User-Agent": "Mozilla/5.0"}
# ─────────────────────────────────────────────────────────────

KW_RE   = re.compile(r"\b(" + "|".join(map(re.escape, KEYWORDS)) + r")\b", re.I)
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
        banner(f"📥 Lote {batch+1}: {len(recs)} registros", quiet)

        for rec in recs:
            yield rec

        token_elem = root.find(".//oai:resumptionToken", ns)
        token = token_elem.text.strip() if token_elem is not None and token_elem.text else None
        if not token:
            banner("🏁 Fin de lotes.", quiet); break
        batch += 1
        time.sleep(DELAY_LOT)

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

def load_master():
    base_cols = ["display_title","display_creator","display_publisher",
                 "display_creationdate","display_language","display_identifier"]
    if os.path.exists(EXCEL):
        return pd.read_excel(EXCEL), base_cols
    pd.DataFrame(columns=base_cols).to_excel(EXCEL, index=False)
    return pd.read_excel(EXCEL), base_cols

def append_rows(df_new, quiet):
    if df_new.empty:
        banner("⚠️ No filas nuevas.", quiet); return 0
    start = load_workbook(EXCEL).active.max_row if os.path.exists(EXCEL) else 0
    mode  = "a" if start else "w"
    with pd.ExcelWriter(EXCEL, engine="openpyxl", mode=mode,
                        if_sheet_exists="overlay") as w:
        df_new.to_excel(w, index=False, header=(start==0), startrow=start)
    return len(df_new)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-q","--quiet",   action="store_true", help="silencioso")
    ap.add_argument("-v","--verbose", action="store_true", help="verboso")
    args, quiet = ap.parse_args(), None
    quiet = args.quiet and not args.verbose

    master, cols = load_master()
    nuevos, vistos = [], 0
    banner("🚀 Palabras: " + ", ".join(KEYWORDS), quiet)

    for rec in harvest(quiet):
        vistos += 1
        if keyword_ok(rec) and year_ok(rec):
            nuevos.append(to_row(rec, cols))
        if not quiet and vistos % 100 == 0:
            print(f"   Revisados {vistos} – Válidos {len(nuevos)}")

    añad = append_rows(pd.DataFrame(nuevos, columns=cols), quiet)
    banner(f"✅ Añadidos {añad} (de {vistos}). Total filas: {len(master)+añad}", quiet)

if __name__ == "__main__":
    main()
