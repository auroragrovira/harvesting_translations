#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_visualizations.py
==========================
Genera visualizaciones clave para el proyecto Harvesting Translations (1850-1920).

Gráficos generados en reports/images/:
1. heatmap_temas_residuos.png: Residuos estandarizados (auge/caída) de NDCs.
2. area_idiomas_absoluto.png: Evolución del volumen de publicaciones por idioma.
3. area_idiomas_proporcion.png: Evolución del porcentaje de mercado de cada idioma.
4. linea_volumen_total.png: Crecimiento total del corpus.

Uso:
    python scripts/analysis/generate_visualizations.py
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import sys
from scipy.stats import chi2_contingency

# Configuración de estilo
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("talk")

# Ajustar paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_FILE = os.path.join(BASE_DIR, "reports", "csv", "muestra_jsonl_resumen.csv")
IMG_DIR = os.path.join(BASE_DIR, "reports", "images")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

NDC_NAMES = {
    "0": "Generalidades", "1": "Filosofía", "2": "Historia",
    "3": "Ciencias Soc.", "4": "Ciencias Nat.", "5": "Tecnología",
    "6": "Industria", "7": "Artes", "8": "Lenguaje", "9": "Literatura",
}

def load_data():
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: No existe {CSV_FILE}")
        sys.exit(1)
        
    df = pd.read_csv(CSV_FILE)
    # Convertir año a numérico para filtrar (Undated -> NaN)
    df["año_num"] = pd.to_numeric(df["año"], errors='coerce')
    df = df[(df["año_num"] >= 1850) & (df["año_num"] <= 1920)]
    # Usar año_num como la columna año para el resto del script
    df["año"] = df["año_num"].astype(int)
    return df

def plot_heatmap_residuals(df):
    """1. Heatmap de Residuos Estandarizados (NDC vs Año)"""
    print("Generating Heatmap...")
    
    # Filtrar solo ALL para totales por tema
    df_all = df[df["idioma"] == "ALL"]
    pivot = df_all.pivot_table(index="año", columns="ndc", values="num_registros", aggfunc="sum", fill_value=0)
    
    # Calcular residuos
    observed = pivot.values
    chi2, p, dof, expected = chi2_contingency(observed)
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)
    n = observed.sum()
    outer_den = np.outer(1 - row_totals/n, 1 - col_totals/n)
    residuals = (observed - expected) / np.sqrt(expected * outer_den)
    
    residuals_df = pd.DataFrame(residuals, index=pivot.index, columns=[f"{c} {NDC_NAMES.get(str(c), '')}" for c in pivot.columns])
    
    plt.figure(figsize=(14, 20))
    sns.heatmap(residuals_df, cmap="RdBu_r", center=0, annot=False, cbar_kws={'label': 'Residuo Estandarizado (Z-score)'})
    plt.title("Evolución Temática: Auge y Caída Relativa (1850-1920)", fontsize=16, pad=20)
    plt.ylabel("Año")
    plt.xlabel("Materia (NDC)")
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "heatmap_temas_residuos.png"), dpi=300)
    plt.close()

def plot_languages_area(df):
    """2. Gráfico de Áreas Apiladas (Idiomas)"""
    print("Generating Language Area Charts...")
    
    # Excluir ALL y filtrar idiomas principales si hay muchos
    df_lang = df[df["idioma"] != "ALL"]
    
    # Pivotar: Index=Año, Columns=Idioma
    pivot = df_lang.pivot_table(index="año", columns="idioma", values="num_registros", aggfunc="sum", fill_value=0)
    
    # Ordenar columnas por volumen total
    top_langs = pivot.sum().sort_values(ascending=False).index
    pivot = pivot[top_langs]
    
    # 2a. Absoluto
    plt.figure(figsize=(14, 8))
    pivot.plot.area(stacked=True, alpha=0.9, cmap="tab20", figsize=(14, 8))
    plt.title("Evolución del Volumen de Publicaciones por Idioma (1850-1920)", fontsize=16)
    plt.ylabel("Número de Registros")
    plt.xlabel("Año")
    plt.legend(title="Idioma", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "area_idiomas_absoluto.png"), dpi=300)
    plt.close()
    
    # 2b. Proporcional (100%)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
    
    plt.figure(figsize=(14, 8))
    pivot_pct.plot.area(stacked=True, alpha=0.9, cmap="tab20", figsize=(14, 8))
    plt.title("Evolución de la Cuota de Mercado por Idioma (1850-1920)", fontsize=16)
    plt.ylabel("Porcentaje (%)")
    plt.xlabel("Año")
    plt.legend(title="Idioma", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.margins(0, 0)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "area_idiomas_proporcion.png"), dpi=300)
    plt.close()

def plot_total_volume(df):
    """3. Línea de Volumen Total"""
    print("Generating Total Volume Line...")
    
    # Usar ALL para el total real
    df_all = df[df["idioma"] == "ALL"]
    total_per_year = df_all.groupby("año")["num_registros"].sum()
    
    plt.figure(figsize=(14, 6))
    plt.plot(total_per_year.index, total_per_year.values, marker='o', linestyle='-', color='black', linewidth=2, markersize=4)
    plt.fill_between(total_per_year.index, total_per_year.values, color='gray', alpha=0.1)
    
    plt.title("Crecimiento del Corpus Recolectado (1850-1920)", fontsize=16)
    plt.ylabel("Total de Documentos")
    plt.xlabel("Año")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, "linea_volumen_total.png"), dpi=300)
    plt.close()

def main():
    print("=== Generando Visualizaciones ===")
    df = load_data()
    
    plot_heatmap_residuals(df)
    plot_languages_area(df)
    plot_total_volume(df)
    
    print(f"\n[OK] Gráficos generados en: {IMG_DIR}")

if __name__ == "__main__":
    main()
