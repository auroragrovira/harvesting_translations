#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
nichibun_idiomas_originales.py · Processor for Nichibun XML files (jpcoar_2.0)
Extracts all records between 1850-1920 without keyword filters.
"""

import os, re, xml.etree.ElementTree as ET, json, sys, io, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── CONFIG ───────────────────────────────────────────────────
YEAR_MIN, YEAR_MAX = 1850, 1920
XML_PATTERN = re.compile(r"nichibun_jpcoar2_all_\d+\.xml")
JSONL_OUTPUT = "nichibun_idiomas_original_1.jsonl"
# ─────────────────────────────────────────────────────────────

YEAR_RE = re.compile(r"\b(1[89]\d{2}|19\d{2}|20[0-2]\d)\b")

def banner(msg):
    print(msg, flush=True)

def get_xml_files():
    """Busca archivos XML que coincidan con el patrón en la carpeta 'resultados'."""
    results_dir = "resultados"
    if not os.path.exists(results_dir):
        return []
    files = [f for f in os.listdir(results_dir) if XML_PATTERN.match(f)]
    # Ordenar numéricamente por el número en el nombre
    files.sort(key=lambda x: int(re.search(r"(\d+)", x).group(1)))
    return files

def year_ok(text):
    """Comprueba si el texto contiene algún año en el rango permitido."""
    years = {int(y) for y in YEAR_RE.findall(text)}
    return any(YEAR_MIN <= y <= YEAR_MAX for y in years)

def parse_nichibun_xml(file_name):
    """Procesa un archivo XML de Nichibun (formato jpcoar 2.0)."""
    file_path = os.path.join("resultados", file_name)
    ns = {
        "oai": "http://www.openarchives.org/OAI/2.0/",
        "jpcoar": "https://github.com/JPCOAR/schema/blob/master/2.0/"
    }
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        banner(f"⚠️ Error cargando {file_path}: {e}")
        return

    records = root.findall(".//oai:record", ns)
    valid_count = 0
    
    for rec in records:
        # Extraer todo el texto del registro para el filtro de fecha
        text_content = ET.tostring(rec, encoding="unicode", method="text")
        
        if year_ok(text_content):
            metadata = rec.find(".//metadata", ns)
            if metadata is None: continue
            
            # jpcoar suele ser el hijo directo de metadata
            jp = metadata.find("{https://github.com/JPCOAR/schema/blob/master/2.0/}jpcoar")
            if jp is None: continue
            
            row = extract_jpcoar_data(jp)
            if row:
                append_to_jsonl(row)
                valid_count += 1
                
    return len(records), valid_count

def extract_jpcoar_data(jp):
    """Mapea los campos de jpcoar 2.0 a nuestro formato estándar."""
    ns_prefix = "{https://github.com/JPCOAR/schema/blob/master/2.0/}"
    
    def get_texts(tag):
        return [el.text for el in jp.findall(f"{ns_prefix}{tag}") if el.text]

    row = {
        "display_title":        "; ".join(get_texts("title")),
        "display_creator":      "; ".join(get_texts("creatorName") or get_texts("creator")),
        "display_publisher":    "; ".join(get_texts("publisherName")),
        "display_creationdate": "; ".join(get_texts("date")),
        "display_language":     "; ".join(get_texts("language")),
        "display_type":         "; ".join(get_texts("type")),
        "display_coverage":     "; ".join(get_texts("spatial")),
        "display_identifier":   "; ".join([el.text for el in jp.findall(f"{ns_prefix}identifier") if el.text]),
        "source": "nichibun_idiomas"
    }
    return row

def append_to_jsonl(row):
    with open(JSONL_OUTPUT, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def main():
    xml_files = get_xml_files()
    if not xml_files:
        banner("❌ No se encontraron archivos XML. Ejecuta primero 'nichi.bat' para descargarlos.")
        return

    banner(f"🚀 Procesando {len(xml_files)} archivos XML de Nichibun...")
    banner(f"📅 Rango: {YEAR_MIN}-{YEAR_MAX} | Salida: {JSONL_OUTPUT}")
    
    total_processed = 0
    total_valid = 0
    
    for f in xml_files:
        processed, valid = parse_nichibun_xml(f)
        total_processed += processed
        total_valid += valid
        print(f"   [Archivo] {f:<30} | Vistos: {processed:>4} | Válidos: {valid:>4}", flush=True)

    banner(f"\n✅ Proceso completado.")
    banner(f"📊 Total registros revisados: {total_processed}")
    banner(f"📊 Total registros válidos:   {total_valid}")
    banner(f"📄 Resultado guardado en: {JSONL_OUTPUT}")

if __name__ == "__main__":
    main()
