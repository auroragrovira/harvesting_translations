# Analisis Estadistico: Poblacion (API) vs Muestra (JSONL)

Comparacion de proporciones por idioma entre los datos oficiales de la API de CiNii
(opensearch:totalResults) y los registros reales contados en los ficheros JSONL
de `univ_jp/3/`, periodo 1850-1920.

> [!NOTE]
> **H0**: Las proporciones de idiomas en la muestra JSONL no difieren
> significativamente de las proporciones en la poblacion (API).
> Se usa alpha = 0.05.
>
> **Fuentes independientes:**
> - **API**: contajes extraidos de opensearch:totalResults por consultas
>   filtradas por idioma, NDC y periodo.
> - **JSONL**: contaje real de registros en los ficheros descargados,
>   excluidos los ficheros ALL (que contienen el total sin filtro de idioma).

## Metodologia

| Prueba | Que mide | Criterio |
| :--- | :--- | :--- |
| **Chi2 homogeneidad** | Diferencia significativa de distribuciones | p > 0.05 = no sig. |
| **V de Cramer** | Tamano del efecto | <0.10 negligible |
| **Similitud coseno** | Angulo entre vectores de proporciones | 1.0 = identicas |
| **Indice disimilitud** | Proporcion a redistribuir | 0.0 = identicas |
| **Divergencia J-S** | Distancia simetrica | <0.001 = identicas |
| **Pearson r** | Correlacion lineal | 1.0 = perfecta |
| **Dmax** | Mayor diferencia en puntos porcentuales | bajo = similar |

## 1. Comparacion Global (1850-1920)

### NDC 1: Filosofia

- **N (API):** 4,785  |  **N (JSONL):** 3,329

| Idioma | API (n) | API (%) | JSONL (n) | JSONL (%) | Δ (pp) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| DE | 95 | 1.99% | 84 | 2.52% | +0.54 |
| EN | 243 | 5.08% | 175 | 5.26% | +0.18 |
| ES | 112 | 2.34% | 104 | 3.12% | +0.78 |
| FR | 2,008 | 41.96% | 1,425 | 42.81% | +0.84 |
| IT | 22 | 0.46% | 19 | 0.57% | +0.11 |
| JP | 1,973 | 41.23% | 1,252 | 37.61% | -3.62 |
| KO | 2 | 0.04% | 2 | 0.06% | +0.02 |
| RU | 4 | 0.08% | 2 | 0.06% | -0.02 |
| ZH | 326 | 6.81% | 266 | 7.99% | +1.18 |

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 18.5268 | df=8 |
| **p-value** | 0.017606 | Significativo (0.01 < p ≤ 0.05) ❌ |
| **V de Cramér** | 0.016894 | Negligible |
| **Similitud coseno** | 0.998027 | 1.0 = idénticas |
| **Índice disimilitud** | 0.036476 | 0.0 = idénticas |
| **Divergencia J-S** | 0.001170 | Muy similares |
| **Pearson r** | 0.997350 | 1.0 = perfecta |
| **Dmax** | 3.62 pp | Diferencia maxima |


### NDC 6: Industria

- **N (API):** 54,984  |  **N (JSONL):** 51,943

| Idioma | API (n) | API (%) | JSONL (n) | JSONL (%) | Δ (pp) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| DE | 570 | 1.04% | 518 | 1.00% | -0.04 |
| EN | 1,569 | 2.85% | 1,465 | 2.82% | -0.03 |
| ES | 7 | 0.01% | 5 | 0.01% | -0.00 |
| FR | 187 | 0.34% | 173 | 0.33% | -0.01 |
| IT | 5 | 0.01% | 5 | 0.01% | +0.00 |
| JP | 51,145 | 93.02% | 48,403 | 93.18% | +0.17 |
| KO | 38 | 0.07% | 34 | 0.07% | -0.00 |
| RU | 29 | 0.05% | 27 | 0.05% | -0.00 |
| ZH | 1,434 | 2.61% | 1,313 | 2.53% | -0.08 |

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 1.5938 | df=8 |
| **p-value** | 0.991038 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001365 | Negligible |
| **Similitud coseno** | 0.999999 | 1.0 = idénticas |
| **Índice disimilitud** | 0.001674 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000007 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.17 pp | Diferencia maxima |


