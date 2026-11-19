import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set aesthetic theme
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATS_DIR = os.path.join(BASE_DIR, "data", "stats")
IMG_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

# 1. Load Panel A Data (Literature Subcategories 1850-1920)
LIT_FILE = os.path.join(STATS_DIR, "literatura_multilingue_data.json")
with open(LIT_FILE, "r", encoding="utf-8") as f:
    raw_lit = json.load(f)

mod_lit = raw_lit.get("global_1850_1920", {})

NDC_SUB_MAP = {
    "91": "NDC 91: Lit. Japonesa",
    "92": "NDC 92: Lit. China/Oriental",
    "93": "NDC 93: Lit. Inglesa/Americana",
    "94": "NDC 94: Lit. Alemana",
    "95": "NDC 95: Lit. Francesa",
    "96": "NDC 96: Lit. Española",
    "97": "NDC 97: Lit. Italiana",
    "98": "NDC 98: Lit. Rusa",
    "99": "NDC 99: Otras Literaturas"
}

# Language mapping & color palette (matching 1800-1850 style)
LANG_NAMES = {
    "jpn": "Japonés (JP)",
    "chi": "Chino (ZH)",
    "eng": "Inglés (EN)",
    "ger": "Alemán (DE)",
    "fre": "Francés (FR)",
    "spa": "Español (ES)",
    "ita": "Italiano (IT)",
    "dut": "Holandés (NL)",
    "rus": "Ruso (RU)",
    "kor": "Coreano (KO)",
    "others": "Otros / Var."
}

LANG_COLORS = {
    "Japonés (JP)": "#2563eb",       # Royal Blue
    "Chino (ZH)": "#dc2626",         # Crimson Red
    "Inglés (EN)": "#059669",        # Emerald Green
    "Alemán (DE)": "#d97706",        # Amber
    "Francés (FR)": "#7c3aed",       # Violet
    "Español (ES)": "#e11d48",       # Rose
    "Italiano (IT)": "#0891b2",      # Cyan
    "Holandés (NL)": "#f59e0b",      # Orange
    "Ruso (RU)": "#475569",          # Slate
    "Coreano (KO)": "#ec4899",       # Pink
    "Otros / Var.": "#94a3b8"        # Light Slate
}

rows_a = []
for ndc_code, info in mod_lit.items():
    ndc_label = NDC_SUB_MAP.get(ndc_code, f"NDC {ndc_code}")
    langs = info.get("langs", {})
    for lang_code, count in langs.items():
        if count > 0:
            lang_label = LANG_NAMES.get(lang_code, lang_code.upper())
            rows_a.append({
                "materia": ndc_label,
                "idioma": lang_label,
                "cantidad": count
            })

df_a = pd.DataFrame(rows_a)
totals_a = df_a.groupby("materia")["cantidad"].sum().sort_values(ascending=True)
ordered_materias_a = totals_a.index.tolist()

pivot_a = df_a.pivot(index="materia", columns="idioma", values="cantidad").fillna(0).reindex(ordered_materias_a)

# 2. Load Panel B Data (General Thematic Areas 1850-1920)
MATRIX_FILE = os.path.join(STATS_DIR, "cinii_api_matrix_ndc_lang.json")
with open(MATRIX_FILE, "r", encoding="utf-8") as f:
    matrix_b = json.load(f)

NDC_MAIN_MAP = {
    "1": "NDC 1: Filosofía",
    "6": "NDC 6: Industria",
    "7": "NDC 7: Artes",
    "8": "NDC 8: Lenguaje",
    "9": "NDC 9: Literatura"
}

LANG_CODE_MAP = {
    "JP": "Japonés (JP)",
    "ZH": "Chino (ZH)",
    "EN": "Inglés (EN)",
    "DE": "Alemán (DE)",
    "FR": "Francés (FR)",
    "ES": "Español (ES)",
    "IT": "Italiano (IT)",
    "RU": "Ruso (RU)",
    "KO": "Coreano (KO)"
}

