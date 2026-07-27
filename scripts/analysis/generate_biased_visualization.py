import matplotlib.pyplot as plt
import json
import os

# Configuración de paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_FILE = os.path.join(BASE_DIR, "data", "stats", "cinii_full_stats.json")
IMG_DIR = os.path.join(BASE_DIR, "images")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def generate_biased_plot():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    years = []
    totals = []
    
    # Filtrar años 1850-1920
    for year_str in sorted(data.keys(), key=int):
        year = int(year_str)
        if 1850 <= year <= 1920:
            val = data[year_str].get("TOTAL (ALL)", 0)
            if isinstance(val, int):
                years.append(year)
                totals.append(val)
    
    plt.figure(figsize=(14, 7))
    plt.plot(years, totals, marker='o', linestyle='-', color='red', linewidth=2, markersize=4, label="Volumen Bruto (con sesgo)")
    plt.fill_between(years, totals, color='red', alpha=0.1)
    
    # Anotación del pico
    peak_val = data["1900"]["TOTAL (ALL)"]
    plt.annotate(f'Pico 1900: {peak_val:,} registros\n(Sesgo de catalogación detectado)', 
                 xy=(1900, peak_val), 
                 xytext=(1885, peak_val * 0.8),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
                 fontsize=12, color='red', weight='bold')

    plt.title("Diagnóstico de Anomalías: Serie Temporal Bruta (1850-1920)", fontsize=16)
    plt.ylabel("Total de Documentos")
    plt.xlabel("Año")
    plt.yscale('log') # Escala logarítmica para apreciar el crecimiento y el pico
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    
    output_path = os.path.join(IMG_DIR, "linea_con_sesgo.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Gráfico generado en: {output_path}")

if __name__ == "__main__":
    generate_biased_plot()
