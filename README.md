# Harvesting Translations: Infraestructura para el análisis de la circulación cultural en Japón (1800-1920)

Este ecosistema de software proporciona una infraestructura robusta para la recolección masiva (**harvesting**), el procesamiento inteligente (**AI-powered curation**) y el análisis macro-estadístico (**Digital Humanities Analysis**) de metadatos académicos provenientes de los principales repositorios e instituciones nacionales de Japón.

El objetivo central es mapear la evolución de la modernización intelectual japonesa a través del estudio de la distribución idiomática y la intensidad de la traducción durante un arco crítico de 120 años (1800-1920), abarcando desde el aislamiento bibliográfico del periodo Edo hasta el cosmopolitismo de la era Taishō. 

El proyecto incorporó el **análisis sistemático de la distribución lingüística, cronológica y temática** de los fondos bibliográficos a partir de los datos globales de CiNii Books. Asimismo, uno de los objetivos de *Harvesting Translations* fue identificar indicios de actividad traductora mediante búsquedas terminológicas multilingües en los metadatos bibliográficos (mediante descriptores y términos clave de traducción en títulos y menciones de responsabilidad en repositorios como NDL, UTokyo, Waseda, Osaka y Nichibunken).

Metodológicamente, la investigación distingue de forma explícita entre los registros que contienen indicios explícitos de traducción en sus metadatos y los registros bibliográficos en lenguas extranjeras conservados en Japón; estos últimos reflejan el horizonte de adquisición y consulta de obras foráneas pero no deben identificarse directamente con traducciones ni con las lenguas de origen de las obras traducidas.

---

### 🎓 Contexto Académico
Esta investigación presenta **resultados parciales de la tesis doctoral** titulada *"El campo literario japonés de la era Meiji. El caso de Tsubouchi Shōyō como agente del cambio"*, desarrollada dentro del **Programa Doctoral en Humanidades para el Mundo Contemporáneo** de la CEU Escuela Internacional de Doctorado(**CEINDO**).

---

## 🚀 Funcionalidades y Fases del Proyecto

### 1. Recolección Multifuente (Harvesting) (`scripts/harvesting/`)
El proyecto implementa scrapers y conectores especializados utilizando protocolos OAI-PMH, OpenSearch API y técnicas avanzadas de web scraping:

*   **CiNii Books (NII)** (`cinii.py`, `cinii_ndc_harvester.py`): Motor de búsqueda nacional para el barrido exhaustivo de libros y revistas mediante la API de NII, con soporte para gestión de checkpoints y persistencia de datos.
*   **Repositorios Universitarios**: Conectores específicos para la **Universidad de Tokio** (`tokyo.py`), **Universidad de Waseda** (`scrap_waseda.py`), **Universidad de Osaka** (`ouka.py`) y **Nichibunken**.
*   **National Diet Library (NDL)**: Procesador de registros masivos de la Biblioteca Nacional de la Dieta.

### 2. Curaduría y Organización de Datos (`data/`)
Los datos recolectados se almacenan de forma estructurada:
*   **`data/cinii/`**: Datos de CiNii organizados por versiones (`v1_basic`, `v2_by_lang`, `v3_by_ndc_lang`).
*   **`data/ndl/`, `data/waseda/`, etc.**: Datos específicos de cada institución.
*   **`data/stats/`**: Archivos de agregación estadística compilados en JSON (`cinii_translation_summary_1800_1920.json`, `cinii_full_stats.json`, `cinii_api_matrix_ndc_lang.json`).

### 3. Tratamiento de Sesgos de Datos (`scripts/processing/`, `scripts/analysis/`)
El proyecto aborda anomalías de catalogación históricas:
*   **Diagnóstico y Visualización del Sesgo Catalográfico (`generate_biased_visualization.py` → `images/linea_con_sesgo.png`)**: Representación de la serie temporal bruta (1850-1920) en escala logarítmica que evidencia el pico anómalo de 1900 (~42.000 registros frente a ~2.000 anuales promedio), demostrando empíricamente que el 89,9% correspondía a la etiqueta comodín `19--` (obras indatadas del siglo XX).
*   **Corrección de Picos Catalográficos (1800 / 1900)**: Detección y mitigación de la acumulación artificial de registros sin fecha exacta (`18--` y `19--`), aplicando técnicas de deduplicación interna (`apply_internal_correction.py`) e interpolación continuada basada en tendencias de años adyacentes.
*   **Enriquecimiento de Informes**: El script `generate_enriched_reports.py` aplica factores de corrección estadísticos para generar versiones precisas de la distribución de idiomas y materias en `reports/enriched_historical/`.

### 4. Análisis Estadístico y Visualización en Humanidades Digitales (`scripts/analysis/`, `images/`)
Módulo avanzado para la generación de conocimiento historiográfico y visualizaciones de alta resolución (300 DPI) para la tesis doctoral (Capítulo V, Figuras 9 a 15 y gráfica de diagnóstico):

