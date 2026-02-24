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

### 3. Tratamiento de Sesgos de Datos (`scripts/processing/`)
El proyecto aborda anomalías de catalogación históricas:
*   **Corrección del Sesgo de 1900**: Detección y mitigación del pico artificial de registros en el año 1900 (causado por la asignación por defecto de registros sin fecha "19--").
*   **Enriquecimiento de Informes**: El script `generate_enriched_reports.py` aplica factores de corrección estadísticos para generar versiones precisas de la distribución de idiomas y materias.

### 4. Análisis Estadístico y Humanidades Digitales (`scripts/analysis/`, `reports/`)
Módulo avanzado para la generación de conocimiento historiográfico basado en datos:
*   **Análisis NDC (Materia)**: Clasificación temática basada en la Clasificación Decimal Nipona (NDC).
    *   `analisis_temas_tiempo.py`: Estudia la evolución temporal de las materias.
    *   `process_ndc_stats.py`: Genera estadísticas agregadas por NDC.
*   **Matrices de Multilingüismo**: Estudio de la correlación entre idioma y materia (`fetch_api_matrix.py`).
*   **Heurísticas de Traducción**: Cuantificación del trasvase cultural mediante el análisis de clusters terminológicos.

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
├── scripts/                    # Código fuente
│   ├── analysis/               # Generación de informes
│   ├── harvesting/             # Scrapers y conectores de APIs
│   └── processing/             # Limpieza y corrección de sesgos (p. ej. 1900)
├── reports/                    # Resultados del análisis
│   ├── historical/             # Informes históricos base
│   ├── enriched_historical/    # Informes históricos corregidos (sin sesgo 1900)
│   ├── specific/               # Informes temáticos específicos
│   ├── enriched_specific/      # Informes temáticos corregidos
│   └── csv/                    # Tablas de datos agregados en CSV
├── config/                     # Archivos de configuración
└── requirements.txt            # Dependencias del proyecto
```

---

## 🛠️ Configuración e Instalación

### Requisitos Técnicos
*   Python 3.8+
*   Dependencias listadas en `requirements.txt`.

### Instalación
1.  Clonar el repositorio.
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```

### Gestión de Claves (API Credentials)
El proyecto requiere un archivo `api_keys` en la raíz (ignorado por Git por seguridad) con el siguiente formato para usar funcionalidades avanzadas de IA o cuotas aumentadas de CiNii:
```text
chatGPT=sk-tu_clave_openai
cinii=tu_appid_nii_aqui
deepseek=tu_clave_deepseek_aqui
```

---

## ⚖️ Licencia y Propósito Académico
Este proyecto se distribuye bajo la licencia **MIT** y está diseñado exclusivamente para fines de investigación académica en el ámbito de las Humanidades Digitales y la Historia Cultural del Japón Moderno.
