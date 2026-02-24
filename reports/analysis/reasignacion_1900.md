# Análisis de Viabilidad: Reasignación de Datos de 1900

**Fecha:** 17/02/2026
**Script utilizado:** `scripts/analysis/analyze_1900_redistribution.py`

## Objetivo
Determinar si los registros acumulados en el año 1900 (mayormente con fecha "19--") pueden ser reasignados a sus años reales cruzando datos con el resto del corpus (1850-1920).

## Resultados

| Métrica | Valor | Notas |
| :--- | :--- | :--- |
| **Total registros en 1900** | **42,429** | Incluye puros y "19--" |
| **Coincidencias encontradas** | **1,023** | Duplicados en otros años |
| **Tasa de éxito** | **2.41%** | Muy baja |

### Top Años de Coincidencia (Destino Potencial)
De los 1,023 registros que sí tienen una copia con fecha válida, se distribuyen así:
-   1901: 91
-   1899: 79
-   1898: 50
-   1903: 48
-   1902: 45

## Conclusión

La estrategia de reasignación automática **NO es viable** para solucionar el pico de 1900.
-   El **97.6%** de los registros de 1900 son únicos dentro de nuestra ventana de tiempo (1850-1920).
-   Esto significa que son libros *distintos* a los que ya tenemos catalogados en otros años, simplemente carecen de fecha específica catalogada.
-   Reasignarlos requeriría consultas externas (API) una por una, no deduplicación interna.