### NDC 7: Artes

- **N (API):** 4,340  |  **N (JSONL):** 2,457

| Idioma | API (n) | API (%) | JSONL (n) | JSONL (%) | Δ (pp) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| DE | 191 | 4.40% | 160 | 6.51% | +2.11 |
| EN | 993 | 22.88% | 771 | 31.38% | +8.50 |
| ES | 13 | 0.30% | 12 | 0.49% | +0.19 |
| FR | 85 | 1.96% | 70 | 2.85% | +0.89 |
| IT | 12 | 0.28% | 10 | 0.41% | +0.13 |
| JP | 2,890 | 66.59% | 1,386 | 56.41% | -10.18 |
| KO | 2 | 0.05% | 1 | 0.04% | -0.01 |
| RU | 4 | 0.09% | 1 | 0.04% | -0.05 |
| ZH | 150 | 3.46% | 46 | 1.87% | -1.58 |

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 105.0795 | df=8 |
| **p-value** | 0.000000 | Altamente significativo (p ≤ 0.01) ❌ |
| **V de Cramér** | 0.043960 | Negligible |
| **Similitud coseno** | 0.983522 | 1.0 = idénticas |
| **Índice disimilitud** | 0.118205 | 0.0 = idénticas |
| **Divergencia J-S** | 0.008317 | Muy similares |
| **Pearson r** | 0.979717 | 1.0 = perfecta |
| **Dmax** | 10.18 pp | Diferencia maxima |


### NDC 8: Lenguaje

- **N (API):** 35,709  |  **N (JSONL):** 29,061

| Idioma | API (n) | API (%) | JSONL (n) | JSONL (%) | Δ (pp) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| DE | 3,558 | 9.96% | 3,243 | 11.16% | +1.20 |
| EN | 2,536 | 7.10% | 2,083 | 7.17% | +0.07 |
| ES | 25 | 0.07% | 19 | 0.07% | -0.00 |
| FR | 574 | 1.61% | 497 | 1.71% | +0.10 |
| IT | 39 | 0.11% | 23 | 0.08% | -0.03 |
| JP | 25,212 | 70.60% | 20,704 | 71.24% | +0.64 |
| KO | 50 | 0.14% | 40 | 0.14% | -0.00 |
| RU | 21 | 0.06% | 10 | 0.03% | -0.02 |
| ZH | 3,694 | 10.34% | 2,442 | 8.40% | -1.94 |

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 91.1759 | df=8 |
| **p-value** | 0.000000 | Altamente significativo (p ≤ 0.01) ❌ |
| **V de Cramér** | 0.013265 | Negligible |
| **Similitud coseno** | 0.999497 | 1.0 = idénticas |
| **Índice disimilitud** | 0.020032 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000717 | Prácticamente idénticas |
| **Pearson r** | 0.999373 | 1.0 = perfecta |
| **Dmax** | 1.94 pp | Diferencia maxima |


### NDC 9: Literatura

- **N (API):** 27,653  |  **N (JSONL):** 20,779

| Idioma | API (n) | API (%) | JSONL (n) | JSONL (%) | Δ (pp) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| DE | 802 | 2.90% | 662 | 3.19% | +0.29 |
| EN | 3,189 | 11.53% | 2,305 | 11.09% | -0.44 |
| ES | 108 | 0.39% | 90 | 0.43% | +0.04 |
| FR | 552 | 2.00% | 432 | 2.08% | +0.08 |
| IT | 73 | 0.26% | 60 | 0.29% | +0.02 |
| JP | 19,775 | 71.51% | 15,394 | 74.08% | +2.57 |
| KO | 63 | 0.23% | 42 | 0.20% | -0.03 |
| RU | 75 | 0.27% | 47 | 0.23% | -0.05 |
| ZH | 3,016 | 10.91% | 1,747 | 8.41% | -2.50 |

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 93.8904 | df=8 |
| **p-value** | 0.000000 | Altamente significativo (p ≤ 0.01) ❌ |
| **V de Cramér** | 0.015567 | Negligible |
| **Similitud coseno** | 0.999226 | 1.0 = idénticas |
| **Índice disimilitud** | 0.030091 | 0.0 = idénticas |
| **Divergencia J-S** | 0.001006 | Muy similares |
| **Pearson r** | 0.999161 | 1.0 = perfecta |
| **Dmax** | 2.57 pp | Diferencia maxima |


