# Harvesting Translations: Infraestructura para el Análisis del Trasvase Cultural en Japón (1800-1920)

Este ecosistema de software proporciona una infraestructura robusta para la recolección masiva (**harvesting**), el procesamiento inteligente (**AI-powered curation**) y el análisis macro-estadístico (**Digital Humanities Analysis**) de metadatos académicos provenientes de los principales repositorios e instituciones nacionales de Japón.

El objetivo central es mapear la evolución de la modernización intelectual japonesa a través del estudio de la distribución idiomática y la intensidad de la traducción durante un arco crítico de 120 años (1800-1920), abarcando desde el aislamiento bibliográfico del periodo Edo hasta el cosmopolitismo de la era Taishō.

---

### 🎓 Contexto Académico
Esta investigación presenta **resultados parciales de la tesis doctoral** titulada *"El cambio en el campo literario. El caso del Japón Meiji a través de la figura de Tsubouchi Shoyo"*, desarrollada dentro del **Programa Doctoral en Humanidades para el Mundo Contemporáneo** de la Escuela Internacional de Doctorado CEU (**CEINDO**).

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

### 3. Tratamiento de Sesgos de Datos (`scripts/processing/`)
El proyecto aborda anomalías de catalogación históricas:
*   **Corrección de Picos Catalográficos (1800 / 1900)**: Detección y mitigación de la acumulación artificial de registros sin fecha exacta (`18--` y `19--`), aplicando técnicas de estimación e interpolación continuada basadas en tendencias de años adyacentes.
*   **Enriquecimiento de Informes**: El script `generate_enriched_reports.py` aplica factores de corrección estadísticos para generar versiones precisas de la distribución de idiomas y materias.

### 4. Análisis Estadístico y Visualización en Humanidades Digitales (`scripts/analysis/`, `images/`)
Módulo avanzado para la generación de conocimiento historiográfico y visualizaciones de alta resolución (300 DPI) para publicación:
*   **Gráfica 1 — Comparativa Literatura Autóctona vs. Traducida (1800-1920)** (`plot_translation_comparison.py`):
    *   *Panel A (Evolución Anual):* Serie temporal comparativa entre la literatura escrita originalmente en japonés y las obras traducidas hacia el japonés.
    *   *Panel B (Tasa de Traducción por Décadas):* Porcentaje relativo de penetración de las traducciones sobre el volumen editorial total por décadas.
*   **Panel Combinado (Gráficas 2 y 3) — Lenguas de Origen y Difusión Temática NDC** (`plot_combined_translations_panel.py`):
    *   *Panel 2 (Distribución por Lenguas de Origen):* Volumen y porcentaje de transferencias por idioma de origen (Inglés EN, Alemán DE, Chino ZH, Francés FR, Ruso RU, Español ES, Italiano IT, Coreano KO).
    *   *Panel 3 (Penetración Temática por Disciplinas NDC):* Composición idiomática por áreas temáticas de la Clasificación Decimal Nipona (NDC 1: Filosofía/Religión, NDC 6: Industria/Tecnología, NDC 7: Artes, NDC 8: Lenguaje, NDC 9: Literatura), utilizando notación formal en miles.

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
├── images/                     # Visualizaciones de alta resolución (300 DPI)
│   ├── comparativa_literatura_traduccion_1800_1920.png   # Gráfica 1 (Evolución y Tasa Decadal)
│   └── panel_combinado_lenguas_temas_traduccion.png      # Panel Combinado (Lenguas de Origen y NDC)
├── scripts/                    # Código fuente
│   ├── analysis/               # Visualizaciones e informes estadísticos
│   │   ├── plot_translation_comparison.py          # Generador de Gráfica 1
│   │   └── plot_combined_translations_panel.py     # Generador de Panel Combinado (2 y 3)
│   ├── harvesting/             # Scrapers y conectores de APIs
│   └── processing/             # Limpieza y corrección de sesgos (1800 / 1900)
├── reports/                    # Resultados del análisis e informes
│   ├── historical/             # Informes históricos base
│   ├── enriched_historical/    # Informes históricos corregidos
│   ├── specific/               # Informes temáticos específicos
│   └── csv/                    # Tablas de datos agregados en CSV
├── config/                     # Archivos de configuración
└── requirements.txt            # Dependencias del proyecto
```

---

## 🛠️ Configuración e Instalación

### Requisitos Técnicos
*   Python 3.8+
*   Dependencias listadas en `requirements.txt` (`pandas`, `matplotlib`, `seaborn`, `numpy`).

### Instalación
1.  Clonar el repositorio.
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```

### Generación de Gráficas de Resultados
Para regenerar las visualizaciones estadísticas estandarizadas del proyecto:
```bash
python scripts/analysis/plot_translation_comparison.py
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
