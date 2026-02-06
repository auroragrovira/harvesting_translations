import json
from collections import defaultdict

def analyze_missing_langs():
    with open('cinii_full_stats.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    languages = [
        "Japonés (JP)", "Inglés (EN)", "Chino (ZH)", "Alemán (DE)", 
        "Francés (FR)", "Ruso (RU)", "Italiano (IT)", "Español (ES)", 
        "Coreano (KO)"
    ]

    total_all = 0
    total_tracked = 0
    
    for year_str, stats in data.items():
        t_year = stats.get("TOTAL (ALL)", 0)
        if isinstance(t_year, str): continue
        total_all += t_year
        
        for lang in languages:
            count = stats.get(lang, 0)
            if isinstance(count, str): continue
            total_tracked += count

    print(f"Total Global (API ALL): {total_all:,}")
    print(f"Total Registros Clasificados: {total_tracked:,}")
    print(f"Diferencia (Otros/Vacíos): {total_all - total_tracked:,}")
    print(f"Porcentaje Clasificado: {(total_tracked/total_all*100):.2f}%")
    print(f"Porcentaje Sin Clasificar: {((total_all - total_tracked)/total_all*100):.2f}%")

if __name__ == "__main__":
    analyze_missing_langs()
