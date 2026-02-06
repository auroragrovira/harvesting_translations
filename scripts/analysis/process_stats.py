import json
from collections import defaultdict

def process_stats():
    with open('cinii_full_stats.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    global_total = 0
    global_langs = defaultdict(int)

    decades = defaultdict(lambda: {"total": 0, "langs": defaultdict(int)})

    languages = [
        "Japonés (JP)", "Inglés (EN)", "Chino (ZH)", "Alemán (DE)", 
        "Francés (FR)", "Ruso (RU)", "Italiano (IT)", "Español (ES)", 
        "Coreano (KO)"
    ]

    for year_str, stats in data.items():
        year = int(year_str)
        decade = (year // 10) * 10
        
        total_year = stats.get("TOTAL (ALL)", 0)
        if isinstance(total_year, str):
            total_year = 0
        
        global_total += total_year
        decades[decade]["total"] += total_year

        for lang in languages:
            count = stats.get(lang, 0)
            if isinstance(count, str):
                count = 0
            
            global_langs[lang] += count
            decades[decade]["langs"][lang] += count

    # Generate the report
    report = []
    report.append("# Resumen Estadístico de CiNii (1850-1920)")
    report.append("\n## Resumen Global: Todos los años")
    report.append(f"- **Total de documentos:** {global_total:,}")
    report.append("\n| Idioma | Cantidad | Porcentaje |")
    report.append("| :--- | :---: | :---: |")
    
    for lang in languages:
        count = global_langs[lang]
        percentage = (count / global_total * 100) if global_total > 0 else 0
        report.append(f"| {lang} | {count:,} | {percentage:.2f}% |")

    report.append("\n## Resumen por Décadas")
    
    sorted_decades = sorted(decades.keys())
    for decade in sorted_decades:
        d_total = decades[decade]["total"]
        report.append(f"\n### Década de {decade}")
        report.append(f"- **Total de documentos:** {d_total:,}")
        report.append("\n| Idioma | Cantidad | Porcentaje |")
        report.append("| :--- | :---: | :---: |")
        
        for lang in languages:
            count = decades[decade]["langs"][lang]
            percentage = (count / d_total * 100) if d_total > 0 else 0
            report.append(f"| {lang} | {count:,} | {percentage:.2f}% |")

    with open('cinii_resumen_estadistico.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(report))

    print("Informe generado en 'cinii_resumen_estadistico.md'")

if __name__ == "__main__":
    process_stats()
