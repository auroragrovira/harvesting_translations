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

def analyze_samples():
    if not os.path.exists(INPUT_DIR):
        print(f"Error: La carpeta {INPUT_DIR} no existe.")
        return

    total_count = 0
    non_jp_count = 0
    samples_non_jp = []
    samples_jp = []
    
    jsonl_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.jsonl')]

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
                        
                        lang = record.get('display_language', '')
                        title = record.get('display_title', '')
                        
                        is_jp = False
                        if lang:
                            if isinstance(lang, list):
                                lang = " ".join(lang)
                            if 'ja' in lang.lower() or 'jpn' in lang.lower():
                                is_jp = True
                        else:
                            if is_japanese(title):
                                is_jp = True
                        
                        if not is_jp:
                            non_jp_count += 1
                            if len(samples_non_jp) < 15:
                                samples_non_jp.append((title, lang))
                        else:
                            if len(samples_jp) < 5:
                                samples_jp.append((title, lang))
                    except: continue
        except Exception as e:
            pass

    print(f"Total: {total_count} | No Japoneses: {non_jp_count} ({ (non_jp_count/total_count*100) if total_count > 0 else 0 :.2f}%)")
    
    print("\n--- EJEMPLOS CLASIFICADOS COMO JAPONÉS ---")
    for t, l in samples_jp:
        print(f"Título: {t} | Idioma: {l}")

    print("\n--- EJEMPLOS CLASIFICADOS COMO 'NO JAPONÉS' ---")
    for t, l in samples_non_jp:
        print(f"Título: {t} | Idioma: {l}")

if __name__ == "__main__":
    analyze_samples()
