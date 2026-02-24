# -*- coding: utf-8 -*-
"""
analisis_proporciones.py
========================
Análisis estadístico de no diferencia de proporciones entre:
  - Población (API): proporciones del informe ndc_api.csv, basadas en
    opensearch:totalResults (incluye registros sin idioma).
  - Muestra (JSONL): contajes reales de los ficheros JSONL en univ_jp/3/,
    agregados por década, NDC e idioma, excluyendo los ficheros "ALL"
    (que representan el total sin filtro de idioma).

Tests y medidas:
  1. Chi-cuadrado de homogeneidad (H0: proporciones iguales)
  2. V de Cramér (tamaño del efecto)
  3. Similitud coseno
  4. Índice de disimilitud (Duncan)
  5. Divergencia Jensen-Shannon
  6. Correlación de Pearson
  7. Diferencia máxima absoluta (pp)

Uso:
    python scripts/analisis_proporciones.py

Genera: reports/analisis_proporciones.md
"""

import csv
import math
import os
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_DIR = os.path.join(BASE_DIR, "reports", "csv")
OUT_FILE = os.path.join(BASE_DIR, "reports", "analysis", "analisis_proporciones.md")


# ---------------------------------------------------------------------------
# CSV I/O
# ---------------------------------------------------------------------------

def read_csv(filename):
    filepath = os.path.join(CSV_DIR, filename)
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Chi-squared p-value (pure Python, no scipy)
# ---------------------------------------------------------------------------

def _gamma_inc_cf(a, x, max_iter=200, eps=1e-12):
    f = x + 1.0 - a
    if abs(f) < 1e-30: f = 1e-30
    c = f; d = 0.0
    for n in range(1, max_iter + 1):
        an = -n * (n - a); bn = x + 2.0 * n + 1.0 - a
        d = bn + an * d
        if abs(d) < 1e-30: d = 1e-30
        c = bn + an / c
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d; delta = c * d; f *= delta
        if abs(delta - 1.0) < eps: break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) / f

def _gamma_inc_series(a, x, max_iter=200, eps=1e-12):
    if x == 0: return 0.0
    ap = a; s = 1.0 / a; ds = s
    for _ in range(1, max_iter + 1):
        ap += 1; ds *= x / ap; s += ds
        if abs(ds) < abs(s) * eps: break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))

def regularized_gamma_p(a, x):
    if x < 0 or a <= 0: return 0.0
    return _gamma_inc_series(a, x) if x < a + 1 else 1.0 - _gamma_inc_cf(a, x)

def chi2_sf(x, df):
    if df <= 0 or x < 0: return 1.0
    return 1.0 - regularized_gamma_p(df / 2.0, x / 2.0)


# ---------------------------------------------------------------------------
# Estadísticos
# ---------------------------------------------------------------------------

def chi_squared_test(obs_a, obs_b, cats):
    """Chi-cuadrado de homogeneidad con contajes observados."""
    t_a = sum(obs_a.get(c, 0) for c in cats)
    t_b = sum(obs_b.get(c, 0) for c in cats)
    if t_a == 0 or t_b == 0: return 0, 0, 1.0
    t = t_a + t_b
    chi2 = 0.0; k = 0
    for c in cats:
        oa = obs_a.get(c, 0); ob = obs_b.get(c, 0)
        col = oa + ob
        if col == 0: continue
        k += 1
        ea = t_a * col / t; eb = t_b * col / t
        if ea > 0: chi2 += (oa - ea)**2 / ea
        if eb > 0: chi2 += (ob - eb)**2 / eb
    df = max(k - 1, 0)
    return chi2, df, chi2_sf(chi2, df) if df > 0 else 1.0

def cramers_v(chi2, n, k):
    return math.sqrt(chi2 / (n * (k - 1))) if n > 0 and k > 1 else 0.0

def cosine_sim(a, b, cats):
    dot = sum(a.get(c,0)*b.get(c,0) for c in cats)
    na = math.sqrt(sum(a.get(c,0)**2 for c in cats))
    nb = math.sqrt(sum(b.get(c,0)**2 for c in cats))
    return dot/(na*nb) if na>0 and nb>0 else 0.0

def duncan_dis(pa, pb, cats):
    return 0.5*sum(abs(pa.get(c,0)-pb.get(c,0)) for c in cats)

def jsd(pa, pb, cats):
    def kl(p, q):
        return sum(p.get(c,0)*math.log(p.get(c,0)/q[c]) for c in cats if p.get(c,0)>0 and q.get(c,0)>0)
    m = {c: (pa.get(c,0)+pb.get(c,0))/2 for c in cats}
    return 0.5*kl(pa,m) + 0.5*kl(pb,m)