*   **Gráfica Metodológica de Diagnóstico — Detección del Sesgo Catalográfico (1850–1920)** (`generate_biased_visualization.py` → `images/linea_con_sesgo.png`):
    *   Curva de volumen bruto en escala logarítmica que aísla visualmente el artefacto de catalogación de 1900 (42.429 registros), fundamentando la necesidad metodológica de emplear series enriquecidas y correcciones de escala.
*   **Figura 9 — Distribución Lingüística del Periodo Edo (1800–1850)** (`plot_edo_languages.py` → `images/distribucion_idiomas_edo_1800_1850_9.png`):
    *   *Panel 1 (Distribución Global):* Volumen absoluto y porcentaje relativo por idioma en el fondo bibliográfico de Edo (1800-1850).
    *   *Panel 2 (Evolución Decadal):* Variación de la cuota porcentual de idiomas por décadas (décadas de 1800 a 1840).
*   **Figura 10 — Distribución de Materias e Idiomas en el Periodo Edo (1800–1850)** (`plot_edo_topics_languages.py` → `images/distribucion_temas_idiomas_1800_1850_10.png`):
    *   *Panel A (Subcategorías de Literatura):* Desglose lingüístico dentro de las divisiones de literatura (NDC 91 a 99).
    *   *Panel B (Áreas Temáticas Generales):* Composición por idiomas en las principales disciplinas (NDC 1 Filosofía/Religión, NDC 6 Industria/Tecnología, NDC 7 Artes, NDC 8 Lenguaje, NDC 9 Literatura).
*   **Figura 11 — Evolución del Volumen Total de Publicaciones (1800–1920)** (`plot_yearly_volume.py` → `images/linea_volumen_total_1800_1920_11.png`):
    *   Serie temporal continua del volumen anual de documentos catalogados a lo largo del arco completo de 120 años, reflejando la transición histórica del periodo Edo hacia las eras Meiji y Taishō.
*   **Figura 12 — Distribución Lingüística del Periodo Moderno (1850–1920)** (`plot_modern_languages.py` → `images/distribucion_idiomas_moderno_1850_1920_12.png`):
    *   *Panel 1 (Distribución Global):* Volumen total y porcentaje de documentos por idioma catalogados en la era moderna (1850-1920).
    *   *Panel 2 (Evolución Decadal):* Evolución de las cuotas lingüísticas por décadas (décadas de 1850 a 1910), visibilizando la diversificación idiomática.
*   **Figura 13 — Distribución de Materias e Idiomas en el Periodo Moderno (1850–1920)** (`plot_modern_topics_languages.py` → `images/distribucion_temas_idiomas_1850_1920_13.png`):
    *   *Panel A (Subcategorías de Literatura):* Desglose idiomático en las subdivisiones de literatura (NDC 91 a 99) en escala logarítmica.
    *   *Panel B (Áreas Temáticas Generales):* Composición por idiomas en las cinco áreas disciplinares principales (NDC 1, 6, 7, 8, 9).
*   **Figura 14 — Evolución de Registros con Indicios de Traducción al Japonés (1800–1920)** (`plot_translation_comparison.py` → `images/evolucion_registros_indicios_traduccion_JP_14.png`):
    *   *Panel A (Evolución Anual):* Serie temporal comparativa entre la literatura en japonés sin indicios de traducción y las obras con indicios explícitos de traducción hacia el japonés.
    *   *Panel B (Tasa de Traducción por Décadas):* Porcentaje relativo de penetración de las obras traducidas sobre la producción japonesa por décadas.
*   **Figura 15 — Panel Combinado: Distribución Lingüística y Temática de los Registros en Lenguas Extranjeras (1850–1920)** (`plot_combined_translations_panel.py` → `images/panel_combinado_lenguas_temas_traduccion_15.png`):
    *   *Panel Izquierdo (Distribución por lenguas):* Volumen y porcentaje relativo de registros bibliográficos en lenguas extranjeras catalogados en Japón (Inglés EN, Alemán DE, Francés FR, Chino ZH, Ruso RU, Italiano IT, Español ES, Coreano KO).
    *   *Panel Derecho (Distribución temática por lenguas):* Composición disciplinar por áreas temáticas de la Clasificación Decimal Nipona (NDC 1, 6, 7, 8, 9), desglosada por idioma de catalogación en miles de documentos.

---

## 📂 Estructura del Proyecto

