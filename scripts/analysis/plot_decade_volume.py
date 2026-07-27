#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
plot_decade_volume.py
=====================
Genera una visualización premium del volumen total de registros por década
desde 1800 hasta 1920, combinando datos del periodo Edo (1800-1850) y el
periodo moderno (1850-1920) corregidos de reports/enriched_historical/.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar estilo premium de Seaborn
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# Directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMG_DIR = os.path.join(BASE_DIR, "images")

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# Datos obtenidos de cinii_edo_resumen.md (1800s-1840s) y cinii_resumen_estadistico.md (1850s-1920s)
decades = [
    "1800s*", "1810s", "1820s", "1830s", "1840s", "1850s",
    "1860s", "1870s", "1880s", "1890s", "1900s*", "1910s", "1920s*"
]
volumes = [
    67621,   # 1800s (Edo, incluye sesgo de 1800: 50,115)
    19394,   # 1810s (Edo)
    23295,   # 1820s (Edo)
    26665,   # 1830s (Edo)
    33748,   # 1840s (Edo)
    39772,   # 1850s (Moderno)
    47563,   # 1860s (Moderno)
    74021,   # 1870s (Moderno)
    110669,  # 1880s (Moderno)
    144640,  # 1890s (Moderno)
    222113,  # 1900s (Moderno, corregido/enriquecido)
    262047,  # 1910s (Moderno)
    33627    # 1920s (Solo el año 1920)
]

# Configurar figura y ejes con fondo ligeramente grisáceo premium
fig, ax = plt.subplots(figsize=(14, 8.5), dpi=300)
fig.patch.set_facecolor('#f8fafc')
ax.set_facecolor('#ffffff')

# Crear paleta de degradado de azul-teal moderno (crest/mako)
colors = sns.color_palette("viridis", len(decades))

# Graficar barras con bordes redondeados (simulados por estética) y sombra sutil
bars = ax.bar(decades, volumes, color=colors, edgecolor='none', width=0.6, alpha=0.85, zorder=3)

# Añadir etiquetas de valor sobre cada barra con formato de miles y diseño limpio
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:,}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 6),  # 6 puntos de desfase vertical
                textcoords="offset points",
                ha='center', va='bottom', fontsize=11, fontweight='bold', color='#1e293b')

# Personalizar rejilla y eliminar bordes innecesarios
ax.grid(axis='y', linestyle='--', alpha=0.5, color='#cbd5e1', zorder=0)
ax.grid(visible=False, axis='x')
sns.despine(left=True, bottom=True)

# Título y etiquetas con tipografía limpia y espaciado generoso
ax.set_title("Volumen Total de Registros por Década (1800-1920)\nDatos Enriquecidos de CiNii", 
             fontsize=20, fontweight='bold', pad=25, color='#0f172a')
ax.set_ylabel("Número de Registros", fontsize=14, labelpad=15, fontweight='semibold', color='#334155')
ax.set_xlabel("Década", fontsize=14, labelpad=15, fontweight='semibold', color='#334155')

# Personalización de las etiquetas de los ejes
ax.tick_params(axis='both', which='major', labelsize=12, labelcolor='#475569')

# Formatear el eje Y con separadores de miles
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

# Cuadro de notas explicativas elegante en la parte inferior
notes = (
    "Notas de Calidad de Datos:\n"
    " • 1800s*: Incluye el sesgo de catalogación del año 1800 (50,115 registros de 67,621 totales, debido a registros undated catalogados ahí).\n"
    " • 1900s*: Datos corregidos en el dataset enriquecido para eliminar el sesgo del año 1900 aplicando un factor de corrección del 5.75%.\n"
    " • 1920s*: Periodo trunco; contiene únicamente los registros del año 1920 (33,627 registros)."
)
ax.text(0.0, -0.18, notes, transform=ax.transAxes, fontsize=10.5, color='#475569',
        verticalalignment='top', bbox=dict(boxstyle='round,pad=0.6', facecolor='#f1f5f9', edgecolor='#cbd5e1', alpha=0.9))

# Ajustar márgenes para que el cuadro de notas no se corte
plt.tight_layout()
plt.subplots_adjust(bottom=0.23)

# Guardar en alta resolución
output_path = os.path.join(IMG_DIR, "volumen_total_decadas_1800_1920.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"[SUCCESS] Gráfico generado en: {output_path}")