def pearson_r(a, b, cats):
    va = [a.get(c,0) for c in cats]; vb = [b.get(c,0) for c in cats]
    n = len(va)
    if n == 0: return 0.0
    ma = sum(va)/n; mb = sum(vb)/n
    cov = sum((x-ma)*(y-mb) for x,y in zip(va,vb))
    sa = math.sqrt(sum((x-ma)**2 for x in va))
    sb = math.sqrt(sum((y-mb)**2 for y in vb))
    return cov/(sa*sb) if sa>0 and sb>0 else 0.0

def to_props(counts, cats):
    t = sum(counts.get(c,0) for c in cats)
    return {c: counts.get(c,0)/t if t>0 else 0 for c in cats}


# ---------------------------------------------------------------------------
# Interpretaciones
# ---------------------------------------------------------------------------

def interp_p(p):
    if p > 0.10: return "No significativo (p > 0.10) ✅"
    if p > 0.05: return "Marginal (0.05 < p ≤ 0.10) ⚠️"
    if p > 0.01: return "Significativo (0.01 < p ≤ 0.05) ❌"
    return "Altamente significativo (p ≤ 0.01) ❌"

def interp_v(v):
    if v < 0.10: return "Negligible"
    if v < 0.30: return "Pequeño"
    if v < 0.50: return "Medio"
    return "Grande"

def interp_jsd(j):
    if j < 0.001: return "Prácticamente idénticas"
    if j < 0.01: return "Muy similares"
    if j < 0.05: return "Similares"
    return "Diferentes"


# ---------------------------------------------------------------------------
# Construir contajes de la muestra JSONL
# ---------------------------------------------------------------------------

