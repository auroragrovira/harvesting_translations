# Harvesting Translations: Infraestructura para el Análisis del Trasvase Cultural en Japón (1800-1920)

Este ecosistema de software proporciona una infraestructura robusta para la recolección masiva (**harvesting**), el procesamiento inteligente (**AI-powered curation**) y el análisis macro-estadístico (**Digital Humanities Analysis**) de metadatos académicos provenientes de los principales repositorios e instituciones nacionales de Japón.

El objetivo central es mapear la evolución de la modernización intelectual japonesa a través del estudio de la distribución idiomática y la intensidad de la traducción durante un arco crítico de 120 años (1800-1920), abarcando desde el aislamiento bibliográfico del periodo Edo hasta el cosmopolitismo de la era Taishō.

---

### 🎓 Contexto Académico
Esta investigación presenta **resultados parciales de la tesis doctoral** titulada *"El cambio en el campo literario. El caso del Japón Meiji a través de la figura de Tsubouchi Shoyo"*, desarrollada dentro del **Programa Doctoral en Humanidades para el Mundo Contemporáneo** de la Escuela Internacional de Doctorado CEU (**CEINDO**).

---

## 🚀 Funcionalidades y Fases del Proyecto

### 1. Recolección Multifuente (Harvesting)
El proyecto implementa scrapers y conectores especializados utilizando protocolos OAI-PMH, OpenSearch API y técnicas avanzadas de web scraping:

*   **CiNii Books (NII)**: Motor de búsqueda nacional para el barrido exhaustivo de libros y revistas mediante la API de NII, con soporte para gestión de checkpoints y persistencia de datos.
*   **National Diet Library (NDL)**: Procesador de registros masivos de la Biblioteca Nacional de la Dieta.
*   **Repositorios Universitarios**: Conectores específicos para la **Universidad de Tokio**, **Universidad de Waseda** y **Universidad de Osaka (Ouka)**.
*   **Nichibunken**: Sistema de cosecha de fondos del International Research Center for Japanese Studies.

### 2. Curaduría y Limpieza con IA (AI-Powered Curation)
Implementación de modelos de lenguaje (LLMs como GPT-4) para la normalización de metadatos históricos:
*   **Corrección Estructural**: Realineación automática de columnas y sanación de errores de parsing en registros antiguos.
*   **Enriquecimiento Semántico**: Detección de entidades, roles de autoría y corrección de códigos de idioma ISO-639.
*   **Muestreo Validado**: Protocolos de validación cruzada para asegurar la representatividad estadística del corpus frente al universo absoluto del catálogo nacional.

### 3. Análisis Estadístico y Humanidades Digitales
Módulo avanzado para la generación de conocimiento historiográfico basado en datos:
*   **Análisis NDC (Materia)**: Clasificación temática basada en la Clasificación Decimal Nipona (NDC) para rastrear el giro tecnológico y literario del país.
*   **Matrices de Multilingüismo**: Estudio de la correlación entre idioma y materia, identificando el papel del **Inglés como infraestructura de intermediación** cultural.
*   **Heurísticas de Traducción**: Cuantificación del trasvase cultural mediante el análisis de clusters terminológicos (`訳`, `翻訳`, `訳者`) en el catálogo nacional.

---

## 📂 Documentación y Resultados Técnicos

Este repositorio contiene un ecosistema de herramientas en Python diseñadas para el harvesting, procesamiento y análisis macro-estadístico del catálogo nacional japonés (CiNii Books).

### 1. Módulos de Cosecha y Análisis por Materia (NDC)
*   `cinii_ndc_harvester.py`: Extracción masiva de metadatos segmentados por códigos NDC.
*   `fetch_ndc_api_stats.py`: Consulta universos absolutos de registros vía API.
*   `fetch_api_matrix.py`: Correlación entre códigos NDC e idioma (`dc:language`).
*   `fetch_api_evolution.py`: Evolución de proporciones idiomáticas por décadas.
*   **Informes clave**: `cinii_resumen_ndc_api.md`, `cinii_evolucion_proporciones.md`.

### 2. Análisis del Periodo Edo (1800-1850)
*   `fetch_edo_stats.py`: Estadísticas e idiomas del arco pre-moderno.
*   `fetch_edo_translation_stats.py`: Detección heurística de traducciones pre-Meiji.
*   **Informes clave**: `cinii_edo_resumen.md`, `cinii_edo_traducciones.md`.

### 3. Análisis de Literatura y Subcategorías (NDC 9)
*   `fetch_lite_subcategories.py`: Desglose de subcategorías literarias en japonés.
*   `fetch_lite_all_langs.py`: Análisis multilingüe para identificar lenguas puente (Inglés).
*   **Informes clave**: `analisis_literatura.md`, `analisis_literatura_multilingue.md`.

### 4. Diagnóstico y Calidad de Datos
*   `fetch_translation_stats.py`: Motor de detección de traducciones (keywords `訳`, `翻訳`).
*   `check_lang_metadata.py`: Auditoría del campo de metadatos de idioma.
*   `verify_samples.py`: Validación de representatividad frente a la API oficial.
*   `analyze_duplicates.py` / `analyze_missing.py`: Control de calidad del corpus local.


---

## 🛠️ Configuración e Instalación

### Requisitos Técnicos
*   Python 3.8+
*   Dependencias: `pandas`, `requests`, `openpyxl`.
    ```bash
    pip install pandas requests openpyxl
    ```

### Gestión de Claves (API Credentials)
El proyecto requiere un archivo `api_keys` en la raíz (ignorado por Git por seguridad) con el siguiente formato:
```text
chatGPT=sk-tu_clave_openai
cinii=tu_appid_nii_aqui
deepseek=tu_clave_deepseek_aqui
```

---

## ⚖️ Licencia y Propósito Académico
Este proyecto se distribuye bajo la licencia **MIT** y está diseñado exclusivamente para fines de investigación académica en el ámbito de las Humanidades Digitales y la Historia Cultural del Japón Moderno.
