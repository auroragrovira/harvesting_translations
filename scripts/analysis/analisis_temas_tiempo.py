#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analisis_temas_tiempo.py
========================
Analiza la evolución de la distribución de materias (NDC) a lo largo del tiempo (1850-1920).

Objetivos:
1. Crear tabla de contingencia Año x NDC (usando registros 'ALL').
2. Realizar test Chi-cuadrado de independencia.
3. Calcular residuos estandarizados ajustados para detectar años/temas 
   con frecuencias significativamente mayores o menores a lo esperado.
4. Generar informe en reports/analysis/analisis_temas_tiempo.md.
"""

import csv
import math
import os
import sys
from collections import defaultdict

# Ajustar paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_FILE = os.path.join(BASE_DIR, "reports", "csv", "muestra_jsonl_resumen.csv")
OUT_FILE = os.path.join(BASE_DIR, "reports", "analysis", "analisis_temas_tiempo.md")

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

def read_data():
    """Lee el CSV y devuelve diccionario[año][ndc] = count (solo idioma ALL)."""
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: No se encuentra {CSV_FILE}")
        sys.exit(1)

    data = defaultdict(lambda: defaultdict(int))
    years = set()
    ndcs = set()

    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["idioma"] != "ALL":
                continue
            
            year_str = row["año"]
            try:
                n = row["ndc"] # Str 0-9
                c = int(row["num_registros"])
                
                if year_str == "Undated":
                    continue # Excluir del análisis temporal para evitar sesgo
                
                y = int(year_str)
            except ValueError:
                continue

            if 1850 <= y <= 1920:
                data[y][n] += c
                years.add(y)
                ndcs.add(n)
                
    return data, sorted(list(years)), sorted(list(ndcs))

def chi_square_test(data, years, ndcs):
    """
    Calcula Chi2, p-value, V de Cramér y Residuos Ajustados.
    """
    # Totales marginales
    row_totals = {y: sum(data[y][n] for n in ndcs) for y in years}
    col_totals = {n: sum(data[y][n] for y in years) for n in ndcs}
    grand_total = sum(row_totals.values())
    
    if grand_total == 0:
        return None

    # Chi2 y Residuos
    chi2 = 0.0
    residuals = defaultdict(lambda: defaultdict(float))
    
    for y in years:
        for n in ndcs:
            obs = data[y][n]
            # Frecuencia esperada
            exp = (row_totals[y] * col_totals[n]) / grand_total
            
            if exp > 0:
                chi2 += (obs - exp)**2 / exp
                
                # Residuo Estandarizado Ajustado (Haberman)
                # R = (O - E) / sqrt(E * (1 - row_prop) * (1 - col_prop))
                row_prop = row_totals[y] / grand_total
                col_prop = col_totals[n] / grand_total
                variance = exp * (1 - row_prop) * (1 - col_prop)
                
                if variance > 0:
                    residuals[y][n] = (obs - exp) / math.sqrt(variance)
                else:
                    residuals[y][n] = 0.0
            else:
                residuals[y][n] = 0.0

    # Grados de libertad
    df = (len(years) - 1) * (len(ndcs) - 1)
    
    # Cramer's V
    min_dim = min(len(years) - 1, len(ndcs) - 1)
    cramer_v = math.sqrt(chi2 / (grand_total * min_dim)) if grand_total > 0 and min_dim > 0 else 0

    return {
        "chi2": chi2,
        "df": df,
        "n": grand_total,
        "cramer_v": cramer_v,
        "residuals": residuals,
        "row_totals": row_totals,
        "col_totals": col_totals
    }

def get_significance_icon(resid):
    if resid > 3.29: return "⬆️⬆️" # p < 0.001
    if resid > 2.58: return "⬆️"   # p < 0.01
    if resid > 1.96: return "↗️"   # p < 0.05
    if resid < -3.29: return "⬇️⬇️"
    if resid < -2.58: return "⬇️"
    if resid < -1.96: return "↘️"
    return "·"

def generate_report(stats, data, years, ndcs):
    lines = []
    lines.append("# Análisis de Evolución Temática (1850-1920)")
    lines.append("")
    lines.append("Análisis de independencia (Chi-cuadrado) y residuos estandarizados para detectar")
    lines.append("cambios significativos en la proporción de materias (NDC) a lo largo de los años.")
    lines.append("")
    
    lines.append("## 1. Resumen Estadístico Global")
    lines.append("")
    lines.append(f"- **Total de Documentos**: {stats['n']:,}")
    lines.append(f"- **Años analizados**: {len(years)}")
    lines.append(f"- **Categorías NDC**: {len(ndcs)}")
    lines.append(f"- **Estadístico Chi-cuadrado**: {stats['chi2']:.2f}")
    lines.append(f"- **Grados de libertad**: {stats['df']}")
    lines.append(f"- **V de Cramér**: {stats['cramer_v']:.4f}")
    
    interp_v = "Despreciable"
    if stats['cramer_v'] > 0.1: interp_v = "Pequeño"
    if stats['cramer_v'] > 0.3: interp_v = "Mediano"
    if stats['cramer_v'] > 0.5: interp_v = "Grande"
    
    lines.append(f"- **Interpretación del Efecto**: {interp_v}")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append(f"> Un valor de V de Cramér de **{stats['cramer_v']:.3f}** indica que la asociación entre")
    lines.append("> el año y la temática es **{interp_v.lower()}**.")
    lines.append("> Los residuos ajustados a continuación muestran *dónde* ocurren las desviaciones.")
    lines.append("")

    lines.append("## 2. Mapa de Calor de Desviaciones Significativas")
    lines.append("")
    lines.append("Los símbolos indican si la frecuencia observada es mayor (⬆️) o menor (⬇️) a la esperada")
    lines.append("bajo la hipótesis de distribución constante.")
    lines.append("")
    lines.append("- `⬆️⬆️` / `⬇️⬇️`: Desviación muy fuerte (p < 0.001)")
    lines.append("- `⬆️` / `⬇️`: Desviación fuerte (p < 0.01)")
    lines.append("- `↗️` / `↘️`: Desviación moderada (p < 0.05)")
    lines.append("- `·`: Dentro de lo esperado")
    lines.append("")

    # Tabla Header
    header = "| Año | " + " | ".join([f"{n} {NDC_NAMES[n][:3]}." for n in ndcs]) + " |"
    sep = "| :--- | " + " | ".join([":---:" for _ in ndcs]) + " |"
    lines.append(header)
    lines.append(sep)

    # Tabla Body (agrupado por quinquenios para brevedad si son muchos años, 
    # pero el usuario pidió entre años. 1850-1920 = 70 filas. Es manejable.)
    
    for y in years:
        row_str = f"| **{y}** |"
        for n in ndcs:
            resid = stats['residuals'][y][n]
            icon = get_significance_icon(resid)
            row_str += f" {icon} |"
        lines.append(row_str)

    lines.append("")
    
    lines.append("## 3. Anomalías Destacadas (Top 20)")
    lines.append("")
    lines.append("Las desviaciones positivas más fuertes (auges temáticos inusuales).")
    lines.append("")
    lines.append("| Año | NDC | Materia | Obs | Esp | Residuo |")
    lines.append("| :--- | :---: | :--- | :---: | :---: | :---: |")
    
    # Flatten residuals
    all_resids = []
    for y in years:
        for n in ndcs:
            if stats['residuals'][y][n] > 0: # Solo interesan los auges para este top
                all_resids.append({
                    'y': y, 'n': n, 
                    'val': stats['residuals'][y][n],
                    'obs': data[y][n],
                    # Recalcular esperado solo para mostrar
                    'exp': (stats['row_totals'][y] * stats['col_totals'][n])/stats['n']
                })
    
    # Sort by residual desc
    all_resids.sort(key=lambda x: x['val'], reverse=True)
    
    for r in all_resids[:20]:
        materia = NDC_NAMES[r['n']]
        lines.append(f"| {r['y']} | {r['n']} | {materia} | {r['obs']:,} | {r['exp']:.1f} | +{r['val']:.2f} |")

    lines.append("")
    
    # Escribir
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"Informe generado: {OUT_FILE}")

def main():
    print("Leyendo datos...")
    data, years, ndcs = read_data()
    
    print(f"Datos cargados: {len(years)} años, {len(ndcs)} categorías.")
    
    print("Calculando estadísticas...")
    stats = chi_square_test(data, years, ndcs)
    
    if not stats:
        print("No hay datos suficientes.")
        return

    print("Generando informe...")
    generate_report(stats, data, years, ndcs)
    print("Hecho.")

if __name__ == "__main__":
    main()
