# Informe de Recuperación de Fechas (1900/19--)

**Fecha:** 17/02/2026
**Estrategia:** Enriquecimiento Interno, Externo (Google Books) y LLM (ChatGPT/DeepSeek)

## Fase 1: Corrección Interna (Ejecutada)
-   **Método:** Cruzar datos con registros existentes en otros años (1850-1920).
-   **Resultado**: **1,023 registros** recuperados y movidos a su año correcto.
-   **Impacto**: 2.4% del volumen total de 1900.
Estos registros ya han sido limpiados de la carpeta 1900.

## Fase 2: Enriquecimiento Externo (Google Books API)
-   **Prueba Piloto**: 50 registros.
-   **Resultado**: **0 coincidencias** (0%).
-   **Causa**: Literatura gris, textos menores, falta de metadatos en Google Books.

## Fase 3: Enriquecimiento con LLMs (ChatGPT + DeepSeek)
-   **Prueba Piloto**: 50 registros aleatorios.
-   **Modelos**: GPT-4o vs DeepSeek-V3.
-   **Criterio de Éxito**: Consenso (ambos modelos dan el mismo año exacto).
-   **Resultado**:
    -   **Coincidencias (Consenso)**: **2 de 50 (4.0%)**.
    -   **GPT-4o**: Tendencia a responder "Unknown" ante falta de certeza.
    -   **DeepSeek**: Tendencia a "alucinar" fechas o dar estimaciones muy variadas (ej. 1655, 1980) para libros que deberían ser de la era Meiji (1868-1912).
-   **Ejemplo de Discrepancia**:
    -   *Libro*: "槐記" -> GPT: 1910, DeepSeek: 1916.
    -   *Libro*: "Contes extraordinaires" -> GPT: 1856, DeepSeek: 1864.

## Conclusión Final
Ninguna estrategia automatizada ofrece una tasa de éxito suficiente (>80-90%) para justificar el coste y el riesgo de "ensuciar" el dataset con fechas incorrectas.
-   **Google Books**: Ineficaz por tipo de material.
-   **LLMs**: Costoso y con baja tasa de consenso (4%). Riesgo de alucinación alto.

### Recomendación Definitiva
1.  **Aceptar la limitación**: Los registros de 1900 son, en su inmensa mayoría, **indatables automáticamente**.
2.  **Excluir explícitamente el año 1900** de los análisis temporales de volumen y tendencias.
3.  Utilizar estos registros solo para conteos globales (totales por idioma/tema independientemente del año).
