import os

def count_lines(filepath):
    try:
        with open(filepath, 'rb') as f:
            return sum(1 for _ in f)
    except:
        return 0

dir1 = os.path.join("univ_jp", "1")
dir2 = os.path.join("univ_jp", "2")

years = range(1850, 1921)

print(f"{'Año':<6} | {'Carpeta 1':<12} | {'Carpeta 2':<12} | {'Diferencia'}")
print("-" * 50)

for year in years:
    # Carpeta 1: archivos tipo cinii_1850.jsonl
    f1 = os.path.join(dir1, f"cinii_{year}.jsonl")
    # Carpeta 2: archivos tipo cinii_1850_ALL.jsonl (o similares con sufijo)
    # Buscamos archivos que empiecen por cinii_YEAR
    files2 = [os.path.join(dir2, f) for f in os.listdir(dir2) if f.startswith(f"cinii_{year}_") and f.endswith(".jsonl")]
    
    count1 = count_lines(f1)
    count2 = sum(count_lines(f) for f in files2)
    
    diff = count2 - count1
    if count1 > 0 or count2 > 0:
        print(f"{year:<6} | {count1:<12} | {count2:<12} | {diff:+}")
