#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_yearly_volume.py
=====================
Genera un gráfico de línea premium que refleja el volumen total anual de registros
desde 1800 hasta 1920, aplicando la corrección del año 1900 y estimando el año 1800
para eliminar el sesgo de catalogación. Sin anotaciones ni leyendas.
"""

import os
import json
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar estilo premium
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# Directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "stats")
IMG_DIR = os.path.join(BASE_DIR, "images")

# Cargar datos de Edo (1800-1849)
edo_path = os.path.join(DATA_DIR, "cinii_edo_full_stats.json")
with open(edo_path, "r", encoding="utf-8") as f:
    edo_data = json.load(f)

# Cargar datos modernos (1850-1920)
modern_path = os.path.join(DATA_DIR, "cinii_full_stats.json")
with open(modern_path, "r", encoding="utf-8") as f:
    modern_data = json.load(f)

# Factor de corrección para 1900
FACTOR_TOTAL = 0.0575

years = []
volumes = []

# Extraer 1800 a 1849
for y in sorted(int(k) for k in edo_data.keys()):
    if 1800 <= y < 1850:
        years.append(y)
        volumes.append(int(edo_data[str(y)]["TOTAL"]))

# Extraer 1850 a 1920
for y in sorted(int(k) for k in modern_data.keys()):
    if 1850 <= y <= 1920:
        val = modern_data[str(y)]["TOTAL (ALL)"]
        if y == 1900:
            val = int(val * FACTOR_TOTAL)
        years.append(y)
        volumes.append(val)

# Construir diccionario de datos únicos
unique_data = {}
for yr, vol in zip(years, volumes):
    unique_data[yr] = vol

# --- CORRECCIÓN DEL SESGO DEL AÑO 1800 ---
# Se calcula la estimación para el año 1800 como la media de los años adyacentes de la década (1801 a 1809)
edo_years_for_avg = list(range(1801, 1810))
avg_1800 = int(sum(unique_data[y] for y in edo_years_for_avg) / len(edo_years_for_avg))
unique_data[1800] = avg_1800

# Ordenar las series para graficar
sorted_years = sorted(unique_data.keys())
sorted_volumes = [unique_data[y] for y in sorted_years]

# Configurar figura premium
fig, ax = plt.subplots(figsize=(14, 6.5), dpi=300)
fig.patch.set_facecolor('#f8fafc')
ax.set_facecolor('#ffffff')

# Graficar línea y relleno suave
line_color = '#0284c7'  # Azul moderno
fill_color = '#e0f2fe'  # Azul muy claro de fondo

ax.plot(sorted_years, sorted_volumes, color=line_color, linewidth=2.5, zorder=3)
ax.fill_between(sorted_years, sorted_volumes, color=fill_color, alpha=0.6, zorder=2)

# Personalizar rejilla y espinas
ax.grid(axis='both', linestyle='--', alpha=0.5, color='#cbd5e1', zorder=0)
sns.despine(left=True, bottom=True)

# Título de la gráfica
ax.set_title("Evolución del volumen anual del corpus recolectado (1800-1920)", 
             fontsize=18, fontweight='bold', pad=20, color='#0f172a')
ax.set_ylabel("Total de Documentos (Población)", fontsize=13, labelpad=12, fontweight='semibold', color='#334155')
ax.set_xlabel("Año", fontsize=13, labelpad=12, fontweight='semibold', color='#334155')

# Configurar límites del eje X
ax.set_xlim(1798, 1922)
ax.set_xticks(range(1800, 1921, 10))

# Formatear eje Y con separadores de miles
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax.tick_params(axis='both', which='major', labelsize=11, labelcolor='#475569')

# Ajustar diseño
plt.tight_layout()

# Guardar en alta resolución
output_path = os.path.join(IMG_DIR, "linea_volumen_total_1800_1920.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"[SUCCESS] Gráfico de línea generado y guardado en: {output_path}")
