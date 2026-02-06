import os
import json
import sys
import re
from collections import Counter

# Configuración de salida para consola
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

INPUT_DIR = os.path.join("univ_jp", "1")

def is_japanese(text):
    if not text:
        return False
    # Rango Unicode para caracteres japoneses (Hiragana, Katakana, y Kanji común)
    jp_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
    return bool(jp_pattern.search(text))

def analyze_duplicates():
    if not os.path.exists(INPUT_DIR):
        print(f"Error: La carpeta {INPUT_DIR} no existe.")
        return

    titles_jp = Counter()
    titles_non_jp = Counter()
    
    jsonl_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.jsonl')]
    print(f"Analizando duplicados en {len(jsonl_files)} archivos...")

    for filename in jsonl_files:
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        record = json.loads(line)
                        title = record.get('display_title', '').strip()
                        if not title: continue
                        
                        if is_japanese(title):
                            titles_jp[title] += 1
                        else:
                            titles_non_jp[title] += 1
                    except: continue
        except Exception as e:
            print(f"Error en {filename}: {e}")

    # Cálculos para Japonés
    total_jp = sum(titles_jp.values())
    unique_jp = len(titles_jp)
    repeated_jp = total_jp - unique_jp
    perc_repeated_jp = (repeated_jp / total_jp * 100) if total_jp > 0 else 0

    # Cálculos para Otros Idiomas
    total_non_jp = sum(titles_non_jp.values())
    unique_non_jp = len(titles_non_jp)
    repeated_non_jp = total_non_jp - unique_non_jp
    perc_repeated_non_jp = (repeated_non_jp / total_non_jp * 100) if total_non_jp > 0 else 0

    print("-" * 50)
    print(f"{'CATEGORÍA':<20} | {'TOTAL':<10} | {'ÚNICOS':<10} | {'% REPETIDOS'}")
    print("-" * 50)
    print(f"{'Japonés':<20} | {total_jp:<10} | {unique_jp:<10} | {perc_repeated_jp:.2f}%")
    print(f"{'Otros Idiomas':<20} | {total_non_jp:<10} | {unique_non_jp:<10} | {perc_repeated_non_jp:.2f}%")
    print("-" * 50)
    print(f"TOTAL GLOBAL: {total_jp + total_non_jp}")

if __name__ == "__main__":
    analyze_duplicates()
