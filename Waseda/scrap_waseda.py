#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
scrap_waseda.py  –  Primo VE scraper (Waseda University)

• Descarga resultados en lotes de 50 y los vuelca en un Excel incremental.
• Filtra (opcional) registros que contengan ALGÚN año dentro del rango indicado
  en cualquier campo cuyo nombre incluya 'date'.
• Reintentos HTTP automáticos con back-off.
• Tras dos errores seguidos lanza ipconfig /release & /renew (solo Windows).
"""

import requests, pandas as pd, time, os, subprocess, re
from openpyxl import load_workbook
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ───────── CONFIGURACIÓN ─────────
SEARCH_QUERY = "翻译者"      # cambia por «翻译者», «번역자», etc.
ENABLE_YEAR_FILTER = True       # True = activar filtro; False = guardar todo
YEAR_MIN, YEAR_MAX = 1850, 1920
FILENAME      = "waseda_primo_results.xlsx"
START_OFFSET  = 5050               # reanudar manualmente (múltiplo de 50)
LIMIT         = 50              # tamaño del lote (máx. permitido)
SHORT_DELAY   = 2               # s entre lotes
LONG_DELAY    = 10              # s cada 10 lotes
ERR_DELAY     = 30              # s tras reintentos agotados
MAX_ERRS      = 2               # invoca ipconfig tras N fallos seguidos
TIMEOUT       = 60              # seg. para cada llamada
# ─────────────────────────────────

BASE = "https://waseda.primo.exlibrisgroup.com/primaws/rest/pub/pnxs"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

# sesión con reintentos
retry_strategy = Retry(
    total            = 3,
    backoff_factor   = 3,                 # 3 s, 6 s, 9 s…
    status_forcelist = [429, 500, 502, 503, 504],
    allowed_methods  = ["GET"]
)
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

year_pattern = re.compile(r"\b(1[89]\d{2}|19\d{2}|20[0-2]\d)\b")  # 1800-2029

# ───────── FUNCIONES ─────────
def fetch(offset: int) -> dict:
    params = {
        "q"    : f"any,contains,{SEARCH_QUERY}",
        "vid"  : "81SOKEI_WUNI:WINE",
        "lang" : "en",
        "offset": offset,
        "limit" : LIMIT
    }
    r = session.get(BASE, params=params, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    js = r.json()
    total = js.get("info", {}).get("total", "?")
    print(f"→ offset={offset:<5} docs={len(js.get('docs', []))} / total≈{total}")
    return js

def year_ok(doc: dict) -> bool:
    """True si ALGÚN año del doc está dentro del rango."""
    if not ENABLE_YEAR_FILTER:
        return True
    for section, content in doc.get("pnx", {}).items():
        for key, values in content.items():
            if "date" not in key.lower():
                continue
            if not isinstance(values, list):
                values = [values]
            for val in values:
                for yr_str in year_pattern.findall(str(val)):
                    yr = int(yr_str)
                    if YEAR_MIN <= yr <= YEAR_MAX:
                        return True
    return False

def flatten(doc: dict) -> dict:
    flat = {}
    for section, content in doc.get("pnx", {}).items():
        for k, v in content.items():
            flat[f"{section}_{k}"] = "; ".join(v) if isinstance(v, list) else str(v) or ""
    return flat

def append_excel(df: pd.DataFrame):
    if os.path.exists(FILENAME):
        start = load_workbook(FILENAME).active.max_row
        with pd.ExcelWriter(FILENAME, engine="openpyxl", mode="a", if_sheet_exists="overlay") as wr:
            df.to_excel(wr, index=False, header=False, startrow=start)
    else:
        df.to_excel(FILENAME, index=False)

def release_renew():
    print("🔄  ipconfig /release & /renew …")
    try:
        subprocess.run("ipconfig /release", check=True, shell=True, stdout=subprocess.DEVNULL)
        time.sleep(3)
        subprocess.run("ipconfig /renew",  check=True, shell=True, stdout=subprocess.DEVNULL)
        print("   ✅ DHCP renovado.")
    except subprocess.CalledProcessError:
        print("   ⚠️  No se pudo renovar DHCP (continúa).")

# ───────── MAIN LOOP ─────────
def main():
    offset = START_OFFSET
    saved, batch_no, consecutive_err = 0, 0, 0
    total_expected = None

    while True:
        try:
            js = fetch(offset)
            consecutive_err = 0
        except Exception as e:
            consecutive_err += 1
            print(f"❗ {type(e).__name__}: {e}  (err {consecutive_err}/{MAX_ERRS})")
            if consecutive_err >= MAX_ERRS:
                release_renew()
                consecutive_err = 0
            print(f"⏳ Espera {ERR_DELAY}s…")
            time.sleep(ERR_DELAY)
            continue

        docs = js.get("docs", [])
        if not docs:
            print("🛑 Lote vacío → fin de datos.")
            break

        if total_expected is None:
            total_expected = js.get("info", {}).get("total", 0)

        good = [d for d in docs if year_ok(d)]
        if good:
            append_excel(pd.DataFrame([flatten(d) for d in good]))
            saved += len(good)

        batch_no += 1
        print(f"✅ batch {batch_no}: {len(good)}/{len(docs)} guardados | acumulado={saved}/{total_expected}")

        offset += len(docs)
        time.sleep(LONG_DELAY if batch_no % 10 == 0 else SHORT_DELAY)

        if saved >= total_expected:
            break

    print(f"\n🏁 Export finalizado: {saved} registros guardados en «{FILENAME}»")

# ───────── EJECUCIÓN ─────────
if __name__ == "__main__":
    if os.name != "nt":
        print("La auto-renovación IP solo funciona en Windows.")
    main()
