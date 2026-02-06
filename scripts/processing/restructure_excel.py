import pandas as pd
import json
import os
import requests
import time
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

def read_api_key():
    """Lee la clave API de ChatGPT desde el archivo api_keys"""
    try:
        with open('api_keys', 'r') as f:
            for line in f:
                if line.startswith('chatGPT='):
                    return line.strip().split('=')[1]
    except FileNotFoundError:
        print("Error: No se encontró el archivo api_keys")
        return None

def load_excel_data(excel_file):
    """Carga todo el archivo Excel"""
    try:
        df = pd.read_excel(excel_file)
        return df
    except Exception as e:
        print(f"Error leyendo el archivo Excel: {e}")
        return None

def extract_batch_rows(df, start_idx, batch_size=5):
    """Extrae un lote de filas del DataFrame"""
    end_idx = min(start_idx + batch_size, len(df))
    return df.iloc[start_idx:end_idx]

def send_to_gpt4(dataframe, api_key, batch_number, batch_id):
    """Envía un lote de filas a GPT-4 para corrección"""
    
    # Convertir el DataFrame a formato legible
    data_text = dataframe.to_string(index=True)
    
    prompt = f"""
Corrige estas {len(dataframe)} filas de Excel con columnas desalineadas (lote {batch_number}, ID: {batch_id}):

{data_text}

PROBLEMA: Celdas vacías desplazan columnas hacia la izquierda.

SOLUCIÓN: Reorganiza los valores en las posiciones correctas, dejando vacías las celdas que deben estar vacías.

IMPORTANTE: Devuelve SOLO este formato exacto:

FILA_1: Alma, book, fre, título, tema, formato, ...
FILA_2: Alma, book, fre, título, tema, formato, ...
FILA_3: Alma, book, fre, título, tema, formato, ...

Cada fila debe tener exactamente {len(dataframe.columns)} valores separados por comas.
Usa espacios vacíos para celdas vacías.
NO uses comillas dobles.
NO incluyas números de fila al inicio.
"""

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Eres un experto en análisis de datos y estructura de archivos Excel. Ayudas a corregir problemas de formato y estructura."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'batch_id': batch_id,
                'batch_number': batch_number,
                'response': result['choices'][0]['message']['content'],
                'status': 'success'
            }
        else:
            return {
                'batch_id': batch_id,
                'batch_number': batch_number,
                'response': None,
                'status': 'error',
                'error': f"API error {response.status_code}: {response.text}"
            }
        
    except Exception as e:
        return {
            'batch_id': batch_id,
            'batch_number': batch_number,
            'response': None,
            'status': 'error',
            'error': str(e)
        }

def parse_gpt_response(response_text):
    """Parsea la respuesta de GPT-4 y extrae los datos corregidos"""
    try:
        # Limpiar la respuesta
        response_text = response_text.strip()
        
        # Buscar formato FILA_X: valor1, valor2, , valor4, ...
        import re
        pattern = r'FILA_\d+:\s*(.*?)(?=FILA_\d+:|$)'
        matches = re.findall(pattern, response_text, re.DOTALL)
        
        if not matches:
            print("No se encontró formato FILA_X en la respuesta")
            print(f"Respuesta recibida: {response_text[:200]}...")
            return None
        
        corrected_rows = []
        for i, match in enumerate(matches):
            try:
                # Limpiar el match
                match = match.strip()
                
                # Dividir por comas
                values = [v.strip() for v in match.split(',')]
                
                # Limpiar valores vacíos y comillas extra
                cleaned_values = []
                for value in values:
                    if value == '' or value == ' ':
                        cleaned_values.append('')
                    else:
                        # Remover comillas dobles extra
                        cleaned_value = value.strip()
                        if cleaned_value.startswith('"""') and cleaned_value.endswith('"""'):
                            cleaned_value = cleaned_value[3:-3]
                        elif cleaned_value.startswith('"') and cleaned_value.endswith('"'):
                            cleaned_value = cleaned_value[1:-1]
                        cleaned_values.append(cleaned_value)
                
                if len(cleaned_values) > 0:
                    corrected_rows.append({"row_data": cleaned_values})
                    print(f"  ✅ Extraída fila {i+1} con {len(cleaned_values)} valores")
                
            except Exception as e:
                print(f"  ⚠️  Error procesando fila {i+1}: {e}")
                continue
        
        if corrected_rows:
            print(f"✅ Parsing exitoso: {len(corrected_rows)} filas")
            return {"corrected_rows": corrected_rows, "explanation": "Formato FILA_X simple"}
        else:
            print("❌ No se pudieron extraer filas")
            return None
            
    except Exception as e:
        print(f"Error parseando la respuesta de GPT-4: {e}")
        return None

