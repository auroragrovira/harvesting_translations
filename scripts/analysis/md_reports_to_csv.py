# -*- coding: utf-8 -*-
"""
md_reports_to_csv.py
====================
Parsea los informes markdown de reports/historical/ y reports/specific/
y genera CSVs explotables en reports/csv/.

Uso:
    python scripts/md_reports_to_csv.py
"""

import csv
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_HIST = os.path.join(BASE_DIR, "reports", "historical")
REPORTS_SPEC = os.path.join(BASE_DIR, "reports", "specific")
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

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def clean_num(s):
    """Elimina separadores de miles y espacios, devuelve int o float."""
    s = s.strip().replace(",", "").replace(".", "").replace("\u00a0", "")
    if not s or s == "-":
        return 0
    return int(s)


def clean_pct(s):
    """Extrae porcentaje como float."""
    s = s.strip().replace("%", "").replace(",", ".")
    if not s or s == "-":
        return 0.0
    return float(s)


def write_csv(filepath, rows, fieldnames):
    """Escribe una lista de dicts a CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  -> {filepath}  ({len(rows)} filas)")


def read_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.readlines()

# ---------------------------------------------------------------------------
# 1. Parsear cinii_resumen_ndc*.md  (API y muestra)
#    Estructura: Resumen Global por Materia, Resumen por Décadas, Desglose por Años
# ---------------------------------------------------------------------------

def parse_ndc_report(filepath, fuente):
    """
    Parsea cinii_resumen_ndc.md o cinii_resumen_ndc_api.md.
    Devuelve filas con: fuente, nivel, periodo, ndc, materia, idioma, cantidad, porcentaje
    """
    lines = read_lines(filepath)
    rows = []
    current_ndc = None
    current_materia = None
    current_nivel = None  # "global", "decada", "año"
    current_periodo = None
    in_table = False

    # Mapeo de idiomas con nombre largo a código
    lang_map = {
        "Francés (FR)": "FR", "Japonés (JP)": "JP", "Chino (ZH)": "ZH",
        "Inglés (EN)": "EN", "Español (ES)": "ES", "Alemán (DE)": "DE",
        "Italiano (IT)": "IT", "Ruso (RU)": "RU", "Coreano (KO)": "KO",
    }

    for line in lines:
        line = line.strip()

        # Detectar secciones de nivel
        if re.match(r"^##\s+Resumen Global", line):
            current_nivel = "global"
            current_periodo = "1850-1920"
            continue
        if re.match(r"^##\s+Resumen por Décadas", line):
            current_nivel = "decada"
            continue
        if re.match(r"^##\s+Desglose por Años", line):
            current_nivel = "año"
            continue

        # Detectar NDC encabezado dentro de sección global
        m = re.match(r"^###\s+NDC\s+(\d+):\s+(.+)", line)
        if m:
            current_ndc = m.group(1)
            current_materia = m.group(2).strip()
            in_table = False
            continue

        # Detectar década
        m = re.match(r"^###\s+Década de\s+(\d{4})", line)
        if m:
            current_periodo = m.group(1) + "s"
            current_ndc = None
            current_materia = None
            in_table = False
            continue

        # Detectar año
        m = re.match(r"^###\s+Año\s+(\d{4})", line)
        if m:
            current_periodo = m.group(1)
            current_ndc = None
            current_materia = None
            in_table = False
            continue

        # Detectar inicio de tabla (header separador)
        if line.startswith("| :"):
            in_table = True
            continue

        # Parsear filas de tabla
        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]  # quitar vacíos
            if not cells:
                continue

            if current_nivel == "global":
                # Tabla global: | Idioma | Cantidad | Porcentaje |
                if len(cells) >= 3:
                    idioma_raw = cells[0]
                    idioma = lang_map.get(idioma_raw, idioma_raw)
                    cantidad = clean_num(cells[1])
                    porcentaje = clean_pct(cells[2])
                    if cantidad > 0:
                        rows.append({
                            "fuente": fuente, "nivel": current_nivel,
                            "periodo": current_periodo, "ndc": current_ndc,
                            "materia": current_materia, "idioma": idioma,
                            "cantidad": cantidad, "porcentaje": porcentaje,
                        })
            elif current_nivel in ("decada", "año"):
                # Tabla década/año: | NDC | Materia | Idioma | Cantidad | (opt %) |
                if len(cells) >= 4:
                    ndc_cell = cells[0].strip()
                    materia_cell = cells[1].strip()
                    idioma_raw = cells[2].strip()
                    cantidad_raw = cells[3].strip()

                    # Filas con NDC vacío heredan del anterior
                    if ndc_cell:
                        current_ndc = ndc_cell
                        current_materia = materia_cell if materia_cell else NDC_NAMES.get(ndc_cell, "")
                    if materia_cell and not ndc_cell:
                        current_materia = materia_cell
                    if not current_materia and current_ndc:
                        current_materia = NDC_NAMES.get(current_ndc, "")

                    idioma = lang_map.get(idioma_raw, idioma_raw)
                    cantidad = clean_num(cantidad_raw)
                    porcentaje = clean_pct(cells[4]) if len(cells) >= 5 else 0.0

                    if cantidad > 0:
                        rows.append({
                            "fuente": fuente, "nivel": current_nivel,
                            "periodo": current_periodo, "ndc": current_ndc,
                            "materia": current_materia, "idioma": idioma,
                            "cantidad": cantidad, "porcentaje": porcentaje,
                        })

        # Fin de tabla
        if in_table and not line.startswith("|") and line != "":
            in_table = False

    return rows

# ---------------------------------------------------------------------------
# 2. Parsear cinii_resumen_estadistico.md
# ---------------------------------------------------------------------------

def parse_estadistico(filepath):
    """
    Parsea cinii_resumen_estadistico.md.
    Devuelve filas: nivel, periodo, idioma, cantidad, porcentaje
    """
    lines = read_lines(filepath)
    rows = []
    current_nivel = None
    current_periodo = None
    in_table = False

    lang_map = {
        "Francés (FR)": "FR", "Japonés (JP)": "JP", "Chino (ZH)": "ZH",
        "Inglés (EN)": "EN", "Español (ES)": "ES", "Alemán (DE)": "DE",
        "Italiano (IT)": "IT", "Ruso (RU)": "RU", "Coreano (KO)": "KO",
    }

    for line in lines:
        line = line.strip()

        if re.match(r"^##\s+Resumen Global", line):
            current_nivel = "global"
            current_periodo = "1850-1920"
            continue

        m = re.match(r"^###\s+Década de\s+(\d{4})", line)
        if m:
            current_nivel = "decada"
            current_periodo = m.group(1) + "s"
            in_table = False
            continue

        if line.startswith("| :"):
            in_table = True
            continue

        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 3:
                idioma_raw = cells[0]
                idioma = lang_map.get(idioma_raw, idioma_raw)
                cantidad = clean_num(cells[1])
                porcentaje = clean_pct(cells[2])
                if cantidad > 0:
                    rows.append({
                        "nivel": current_nivel, "periodo": current_periodo,
                        "idioma": idioma, "cantidad": cantidad,
                        "porcentaje": porcentaje,
                    })

        if in_table and not line.startswith("|") and line != "":
            in_table = False

    return rows

# ---------------------------------------------------------------------------
# 3. Parsear cinii_edo_resumen.md
# ---------------------------------------------------------------------------

def parse_edo_resumen(filepath):
    """
    Parsea cinii_edo_resumen.md (1800-1850).
    Devuelve filas: nivel, periodo, idioma, cantidad, porcentaje
    """
    lines = read_lines(filepath)
    rows = []
    current_nivel = None
    current_periodo = None
    in_table = False

    lang_map = {
        "Francés (FR)": "FR", "Japonés (JP)": "JP", "Chino (ZH)": "ZH",
        "Inglés (EN)": "EN", "Español (ES)": "ES", "Alemán (DE)": "DE",
        "Italiano (IT)": "IT", "Ruso (RU)": "RU", "Coreano (KO)": "KO",
        "Latín (LA)": "LA", "Holandés (NL)": "NL",
    }

    for line in lines:
        line = line.strip()

        if re.match(r"^##\s+1\.\s+Resumen Global", line):
            current_nivel = "global"
            current_periodo = "1800-1850"
            continue

        m = re.match(r"^###\s+Década de\s+(\d{4})", line)
        if m:
            current_nivel = "decada"
            current_periodo = m.group(1) + "s"
            in_table = False
            continue

        m = re.match(r"^###\s+Año\s+(\d{4})", line)
        if m:
            current_nivel = "año"
            current_periodo = m.group(1)
            in_table = False
            continue

        if line.startswith("| :"):
            in_table = True
            continue

        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 3:
                idioma_raw = cells[0]
                # Saltar filas de excedente
                if "Excedente" in idioma_raw or "Multilingüismo" in idioma_raw:
                    continue
                idioma = lang_map.get(idioma_raw, idioma_raw)
                cantidad = clean_num(cells[1])
                porcentaje = clean_pct(cells[2])
                if cantidad > 0:
                    rows.append({
                        "nivel": current_nivel, "periodo": current_periodo,
                        "idioma": idioma, "cantidad": cantidad,
                        "porcentaje": porcentaje,
                    })

        if in_table and not line.startswith("|") and line != "":
            in_table = False

    return rows

# ---------------------------------------------------------------------------
# 4. Parsear traducciones
# ---------------------------------------------------------------------------

def parse_traducciones(filepath, periodo_label):
    """
    Parsea cinii_translation_stats.md o cinii_edo_traducciones.md.
    Devuelve filas con datos de traducciones.
    """
    lines = read_lines(filepath)
    rows = []
    current_nivel = None
    current_periodo = None
    current_decada = None
    in_table = False
    table_type = None  # "resumen_decada", "ndc_decada", "anual"

    for line in lines:
        line = line.strip()

        # Detectar sección de resumen por décadas
        if re.match(r"^##\s+2\.\s+Resumen por Décadas", line) or re.match(r"^##\s+3\.\s+Resumen por Décadas", line):
            table_type = "resumen_decada"
            current_nivel = "decada"
            in_table = False
            continue

        # Detectar sección de NDC por décadas
        if re.match(r"^##\s+3\.\s+Desglose por Materia", line):
            table_type = "ndc_decada"
            current_nivel = "decada_ndc"
            in_table = False
            continue

        # Detectar sección anual
        if re.match(r"^##\s+4\.\s+Desglose", line) or re.match(r"^##\s+4\.\s+Desglose Anual", line):
            table_type = "anual"
            current_nivel = "año"
            in_table = False
            continue

        # Detectar década
        m = re.match(r"^###\s+Década de\s+(\d{4})", line)
        if m:
            current_decada = m.group(1) + "s"
            current_periodo = current_decada
            in_table = False
            continue

        if line.startswith("| :"):
            in_table = True
            continue

        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]

            if table_type == "resumen_decada" and len(cells) >= 4:
                rows.append({
                    "nivel": "decada", "periodo": cells[0].strip(),
                    "ndc": "", "materia": "",
                    "total_jpn": clean_num(cells[1]),
                    "traducciones": clean_num(cells[2]),
                    "porcentaje": clean_pct(cells[3]),
                })
            elif table_type == "ndc_decada" and len(cells) >= 5:
                rows.append({
                    "nivel": "decada_ndc", "periodo": current_decada,
                    "ndc": cells[0], "materia": cells[1],
                    "total_jpn": clean_num(cells[2]),
                    "traducciones": clean_num(cells[3]),
                    "porcentaje": clean_pct(cells[4]),
                })
            elif table_type == "anual" and len(cells) >= 4:
                rows.append({
                    "nivel": "año", "periodo": cells[0],
                    "ndc": "", "materia": "",
                    "total_jpn": clean_num(cells[1]),
                    "traducciones": clean_num(cells[2]),
                    "porcentaje": clean_pct(cells[3]) if "%" in cells[3] else clean_pct(cells[4]) if len(cells) >= 5 else 0.0,
                })

        if in_table and not line.startswith("|") and line != "":
            in_table = False

    return rows

# ---------------------------------------------------------------------------
# 5. Parsear evolución de proporciones
# ---------------------------------------------------------------------------

def parse_evolucion(filepath):
    """
    Parsea cinii_evolucion_proporciones.md.
    Genera varias tablas a partir de las secciones.
    """
    lines = read_lines(filepath)
    all_rows = []
    current_section = None
    in_table = False
    header_cols = []

    for line in lines:
        line = line.strip()

        if re.match(r"^##\s+1\.\s+Evolución por Idiomas", line):
            current_section = "idiomas"
            in_table = False
            continue
        if re.match(r"^##\s+2\.\s+Evolución por Materias", line):
            current_section = "materias"
            in_table = False
            continue
        if re.match(r"^##\s+3\.\s+Evolución Cruzada", line):
            current_section = "cruzada"
            in_table = False
            continue
        m = re.match(r"^###\s+Evolución en\s+(.+?)\s*\(NDC\s+(\d+)\)", line)
        if m:
            current_section = f"cruzada_ndc{m.group(2)}"
            in_table = False
            continue

        # Detectar header
        if line.startswith("|") and "Década" in line:
            header_cols = [c.strip() for c in line.split("|")[1:-1]]
            continue
        if line.startswith("| :"):
            in_table = True
            continue

        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            row = {"seccion": current_section}
            for i, col in enumerate(header_cols):
                if i < len(cells):
                    row[col] = cells[i]
            all_rows.append(row)

        if in_table and not line.startswith("|") and line != "":
            in_table = False

    return all_rows

# ---------------------------------------------------------------------------
# 6. Parsear cinii_api_resumen_matriz.md
# ---------------------------------------------------------------------------

def parse_api_matriz(filepath):
    """
    Parsea cinii_api_resumen_matriz.md (solo datos globales por NDC).
    """
    lines = read_lines(filepath)
    rows = []
    current_ndc = None
    current_materia = None
    in_table = False

    for line in lines:
        line = line.strip()

        m = re.match(r"^###\s+NDC\s+(\d+):\s+(.+)", line)
        if m:
            current_ndc = m.group(1)
            current_materia = m.group(2).strip()
            in_table = False
            continue

        if line.startswith("| :"):
            in_table = True
            continue

        if in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 3:
                idioma = cells[0]
                cantidad = clean_num(cells[1])
                porcentaje = clean_pct(cells[2])
                if cantidad > 0:
                    rows.append({
                        "ndc": current_ndc, "materia": current_materia,
                        "idioma": idioma, "cantidad": cantidad,
                        "porcentaje": porcentaje,
                    })

        if in_table and not line.startswith("|") and line != "":
            in_table = False

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("=== Convirtiendo MDs a CSVs ===\n")

    # 1. NDC API (población)
    fp = os.path.join(REPORTS_HIST, "cinii_resumen_ndc_api.md")
    if os.path.exists(fp):
        rows = parse_ndc_report(fp, "api")
        write_csv(os.path.join(OUT_DIR, "ndc_api.csv"), rows,
                  ["fuente", "nivel", "periodo", "ndc", "materia", "idioma", "cantidad", "porcentaje"])

    # 2. NDC muestra
    fp = os.path.join(REPORTS_HIST, "cinii_resumen_ndc.md")
    if os.path.exists(fp):
        rows = parse_ndc_report(fp, "muestra")
        write_csv(os.path.join(OUT_DIR, "ndc_muestra.csv"), rows,
                  ["fuente", "nivel", "periodo", "ndc", "materia", "idioma", "cantidad", "porcentaje"])

    # 3. Estadístico global
    fp = os.path.join(REPORTS_HIST, "cinii_resumen_estadistico.md")
    if os.path.exists(fp):
        rows = parse_estadistico(fp)
        write_csv(os.path.join(OUT_DIR, "estadistico_global.csv"), rows,
                  ["nivel", "periodo", "idioma", "cantidad", "porcentaje"])

    # 4. Edo resumen
    fp = os.path.join(REPORTS_HIST, "cinii_edo_resumen.md")
    if os.path.exists(fp):
        rows = parse_edo_resumen(fp)
        write_csv(os.path.join(OUT_DIR, "edo_resumen.csv"), rows,
                  ["nivel", "periodo", "idioma", "cantidad", "porcentaje"])

    # 5. Traducciones 1850-1920
    fp = os.path.join(REPORTS_SPEC, "cinii_translation_stats.md")
    if os.path.exists(fp):
        rows = parse_traducciones(fp, "1850-1920")
        write_csv(os.path.join(OUT_DIR, "traducciones_1850_1920.csv"), rows,
                  ["nivel", "periodo", "ndc", "materia", "total_jpn", "traducciones", "porcentaje"])

    # 6. Traducciones Edo
    fp = os.path.join(REPORTS_HIST, "cinii_edo_traducciones.md")
    if os.path.exists(fp):
        rows = parse_traducciones(fp, "1800-1850")
        write_csv(os.path.join(OUT_DIR, "traducciones_edo.csv"), rows,
                  ["nivel", "periodo", "ndc", "materia", "total_jpn", "traducciones", "porcentaje"])

    # 7. Evolución proporciones
    fp = os.path.join(REPORTS_HIST, "cinii_evolucion_proporciones.md")
    if os.path.exists(fp):
        rows = parse_evolucion(fp)
        if rows:
            fieldnames = list(rows[0].keys())
            # Recabar todas las claves
            for r in rows:
                for k in r.keys():
                    if k not in fieldnames:
                        fieldnames.append(k)
            write_csv(os.path.join(OUT_DIR, "evolucion_proporciones.csv"), rows, fieldnames)

    # 8. API Matriz global
    fp = os.path.join(REPORTS_HIST, "cinii_api_resumen_matriz.md")
    if os.path.exists(fp):
        rows = parse_api_matriz(fp)
        write_csv(os.path.join(OUT_DIR, "api_matriz_global.csv"), rows,
                  ["ndc", "materia", "idioma", "cantidad", "porcentaje"])

    print("\n=== Conversión completada ===")


if __name__ == "__main__":
    main()
