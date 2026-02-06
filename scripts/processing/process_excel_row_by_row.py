import pandas as pd
import json
import requests
import time
import os

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

def load_reference_structure():
    """Carga la estructura de referencia desde el CSV de las 5 filas"""
    try:
        ref_df = pd.read_csv("sample_first_5_rows.csv")
        return ref_df.columns.tolist(), ref_df
    except Exception as e:
        print(f"Error cargando estructura de referencia: {e}")
        return None, None

def send_batch_to_gpt4(batch_rows, reference_columns, api_key, batch_number, start_row):
    """Envía un lote de filas a GPT-4 para corrección"""
    
    # Convertir las filas a formato más conciso
    batch_text = ""
    for i, row_data in enumerate(batch_rows):
        row_number = start_row + i
        batch_text += f"\nFILA {row_number}: "
        # Solo mostrar valores no vacíos para reducir el texto
        non_empty_values = []
        for j, value in enumerate(row_data):
            if pd.notna(value) and str(value).strip() != "":
                col_name = reference_columns[j] if j < len(reference_columns) else f"Col_{j}"
                non_empty_values.append(f"{col_name}={value}")
        batch_text += " | ".join(non_empty_values[:10])  # Limitar a 10 valores por fila
    
    prompt = f"""
Corrige estas {len(batch_rows)} filas que tienen columnas desalineadas:

{batch_text}

Columnas esperadas ({len(reference_columns)}): {', '.join(reference_columns[:10])}...

Problema: algunas celdas vacías no están vacías, desplazando columnas.

Devuelve JSON:
{{
    "corrected_rows": [
        {{"row_number": {start_row}, "corrected_row": ["val1", "val2", "", "val4", ...]}},
        {{"row_number": {start_row + 1}, "corrected_row": ["val1", "", "val3", "val4", ...]}},
        ...
    ]
}}

Cada corrected_row debe tener {len(reference_columns)} elementos.
"""

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Eres un experto en análisis de datos y estructura de archivos Excel. Ayudas a corregir problemas de formato y estructura. Siempre devuelves respuestas en formato JSON válido."},
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
            return result['choices'][0]['message']['content']
        else:
            print(f"Error en la API para lote {batch_number}: {response.status_code} - {response.text}")
            return None
        
    except Exception as e:
        print(f"Error enviando lote {batch_number} a GPT-4: {e}")
        return None

def parse_gpt_response(response_text, batch_number):
    """Parsea la respuesta de GPT-4 y extrae los datos corregidos"""
    try:
        # Buscar el JSON en la respuesta
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            print(f"No se encontró JSON válido en la respuesta para lote {batch_number}")
            return None
            
        json_str = response_text[start_idx:end_idx]
        data = json.loads(json_str)
        
        return data
        
    except Exception as e:
        print(f"Error parseando la respuesta de GPT-4 para lote {batch_number}: {e}")
        return None