def extract_data_manually(response_text):
    """Extrae datos manualmente cuando el JSON está mal formado"""
    try:
        print("Intentando extracción manual...")
        
        # Buscar patrones de filas corregidas
        corrected_rows = []
        
        # Buscar arrays que empiecen con ["valor1", "valor2", ...
        import re
        
        # Patrón más flexible para encontrar arrays
        pattern = r'"row_\d+":\s*\[([^\]]*(?:\[[^\]]*\][^\]]*)*)\]'
        matches = re.findall(pattern, response_text, re.DOTALL)
        
        if not matches:
            # Patrón alternativo más simple
            pattern = r'"row_\d+":\s*\[(.*?)\]'
            matches = re.findall(pattern, response_text, re.DOTALL)
        
        for i, match in enumerate(matches):
            try:
                # Limpiar el match
                match = match.strip()
                
                # Dividir por comas pero respetando comillas
                values = []
                current_value = ""
                in_quotes = False
                quote_char = None
                
                for char in match:
                    if char in ['"', "'"] and (not current_value or current_value[-1] != '\\'):
                        if not in_quotes:
                            in_quotes = True
                            quote_char = char
                        elif char == quote_char:
                            in_quotes = False
                            quote_char = None
                    elif char == ',' and not in_quotes:
                        # Procesar valor
                        value = current_value.strip()
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        elif value == '""' or value == "''":
                            value = ""
                        
                        values.append(value)
                        current_value = ""
                        continue
                    
                    current_value += char
                
                # Procesar último valor
                if current_value.strip():
                    value = current_value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    elif value == '""' or value == "''":
                        value = ""
                    values.append(value)
                
                if len(values) > 0:
                    corrected_rows.append({"row_data": values})
                    print(f"  ✅ Extraída fila {i+1} con {len(values)} valores")
                
            except Exception as e:
                print(f"  ⚠️  Error procesando fila {i+1}: {e}")
                continue
        
        if corrected_rows:
            print(f"✅ Extracción manual exitosa: {len(corrected_rows)} filas")
            return {"corrected_rows": corrected_rows, "explanation": "Extracción manual"}
        else:
            print("❌ No se pudieron extraer filas manualmente")
            return None
            
    except Exception as e:
        print(f"Error en extracción manual: {e}")
        return None

def append_to_result_csv(corrected_data, original_df, csv_filename):
    """Añade datos corregidos al CSV de resultado"""
    
    if not corrected_data or 'corrected_rows' not in corrected_data:
        print("No hay datos corregidos para procesar")
        return None
    
    # Crear DataFrame con los datos corregidos
    corrected_rows = []
    for row_data in corrected_data['corrected_rows']:
        if 'row_data' in row_data:
            # Estructura de extracción manual
            corrected_rows.append(row_data['row_data'])
        else:
            # Estructura original
            for row_name, row_values in row_data.items():
                corrected_rows.append(row_values)
    
    if corrected_rows:
        # Asegurar que todas las filas tengan la misma longitud
        max_cols = len(original_df.columns)
        processed_rows = []
        
        for row_data in corrected_rows:
            if isinstance(row_data, dict) and 'row_data' in row_data:
                values = row_data['row_data']
            elif isinstance(row_data, dict):
                # Estructura original
                for row_name, row_values in row_data.items():
                    values = row_values
                    break
            elif isinstance(row_data, list):
                # Si ya es una lista directamente
                values = row_data
            else:
                print(f"⚠️  Formato de datos inesperado: {type(row_data)}")
                continue
            
            # Truncar o rellenar para que tenga exactamente max_cols elementos
            if len(values) > max_cols:
                values = values[:max_cols]  # Truncar si hay más
            elif len(values) < max_cols:
                values.extend([''] * (max_cols - len(values)))  # Rellenar si hay menos
            
            processed_rows.append(values)
        
        # Usar las mismas columnas que el DataFrame original
        corrected_df = pd.DataFrame(processed_rows, columns=original_df.columns)
        
        # Verificar si el archivo CSV ya existe
        if os.path.exists(csv_filename):
            # Leer el CSV existente y añadir las nuevas filas
            existing_df = pd.read_csv(csv_filename)
            combined_df = pd.concat([existing_df, corrected_df], ignore_index=True)
            combined_df.to_csv(csv_filename, index=False, encoding='utf-8')
        else:
            # Crear nuevo CSV
            corrected_df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"✅ {len(corrected_rows)} filas añadidas a {csv_filename}")
        return corrected_df
    else:
        print("No se pudieron procesar las filas corregidas")
        return None

def save_final_xlsx(csv_filename, xlsx_filename):
    """Convierte el CSV final a XLSX"""
    try:
        df = pd.read_csv(csv_filename)
        df.to_excel(xlsx_filename, index=False)
        print(f"✅ Archivo XLSX final creado: {xlsx_filename}")
    except Exception as e:
        print(f"❌ Error creando XLSX: {e}")

