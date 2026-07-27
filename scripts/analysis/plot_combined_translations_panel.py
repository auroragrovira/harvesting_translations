#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_combined_translations_panel.py
===================================
Genera el Panel Combinado (Gráficas 2 y 3):
- Panel 2 (Izquierda): Distribución por lenguas de origen (Escala académica formal en miles).
- Panel 3 (Derecha): Penetración temática por disciplinas (NDC) (Escala académica formal en miles).
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# --- ESTILO Y CONFIGURACIÓN ---
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATS_DIR = os.path.join(BASE_DIR, "data", "stats")
FULL_STATS_FILE = os.path.join(STATS_DIR, "cinii_full_stats.json")
MATRIX_FILE = os.path.join(STATS_DIR, "cinii_api_matrix_ndc_lang.json")
IMG_DIR = os.path.join(BASE_DIR, "images")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# Mapeo de idiomas y colores estandarizados del proyecto
LANG_CODE_MAP = {
    "EN": "Inglés (EN)",
    "DE": "Alemán (DE)",
    "ZH": "Chino (ZH)",
    "FR": "Francés (FR)",
    "RU": "Ruso (RU)",
    "IT": "Italiano (IT)",
    "ES": "Español (ES)",
    "KO": "Coreano (KO)"
}

LANG_COLORS = {
    "Inglés (EN)": "#059669",     # Emerald Green
    "Alemán (DE)": "#d97706",     # Amber
    "Chino (ZH)": "#dc2626",      # Crimson Red
    "Francés (FR)": "#7c3aed",    # Violet
    "Ruso (RU)": "#475569",       # Slate
    "Italiano (IT)": "#0891b2",   # Cyan
    "Español (ES)": "#e11d48",    # Rose
    "Coreano (KO)": "#ec4899"     # Pink
}

def format_thousands(x, pos):
    """Formateador académico formal: valores expresados en miles."""
    val = x / 1000.0
    if val.is_integer():
        return f"{int(val)}"
    return f"{val:.1f}"

def load_data():
    # 1. Cargar datos del Panel 2 (Lenguas de origen 1850-1920)
    with open(FULL_STATS_FILE, "r", encoding="utf-8") as f:
        full_data = json.load(f)

    lang_totals = {name: 0 for name in LANG_CODE_MAP.values()}

    for year, d in full_data.items():
        for key, val in d.items():
            if val == "Error" or not isinstance(val, (int, float)):
                continue
            for code, name in LANG_CODE_MAP.items():
                if code in key:
                    lang_totals[name] += int(val)

    df_lang = pd.DataFrame(list(lang_totals.items()), columns=["Idioma", "Cantidad"])
    df_lang = df_lang.sort_values(by="Cantidad", ascending=True)
    total_foreign = df_lang["Cantidad"].sum()
    df_lang["Porcentaje"] = (df_lang["Cantidad"] / total_foreign * 100) if total_foreign > 0 else 0

    # 2. Cargar datos del Panel 3 (Matriz NDC x Lengua)
    with open(MATRIX_FILE, "r", encoding="utf-8") as f:
        matrix_data = json.load(f)

    NDC_MAP = {
        "1": "NDC 1: Filosofía y Religión",
        "6": "NDC 6: Industria y Tecnología",
        "7": "NDC 7: Artes",
        "8": "NDC 8: Lenguaje y Lingüística",
        "9": "NDC 9: Literatura"
    }

    rows_ndc = []
    for ndc_code, info in matrix_data.items():
        if ndc_code in NDC_MAP and info.get("TOTAL", 0) > 0:
            label = NDC_MAP[ndc_code]
            for code, name in LANG_CODE_MAP.items():
                val = info.get(code, 0)
                if val > 0:
                    rows_ndc.append({
                        "materia": label,
                        "idioma": name,
                        "cantidad": val
                    })

    df_ndc = pd.DataFrame(rows_ndc)
    totals_ndc = df_ndc.groupby("materia")["cantidad"].sum().sort_values(ascending=True)
    ordered_materias = totals_ndc.index.tolist()

    pivot_ndc = df_ndc.pivot(index="materia", columns="idioma", values="cantidad").fillna(0).reindex(ordered_materias)

    return df_lang, pivot_ndc, totals_ndc

