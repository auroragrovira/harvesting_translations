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

def test_small_batch():
    """Prueba con un lote pequeño de 3 filas"""
    
    print("=== Prueba con Lote Pequeño ===")
    
    # Leer clave API
    api_key = read_api_key()
    if not api_key:
        return
    
    # Cargar estructura de referencia
    ref_df = pd.read_csv("sample_first_5_rows.csv")
    reference_columns = ref_df.columns.tolist()
    
    # Leer solo las primeras 3 filas del Excel original
    df = pd.read_excel("results - copia.xlsx", nrows=3)
    
    print(f"Procesando {len(df)} filas de prueba...")
    
    # Preparar datos de prueba
    batch_rows = []
    for i, row in df.iterrows():
        batch_rows.append(row.tolist())
    
    # Crear prompt simple
    batch_text = ""
    for i, row_data in enumerate(batch_rows):
        row_number = i + 1
        batch_text += f"\nFILA {row_number}: "
        # Solo mostrar valores no vacíos
        non_empty_values = []
        for j, value in enumerate(row_data):
            if pd.notna(value) and str(value).strip() != "":
                col_name = reference_columns[j] if j < len(reference_columns) else f"Col_{j}"
                non_empty_values.append(f"{col_name}={str(value)[:50]}")  # Limitar longitud
        batch_text += " | ".join(non_empty_values[:8])  # Solo 8 valores por fila
    
    prompt = f"""
Corrige estas 3 filas con columnas desalineadas:

{batch_text}

Columnas esperadas: {', '.join(reference_columns[:10])}...

Problema: celdas vacías desplazan columnas.

Devuelve JSON:
{{
    "corrected_rows": [
        {{"row_number": 1, "corrected_row": ["val1", "val2", "", "val4", ...]}},
        {{"row_number": 2, "corrected_row": ["val1", "", "val3", "val4", ...]}},
        {{"row_number": 3, "corrected_row": ["val1", "val2", "val3", "", ...]}}
    ]
}}

Cada corrected_row debe tener {len(reference_columns)} elementos.
"""

    print("Enviando a GPT-4...")
    print(f"Longitud del prompt: {len(prompt)} caracteres")
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Eres un experto en análisis de datos Excel. Devuelves solo JSON válido."},
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
            gpt_response = result['choices'][0]['message']['content']
            
            print("✅ Respuesta recibida de GPT-4")
            print("\nRespuesta completa:")
            print(gpt_response)
            
            # Intentar parsear
            try:
                start_idx = gpt_response.find('{')
                end_idx = gpt_response.rfind('}') + 1
                
                if start_idx != -1 and end_idx > 0:
                    json_str = gpt_response[start_idx:end_idx]
                    data = json.loads(json_str)
                    
                    print("\n✅ JSON parseado exitosamente:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # Crear archivo de prueba
                    if 'corrected_rows' in data:
                        corrected_data = []
                        for row_info in data['corrected_rows']:
                            corrected_data.append(row_info['corrected_row'])
                        
                        test_df = pd.DataFrame(corrected_data, columns=reference_columns)
                        test_df.to_csv("test_corrected_3_rows.csv", index=False, encoding='utf-8')
                        test_df.to_excel("test_corrected_3_rows.xlsx", index=False)
                        
                        print("\n✅ Archivos de prueba creados:")
                        print("   - test_corrected_3_rows.csv")
                        print("   - test_corrected_3_rows.xlsx")
                    
                else:
                    print("❌ No se encontró JSON válido en la respuesta")
                    
            except Exception as e:
                print(f"❌ Error parseando JSON: {e}")
                
        else:
            print(f"❌ Error en la API: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error enviando datos: {e}")

if __name__ == "__main__":
    test_small_batch()