def process_batch_parallel(batch_data, api_key):
    """Procesa un lote en paralelo"""
    batch_df, batch_number, batch_id = batch_data
    
    print(f"🚀 Iniciando lote {batch_number} (ID: {batch_id})")
    
    # Enviar a GPT-4
    result = send_to_gpt4(batch_df, api_key, batch_number, batch_id)
    
    if result['status'] == 'success':
        # Parsear respuesta
        corrected_data = parse_gpt_response(result['response'])
        
        if corrected_data:
            return {
                'batch_id': batch_id,
                'batch_number': batch_number,
                'status': 'success',
                'corrected_data': corrected_data,
                'batch_df': batch_df
            }
        else:
            return {
                'batch_id': batch_id,
                'batch_number': batch_number,
                'status': 'parse_error',
                'batch_df': batch_df,
                'error': 'Error parseando respuesta'
            }
    else:
        return {
            'batch_id': batch_id,
            'batch_number': batch_number,
            'status': 'api_error',
            'batch_df': batch_df,
            'error': result.get('error', 'Error desconocido')
        }

def main():
    """Función principal - Procesa todo el Excel en lotes paralelos de 5"""
    excel_file = "results - copia.xlsx"
    csv_result = "corrected_complete_dataset.csv"
    xlsx_result = "corrected_complete_dataset.xlsx"
    
    print("=== Script de Reestructuración de Excel Completo (PARALELO) ===")
    print(f"Procesando archivo: {excel_file}")
    
    # Leer clave API
    api_key = read_api_key()
    if not api_key:
        return
    
    # Cargar todo el Excel
    print("\n1. Cargando archivo Excel completo...")
    df = load_excel_data(excel_file)
    
    if df is None:
        print("Error: No se pudo cargar el archivo Excel")
        return
    
    print(f"✅ Archivo cargado: {len(df)} filas, {len(df.columns)} columnas")
    
    # Preparar lotes
    batch_size = 3
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    print(f"\n2. Preparando {total_batches} lotes de {batch_size} filas para procesamiento paralelo...")
    
    # Crear lista de lotes con identificadores únicos
    batch_list = []
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        batch_df = extract_batch_rows(df, start_idx, batch_size)
        batch_id = str(uuid.uuid4())[:8]  # ID único de 8 caracteres
        batch_list.append((batch_df, batch_num + 1, batch_id))
    
    print(f"✅ {len(batch_list)} lotes preparados con IDs únicos")
    
    # Procesar en paralelo con máximo 5 workers
    max_workers = 5
    successful_batches = 0
    failed_batches = 0
    
    print(f"\n3. Procesando lotes en paralelo (máximo {max_workers} simultáneos)...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Enviar todos los lotes
        future_to_batch = {
            executor.submit(process_batch_parallel, batch_data, api_key): batch_data 
            for batch_data in batch_list
        }
        
        # Procesar resultados conforme van llegando
        for future in as_completed(future_to_batch):
            batch_data = future_to_batch[future]
            batch_df, batch_number, batch_id = batch_data
            
            try:
                result = future.result()
                
                if result['status'] == 'success':
                    # Añadir al CSV de resultado
                    append_to_result_csv(result['corrected_data'], df, csv_result)
                    successful_batches += 1
                    print(f"✅ Lote {batch_number} (ID: {batch_id}) completado exitosamente")
                else:
                    # Usar datos originales
                    batch_df.to_csv(csv_result, mode='a', header=not os.path.exists(csv_result), index=False, encoding='utf-8')
                    failed_batches += 1
                    print(f"❌ Lote {batch_number} (ID: {batch_id}) falló: {result.get('error', 'Error desconocido')}")
                
                # Mostrar progreso cada 10 lotes
                total_processed = successful_batches + failed_batches
                if total_processed % 10 == 0:
                    print(f"\n📊 Progreso: {total_processed}/{total_batches} lotes procesados")
                    print(f"   ✅ Exitosos: {successful_batches}")
                    print(f"   ❌ Fallidos: {failed_batches}")
                
            except Exception as e:
                failed_batches += 1
                print(f"❌ Error procesando lote {batch_number} (ID: {batch_id}): {e}")
    
    # Crear archivo XLSX final
    print(f"\n4. Creando archivo XLSX final...")
    save_final_xlsx(csv_result, xlsx_result)
    
    # Estadísticas finales
    print(f"\n=== Proceso Completado ===")
    print(f"📊 Estadísticas finales:")
    print(f"   Total lotes: {total_batches}")
    print(f"   Exitosos: {successful_batches}")
    print(f"   Fallidos: {failed_batches}")
    print(f"   Tasa de éxito: {successful_batches/total_batches*100:.1f}%")
    print(f"\n📁 Archivos generados:")
    print(f"   - {csv_result}")
    print(f"   - {xlsx_result}")

if __name__ == "__main__":
    main()