def main():
    df_lang, pivot_ndc, totals_ndc = load_data()

    all_langs = [l for l in LANG_COLORS.keys() if l in df_lang["Idioma"].values or l in pivot_ndc.columns]

    # --- CONFIGURACIÓN DE LA FIGURA MULTI-PANEL CON ANCHO AMPLIADO Y SIN TRASLAPOS ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7.5), dpi=300)
    fig.patch.set_facecolor('#f8fafc')
    ax1.set_facecolor('#ffffff')
    ax2.set_facecolor('#ffffff')

    # --- PANEL 2 (Izquierda): Distribución por Lenguas de Origen ---
    colors_lang = [LANG_COLORS.get(l, "#94a3b8") for l in df_lang["Idioma"]]
    bars1 = ax1.barh(df_lang["Idioma"], df_lang["Cantidad"], color=colors_lang, alpha=0.88, height=0.58)

    max_c1 = df_lang["Cantidad"].max()
    for bar, perc in zip(bars1, df_lang["Porcentaje"]):
        width = bar.get_width()
        ax1.annotate(f"{width:,} ({perc:.1f}%)",
                     xy=(width, bar.get_y() + bar.get_height() / 2),
                     xytext=(6, 0),
                     textcoords="offset points",
                     ha='left', va='center', fontsize=9.5, fontweight='bold', color='#1e293b')

    ax1.set_title("Distribución por lenguas de origen", fontsize=13.5, fontweight='bold', pad=14, color='#0f172a')
    ax1.set_xlabel("Número de documentos (en miles)", fontsize=11.5, labelpad=8, color='#334155')
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_thousands))
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))
    ax1.grid(axis='x', linestyle='--', alpha=0.5)
    ax1.grid(visible=False, axis='y')
    ax1.set_xlim(0, max_c1 * 1.25)
    sns.despine(ax=ax1, left=True, bottom=True)

    # --- PANEL 3 (Derecha): Penetración Temática por Disciplinas (NDC) ---
    pivot_ndc = pivot_ndc.reindex(columns=[l for l in all_langs if l in pivot_ndc.columns], fill_value=0)
    colors_ndc = [LANG_COLORS[col] for col in pivot_ndc.columns]

    pivot_ndc.plot(kind="barh", stacked=True, ax=ax2, color=colors_ndc, width=0.58, edgecolor="white", linewidth=0.5)

    max_c2 = totals_ndc.max()
    for idx, (materia, total) in enumerate(totals_ndc.items()):
        ax2.text(total + (max_c2 * 0.02), idx, f"{int(total):,}", va='center', fontsize=9.5, fontweight='bold', color='#1e293b')

    ax2.set_title("Penetración temática por disciplinas (NDC)", fontsize=13.5, fontweight='bold', pad=14, color='#0f172a')
    ax2.set_xlabel("Número de documentos (en miles)", fontsize=11.5, labelpad=8, color='#334155')
    ax2.set_ylabel("") # Sin etiqueta vertical para no colisionar
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_thousands))
    ax2.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))
    ax2.grid(axis='x', linestyle='--', alpha=0.5)
    ax2.grid(visible=False, axis='y')
    ax2.set_xlim(0, max_c2 * 1.20)
    
    # Leyenda ubicada a la derecha fuera del área de dibujo sin solapamiento
    ax2.legend(title="Idioma de origen", bbox_to_anchor=(1.03, 0.95), loc="upper left", frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9.5)
    sns.despine(ax=ax2, left=True, bottom=True)

    # Título Principal del Panel Combinado
    fig.suptitle("Distribución de lenguas de origen y penetración temática de las traducciones (1850-1920)", 
                 fontsize=16, fontweight='bold', color='#0f172a', y=0.98)

    plt.tight_layout()
    plt.subplots_adjust(top=0.88, wspace=0.45)

    output_path = os.path.join(IMG_DIR, "panel_combinado_lenguas_temas_traduccion.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[OK] Panel Combinado (Opción A) generado exitosamente en: {output_path}")

if __name__ == "__main__":
    main()
