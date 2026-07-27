#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_visualizations.py
==========================
Genera visualizaciones clave para el proyecto Harvesting Translations (1850-1920).

Este script utiliza dos fuentes de datos:
1. data/stats/cinii_full_stats.json: Para gráficos de área e importancia de idiomas (POBLACIÓN TOTAL).
2. reports/csv/muestra_jsonl_resumen.csv: Para el mapa de calor temático (MUESTRA ENRIQUECIDA).

Uso:
    python scripts/analysis/generate_visualizations.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import numpy as np
from scipy.stats import chi2_contingency

# Configuración de estilo
sns.set_theme(style="whitegrid")
sns.set_context("talk")

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_FILE = os.path.join(BASE_DIR, "reports", "csv", "muestra_jsonl_resumen.csv")
STATS_JSON = os.path.join(BASE_DIR, "data", "stats", "cinii_full_stats.json")
IMG_DIR = os.path.join(BASE_DIR, "images")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# Mapeo de nombres de idiomas para el JSON
LANG_MAP = {
    "Japonés (JP)": "JP",
    "Inglés (EN)": "EN",
    "Chino (ZH)": "ZH",
    "Alemán (DE)": "DE",
    "Francés (FR)": "FR",
    "Español (ES)": "ES",
    "Italiano (IT)": "IT",
    "Ruso (RU)": "RU",
    "Coreano (KO)": "KO"
}

NDC_NAMES = {
    "0": "Generalidades", "1": "Filosofía", "2": "Historia",
    "3": "Ciencias Soc.", "4": "Ciencias Nat.", "5": "Tecnología",
    "6": "Industria", "7": "Artes", "8": "Lenguaje", "9": "Literatura",
}

def load_full_stats():
    """Carga los datos totales (población) desde el JSON."""
    if not os.path.exists(STATS_JSON):
        print(f"WARN: No existe {STATS_JSON}. Usando escalas de muestra.")
        return None
        
    with open(STATS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rows = []
    for year_str, stats in data.items():
        year = int(year_str)
        if 1850 <= year <= 1920:
            for full_name, short_name in LANG_MAP.items():
                val = stats.get(full_name, 0)
                if isinstance(val, int):
                    rows.append({
                        "Año": year,
                        "Idioma": short_name,
                        "Registros": val
                    })
    return pd.DataFrame(rows)

def load_sample_csv():
    """Carga la muestra enriquecida desde el CSV."""
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: No existe {CSV_FILE}")
        return None
    return pd.read_csv(CSV_FILE)

def plot_languages_area(df_full):
    """Genera gráficos de área usando la población total."""
    print("Generating Language Area Charts (Full Scale)...")
    if df_full is None: return

    pivot_df = df_full.pivot(index="Año", columns="Idioma", values="Registros").fillna(0)
    order = ["JP"] + [l for l in pivot_df.sum().sort_values(ascending=False).index if l != "JP"]
    pivot_df = pivot_df[order]

    # 1. Absoluto
    plt.figure(figsize=(14, 8))
    pivot_df.plot.area(ax=plt.gca(), alpha=0.8, cmap="tab20")
    plt.title("Evolución del Volumen de Publicaciones por Idioma (1850-1920)", fontsize=18)
    plt.ylabel("Número de Registros (Escala Real)")
    plt.xlabel("Año")
    plt.legend(title="Idioma", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "area_idiomas_absoluto.png"), dpi=300)
    plt.close()

    # 2. Proporcional
    plt.figure(figsize=(14, 8))
    pivot_perc = pivot_df.div(pivot_df.sum(axis=1), axis=0) * 100
    pivot_perc.plot.area(ax=plt.gca(), alpha=0.8, cmap="tab20")
    plt.title("Evolución de la Cuota de Mercado por Idioma (1850-1920)", fontsize=18)
    plt.ylabel("Porcentaje (%)")
    plt.xlabel("Año")
    plt.legend(title="Idioma", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "area_idiomas_proporcion.png"), dpi=300)
    plt.close()

def plot_heatmap_residuals(df_sample):
    """Genera heatmap de residuos usando la muestra enriquecida (NDC)."""
    print("Generating Thematic Heatmap (Sample Data)...")
    if df_sample is None: return
    
    df_all = df_sample[df_sample["idioma"] == "ALL"].copy()
    df_all = df_all[df_all["año"] != "Undated"]
    df_all["año_num"] = pd.to_numeric(df_all["año"])
    df_all = df_all[(df_all["año_num"] >= 1850) & (df_all["año_num"] <= 1920)]

    pivot = df_all.pivot_table(index="año_num", columns="ndc", values="num_registros", aggfunc="sum", fill_value=0)
    
    observed = pivot.values
    chi2, p, dof, expected = chi2_contingency(observed)
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)
    n = observed.sum()
    outer_den = np.outer(1 - row_totals/n, 1 - col_totals/n)
    residuals = (observed - expected) / np.sqrt(expected * outer_den)
    
    residuals_df = pd.DataFrame(residuals, index=pivot.index, columns=[f"{c} {NDC_NAMES.get(str(c), '')}" for c in pivot.columns])
    
    plt.figure(figsize=(14, 20))
    sns.heatmap(residuals_df, cmap="RdBu_r", center=0, cbar_kws={'label': 'Residuo Estandarizado'})
    plt.title("Evolución Temática: Auge y Caída Relativa (Muestra Limpia)", fontsize=18)
    plt.ylabel("Año")
    plt.xlabel("Materia (NDC)")
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "heatmap_temas_residuos.png"), dpi=300)
    plt.close()

def plot_total_volume(df_full):
    """Genera línea de volumen total usando población real."""
    print("Generating Total Volume Line (Full Scale)...")
    if df_full is None: return
    
    total_by_year = df_full.groupby("Año")["Registros"].sum()

    plt.figure(figsize=(14, 6))
    plt.plot(total_by_year.index, total_by_year.values, marker='o', color='black', markersize=3, linewidth=1)
    plt.fill_between(total_by_year.index, total_by_year.values, color='gray', alpha=0.1)
    plt.title("Crecimiento del Corpus Recolectado (1850-1920)", fontsize=18)
    plt.ylabel("Total de Documentos (Población)")
    plt.xlabel("Año")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "linea_volumen_total.png"), dpi=300)
    plt.close()

def main():
    print("=== Generando Visualizaciones Combinadas ===")
    df_full = load_full_stats()
    df_sample = load_sample_csv()
    
    plot_languages_area(df_full)
    plot_heatmap_residuals(df_sample)
    plot_total_volume(df_full)
    
    print(f"\n[OK] Gráficos generados en: {IMG_DIR}")

if __name__ == "__main__":
    main()
