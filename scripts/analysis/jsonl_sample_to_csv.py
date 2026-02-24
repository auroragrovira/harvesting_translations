# -*- coding: utf-8 -*-
"""
jsonl_sample_to_csv.py
======================
Recorre univ_jp/3/ y agrega los JSONL en un CSV resumen.

Los ficheros siguen el patrón: cinii_{IDIOMA}_{NDC}.jsonl
  - IDIOMA: JP, EN, DE, FR, ZH, ES, IT, RU, KO, ALL
  - NDC: 0-9

Para cada fichero cuenta los registros y genera un CSV con:
  año, ndc, idioma, num_registros

Uso:
    python scripts/jsonl_sample_to_csv.py
"""

import csv
import os
import re
import sys
import json
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLE_DIR = os.path.join(BASE_DIR, "data", "cinii", "v3_by_ndc_lang")
OUT_DIR = os.path.join(BASE_DIR, "reports", "csv")

NDC_NAMES = {
    "0": "Generalidades",
    "1": "Filosofía",
    "2": "Historia",
    "3": "Ciencias Sociales",
    "4": "Ciencias Naturales",
    "5": "Tecnología",
    "6": "Industria",
    "7": "Artes",
    "8": "Lenguaje",
    "9": "Literatura",
}


def count_records(filepath, dir_year):
    """Cuenta registros y los clasifica por año real o 'Undated'."""
    counts = defaultdict(int)
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                date_raw = str(record.get("display_creationdate", ""))
                
                # Si el año es 1900 y la fecha es genérica o indeterminada, marcar como Undated
                if dir_year == "1900" and (date_raw == "19--" or date_raw == "1900" or date_raw == "190-"):
                    counts["Undated"] += 1
                else:
                    counts[dir_year] += 1
            except:
                continue
    return counts


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=== Agregando JSONL de univ_jp/3 a CSV ===\n")

    rows = []
    pattern = re.compile(r"cinii_([A-Za-z]+)_(\d+)\.jsonl")

    if not os.path.exists(SAMPLE_DIR):
        print(f"ERROR: No existe {SAMPLE_DIR}")
        sys.exit(1)

    year_dirs = sorted([
        d for d in os.listdir(SAMPLE_DIR)
        if os.path.isdir(os.path.join(SAMPLE_DIR, d)) and re.match(r"\d{4}", d)
    ])

    for year_dir in year_dirs:
        year_path = os.path.join(SAMPLE_DIR, year_dir)
        files = sorted([
            f for f in os.listdir(year_path)
            if f.endswith(".jsonl")
        ])

        for fname in files:
            m = pattern.match(fname)
            if not m:
                print(f"  WARN: No se pudo parsear nombre: {fname}")
                continue

            idioma = m.group(1).upper()
            ndc = m.group(2)
            filepath = os.path.join(year_path, fname)
            
            # Obtener contajes (puede haber 'Undated' y el año del dir)
            counts = count_records(filepath, year_dir)

            for result_year, num_registros in counts.items():
                if num_registros > 0:
                    rows.append({
                        "año": result_year,
                        "ndc": ndc,
                        "materia": NDC_NAMES.get(ndc, ""),
                        "idioma": idioma,
                        "num_registros": num_registros,
                    })

    # Escribir CSV
    out_path = os.path.join(OUT_DIR, "muestra_jsonl_resumen.csv")
    fieldnames = ["año", "ndc", "materia", "idioma", "num_registros"]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  -> {out_path}  ({len(rows)} filas)")
    print(f"\n  Años procesados: {len(year_dirs)}")
    print(f"  Ficheros JSONL procesados: {len(rows)}")

    # Resumen rápido
    total_registros = sum(r["num_registros"] for r in rows)
    print(f"  Total de registros en la muestra: {total_registros:,}")

    print("\n=== Agregación completada ===")


if __name__ == "__main__":
    main()