## 2. Comparacion por Decadas

### Decada 1850s

#### NDC 1: Filosofia

- N API: 57 | N JSONL: 57

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0000 | df=6 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000000 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000000 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.00 pp | Diferencia maxima |


#### NDC 6: Industria

- N API: 131 | N JSONL: 132

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0018 | df=4 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001325 | Negligible |
| **Similitud coseno** | 0.999996 | 1.0 = idénticas |
| **Índice disimilitud** | 0.002487 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000004 | Prácticamente idénticas |
| **Pearson r** | 0.999998 | 1.0 = perfecta |
| **Dmax** | 0.25 pp | Diferencia maxima |


#### NDC 7: Artes

- N API: 80 | N JSONL: 80

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0000 | df=5 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000000 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000000 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.00 pp | Diferencia maxima |


#### NDC 8: Lenguaje

- N API: 1,252 | N JSONL: 1,257

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0239 | df=5 |
| **p-value** | 0.999995 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001381 | Negligible |
| **Similitud coseno** | 0.999999 | 1.0 = idénticas |
| **Índice disimilitud** | 0.001716 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000005 | Prácticamente idénticas |
| **Pearson r** | 0.999999 | 1.0 = perfecta |
| **Dmax** | 0.15 pp | Diferencia maxima |


#### NDC 9: Literatura

- N API: 1,705 | N JSONL: 1,707

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.1992 | df=7 |
| **p-value** | 0.999975 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.002888 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000584 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000029 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.06 pp | Diferencia maxima |


### Decada 1860s

#### NDC 1: Filosofia

- N API: 95 | N JSONL: 97

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0031 | df=4 |
| **p-value** | 0.999999 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001996 | Negligible |
| **Similitud coseno** | 0.999994 | 1.0 = idénticas |
| **Índice disimilitud** | 0.002604 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000008 | Prácticamente idénticas |
| **Pearson r** | 0.999994 | 1.0 = perfecta |
| **Dmax** | 0.18 pp | Diferencia maxima |


#### NDC 6: Industria

- N API: 347 | N JSONL: 348

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0005 | df=5 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000386 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000762 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.08 pp | Diferencia maxima |


#### NDC 7: Artes

- N API: 76 | N JSONL: 76

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0000 | df=6 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000000 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000000 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.00 pp | Diferencia maxima |


#### NDC 8: Lenguaje

- N API: 1,295 | N JSONL: 1,300

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0054 | df=6 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000587 | Negligible |
| **Similitud coseno** | 0.999999 | 1.0 = idénticas |
| **Índice disimilitud** | 0.001378 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000001 | Prácticamente idénticas |
| **Pearson r** | 0.999999 | 1.0 = perfecta |
| **Dmax** | 0.14 pp | Diferencia maxima |


#### NDC 9: Literatura

- N API: 1,768 | N JSONL: 1,773

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0019 | df=8 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000261 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000606 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.06 pp | Diferencia maxima |


### Decada 1870s

#### NDC 1: Filosofia

- N API: 151 | N JSONL: 152

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0876 | df=6 |
| **p-value** | 0.999986 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.006942 | Negligible |
| **Similitud coseno** | 0.999932 | 1.0 = idénticas |
| **Índice disimilitud** | 0.006361 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000145 | Prácticamente idénticas |
| **Pearson r** | 0.999903 | 1.0 = perfecta |
| **Dmax** | 0.64 pp | Diferencia maxima |


#### NDC 6: Industria

- N API: 4,293 | N JSONL: 4,298

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0002 | df=5 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000062 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000062 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.01 pp | Diferencia maxima |