rows_b = []
for ndc_code, info in matrix_b.items():
    if ndc_code in NDC_MAIN_MAP and info.get("TOTAL", 0) > 0:
        ndc_label = NDC_MAIN_MAP[ndc_code]
        for k, v in info.items():
            if k not in ["TOTAL"] and v > 0:
                lang_label = LANG_CODE_MAP.get(k, k)
                rows_b.append({
                    "materia": ndc_label,
                    "idioma": lang_label,
                    "cantidad": v
                })

df_b = pd.DataFrame(rows_b)
totals_b = df_b.groupby("materia")["cantidad"].sum().sort_values(ascending=True)
ordered_materias_b = totals_b.index.tolist()

pivot_b = df_b.pivot(index="materia", columns="idioma", values="cantidad").fillna(0).reindex(ordered_materias_b)

# Unified Language Order
all_languages = [l for l in LANG_COLORS.keys() if l in pivot_a.columns or l in pivot_b.columns]
colors_list = [LANG_COLORS[l] for l in all_languages]

pivot_a = pivot_a.reindex(columns=all_languages, fill_value=0)
pivot_b = pivot_b.reindex(columns=all_languages, fill_value=0)

# Plotting - 2 Panel Layout with widened figure and increased wspace
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17.5, 7), gridspec_kw={'width_ratios': [1, 1]})

# Panel A Plot
pivot_a.plot(kind="barh", stacked=True, ax=ax1, color=colors_list, width=0.65, edgecolor="white", linewidth=0.5)
ax1.set_title("Subcategorías de Literatura", fontsize=13, fontweight='bold', pad=12, color='#1e293b')
ax1.set_xlabel("Número de registros", fontsize=11, fontweight='semibold', color='#334155')
ax1.set_ylabel("") # Remove Y-axis title
ax1.set_xscale("log")
ax1.set_xlim(1, 100000)
ax1.get_legend().remove()

# Add values on bar ends for Panel A
for idx, (materia, total) in enumerate(totals_a.items()):
    ax1.text(total * 1.15, idx, f"{int(total):,}", va='center', fontsize=9.5, fontweight='bold', color='#1e293b')

# Panel B Plot
pivot_b.plot(kind="barh", stacked=True, ax=ax2, color=colors_list, width=0.65, edgecolor="white", linewidth=0.5)
ax2.set_title("Áreas temáticas generales", fontsize=13, fontweight='bold', pad=12, color='#1e293b')
ax2.set_xlabel("Número de registros", fontsize=11, fontweight='semibold', color='#334155')
ax2.set_ylabel("") # Remove Y-axis title
ax2.set_xscale("log")
ax2.set_xlim(1, 100000)

# Add values on bar ends for Panel B
for idx, (materia, total) in enumerate(totals_b.items()):
    ax2.text(total * 1.15, idx, f"{int(total):,}", va='center', fontsize=9.5, fontweight='bold', color='#1e293b')

# Legend shifted down to bbox_to_anchor=(1.02, 0.78) so top bar labels have zero overlap
ax2.legend(title="Idioma", bbox_to_anchor=(1.02, 0.78), loc="upper left", frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=10)

# Main Title
fig.suptitle("Distribución del volumen de registros por áreas temáticas e idioma (1850-1920)",
             fontsize=16.5, fontweight='bold', color='#0f172a', y=0.98)

plt.tight_layout()
plt.subplots_adjust(top=0.88, wspace=0.48)

# Save image to project and artifacts
out_path_project = os.path.join(IMG_DIR, "distribucion_temas_idiomas_1850_1920_13.png")
plt.savefig(out_path_project, dpi=300, bbox_inches='tight')

ARTIFACTS_DIR = r"C:\Users\User\.gemini\antigravity\brain\ff2b3470-db70-4aae-b1cc-5587302dec00\artifacts"
out_path_artifact = os.path.join(ARTIFACTS_DIR, "distribucion_temas_idiomas_1850_1920.png")
plt.savefig(out_path_artifact, dpi=300, bbox_inches='tight')

plt.close()

print(f"[SUCCESS] Gráfico para 1850-1920 generado correctamente en:\n  - {out_path_project}\n  - {out_path_artifact}")
