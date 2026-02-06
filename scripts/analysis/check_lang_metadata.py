import json
import os
import glob

def check_languages():
    path = r'c:\Users\User\Desktop\github\harvesting_translations\univ_jp\2\cinii_*_ALL.jsonl'
    files = glob.glob(path)
    
    total_records = 0
    records_with_lang = 0
    records_empty_lang = 0
    
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    total_records += 1
                    lang = data.get('display_language', '')
                    if lang and str(lang).strip():
                        records_with_lang += 1
                    else:
                        records_empty_lang += 1
                except:
                    continue
                    
    print(f"Total de registros analizados: {total_records}")
    print(f"Registros con metadato de idioma: {records_with_lang}")
    print(f"Registros con idioma vacío: {records_empty_lang}")
    
    if total_records > 0:
        pct_with = (records_with_lang / total_records) * 100
        pct_without = (records_empty_lang / total_records) * 100
        print(f"Porcentaje con idioma: {pct_with:.2f}%")
        print(f"Porcentaje sin idioma: {pct_without:.2f}%")

if __name__ == "__main__":
    check_languages()