def build_jsonl_counts(jsonl_rows):
    """
    Agrega los contajes JSONL (excluyendo idioma=ALL) por década y NDC.
    También agrega por global+NDC.
    Devuelve dict: (nivel, periodo, ndc) -> {idioma: count}
    """
    result = defaultdict(lambda: defaultdict(int))

    for r in jsonl_rows:
        lang = r["idioma"]
        if lang == "ALL":
            continue
        ndc = r["ndc"]
        year_str = r["año"]
        count = int(r["num_registros"])

        if year_str == "Undated":
            # Si queremos rastrear Undated por NDC
            result[("global", "Undated", ndc)][lang] += count
            continue

        try:
            year = int(year_str)
        except ValueError:
            continue

        # Global
        result[("global", "1850-1920", ndc)][lang] += count

        # Por década
        decade_start = (year // 10) * 10
        decade = f"{decade_start}s"
        result[("decada", decade, ndc)][lang] += count

        # Por año
        result[("anual", str(year), ndc)][lang] += count

    return result


def build_api_counts(api_rows):
    """
    Extrae contajes de la API por nivel, periodo y NDC.
    Devuelve dict: (nivel, periodo, ndc) -> {idioma: count}
    """
    result = defaultdict(lambda: defaultdict(int))
    for r in api_rows:
        key = (r["nivel"], r["periodo"], r["ndc"])
        result[key][r["idioma"]] += int(r["cantidad"])
    return result


# ---------------------------------------------------------------------------
# Análisis multicomparación
# ---------------------------------------------------------------------------

def run_comparison(api_counts, jsonl_counts, cats):
    """Ejecuta todas las medidas estadísticas."""
    n_api = sum(api_counts.get(c,0) for c in cats)
    n_jsonl = sum(jsonl_counts.get(c,0) for c in cats)

    chi2, df, p = chi_squared_test(api_counts, jsonl_counts, cats)
    v = cramers_v(chi2, n_api + n_jsonl, len(cats))

    pa = to_props(api_counts, cats)
    pj = to_props(jsonl_counts, cats)

    return {
        "n_api": n_api, "n_jsonl": n_jsonl,
        "cats": cats,
        "api_counts": api_counts, "jsonl_counts": jsonl_counts,
        "api_props": pa, "jsonl_props": pj,
        "chi2": chi2, "df": df, "p": p,
        "v": v,
        "cos": cosine_sim(pa, pj, cats),
        "duncan": duncan_dis(pa, pj, cats),
        "jsd": jsd(pa, pj, cats),
        "pearson": pearson_r(pa, pj, cats),
        "max_diff": max(abs(pa.get(c,0)-pj.get(c,0))*100 for c in cats) if cats else 0,
    }


def fmt_detail(r, label):
    """Formatea tabla de detalle con proporciones."""
    lines = [f"### {label}", "",
             f"- **N (API):** {r['n_api']:,}  |  **N (JSONL):** {r['n_jsonl']:,}", ""]
    lines.append("| Idioma | API (n) | API (%) | JSONL (n) | JSONL (%) | Δ (pp) |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    for c in r["cats"]:
        na = r["api_counts"].get(c,0); nj = r["jsonl_counts"].get(c,0)
        pa = r["api_props"].get(c,0)*100; pj = r["jsonl_props"].get(c,0)*100
        d = pj - pa
        lines.append(f"| {c} | {na:,} | {pa:.2f}% | {nj:,} | {pj:.2f}% | {d:+.2f} |")
    lines.extend(["", fmt_stats(r)])
    return "\n".join(lines)


def fmt_compact(r, label):
    """Formato compacto (solo estadísticos)."""
    lines = [f"#### {label}", "",
             f"- N API: {r['n_api']:,} | N JSONL: {r['n_jsonl']:,}", "",
             fmt_stats(r)]
    return "\n".join(lines)


def fmt_stats(r):
    lines = ["| Medida | Valor | Interpretación |",
             "| :--- | :---: | :--- |",
             f"| **χ²** | {r['chi2']:.4f} | df={r['df']} |",
             f"| **p-value** | {r['p']:.6f} | {interp_p(r['p'])} |",
             f"| **V de Cramér** | {r['v']:.6f} | {interp_v(r['v'])} |",
             f"| **Similitud coseno** | {r['cos']:.6f} | 1.0 = idénticas |",
             f"| **Índice disimilitud** | {r['duncan']:.6f} | 0.0 = idénticas |",
             f"| **Divergencia J-S** | {r['jsd']:.6f} | {interp_jsd(r['jsd'])} |",
             f"| **Pearson r** | {r['pearson']:.6f} | 1.0 = perfecta |",
             f"| **Dmax** | {r['max_diff']:.2f} pp | Diferencia maxima |",
             ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

NDC_NAMES = {
    "1": "Filosofia", "6": "Industria", "7": "Artes",
    "8": "Lenguaje", "9": "Literatura",
}


def main():
    print("=== Analisis de Proporciones: API vs Muestra JSONL ===\n")

    api_rows = read_csv("ndc_api.csv")
    jsonl_rows = read_csv("muestra_jsonl_resumen.csv")

    api_data = build_api_counts(api_rows)
    jsonl_data = build_jsonl_counts(jsonl_rows)

    report = []
    report.append("# Analisis Estadistico: Poblacion (API) vs Muestra (JSONL)")
    report.append("")
    report.append("Comparacion de proporciones por idioma entre los datos oficiales de la API de CiNii")
    report.append("(opensearch:totalResults) y los registros reales contados en los ficheros JSONL")
    report.append("de `univ_jp/3/`, periodo 1850-1920.")
    report.append("")
    report.append("> [!NOTE]")
    report.append("> **H0**: Las proporciones de idiomas en la muestra JSONL no difieren")
    report.append("> significativamente de las proporciones en la poblacion (API).")
    report.append("> Se usa alpha = 0.05.")
    report.append(">")
    report.append("> **Fuentes independientes:**")
    report.append("> - **API**: contajes extraidos de opensearch:totalResults por consultas")
    report.append(">   filtradas por idioma, NDC y periodo.")
    report.append("> - **JSONL**: contaje real de registros en los ficheros descargados,")
    report.append(">   excluidos los ficheros ALL (que contienen el total sin filtro de idioma).")
    report.append("")

    report.append("## Metodologia")
    report.append("")
    report.append("| Prueba | Que mide | Criterio |")
    report.append("| :--- | :--- | :--- |")
    report.append("| **Chi2 homogeneidad** | Diferencia significativa de distribuciones | p > 0.05 = no sig. |")
    report.append("| **V de Cramer** | Tamano del efecto | <0.10 negligible |")
    report.append("| **Similitud coseno** | Angulo entre vectores de proporciones | 1.0 = identicas |")
    report.append("| **Indice disimilitud** | Proporcion a redistribuir | 0.0 = identicas |")
    report.append("| **Divergencia J-S** | Distancia simetrica | <0.001 = identicas |")
    report.append("| **Pearson r** | Correlacion lineal | 1.0 = perfecta |")
    report.append("| **Dmax** | Mayor diferencia en puntos porcentuales | bajo = similar |")
    report.append("")

    all_results = []

    # ================================================================
    # 1. Global
    # ================================================================
    report.append("## 1. Comparacion Global (1850-1920)")
    report.append("")

    ndcs = sorted(NDC_NAMES.keys())
    for ndc in ndcs:
        api_key = ("global", "1850-1920", ndc)
        jsonl_key = ("global", "1850-1920", ndc)

        if api_key not in api_data or jsonl_key not in jsonl_data:
            continue

        cats = sorted(set(list(api_data[api_key].keys()) + list(jsonl_data[jsonl_key].keys())))
        if not cats:
            continue

        r = run_comparison(api_data[api_key], jsonl_data[jsonl_key], cats)
        r["label"] = f"Global NDC {ndc}: {NDC_NAMES[ndc]}"
        all_results.append(r)
        report.append(fmt_detail(r, f"NDC {ndc}: {NDC_NAMES[ndc]}"))
        report.append("")

    # ================================================================
    # 2. Por decadas
    # ================================================================
    report.append("## 2. Comparacion por Decadas")
    report.append("")

    decades = sorted(set(k[1] for k in api_data if k[0] == "decada"))

    for decade in decades:
        report.append(f"### Decada {decade}")
        report.append("")

        for ndc in ndcs:
            api_key = ("decada", decade, ndc)
            jsonl_key = ("decada", decade, ndc)

            if api_key not in api_data or jsonl_key not in jsonl_data:
                continue

            cats = sorted(set(list(api_data[api_key].keys()) + list(jsonl_data[jsonl_key].keys())))
            if not cats: continue

            r = run_comparison(api_data[api_key], jsonl_data[jsonl_key], cats)
            r["label"] = f"Decada {decade} NDC {ndc}"
            all_results.append(r)
            report.append(fmt_compact(r, f"NDC {ndc}: {NDC_NAMES[ndc]}"))
            report.append("")

    # ================================================================
    # 3. Resumen
    # ================================================================
    report.append("## 3. Tabla Resumen")
    report.append("")
    report.append("| Comparacion | N API | N JSONL | Chi2 | p-value | V Cramer | Coseno | J-S | Dmax | OK |")
    report.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    n_sig = 0
    for r in all_results:
        ok = "pass" if r["p"] > 0.05 else "FAIL"
        if r["p"] <= 0.05: n_sig += 1
        report.append(
            f"| {r['label']} | {r['n_api']:,} | {r['n_jsonl']:,} | "
            f"{r['chi2']:.2f} | {r['p']:.4f} | {r['v']:.4f} | "
            f"{r['cos']:.4f} | {r['jsd']:.6f} | {r['max_diff']:.2f}pp | {ok} |"
        )
    report.append("")

    # ================================================================
    # 4. Conclusiones
    # ================================================================
    n_total = len(all_results)
    pct_ok = (n_total - n_sig) / n_total * 100 if n_total else 0

    report.append("## 4. Conclusiones")
    report.append("")
    report.append(f"- **Comparaciones realizadas:** {n_total}")
    report.append(f"- **No significativas (p > 0.05):** {n_total - n_sig} ({pct_ok:.1f}%)")
    report.append(f"- **Significativas (p <= 0.05):** {n_sig} ({100-pct_ok:.1f}%)")
    report.append("")

    if all_results:
        av = lambda k: sum(r[k] for r in all_results)/len(all_results)
        report.append("### Promedios de medidas de similitud")
        report.append("")
        report.append("| Medida | Promedio | Interpretacion |")
        report.append("| :--- | :---: | :--- |")
        report.append(f"| V de Cramer | {av('v'):.6f} | {interp_v(av('v'))} |")
        report.append(f"| Similitud coseno | {av('cos'):.6f} | {'Muy alta' if av('cos')>0.99 else 'Alta'} |")
        report.append(f"| Indice disimilitud | {av('duncan'):.6f} | {'Muy baja' if av('duncan')<0.05 else 'Baja'} |")
        report.append(f"| Divergencia J-S | {av('jsd'):.6f} | {interp_jsd(av('jsd'))} |")
        report.append(f"| Pearson r | {av('pearson'):.6f} | {'Muy alta' if av('pearson')>0.99 else 'Alta'} |")
        report.append(f"| Dmax promedio | {av('max_diff'):.2f} pp | |")
        report.append("")

    if pct_ok >= 90:
        report.append("> [!TIP]")
        report.append(f"> **Conclusion:** La muestra descargada es estadisticamente representativa.")
        report.append(f"> El {pct_ok:.1f}% de las comparaciones no muestran diferencias significativas.")
        report.append(f"> Las medidas complementarias confirman alta similitud entre distribuciones.")
        report.append(f"> **El analisis cualitativo basado en esta muestra es coherente y generalizable.**")
    elif pct_ok >= 70:
        report.append("> [!IMPORTANT]")
        report.append(f"> **Conclusion:** La muestra es mayoritariamente representativa ({pct_ok:.1f}%),")
        report.append(f"> con algunas diferencias en ciertos estratos que deben considerarse.")
    else:
        report.append("> [!WARNING]")
        report.append(f"> **Conclusion:** Se detectan diferencias significativas en un {100-pct_ok:.1f}%")
        report.append(f"> de las comparaciones. Revisar posibles causas de discrepancia.")
    report.append("")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"  -> Informe: {OUT_FILE}")
    print(f"  -> Comparaciones: {n_total}")
    print(f"  -> No significativas: {n_total - n_sig} ({pct_ok:.1f}%)")
    print(f"  -> Significativas: {n_sig}")
    print("\n=== Analisis completado ===")


if __name__ == "__main__":
    main()