def process_excel_row_by_row():
    """Procesa el Excel fila por fila"""
    
    print("=== Procesamiento Fila por Fila del Excel ===")
    
    # Leer clave API
    api_key = read_api_key()
    if not api_key:
        return
    
    # Cargar estructura de referencia
    print("1. Cargando estructura de referencia...")
    reference_columns, reference_df = load_reference_structure()
    if not reference_columns:
        return
    
    print(f"   ✅ Estructura de referencia cargada: {len(reference_columns)} columnas")
    
    # Leer el archivo Excel completo
    print("2. Leyendo archivo Excel completo...")
    try:
        df = pd.read_excel("results - copia.xlsx")
        print(f"   ✅ Archivo leído: {len(df)} filas, {len(df.columns)} columnas")
    except Exception as e:
        print(f"   ❌ Error leyendo Excel: {e}")
        return
    
    # Preparar listas para almacenar resultados
    corrected_rows = []
    processing_log = []
    
    print("3. Procesando filas en lotes de 5...")
    
    batch_size = 5
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    # Procesar en lotes
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(df))
        
        print(f"   Procesando lote {batch_num + 1}/{total_batches} (filas {start_idx + 1} a {end_idx})...")
        
        # Preparar lote de filas
        batch_rows = []
        for i in range(start_idx, end_idx):
            row_data = df.iloc[i].tolist()
            batch_rows.append(row_data)
        
        # Enviar lote a GPT-4
        gpt_response = send_batch_to_gpt4(batch_rows, reference_columns, api_key, batch_num + 1, start_idx + 1)
        
        if not gpt_response:
            print(f"   ⚠️  Sin respuesta para lote {batch_num + 1}, usando datos originales")
            # Usar datos originales si no hay respuesta
            for i, row_data in enumerate(batch_rows):
                corrected_row = row_data[:len(reference_columns)]  # Truncar a la longitud correcta
                corrected_rows.append(corrected_row)
                processing_log.append({
                    "row": start_idx + i + 1,
                    "status": "error",
                    "explanation": "Sin respuesta de GPT-4"
                })
        else:
            # Parsear respuesta
            corrected_data = parse_gpt_response(gpt_response, batch_num + 1)
            
            if corrected_data and 'corrected_rows' in corrected_data:
                # Procesar cada fila corregida
                for corrected_row_info in corrected_data['corrected_rows']:
                    row_number = corrected_row_info.get('row_number', start_idx + len(corrected_rows) + 1)
                    corrected_row = corrected_row_info.get('corrected_row', [])
                    
                    corrected_rows.append(corrected_row)
                    processing_log.append({
                        "row": row_number,
                        "status": "success",
                        "explanation": corrected_data.get('explanation', 'Sin explicación')
                    })
                
                print(f"   ✅ Lote {batch_num + 1} corregido ({len(corrected_data['corrected_rows'])} filas)")
            else:
                print(f"   ⚠️  Error parseando respuesta para lote {batch_num + 1}, usando datos originales")
                for i, row_data in enumerate(batch_rows):
                    corrected_row = row_data[:len(reference_columns)]
                    corrected_rows.append(corrected_row)
                    processing_log.append({
                        "row": start_idx + i + 1,
                        "status": "parse_error",
                        "explanation": "Error parseando respuesta de GPT-4"
                    })
        
        # Pausa para evitar límites de API
        time.sleep(2)
        
        # Guardar progreso cada 5 lotes
        if (batch_num + 1) % 5 == 0:
            save_progress(corrected_rows, reference_columns, processing_log, end_idx)
    
    # Guardar resultados finales
    print("4. Guardando resultados finales...")
    save_final_results(corrected_rows, reference_columns, processing_log)
    
    print("=== Procesamiento completado ===")

def save_progress(corrected_rows, reference_columns, processing_log, processed_count):
    """Guarda el progreso actual"""
    try:
        # Crear DataFrame temporal
        temp_df = pd.DataFrame(corrected_rows, columns=reference_columns)
        
        # Guardar CSV temporal
        temp_df.to_csv(f"progress_{processed_count}_rows.csv", index=False, encoding='utf-8')
        
        # Guardar log temporal
        with open(f"progress_log_{processed_count}.json", "w", encoding='utf-8') as f:
            json.dump(processing_log, f, ensure_ascii=False, indent=2)
        
        # Estadísticas del progreso
        success_count = sum(1 for log in processing_log if log['status'] == 'success')
        error_count = len(processing_log) - success_count
        
        print(f"   💾 Progreso guardado: {processed_count} filas procesadas")
        print(f"      ✅ Exitosas: {success_count} | ❌ Errores: {error_count}")
        
    except Exception as e:
        print(f"   ⚠️  Error guardando progreso: {e}")

def save_final_results(corrected_rows, reference_columns, processing_log):
    """Guarda los resultados finales"""
    try:
        # Crear DataFrame final
        final_df = pd.DataFrame(corrected_rows, columns=reference_columns)
        
        # Guardar CSV final
        final_df.to_csv("corrected_complete_dataset.csv", index=False, encoding='utf-8')
        print("   ✅ CSV final creado: corrected_complete_dataset.csv")
        
        # Guardar XLSX final
        final_df.to_excel("corrected_complete_dataset.xlsx", index=False)
        print("   ✅ XLSX final creado: corrected_complete_dataset.xlsx")
        
        # Guardar log final
        with open("final_processing_log.json", "w", encoding='utf-8') as f:
            json.dump(processing_log, f, ensure_ascii=False, indent=2)
        print("   ✅ Log final creado: final_processing_log.json")
        
        # Estadísticas
        success_count = sum(1 for log in processing_log if log['status'] == 'success')
        error_count = len(processing_log) - success_count
        
        print(f"\n📊 Estadísticas:")
        print(f"   Total filas procesadas: {len(processing_log)}")
        print(f"   Filas corregidas exitosamente: {success_count}")
        print(f"   Filas con errores: {error_count}")
        print(f"   Tasa de éxito: {success_count/len(processing_log)*100:.1f}%")
        
    except Exception as e:
        print(f"   ❌ Error guardando resultados finales: {e}")

if __name__ == "__main__":
    process_excel_row_by_row()
