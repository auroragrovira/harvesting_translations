# Aurora Results: Recolección y Procesamiento de Datos Académicos

Este proyecto es un conjunto de herramientas diseñadas para la descarga automatizada (harvesting) y la limpieza inteligente de metadatos académicos provenientes de repositorios japoneses (como Nichibun).

## ⚠️ Advertencia de Seguridad

Este proyecto requiere el uso de claves API (OpenAI, etc.). **Nunca subas tus claves reales al repositorio.** El archivo `api_keys` incluido es solo una plantilla.

## 📋 Funcionalidades Principales

### 1. Recolección de Datos (`Harvesting`)
- **`nichi.bat`**: Script batch para Windows que descarga masivamente registros XML del repositorio Nichibun utilizando el protocolo OAI-PMH.
  - Maneja la paginación automática mediante `resumptionToken`.
  - Muestra el progreso de descarga.

### 2. Procesamiento Inteligente (AI-Powered Cleaning)
Los datos descargados a menudo presentan problemas de formato (celdas desplazas, columnas mezcladas). Se utilizan scripts en Python potenciados por LLMs (como GPT-4) para corregirlos.

- **`process_excel_row_by_row.py`**: 
  - Lee un archivo Excel fila por fila.
  - Envía lotes de filas "rotas" a la API de GPT-4.
  - Reconstruye la estructura correcta basándose en el contenido semántico (detecta qué texto es un título, qué es un autor, etc.).
  - Guarda los resultados corregidos en CSV y Excel.

- **`restructure_excel.py`**: 
  - Versión avanzada que procesa lotes en paralelo (multithreading).
  - Acelera significativamente la limpieza de grandes conjuntos de datos.

## 🛠️ Configuración

1. **Claves API**:
   Edita el archivo `api_keys` y coloca tus propias claves:
   ```citation
   chatGPT=sk-...
   ```

2. **Dependencias**:
   - Python 3.x
   - Librerías: `pandas`, `requests`, `openpyxl`
   ```bash
   pip install pandas requests openpyxl
   ```

3. **Uso**:
   - Para descargar datos: Ejecuta `nichi.bat` en una terminal de Windows.
   - Para limpiar datos: Ejecuta `python restructure_excel.py` (asegúrate de tener el archivo Excel de entrada en la carpeta).
