import os
import json
import glob
import sys
import io
import shutil

# Set stdout to utf-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DATA_DIR = os.path.join("data", "cinii", "v3_by_ndc_lang")
TARGET_1900_DIR = os.path.join(BASE_DATA_DIR, "1900")

def normalize_text(text):
    if not text:
        return ""
    return "".join(text.split()).lower()

def load_dataset_index():
    """
    Loads matches from 1850-1920 (excluding 1900).
    Returns a dict: { (normalized_title, normalized_creator): year }
    """
    index = {}
    print("Indexing valid years (1850-1920)...")
    
    # Iterate over years
    years = [str(y) for y in range(1850, 1921) if y != 1900]
    
    for year in years:
        year_path = os.path.join(BASE_DATA_DIR, year)
        if not os.path.exists(year_path):
            continue
            
        print(f"\rScanning {year}...", end="", flush=True)
        for jsonl_file in glob.glob(os.path.join(year_path, "*.jsonl")):
            try:
                with open(jsonl_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip(): continue
                        record = json.loads(line)
                        title = normalize_text(record.get("display_title"))
                        creator = normalize_text(record.get("display_creator"))
                        
                        if title:
                            key = (title, creator)
                            if key not in index:
                                index[key] = year
            except Exception as e:
                print(f"Error reading {jsonl_file}: {e}")
                continue
    print(f"\nIndexed {len(index)} unique records.")
    return index

def apply_correction():
    if not os.path.exists(TARGET_1900_DIR):
        print("1900 directory not found.")
        return

    valid_index = load_dataset_index()
    
    print("\nProcessing 1900 records...")
    
    files = glob.glob(os.path.join(TARGET_1900_DIR, "*.jsonl"))
    total_moved = 0
    
    for jsonl_file in files:
        filename = os.path.basename(jsonl_file)
        # filename format: cinii_LANG_NDC.jsonl, e.g., cinii_JP_9.jsonl
        
        remaining_records = []
        moved_count = 0
        
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    record = json.loads(line)
                    title = normalize_text(record.get("display_title"))
                    creator = normalize_text(record.get("display_creator"))
                    
                    key = (title, creator)
                    
                    if title and key in valid_index:
                        # MATCH FOUND -> MOVE
                        correct_year = valid_index[key]
                        
                        # Update record
                        record["display_creationdate"] = correct_year
                        record["enrichment_source"] = "internal_dedup"
                        
                        # Determine target file path
                        target_dir = os.path.join(BASE_DATA_DIR, correct_year)
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir)
                            
                        target_file = os.path.join(target_dir, filename)
                        
                        # Append to target file
                        with open(target_file, "a", encoding="utf-8") as tf:
                            tf.write(json.dumps(record, ensure_ascii=False) + "\n")
                            
                        moved_count += 1
                        total_moved += 1
                    else:
                        # NO MATCH -> KEEP
                        remaining_records.append(line)
                        
                except Exception as e:
                    print(f"Error processing line: {e}")
                    remaining_records.append(line) # Keep on error to be safe
        
        # Rewrite the 1900 file with only remaining records
        if moved_count > 0:
            print(f"  {filename}: Moved {moved_count} records.")
            with open(jsonl_file, "w", encoding="utf-8") as f:
                for line in remaining_records:
                    f.write(line)
        else:
            print(f"\r  {filename}: No matches found.", end="")

    print("\n" + "-" * 40)
    print(f"Total Records Moved: {total_moved}")
    print("-" * 40)

if __name__ == "__main__":
    apply_correction()