#### NDC 7: Artes

- N API: 95 | N JSONL: 95

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0000 | df=6 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000000 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000000 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.00 pp | Diferencia maxima |


#### NDC 8: Lenguaje

- N API: 2,109 | N JSONL: 2,113

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0069 | df=6 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000521 | Negligible |
| **Similitud coseno** | 0.999999 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000754 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000001 | Prácticamente idénticas |
| **Pearson r** | 0.999999 | 1.0 = perfecta |
| **Dmax** | 0.08 pp | Diferencia maxima |


#### NDC 9: Literatura

- N API: 1,864 | N JSONL: 1,872

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0030 | df=7 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000341 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000603 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.04 pp | Diferencia maxima |


### Decada 1880s

#### NDC 1: Filosofia

- N API: 328 | N JSONL: 329

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0036 | df=7 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000879 | Negligible |
| **Similitud coseno** | 0.999990 | 1.0 = idénticas |
| **Índice disimilitud** | 0.002131 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000003 | Prácticamente idénticas |
| **Pearson r** | 0.999985 | 1.0 = perfecta |
| **Dmax** | 0.21 pp | Diferencia maxima |


#### NDC 6: Industria

- N API: 8,792 | N JSONL: 8,798

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0001 | df=6 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000032 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000035 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.00 pp | Diferencia maxima |


#### NDC 7: Artes

- N API: 215 | N JSONL: 217

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0023 | df=4 |
| **p-value** | 0.999999 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001154 | Negligible |
| **Similitud coseno** | 0.999997 | 1.0 = idénticas |
| **Índice disimilitud** | 0.001715 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000003 | Prácticamente idénticas |
| **Pearson r** | 0.999995 | 1.0 = perfecta |
| **Dmax** | 0.14 pp | Diferencia maxima |


#### NDC 8: Lenguaje

- N API: 3,743 | N JSONL: 3,755

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0108 | df=7 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000454 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000841 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000001 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.08 pp | Diferencia maxima |


#### NDC 9: Literatura

- N API: 3,303 | N JSONL: 3,313

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0055 | df=8 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000322 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000804 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.08 pp | Diferencia maxima |


### Decada 1890s

#### NDC 1: Filosofia

- N API: 592 | N JSONL: 596

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0267 | df=7 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001793 | Negligible |
| **Similitud coseno** | 0.999952 | 1.0 = idénticas |
| **Índice disimilitud** | 0.004478 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000011 | Prácticamente idénticas |
| **Pearson r** | 0.999917 | 1.0 = perfecta |
| **Dmax** | 0.45 pp | Diferencia maxima |


#### NDC 6: Industria

- N API: 10,267 | N JSONL: 10,337

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0721 | df=6 |
| **p-value** | 0.999992 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000764 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000224 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000002 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.01 pp | Diferencia maxima |


#### NDC 7: Artes

- N API: 337 | N JSONL: 344

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0099 | df=6 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001560 | Negligible |
| **Similitud coseno** | 0.999996 | 1.0 = idénticas |
| **Índice disimilitud** | 0.002476 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000007 | Prácticamente idénticas |
| **Pearson r** | 0.999996 | 1.0 = perfecta |
| **Dmax** | 0.14 pp | Diferencia maxima |


#### NDC 8: Lenguaje

- N API: 3,541 | N JSONL: 3,580

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0538 | df=6 |
| **p-value** | 0.999997 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001123 | Negligible |
| **Similitud coseno** | 0.999997 | 1.0 = idénticas |
| **Índice disimilitud** | 0.001769 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000004 | Prácticamente idénticas |
| **Pearson r** | 0.999995 | 1.0 = perfecta |
| **Dmax** | 0.16 pp | Diferencia maxima |


#### NDC 9: Literatura

- N API: 2,895 | N JSONL: 2,915

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0164 | df=8 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000594 | Negligible |
| **Similitud coseno** | 0.999999 | 1.0 = idénticas |
| **Índice disimilitud** | 0.001385 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000001 | Prácticamente idénticas |
| **Pearson r** | 0.999999 | 1.0 = perfecta |
| **Dmax** | 0.14 pp | Diferencia maxima |


