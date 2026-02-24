import os
import json
from collections import defaultdict

BASE_DIR = os.path.join("data", "cinii", "v3_by_ndc_lang")
OUTPUT_JSON = "cinii_ndc_full_stats.json"
OUTPUT_MD = "cinii_resumen_ndc.md"

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
    "9": "Literatura"
}

LANG_NAMES = {
    "ALL": "Total",
    "JP": "Japonés (JP)",
    "EN": "Inglés (EN)",
    "ZH": "Chino (ZH)",
    "DE": "Alemán (DE)",
    "FR": "Francés (FR)",
    "RU": "Ruso (RU)",
    "IT": "Italiano (IT)",
    "ES": "Español (ES)",
    "KO": "Coreano (KO)"
}

def count_lines(filepath):
    count = 0
    with open(filepath, 'rb') as f:
        for line in f:
            count += 1
    return count

def main():
    # stats[year][ndc][lang] = count
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    # global_ndc[ndc][lang] = count
    global_ndc = defaultdict(lambda: defaultdict(int))
    # decade_stats[decade][ndc][lang] = count
    decade_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    years = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))])
    
    print(f"Procesando {len(years)} años...")
    
    for year_str in years:
        year = int(year_str)
        decade = (year // 10) * 10
        year_path = os.path.join(BASE_DIR, year_str)
        files = [f for f in os.listdir(year_path) if f.endswith(".jsonl")]
        
        for filename in files:
            parts = filename.replace(".jsonl", "").split("_")
            if len(parts) == 3:
                _, lang, ndc = parts
                count = count_lines(os.path.join(year_path, filename))
                
                stats[year_str][ndc][lang] = count
                if lang != "ALL":
                    global_ndc[ndc][lang] += count
                    global_ndc[ndc]["TOTAL"] += count
                    decade_stats[decade][ndc][lang] += count
                    decade_stats[decade][ndc]["TOTAL"] += count

    # Save JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)
    
    # Generate Markdown
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("# Resumen Estadístico por Materia (NDC) - CiNii (1850-1920)\n\n")
        
        f.write("## Resumen Global por Materia\n\n")
        
        for ndc_code in sorted(NDC_NAMES.keys()):
            ndc_name = NDC_NAMES[ndc_code]
            total_ndc = global_ndc[ndc_code]["TOTAL"]
            
            f.write(f"### NDC {ndc_code}: {ndc_name}\n")
            f.write(f"- **Total de registros:** {total_ndc:,}\n\n")
            
            if total_ndc > 0:
                f.write("| Idioma | Cantidad | Porcentaje |\n")
                f.write("| :--- | :---: | :---: |\n")
                
                langs = sorted(
                    [(l, c) for l, c in global_ndc[ndc_code].items() if l != "TOTAL"],
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for lang, count in langs:
                    if count > 0:
                        percentage = (count / total_ndc) * 100
                        lang_display = LANG_NAMES.get(lang, lang)
                        f.write(f"| {lang_display} | {count:,} | {percentage:.2f}% |\n")
                f.write("\n")
            else:
                f.write("*No hay registros para esta materia.*\n\n")
        
        f.write("## Resumen por Décadas\n\n")
        
        for decade in sorted(decade_stats.keys()):
            f.write(f"### Década de {decade}\n")
            decade_total = sum(decade_stats[decade][ndc]["TOTAL"] for ndc in decade_stats[decade])
            f.write(f"- **Total de documentos clasificados:** {decade_total:,}\n\n")
            
            f.write("| NDC | Materia | Idioma | Cantidad |\n")
            f.write("| :---: | :--- | :--- | :---: |\n")
            
            for ndc_code in sorted(NDC_NAMES.keys()):
                ndc_name = NDC_NAMES[ndc_code]
                if decade_stats[decade][ndc_code]["TOTAL"] > 0:
                    langs = sorted(
                        [(l, c) for l, c in decade_stats[decade][ndc_code].items() if l != "TOTAL" and c > 0],
                        key=lambda x: x[1],
                        reverse=True
                    )
                    for i, (lang, count) in enumerate(langs):
                        lang_display = LANG_NAMES.get(lang, lang)
                        ndc_display = ndc_code if i == 0 else ""
                        ndc_name_display = ndc_name if i == 0 else ""
                        f.write(f"| {ndc_display} | {ndc_name_display} | {lang_display} | {count:,} |\n")
            f.write("\n")

        f.write("## Desglose por Años (Materia e Idioma)\n\n")
        
        for year_str in years:
            f.write(f"### Año {year_str}\n")
            year_total = sum(stats[year_str][ndc][lang] for ndc in stats[year_str] for lang in stats[year_str][ndc] if lang != "ALL")
            if year_total == 0:
                f.write("*Sin registros*\n\n")
                continue
                
            f.write(f"- **Total del año:** {year_total:,}\n\n")
            
            f.write("| NDC | Materia | Idioma | Cantidad |\n")
            f.write("| :---: | :--- | :--- | :---: |\n")
            
            for ndc_code in sorted(NDC_NAMES.keys()):
                ndc_name = NDC_NAMES[ndc_code]
                langs = sorted(
                    [(l, c) for l, c in stats[year_str][ndc_code].items() if l != "ALL" and c > 0],
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for i, (lang, count) in enumerate(langs):
                    lang_display = LANG_NAMES.get(lang, lang)
                    ndc_display = ndc_code if i == 0 else ""
                    ndc_name_display = ndc_name if i == 0 else ""
                    f.write(f"| {ndc_display} | {ndc_name_display} | {lang_display} | {count:,} |\n")
            f.write("\n")

    print(f"Archivos generados: {OUTPUT_JSON} y {OUTPUT_MD}")

if __name__ == "__main__":
    main()