```text
harvesting_translations/
├── data/                       # Datos crudos y procesados
│   ├── cinii/                  # Datos de CiNii (v1, v2, v3)
│   ├── ndl/                    # Datos National Diet Library
│   ├── waseda/                 # Datos Waseda University
│   ├── tokyo/                  # Datos UTokyo
│   ├── osaka/                  # Datos Osaka University
│   ├── nichibunken/            # Datos Nichibunken
│   └── stats/                  # Agregados estadísticos en JSON
├── images/                     # Visualizaciones de alta resolución (300 DPI) para la tesis (Capítulo V)
│   ├── linea_con_sesgo.png                                 # Diagnóstico metodológico: serie temporal bruta con sesgo (1900)
│   ├── distribucion_idiomas_edo_1800_1850_9.png            # Figura 9: Distribución lingüística en Edo (1800-1850)
│   ├── distribucion_temas_idiomas_1800_1850_10.png         # Figura 10: Materias e idiomas en Edo (1800-1850)
│   ├── linea_volumen_total_1800_1920_11.png                # Figura 11: Volumen total anual (1800-1920)
│   ├── distribucion_idiomas_moderno_1850_1920_12.png       # Figura 12: Distribución lingüística moderna (1850-1920)
│   ├── distribucion_temas_idiomas_1850_1920_13.png         # Figura 13: Materias e idiomas modernos (1850-1920)
│   ├── evolucion_registros_indicios_traduccion_JP_14.png   # Figura 14: Traducciones sobre producción en japonés (1800-1920)
│   └── panel_combinado_lenguas_temas_traduccion_15.png     # Figura 15: Fondos en lenguas extranjeras y materias NDC (1850-1920)
├── scripts/                    # Código fuente
│   ├── analysis/               # Visualizaciones e informes estadísticos
│   │   ├── generate_biased_visualization.py        # Diagnóstico del sesgo catalográfico de 1900
│   │   ├── plot_edo_languages.py                   # Generador de Figura 9
│   │   ├── plot_edo_topics_languages.py            # Generador de Figura 10
│   │   ├── plot_yearly_volume.py                   # Generador de Figura 11
│   │   ├── plot_modern_languages.py                # Generador de Figura 12
│   │   ├── plot_modern_topics_languages.py         # Generador de Figura 13
│   │   ├── plot_translation_comparison.py          # Generador de Figura 14
│   │   └── plot_combined_translations_panel.py     # Generador de Figura 15
│   ├── harvesting/             # Scrapers y conectores de APIs
│   └── processing/             # Limpieza y corrección de sesgos (1800 / 1900)
├── reports/                    # Resultados del análisis e informes
│   ├── historical/             # Informes históricos base
│   ├── enriched_historical/    # Informes históricos corregidos
│   ├── specific/               # Informes temáticos específicos
│   ├── analysis/               # Diagnósticos metodológicos y análisis de sesgos
│   ├── csv/                    # Tablas de datos agregados en CSV
│   └── entorno_reproducibilidad.md # Especificación y congelación del entorno de ejecución
├── config/                     # Archivos de configuración
└── requirements.txt            # Dependencias del proyecto
```

---

## 🛠️ Configuración e Instalación

### Requisitos Técnicos
*   **Python 3.10+** (Recomendado `Python 3.11+` / `3.13.x`; entorno de validación y ejecución determinista: `Python 3.13.14`; véase [`reports/entorno_reproducibilidad.md`](reports/entorno_reproducibilidad.md)).
*   Dependencias listadas en `requirements.txt` (`pandas`, `matplotlib`, `seaborn`, `numpy`, `scipy`, `requests`, `urllib3`, `lxml`).

### Instalación
1.  Clonar el repositorio.
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```

### Generación de Gráficas de Resultados
Para regenerar las visualizaciones estadísticas estandarizadas del proyecto (Figuras 9 a 15 del Capítulo V y gráfica metodológica de diagnóstico):
```bash
# Diagnóstico metodológico: Detección del sesgo catalográfico de 1900 (serie bruta)
python scripts/analysis/generate_biased_visualization.py

# Figura 9: Distribución lingüística en el periodo Edo (1800-1850)
python scripts/analysis/plot_edo_languages.py

# Figura 10: Distribución de materias e idiomas en el periodo Edo (1800-1850)
python scripts/analysis/plot_edo_topics_languages.py

# Figura 11: Evolución del volumen total de publicaciones (1800-1920)
python scripts/analysis/plot_yearly_volume.py

# Figura 12: Distribución lingüística en el periodo moderno (1850-1920)
python scripts/analysis/plot_modern_languages.py

# Figura 13: Distribución de materias e idiomas en el periodo moderno (1850-1920)
python scripts/analysis/plot_modern_topics_languages.py

# Figura 14: Evolución de registros con indicios de traducción al japonés (1800-1920)
python scripts/analysis/plot_translation_comparison.py

# Figura 15: Panel combinado de fondos en lenguas extranjeras y materias NDC (1850-1920)
python scripts/analysis/plot_combined_translations_panel.py
```

### Gestión de Claves (API Credentials)
El proyecto requiere un archivo `api_keys` en la raíz (ignorado por Git por seguridad) para conectividad con la API de CiNii y modelos auxiliares:
```text
chatGPT=sk-tu_clave_openai
cinii=tu_appid_nii_aqui
deepseek=tu_clave_deepseek_aqui
```

---

## ⚖️ Licencia y Propósito Académico
Este proyecto se distribuye bajo la licencia **MIT** y está diseñado exclusivamente para fines de investigación académica en el ámbito de las Humanidades Digitales y la Historia Cultural del Japón Moderno.