### Decada 1900s

#### NDC 1: Filosofia

- N API: 2,281 | N JSONL: 805

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 25.3825 | df=8 |
| **p-value** | 0.001339 | Altamente significativo (p ≤ 0.01) ❌ |
| **V de Cramér** | 0.032064 | Negligible |
| **Similitud coseno** | 0.995321 | 1.0 = idénticas |
| **Índice disimilitud** | 0.062955 | 0.0 = idénticas |
| **Divergencia J-S** | 0.005019 | Muy similares |
| **Pearson r** | 0.994483 | 1.0 = perfecta |
| **Dmax** | 6.16 pp | Diferencia maxima |


#### NDC 6: Industria

- N API: 16,670 | N JSONL: 13,517

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 2.2744 | df=8 |
| **p-value** | 0.971422 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.003069 | Negligible |
| **Similitud coseno** | 0.999997 | 1.0 = idénticas |
| **Índice disimilitud** | 0.001848 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000038 | Prácticamente idénticas |
| **Pearson r** | 0.999997 | 1.0 = perfecta |
| **Dmax** | 0.17 pp | Diferencia maxima |


#### NDC 7: Artes

- N API: 2,366 | N JSONL: 470

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 113.1419 | df=8 |
| **p-value** | 0.000000 | Altamente significativo (p ≤ 0.01) ❌ |
| **V de Cramér** | 0.070618 | Negligible |
| **Similitud coseno** | 0.954287 | 1.0 = idénticas |
| **Índice disimilitud** | 0.217106 | 0.0 = idénticas |
| **Divergencia J-S** | 0.033554 | Similares |
| **Pearson r** | 0.945721 | 1.0 = perfecta |
| **Dmax** | 17.83 pp | Diferencia maxima |


#### NDC 8: Lenguaje

- N API: 12,986 | N JSONL: 6,233

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 191.3006 | df=8 |
| **p-value** | 0.000000 | Altamente significativo (p ≤ 0.01) ❌ |
| **V de Cramér** | 0.035273 | Negligible |
| **Similitud coseno** | 0.993662 | 1.0 = idénticas |
| **Índice disimilitud** | 0.071807 | 0.0 = idénticas |
| **Divergencia J-S** | 0.005527 | Muy similares |
| **Pearson r** | 0.991826 | 1.0 = perfecta |
| **Dmax** | 5.98 pp | Diferencia maxima |


#### NDC 9: Literatura

- N API: 10,265 | N JSONL: 3,307

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 174.7040 | df=8 |
| **p-value** | 0.000000 | Altamente significativo (p ≤ 0.01) ❌ |
| **V de Cramér** | 0.040113 | Negligible |
| **Similitud coseno** | 0.992143 | 1.0 = idénticas |
| **Índice disimilitud** | 0.081822 | 0.0 = idénticas |
| **Divergencia J-S** | 0.010022 | Similares |
| **Pearson r** | 0.990276 | 1.0 = perfecta |
| **Dmax** | 8.08 pp | Diferencia maxima |


### Decada 1910s

#### NDC 1: Filosofia

- N API: 1,103 | N JSONL: 1,112

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0142 | df=6 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001033 | Negligible |
| **Similitud coseno** | 0.999992 | 1.0 = idénticas |
| **Índice disimilitud** | 0.002391 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000003 | Prácticamente idénticas |
| **Pearson r** | 0.999988 | 1.0 = perfecta |
| **Dmax** | 0.24 pp | Diferencia maxima |


#### NDC 6: Industria

- N API: 13,440 | N JSONL: 13,467

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0012 | df=8 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000073 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000081 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.01 pp | Diferencia maxima |


#### NDC 7: Artes

- N API: 1,068 | N JSONL: 1,071

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0006 | df=6 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000210 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000289 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.03 pp | Diferencia maxima |


#### NDC 8: Lenguaje

