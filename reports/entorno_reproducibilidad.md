# Entorno de Ejecución y Reproducibilidad Técnica

**Proyecto:** *Harvesting Translations: Infraestructura para el análisis de la circulación cultural en Japón (1800-1920)*  
**Investigación:** Tesis doctoral «El campo literario japonés de la era Meiji. El caso de Tsubouchi Shōyō como agente del cambio» (CEINDO - Universitat CEU Abat Oliba)  
**Fecha de registro y congelación:** 19 de noviembre de 2026  
**Propósito:** Garantizar la auditabilidad, verificación y replicación determinista de los scripts de recolección, procesamiento estadístico y generación de visualizaciones a 300 DPI.

---

## 1. Especificación del Sistema e Intérprete

| Parámetro | Valor verificado en el entorno actual |
| :--- | :--- |
| **Versión exacta de Python** | `Python 3.13.14` (tags/v3.13.14:fd17997, Jun 10 2026, 13:03:48) [MSC v.1944 64 bit (AMD64)] |
| **Ejecutable Python** | `C:\Users\User\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe` |
| **Sistema Operativo** | Windows 11 Pro / Enterprise (versión `10.0.26200-SP0`) |
| **Arquitectura de hardware** | x86_64 / AMD64 |

---

## 2. Bibliotecas Principales del Proyecto

Contraste entre los umbrales mínimos declarados en `requirements.txt` y las versiones concretas ejecutadas:

| Biblioteca | Versión instalada en entorno | Umbral mínimo (`requirements.txt`) | Función principal en el código |
| :--- | :---: | :---: | :--- |
| **`requests`** | **`2.32.5`** | `>=2.31.0` | Conectividad HTTP / REST con APIs de CiNii Books, NDL, Primo VE y OpenAI. |
| **`urllib3`** | **`2.6.2`** | `>=2.0.0` | Gestión de reintentos exponenciales (`urllib3.util.retry.Retry`) ante saturación. |
| **`pandas`** | **`3.0.0`** | `>=2.0.0` | Carga de datos, agregación temporal y transformaciones matriciales (NDC × Lengua). |
| **`numpy`** | **`2.4.2`** | `>=1.24.0` | Soporte numérico y manipulación de matrices para series estadísticas. |
| **`matplotlib`** | **`3.10.8`** | `>=3.7.0` | Motor de renderizado visual y exportación a 300 DPI (`plt.subplots`, `ticker`). |
| **`seaborn`** | **`0.13.2`** | `>=0.12.0` | Configuración estética (`whitegrid`), despine y paletas cromáticas normalizadas. |
| **`scipy`** | **`1.17.0`** | `>=1.10.0` | Análisis estadístico inferencial, pruebas de $\chi^2$ y residuos estandarizados. |
| **`lxml`** | **`6.0.2`** | `>=4.9.0` | Motor acelerado de parsing para esquemas XML (OAI-PMH, Dublin Core, JPCOAR). |
| **`openpyxl`** | *(Ver nota)* | `>=3.1.0` | Motor de lectura/escritura de archivos Excel (`.xlsx`) utilizado en fases de curaduría. |

> **Nota metodológica sobre `openpyxl`:** Esta biblioteca fue requerida durante las etapas iniciales de curaduría y reestructuración de volcados tabulares en formato `.xlsx` (mediante scripts en `scripts/processing/`). En el entorno actual de generación analítica y visualización, los datos definitivos se leen directamente desde estructuras `.json`, `.jsonl` y `.csv`, por lo que su ausencia en el entorno activo no afecta a la regeneración de las gráficas ni a los informes del Capítulo V.

---

## 3. Registro Completo de Dependencias Congeladas (`pip freeze`)

A continuación se transcribe la lista exhaustiva de paquetes y submódulos resueltos en el entorno de desarrollo:

```text
aiohappyeyeballs==2.6.1
aiohttp==3.13.2
aiosignal==1.4.0
attrs==25.4.0
beautifulsoup4==4.14.3
certifi==2025.11.12
charset-normalizer==3.4.4
contourpy==1.3.3
cycler==0.12.1
fonttools==4.61.1
frozenlist==1.8.0
idna==3.11
kiwisolver==1.4.9
lxml==6.0.2
matplotlib==3.10.8
multidict==6.7.0
numpy==2.4.2
packaging==26.0
pandas==3.0.0
pillow==12.1.1
propcache==0.4.1
pyparsing==3.3.2
python-dateutil==2.9.0.post0
python-docx==1.2.0
requests==2.32.5
scipy==1.17.0
seaborn==0.13.2
six==1.17.0
soupsieve==2.8.3
typing_extensions==4.15.0
tzdata==2025.3
urllib3==2.6.2
yarl==1.22.0
```

---

## 4. Herramientas de Desarrollo y Asistentes de Programación

* **Entorno de desarrollo asistido:** **Google Antigravity IDE**
  * Versión del entorno de desarrollo: **`v2.5.5`** (`Antigravity IDE.exe`).
  * Versión del runtime/núcleo del agente: **`v2.32.1`** (`Antigravity.exe`).
* **Familia de modelos de lenguaje subyacentes:** **Gemini (Google DeepMind)**.
* **Rol técnico del asistente:** Apoyo a la investigación en la escritura, depuración, refactorización de scripts en Python, automatización de pruebas estadísticas y verificación de coherencia interna.
* **Trazabilidad:** Presencia de identificadores de sesión en metadatos y scripts auxiliares en `brain/7b953517-6772-4dbd-9b82-d0b153ac5ff1/scratch/`.

---

## 5. Instrucciones para la Replicación del Entorno

Para replicar de forma exacta el entorno y verificar los resultados de la tesis:

### Opción A: Instalación estándar con umbrales mínimos
```bash
# 1. Crear entorno virtual con Python 3.8 o superior (recomendado 3.10+)
python -m venv venv

# 2. Activar el entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Linux/macOS:
source venv/bin/activate

# 3. Instalar dependencias del proyecto
pip install -r requirements.txt
```

### Opción B: Replicación idéntica del entorno congelado
```bash
# En el entorno virtual activo:
pip install requests==2.32.5 urllib3==2.6.2 pandas==3.0.0 numpy==2.4.2 matplotlib==3.10.8 seaborn==0.13.2 scipy==1.17.0 lxml==6.0.2
```

### Regeneración de visualizaciones estadísticas oficiales (300 DPI):
```bash
# Gráfica 1 (Evolución y Tasa Decadal de Traducción):
python scripts/analysis/plot_translation_comparison.py

# Panel Combinado (Distribución Lingüística y Temática en Lenguas Extranjeras):
python scripts/analysis/plot_combined_translations_panel.py
```
