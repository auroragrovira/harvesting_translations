# Investigación del Origen del Pico de Datos en 1900

**Fecha:** 17/02/2026
**Script utilizado:** `tests/analyze_1900_origins.py`

## Resumen Ejecutivo

El pico anómalo de registros en el año 1900 (~42,000 registros frente a ~2,000 en años adyacentes) **NO** representa un aumento real en la producción editorial de ese año. Es un **artefacto de catalogación**.

El **90%** de los registros asignados a 1900 tienen como fecha original `"19--"`, lo que indica que son libros del siglo XX sin fecha específica, que el sistema de CiNii o el harvester han agrupado por defecto en el inicio del siglo (1900).

## Datos Cuantitativos

| Fecha Original (Metadato) | Cantidad | Porcentaje | Interpretación |
| :--- | :--- | :--- | :--- |
| **`19--`** | **38,135** | **89.9%** | **Siglo XX (año desconocido)** |
| `1900` | 4,161 | 9.8% | Fecha real 1900 |
| `190-` | 133 | 0.3% | Década de 1900 (aprox) |

## Principales Editoriales en "1900"

Las editoriales más frecuentes en este grupo sugieren que se trata de colecciones modernas o archivos diversos mal fechados:

1.  **[出版者不明] (Editor desconocido)**: 4,328 registros.
2.  **放送大学教育振興会 (Open University of Japan)**: 928 registros (Material educativo moderno).
3.  **ティーアンドエイチ**: 750 registros.
4.  **私製 (Autoedición)**: 661 registros.

## Conclusión

Incluir el año 1900 en el análisis temporal introduce un sesgo masivo, ya que mezcla la producción real de 1900 con una bolsa de "libros sin fecha del siglo XX".

**Recomendación:** Para análisis históricos precisos, se debe **excluir el año 1900** o filtrar los registros que tengan `"display_creationdate": "19--"`.