- N API: 9,829 | N JSONL: 9,866

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0759 | df=8 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000694 | Negligible |
| **Similitud coseno** | 0.999999 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000833 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000002 | Prácticamente idénticas |
| **Pearson r** | 0.999999 | 1.0 = perfecta |
| **Dmax** | 0.08 pp | Diferencia maxima |


#### NDC 9: Literatura

- N API: 5,224 | N JSONL: 5,261

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0403 | df=8 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000693 | Negligible |
| **Similitud coseno** | 0.999999 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000826 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000002 | Prácticamente idénticas |
| **Pearson r** | 0.999999 | 1.0 = perfecta |
| **Dmax** | 0.08 pp | Diferencia maxima |


### Decada 1920s

#### NDC 1: Filosofia

- N API: 178 | N JSONL: 181

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0067 | df=5 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001933 | Negligible |
| **Similitud coseno** | 0.999991 | 1.0 = idénticas |
| **Índice disimilitud** | 0.002731 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000009 | Prácticamente idénticas |
| **Pearson r** | 0.999988 | 1.0 = perfecta |
| **Dmax** | 0.27 pp | Diferencia maxima |


#### NDC 6: Industria

- N API: 1,044 | N JSONL: 1,046

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0001 | df=5 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.000097 | Negligible |
| **Similitud coseno** | 1.000000 | 1.0 = idénticas |
| **Índice disimilitud** | 0.000093 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000000 | Prácticamente idénticas |
| **Pearson r** | 1.000000 | 1.0 = perfecta |
| **Dmax** | 0.01 pp | Diferencia maxima |


#### NDC 7: Artes

- N API: 103 | N JSONL: 104

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0174 | df=5 |
| **p-value** | 0.999998 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.004099 | Negligible |
| **Similitud coseno** | 0.999910 | 1.0 = idénticas |
| **Índice disimilitud** | 0.007562 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000042 | Prácticamente idénticas |
| **Pearson r** | 0.999871 | 1.0 = perfecta |
| **Dmax** | 0.76 pp | Diferencia maxima |


#### NDC 8: Lenguaje

- N API: 954 | N JSONL: 957

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0170 | df=5 |
| **p-value** | 0.999998 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001335 | Negligible |
| **Similitud coseno** | 0.999999 | 1.0 = idénticas |
| **Índice disimilitud** | 0.001781 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000004 | Prácticamente idénticas |
| **Pearson r** | 0.999999 | 1.0 = perfecta |
| **Dmax** | 0.15 pp | Diferencia maxima |


#### NDC 9: Literatura

- N API: 629 | N JSONL: 631

| Medida | Valor | Interpretación |
| :--- | :---: | :--- |
| **χ²** | 0.0185 | df=8 |
| **p-value** | 1.000000 | No significativo (p > 0.10) ✅ |
| **V de Cramér** | 0.001353 | Negligible |
| **Similitud coseno** | 0.999997 | 1.0 = idénticas |
| **Índice disimilitud** | 0.001464 | 0.0 = idénticas |
| **Divergencia J-S** | 0.000007 | Prácticamente idénticas |
| **Pearson r** | 0.999997 | 1.0 = perfecta |
| **Dmax** | 0.15 pp | Diferencia maxima |


## 3. Tabla Resumen

