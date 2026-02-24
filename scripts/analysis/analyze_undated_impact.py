import os
import json
import glob
import sys
import io
from collections import defaultdict

# Set stdout to utf-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_1900_DIR = os.path.join(BASE_DIR, "data", "cinii", "v2_by_lang")
REPORTS_DIR = os.path.join(BASE_DIR, "reports", "analysis")

def analyze_undated():
    print("Analizando impacto de registros sin fecha en 1900...")
    
    # Buscamos los archivos de 1900
    files = glob.glob(os.path.join(DATA_1900_DIR, "*1900*.jsonl"))
    if not files:
        # Intentar ruta alternativa si existe v3
        DATA_1900_DIR_V3 = os.path.join(BASE_DIR, "data", "cinii", "v3_by_ndc_lang", "1900")
        files = glob.glob(os.path.join(DATA_1900_DIR_V3, "*.jsonl"))
        
    if not files:
        print("Error: No se encontraron archivos de datos para el año 1900.")
        return

    stats = {
        "total": 0,
        "undated_19xx": 0,  # 19--
        "pure_1900": 0,    # 1900 exacto
        "specific_1900": 0, # 1900.XX.XX
        "junk_title": 0,    # Sin título o título genérico
        "modern_ed": 0      # Editoriales conocidas como modernas (Open University, etc)
    }

    modern_publishers = ["放送大学教育振興会", "ティーアンドエイチ"]

    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue # Skip malformed lines
                
                stats["total"] += 1
                
                date_raw = str(record.get("display_creationdate", ""))
                title = record.get("display_title", "")
                publisher = record.get("display_publisher", "")
                
                # Clasificación de fecha
                if "19--" in date_raw or date_raw == "190-":
                    stats["undated_19xx"] += 1
                elif date_raw == "1900":
                    stats["pure_1900"] += 1
                elif "1900" in date_raw and len(date_raw) > 4:
                    stats["specific_1900"] += 1
                
                # Junk detection
                if not title or "[出版者不明]" in title or "Unknown" in title:
                    stats["junk_title"] += 1
                
                if any(p in str(publisher) for p in modern_publishers):
                    stats["modern_ed"] += 1

    # Generar informe
    report = []
    report.append("# Informe de Impacto: Registros Problemáticos en 1900")
    report.append(f"\n**Total registros analizados:** {stats['total']:,}")
    report.append("\n## Desglose de Calidad de Datos")
    report.append("\n| Categoría | Cantidad | Porcentaje |")
    report.append("| :--- | :---: | :---: |")
    
    def row(label, count):
        pct = (count / stats["total"] * 100) if stats["total"] > 0 else 0
        return f"| {label} | {count:,} | {pct:.2f}% |"

    report.append(row("**Sin Fecha (19--)**", stats["undated_19xx"]))
    report.append(row("Fecha Genérica (1900)", stats["pure_1900"]))
    report.append(row("Fecha Específica (1900-XX-XX)", stats["specific_1900"]))
    report.append(row("Títulos Genéricos/Basura", stats["junk_title"]))
    report.append(row("Editorial Moderna Detectada", stats["modern_ed"]))
    
    useful = stats["total"] - stats["undated_19xx"] - stats["pure_1900"]
    report.append(f"\n**Estimación de registros útiles para serie temporal:** {useful:,} ({ (useful/stats['total']*100) if stats['total']>0 else 0:.2f}%)")
    
    report.append("\n## Conclusión Técnica")
    report.append("\nEl sistema debe clasificar como `Undated` todo registro cuya fecha sea exactamente '19--' o '1900' sin metadatos adicionales de día/mes. "
                  "Esto eliminará el sesgo del año 1900 en las visualizaciones de tendencia.")

    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(os.path.join(REPORTS_DIR, "undated_impact_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print(f"Informe generado en: {os.path.join(REPORTS_DIR, 'undated_impact_report.md')}")

if __name__ == "__main__":
    analyze_undated()
