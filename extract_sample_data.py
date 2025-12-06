import pandas as pd
import json

def extract_and_save_sample():
    """Extrae las primeras 5 filas y las guarda en formato legible"""
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel("results - copia.xlsx")
        
        # Extraer las primeras 5 filas
        first_5 = df.head(5)
        
        print("=== DATOS ORIGINALES (Primeras 5 filas) ===")
        print(f"Número de columnas: {len(df.columns)}")
        print(f"Nombres de columnas: {list(df.columns)}")
        print("\nDatos:")
        print(first_5.to_string())
        
        # Guardar en CSV para revisión
        first_5.to_csv("sample_first_5_rows.csv", index=False, encoding='utf-8')
        print(f"\n✅ Archivo CSV creado: sample_first_5_rows.csv")
        
        # Guardar en Excel para revisión
        first_5.to_excel("sample_first_5_rows.xlsx", index=False)
        print(f"✅ Archivo XLSX creado: sample_first_5_rows.xlsx")
        
        # Crear un resumen de la estructura
        structure_info = {
            "total_columns": len(df.columns),
            "column_names": list(df.columns),
            "unnamed_columns": [col for col in df.columns if 'Unnamed' in str(col)],
            "sample_data": first_5.to_dict('records')
        }
        
        with open("structure_analysis.json", "w", encoding='utf-8') as f:
            json.dump(structure_info, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Análisis de estructura guardado: structure_analysis.json")
        
        return first_5
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    extract_and_save_sample()
