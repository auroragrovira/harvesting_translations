import os
import json
import glob
import sys
import io

# Set stdout to utf-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def normalize_text(text):
    if not text:
        return ""
    return "".join(text.split()).lower()

def load_dataset_index(base_dir):
    """
    Loads matches from 1850-1920 (excluding 1900).
    Returns a dict: { (normalized_title, normalized_creator): year }
    """
    index = {}
    print("Indexing valid years (1850-1920)...")
    
    # Iterate over years
    years = [str(y) for y in range(1850, 1921) if y != 1900]
    
    for year in years:
        year_path = os.path.join(base_dir, year)
        if not os.path.exists(year_path):
            continue
            
        print(f"\rScanning {year}...", end="", flush=True)
        for jsonl_file in glob.glob(os.path.join(year_path, "*.jsonl")):
            with open(jsonl_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        title = normalize_text(record.get("display_title"))
                        creator = normalize_text(record.get("display_creator"))
                        
                        if title:
                            key = (title, creator)
                            # We keep the first valid year found
                            if key not in index:
                                index[key] = year
                    except:
                        continue
    print(f"\nIndexed {len(index)} unique records.")
    return index

def analyze_1900_matches():
    base_data_dir = os.path.join("data", "cinii", "v3_by_ndc_lang")
    target_dir = os.path.join(base_data_dir, "1900")
    
    if not os.path.exists(target_dir):
        print("1900 directory not found.")
        return

    # 1. Build Index of valid years
    valid_index = load_dataset_index(base_data_dir)
    
    # 2. Check 1900 records against index
    print("\nAnalyzing 1900 records...")
    
    total_1900 = 0
    matches_found = 0
    matches_by_year = {} # year -> count
    
    unique_1900_keys = set()

    for jsonl_file in glob.glob(os.path.join(target_dir, "*.jsonl")):
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    total_1900 += 1
                    
                    title = normalize_text(record.get("display_title"))
                    creator = normalize_text(record.get("display_creator"))
                    
                    if not title:
                        continue
                        
                    key = (title, creator)
                    unique_1900_keys.add(key)
                    
                    if key in valid_index:
                        matches_found += 1
                        matched_year = valid_index[key]
                        matches_by_year[matched_year] = matches_by_year.get(matched_year, 0) + 1
                        
                except:
                    continue

    print("-" * 40)
    print(f"Total 1900 Records: {total_1900}")
    print(f"Matches found in other years: {matches_found} ({matches_found/total_1900*100:.2f}%)")
    print("-" * 40)
    
    if matches_found > 0:
        print("Top 10 Resolved Years:")
        sorted_years = sorted(matches_by_year.items(), key=lambda x: x[1], reverse=True)
        for y, count in sorted_years[:10]:
            print(f"  {y}: {count}")
    else:
        print("No significant overlap found. The 1900 records appear to be unique or disjoint from the rest.")

if __name__ == "__main__":
    analyze_1900_matches()
