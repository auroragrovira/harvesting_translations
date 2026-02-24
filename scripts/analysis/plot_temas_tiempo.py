#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_temas_tiempo.py
====================
Genera un mapa de calor (heatmap) de los residuos estandarizados del análisis Chi-cuadrado
entre Año y Materia (NDC) para el periodo 1850-1920.

Uso:
    python scripts/analysis/plot_temas_tiempo.py
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import sys
from scipy.stats import chi2_contingency

# Ajustar paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_FILE = os.path.join(BASE_DIR, "reports", "csv", "muestra_jsonl_resumen.csv")
OUT_IMG = os.path.join(BASE_DIR, "reports", "analysis", "heatmap_temas_tiempo.png")

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

def load_data():
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: No existe {CSV_FILE}")
        sys.exit(1)
        
    df = pd.read_csv(CSV_FILE)
    # Convertir año a numérico para filtrar (Undated -> NaN)
    df["año_num"] = pd.to_numeric(df["año"], errors='coerce')
    df = df[(df["idioma"] == "ALL") & (df["año_num"] >= 1850) & (df["año_num"] <= 1920)]
    
    # Usar año_num como index
    df = df.rename(columns={"año_num": "año_idx"})
    
    # Pivotar: Index=Año, Columns=NDC, Values=num_registros
    pivot = df.pivot_table(index="año_idx", columns="ndc", values="num_registros", aggfunc="sum", fill_value=0)
    
    # Mapear nombres de columnas
    pivot.columns = [f"{c} {NDC_NAMES.get(str(c), '')[:3]}." for c in pivot.columns]
    
    return pivot

def calculate_residuals(df):
    """Calcula residuos estandarizados ajustados (Haberman)."""
    observed = df.values
    chi2, p, dof, expected = chi2_contingency(observed)
    
    # Residuos de Pearson: (O - E) / sqrt(E)
    pearson_residuals = (observed - expected) / np.sqrt(expected)
    
    # Ajuste Haberman (Std. Residuals)
    # r_adj = (O - E) / sqrt(E * (1 - row_prop) * (1 - col_prop))
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)
    n = observed.sum()
    
    row_props = row_totals / n
    col_props = col_totals / n
    
    # Outer product para obtener denominador
    outer_den = np.outer(1 - row_props, 1 - col_props)
    std_residuals = (observed - expected) / np.sqrt(expected * outer_den)
    
    return pd.DataFrame(std_residuals, index=df.index, columns=df.columns)

def plot_heatmap(residuals):
    plt.figure(figsize=(12, 16))
    
    # Mapa de calor
    # Center=0 para que blanco sea neutro, rojo positivo (auge), azul negativo (caída)
    sns.heatmap(residuals, cmap="RdBu_r", center=0, annot=False, cbar_kws={'label': 'Residuo Estandarizado'})
    
    plt.title("Evolución de Temas (1850-1920)\nResiduos Estandarizados (Auge vs Caída)", fontsize=16)
    plt.xlabel("Materia (NDC)", fontsize=12)
    plt.ylabel("Año", fontsize=12)
    
    plt.tight_layout()
    plt.savefig(OUT_IMG, dpi=300)
    print(f"Gráfico guardado en: {OUT_IMG}")

def main():
    print("Cargando datos...")
    df = load_data()
    print(f"Datos: {df.shape[0]} años x {df.shape[1]} categorías")
    
    print("Calculando residuos...")
    residuals = calculate_residuals(df)
    
    print("Generando gráfico...")
    plot_heatmap(residuals)

if __name__ == "__main__":
    main()