| Comparacion | N API | N JSONL | Chi2 | p-value | V Cramer | Coseno | J-S | Dmax | OK |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Global NDC 1: Filosofia | 4,785 | 3,329 | 18.53 | 0.0176 | 0.0169 | 0.9980 | 0.001170 | 3.62pp | FAIL |
| Global NDC 6: Industria | 54,984 | 51,943 | 1.59 | 0.9910 | 0.0014 | 1.0000 | 0.000007 | 0.17pp | pass |
| Global NDC 7: Artes | 4,340 | 2,457 | 105.08 | 0.0000 | 0.0440 | 0.9835 | 0.008317 | 10.18pp | FAIL |
| Global NDC 8: Lenguaje | 35,709 | 29,061 | 91.18 | 0.0000 | 0.0133 | 0.9995 | 0.000717 | 1.94pp | FAIL |
| Global NDC 9: Literatura | 27,653 | 20,779 | 93.89 | 0.0000 | 0.0156 | 0.9992 | 0.001006 | 2.57pp | FAIL |
| Decada 1850s NDC 1 | 57 | 57 | 0.00 | 1.0000 | 0.0000 | 1.0000 | 0.000000 | 0.00pp | pass |
| Decada 1850s NDC 6 | 131 | 132 | 0.00 | 1.0000 | 0.0013 | 1.0000 | 0.000004 | 0.25pp | pass |
| Decada 1850s NDC 7 | 80 | 80 | 0.00 | 1.0000 | 0.0000 | 1.0000 | 0.000000 | 0.00pp | pass |
| Decada 1850s NDC 8 | 1,252 | 1,257 | 0.02 | 1.0000 | 0.0014 | 1.0000 | 0.000005 | 0.15pp | pass |
| Decada 1850s NDC 9 | 1,705 | 1,707 | 0.20 | 1.0000 | 0.0029 | 1.0000 | 0.000029 | 0.06pp | pass |
| Decada 1860s NDC 1 | 95 | 97 | 0.00 | 1.0000 | 0.0020 | 1.0000 | 0.000008 | 0.18pp | pass |
| Decada 1860s NDC 6 | 347 | 348 | 0.00 | 1.0000 | 0.0004 | 1.0000 | 0.000000 | 0.08pp | pass |
| Decada 1860s NDC 7 | 76 | 76 | 0.00 | 1.0000 | 0.0000 | 1.0000 | 0.000000 | 0.00pp | pass |
| Decada 1860s NDC 8 | 1,295 | 1,300 | 0.01 | 1.0000 | 0.0006 | 1.0000 | 0.000001 | 0.14pp | pass |
| Decada 1860s NDC 9 | 1,768 | 1,773 | 0.00 | 1.0000 | 0.0003 | 1.0000 | 0.000000 | 0.06pp | pass |
| Decada 1870s NDC 1 | 151 | 152 | 0.09 | 1.0000 | 0.0069 | 0.9999 | 0.000145 | 0.64pp | pass |
| Decada 1870s NDC 6 | 4,293 | 4,298 | 0.00 | 1.0000 | 0.0001 | 1.0000 | 0.000000 | 0.01pp | pass |
| Decada 1870s NDC 7 | 95 | 95 | 0.00 | 1.0000 | 0.0000 | 1.0000 | 0.000000 | 0.00pp | pass |
| Decada 1870s NDC 8 | 2,109 | 2,113 | 0.01 | 1.0000 | 0.0005 | 1.0000 | 0.000001 | 0.08pp | pass |
| Decada 1870s NDC 9 | 1,864 | 1,872 | 0.00 | 1.0000 | 0.0003 | 1.0000 | 0.000000 | 0.04pp | pass |
| Decada 1880s NDC 1 | 328 | 329 | 0.00 | 1.0000 | 0.0009 | 1.0000 | 0.000003 | 0.21pp | pass |
| Decada 1880s NDC 6 | 8,792 | 8,798 | 0.00 | 1.0000 | 0.0000 | 1.0000 | 0.000000 | 0.00pp | pass |
| Decada 1880s NDC 7 | 215 | 217 | 0.00 | 1.0000 | 0.0012 | 1.0000 | 0.000003 | 0.14pp | pass |
| Decada 1880s NDC 8 | 3,743 | 3,755 | 0.01 | 1.0000 | 0.0005 | 1.0000 | 0.000001 | 0.08pp | pass |
| Decada 1880s NDC 9 | 3,303 | 3,313 | 0.01 | 1.0000 | 0.0003 | 1.0000 | 0.000000 | 0.08pp | pass |
| Decada 1890s NDC 1 | 592 | 596 | 0.03 | 1.0000 | 0.0018 | 1.0000 | 0.000011 | 0.45pp | pass |
| Decada 1890s NDC 6 | 10,267 | 10,337 | 0.07 | 1.0000 | 0.0008 | 1.0000 | 0.000002 | 0.01pp | pass |
| Decada 1890s NDC 7 | 337 | 344 | 0.01 | 1.0000 | 0.0016 | 1.0000 | 0.000007 | 0.14pp | pass |
| Decada 1890s NDC 8 | 3,541 | 3,580 | 0.05 | 1.0000 | 0.0011 | 1.0000 | 0.000004 | 0.16pp | pass |
| Decada 1890s NDC 9 | 2,895 | 2,915 | 0.02 | 1.0000 | 0.0006 | 1.0000 | 0.000001 | 0.14pp | pass |
| Decada 1900s NDC 1 | 2,281 | 805 | 25.38 | 0.0013 | 0.0321 | 0.9953 | 0.005019 | 6.16pp | FAIL |
| Decada 1900s NDC 6 | 16,670 | 13,517 | 2.27 | 0.9714 | 0.0031 | 1.0000 | 0.000038 | 0.17pp | pass |
| Decada 1900s NDC 7 | 2,366 | 470 | 113.14 | 0.0000 | 0.0706 | 0.9543 | 0.033554 | 17.83pp | FAIL |
| Decada 1900s NDC 8 | 12,986 | 6,233 | 191.30 | 0.0000 | 0.0353 | 0.9937 | 0.005527 | 5.98pp | FAIL |
| Decada 1900s NDC 9 | 10,265 | 3,307 | 174.70 | 0.0000 | 0.0401 | 0.9921 | 0.010022 | 8.08pp | FAIL |
| Decada 1910s NDC 1 | 1,103 | 1,112 | 0.01 | 1.0000 | 0.0010 | 1.0000 | 0.000003 | 0.24pp | pass |
| Decada 1910s NDC 6 | 13,440 | 13,467 | 0.00 | 1.0000 | 0.0001 | 1.0000 | 0.000000 | 0.01pp | pass |
| Decada 1910s NDC 7 | 1,068 | 1,071 | 0.00 | 1.0000 | 0.0002 | 1.0000 | 0.000000 | 0.03pp | pass |
| Decada 1910s NDC 8 | 9,829 | 9,866 | 0.08 | 1.0000 | 0.0007 | 1.0000 | 0.000002 | 0.08pp | pass |
| Decada 1910s NDC 9 | 5,224 | 5,261 | 0.04 | 1.0000 | 0.0007 | 1.0000 | 0.000002 | 0.08pp | pass |
| Decada 1920s NDC 1 | 178 | 181 | 0.01 | 1.0000 | 0.0019 | 1.0000 | 0.000009 | 0.27pp | pass |
| Decada 1920s NDC 6 | 1,044 | 1,046 | 0.00 | 1.0000 | 0.0001 | 1.0000 | 0.000000 | 0.01pp | pass |
| Decada 1920s NDC 7 | 103 | 104 | 0.02 | 1.0000 | 0.0041 | 0.9999 | 0.000042 | 0.76pp | pass |
| Decada 1920s NDC 8 | 954 | 957 | 0.02 | 1.0000 | 0.0013 | 1.0000 | 0.000004 | 0.15pp | pass |
| Decada 1920s NDC 9 | 629 | 631 | 0.02 | 1.0000 | 0.0014 | 1.0000 | 0.000007 | 0.15pp | pass |

## 4. Conclusiones

- **Comparaciones realizadas:** 45
- **No significativas (p > 0.05):** 37 (82.2%)
- **Significativas (p <= 0.05):** 8 (17.8%)

### Promedios de medidas de similitud

| Medida | Promedio | Interpretacion |
| :--- | :---: | :--- |
| V de Cramer | 0.006868 | Negligible |
| Similitud coseno | 0.998120 | Muy alta |
| Indice disimilitud | 0.015419 | Muy baja |
| Divergencia J-S | 0.001459 | Muy similares |
| Pearson r | 0.997723 | Muy alta |
| Dmax promedio | 1.37 pp | |

> [!IMPORTANT]
> **Conclusion:** La muestra es mayoritariamente representativa (82.2%),
> con algunas diferencias en ciertos estratos que deben considerarse.
