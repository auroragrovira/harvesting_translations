import os
import json
import sys
import re

# Configuración de salida para consola
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT_DIR = os.path.join("univ_jp", "2")

def is_japanese(text):
    if not text:
        return False
    # Rango Unicode para caracteres japoneses (Hiragana, Katakana, y Kanji común)
    jp_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
    return bool(jp_pattern.search(text))

def analyze_folder_2():
    if not os.path.exists(INPUT_DIR):
        print(f"Error: La carpeta {INPUT_DIR} no existe.")
        return

    total_count = 0
    non_jp_count = 0
    
    jsonl_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.jsonl')]
    print(f"Analizando {len(jsonl_files)} archivos en {INPUT_DIR}...")

    for filename in jsonl_files:
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        record = json.loads(line)
                        total_count += 1
                        
                        # En la carpeta 2 el script SÍ intenta guardar el idioma
                        lang = record.get('display_language', '')
                        title = record.get('display_title', '')
                        
                        is_jp = False
                        if lang:
                            if isinstance(lang, list):
                                lang = " ".join(lang)
                            if 'ja' in lang.lower() or 'jpn' in lang.lower():
                                is_jp = True
                        else:
                            # Si no hay idioma, detectamos por caracteres en el título
                            if is_japanese(title):
                                is_jp = True
                        
                        if not is_jp:
                            non_jp_count += 1
                    except: continue
        except Exception as e:
            print(f"Error en {filename}: {e}")

    print("-" * 40)
    print(f"Resultados para Carpeta 2:")
    print(f"Total de registros: {total_count}")
    print(f"Registros NO japoneses: {non_jp_count}")
    print(f"Porcentaje NO japoneses: {(non_jp_count/total_count*100):.2f}%" if total_count > 0 else "N/A")
    print("-" * 40)

if __name__ == "__main__":
    analyze_folder_2()
