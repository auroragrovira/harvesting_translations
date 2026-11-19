#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_modern_languages.py
========================
Genera una visualización compuesta (2 paneles) de la distribución lingüística
en el periodo moderno (1850-1920) a partir de los datos enriquecidos de CiNii.
- Panel 1: Distribución global de idiomas (Volumen y Porcentaje).
- Panel 2: Evolución porcentual de la cuota de idiomas por década (1850s-1920s).
"""

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Estilo visual premium
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# Directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORT_FILE = os.path.join(BASE_DIR, "reports", "enriched_historical", "cinii_resumen_estadistico.md")
IMG_DIR = os.path.join(BASE_DIR, "images")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# Mapeo de nombres de idioma a etiquetas limpias
LANG_NAMES = {
    "Japonés (JP)": "Japonés (JP)",
    "Inglés (EN)": "Inglés (EN)",
    "Alemán (DE)": "Alemán (DE)",
    "Francés (FR)": "Francés (FR)",
    "Chino (ZH)": "Chino (ZH)",
    "Italiano (IT)": "Italiano (IT)",
    "Ruso (RU)": "Ruso (RU)",
    "Español (ES)": "Español (ES)",
    "Coreano (KO)": "Coreano (KO)"
}

# --- PARSEAR cinii_resumen_estadistico.md ---
with open(REPORT_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Parsear resumen global
global_data = {}
global_match = re.search(r"## Resumen Global: Todos los años\n- \*\*Total de documentos:\*\* ([\d,]+)\n\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
if global_match:
    table_str = global_match.group(2)
    for line in table_str.strip().split("\n"):
        if "|" in line and not line.startswith("| Idioma") and not line.startswith("| :---"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3:
                lang = parts[0]
                count = int(parts[1].replace(",", ""))
                global_data[lang] = count

# Parsear resumen por décadas
decade_sections = re.findall(r"### Década de (\d{4})\n- \*\*Total de documentos:\*\* ([\d,]+)\n\n(.*?)(?=\n###|\Z)", content, re.DOTALL)

decade_dict = {}
for dec_str, total_str, table_str in decade_sections:
    dec_key = f"{dec_str}s"
    decade_dict[dec_key] = {}
    for line in table_str.strip().split("\n"):
        if "|" in line and not line.startswith("| Idioma") and not line.startswith("| :---"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3:
                lang = parts[0]
                count = int(parts[1].replace(",", ""))
                decade_dict[dec_key][lang] = count

# Convertir a DataFrames
df_global = pd.DataFrame(list(global_data.items()), columns=["Idioma", "Cantidad"])
df_global = df_global.sort_values(by="Cantidad", ascending=True)  # Para gráfico de barra horizontal
total_docs = df_global["Cantidad"].sum()
df_global["Porcentaje"] = (df_global["Cantidad"] / total_docs) * 100

df_decades = pd.DataFrame(decade_dict).T
# Ordenar columnas por volumen global descendente
order_langs = list(df_global.sort_values(by="Cantidad", ascending=False)["Idioma"])
df_decades = df_decades[order_langs]

# Agrupar idiomas minoritarios en "Otros" para la gráfica de décadas
main_langs = ["Alemán (DE)", "Inglés (EN)", "Japonés (JP)", "Francés (FR)", "Chino (ZH)"]
df_decades_grouped = df_decades[main_langs].copy()
df_decades_grouped["Otros"] = df_decades.drop(columns=main_langs).sum(axis=1)

# Normalizar a 100% por década
df_decades_perc = df_decades_grouped.div(df_decades_grouped.sum(axis=1), axis=0) * 100

# --- CONFIGURACIÓN DE LA FIGURA ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.5), dpi=300)
fig.patch.set_facecolor('#f8fafc')
ax1.set_facecolor('#ffffff')
ax2.set_facecolor('#ffffff')

# Paleta de colores armoniosa
palette = ["#f59e0b", "#10b981", "#3b82f6", "#ef4444", "#8b5cf6", "#64748b"]
lang_color_map = dict(zip(df_decades_grouped.columns, palette))

# --- PANEL 1: Barras Horizontales (Distribución Global) ---
colors_bar = [lang_color_map.get(lang, "#94a3b8") for lang in df_global["Idioma"]]
bars = ax1.barh(df_global["Idioma"], df_global["Cantidad"], color=colors_bar, alpha=0.85, height=0.65)

# Añadir valores y porcentajes sobre las barras
for bar, perc in zip(bars, df_global["Porcentaje"]):
    width = bar.get_width()
    ax1.annotate(f"{width:,} ({perc:.1f}%)",
                 xy=(width, bar.get_y() + bar.get_height() / 2),
                 xytext=(7, 0),
                 textcoords="offset points",
                 ha='left', va='center', fontsize=9.5, fontweight='bold', color='#334155')

ax1.set_title("Volumen Total por Idioma (1850-1920)", fontsize=14, fontweight='bold', pad=15, color='#0f172a')
ax1.set_xlabel("Número de Documentos", fontsize=12, labelpad=10, color='#334155')
ax1.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax1.grid(axis='x', linestyle='--', alpha=0.5)
ax1.grid(visible=False, axis='y')
ax1.set_xlim(0, max(df_global["Cantidad"]) * 1.25)
sns.despine(ax=ax1, left=True, bottom=True)

# --- PANEL 2: Barras Apiladas (Evolución por Décadas 100%) ---
df_decades_perc.plot(kind='bar', stacked=True, ax=ax2, color=[lang_color_map[col] for col in df_decades_perc.columns], width=0.55, alpha=0.9)

ax2.set_title("Evolución de la Cuota por Década (1850s-1920s)", fontsize=14, fontweight='bold', pad=15, color='#0f172a')
ax2.set_xlabel("Década", fontsize=12, labelpad=10, color='#334155')
ax2.set_ylabel("Porcentaje (%)", fontsize=12, labelpad=10, color='#334155')
ax2.tick_params(axis='x', rotation=45, labelsize=11)
ax2.grid(axis='y', linestyle='--', alpha=0.5)
ax2.grid(visible=False, axis='x')
ax2.set_ylim(0, 100)
sns.despine(ax=ax2, left=True, bottom=True)

# Leyenda en el Panel 2
ax2.legend(title="Idioma", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=10)

# Título Principal
fig.suptitle("Distribución lingüística del corpus 1850-1920", 
             fontsize=17, fontweight='bold', color='#0f172a', y=0.98)

plt.tight_layout()
plt.subplots_adjust(top=0.88)

# Guardar
output_path = os.path.join(IMG_DIR, "distribucion_idiomas_moderno_1850_1920_12.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"[SUCCESS] Gráfico moderno generado en: {output_path}")
