import pandas as pd
import json
import requests
import time

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

def analyze_structure():
    """Analiza la estructura del Excel para identificar problemas"""
    
    print("=== Análisis de Estructura ===")
    
    # Leer archivos
    ref_df = pd.read_csv("sample_first_5_rows.csv")
    original_df = pd.read_excel("results - copia.xlsx", nrows=10)
    
    print(f"Columnas de referencia: {len(ref_df.columns)}")
    print(f"Columnas originales: {len(original_df.columns)}")
    
    # Identificar columnas problemáticas
    unnamed_cols = [col for col in original_df.columns if 'Unnamed' in str(col)]
    print(f"Columnas 'Unnamed': {len(unnamed_cols)}")
    
    # Analizar las primeras filas para ver el patrón
    print("\nAnálisis de las primeras 3 filas:")
    for i in range(min(3, len(original_df))):
        row = original_df.iloc[i]
        non_empty_count = sum(1 for val in row if pd.notna(val) and str(val).strip() != "")
        print(f"Fila {i+1}: {non_empty_count} valores no vacíos de {len(row)} columnas")
    
    return ref_df.columns.tolist(), unnamed_cols

def create_smart_prompt(row_data, reference_columns, row_number):
    """Crea un prompt inteligente basado en el análisis"""
    
    # Identificar valores no vacíos y sus posiciones
    non_empty_data = []
    for i, value in enumerate(row_data):
        if pd.notna(value) and str(value).strip() != "":
            col_name = reference_columns[i] if i < len(reference_columns) else f"Col_{i}"
            non_empty_data.append(f"{col_name}={str(value)[:100]}")  # Limitar longitud
    
    prompt = f"""
Analiza esta fila problemática (fila {row_number}):

Valores encontrados: {' | '.join(non_empty_data[:15])}

Columnas esperadas: {', '.join(reference_columns[:15])}...

PROBLEMA: Las columnas están desalineadas. Algunas celdas que deberían estar vacías tienen datos, desplazando todo hacia la izquierda.

SOLUCIÓN: Reorganiza los valores en las columnas correctas, dejando vacías las celdas que deben estar vacías.

Devuelve solo el array de valores corregidos:
["valor1", "valor2", "", "valor4", ...]

IMPORTANTE: 
- El array debe tener exactamente {len(reference_columns)} elementos
- Usa "" para celdas vacías
- Mantén los valores originales pero en las posiciones correctas
"""
    
    return prompt

def correct_single_row(row_data, reference_columns, api_key, row_number):
    """Corrige una sola fila usando análisis inteligente"""
    
    prompt = create_smart_prompt(row_data, reference_columns, row_number)
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Eres un experto en análisis de datos Excel. Devuelves solo arrays JSON válidos."},
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
            gpt_response = result['choices'][0]['message']['content'].strip()
            
            # Intentar parsear como array JSON
            try:
                # Limpiar la respuesta
                gpt_response = gpt_response.replace('```json', '').replace('```', '').strip()
                
                # Buscar array JSON
                start_idx = gpt_response.find('[')
                end_idx = gpt_response.rfind(']') + 1
                
                if start_idx != -1 and end_idx > 0:
                    json_str = gpt_response[start_idx:end_idx]
                    corrected_row = json.loads(json_str)
                    
                    if len(corrected_row) == len(reference_columns):
                        return corrected_row
                    else:
                        print(f"⚠️  Fila {row_number}: Longitud incorrecta ({len(corrected_row)} vs {len(reference_columns)})")
                        return None
                else:
                    print(f"⚠️  Fila {row_number}: No se encontró array JSON válido")
                    return None
                    
            except Exception as e:
                print(f"⚠️  Fila {row_number}: Error parseando JSON: {e}")
                return None
                
        else:
            print(f"❌ Error API para fila {row_number}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error enviando fila {row_number}: {e}")
        return None

def process_sample_rows():
    """Procesa una muestra de filas para probar el método"""
    
    print("=== Procesamiento Inteligente de Muestra ===")
    
    # Leer clave API
    api_key = read_api_key()
    if not api_key:
        return
    
    # Analizar estructura
    reference_columns, unnamed_cols = analyze_structure()
    
    # Leer muestra de filas
    df = pd.read_excel("results - copia.xlsx", nrows=10)
    
    print(f"\nProcesando {len(df)} filas de muestra...")
    
    corrected_rows = []
    processing_log = []
    
    for i, (index, row) in enumerate(df.iterrows()):
        row_number = i + 1
        print(f"Procesando fila {row_number}...")
        
        row_data = row.tolist()
        
        # Intentar corrección
        corrected_row = correct_single_row(row_data, reference_columns, api_key, row_number)
        
        if corrected_row:
            corrected_rows.append(corrected_row)
            processing_log.append({
                "row": row_number,
                "status": "success",
                "explanation": "Corregida exitosamente"
            })
            print(f"✅ Fila {row_number} corregida")
        else:
            # Usar datos originales truncados
            corrected_row = row_data[:len(reference_columns)]
            corrected_rows.append(corrected_row)
            processing_log.append({
                "row": row_number,
                "status": "error",
                "explanation": "Error en corrección, usando datos originales"
            })
            print(f"⚠️  Fila {row_number}: usando datos originales")
        
        # Pausa entre requests
        time.sleep(1)
    
    # Guardar resultados
    if corrected_rows:
        result_df = pd.DataFrame(corrected_rows, columns=reference_columns)
        
        result_df.to_csv("smart_corrected_sample.csv", index=False, encoding='utf-8')
        result_df.to_excel("smart_corrected_sample.xlsx", index=False)
        
        with open("smart_processing_log.json", "w", encoding='utf-8') as f:
            json.dump(processing_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Resultados guardados:")
        print(f"   - smart_corrected_sample.csv")
        print(f"   - smart_corrected_sample.xlsx")
        print(f"   - smart_processing_log.json")
        
        # Estadísticas
        success_count = sum(1 for log in processing_log if log['status'] == 'success')
        print(f"\n📊 Estadísticas:")
        print(f"   Total filas: {len(processing_log)}")
        print(f"   Exitosas: {success_count}")
        print(f"   Errores: {len(processing_log) - success_count}")
        print(f"   Tasa de éxito: {success_count/len(processing_log)*100:.1f}%")

if __name__ == "__main__":
    process_sample_rows()
