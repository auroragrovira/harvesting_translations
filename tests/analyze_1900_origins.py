import os
import json
from collections import Counter
import glob
import sys
import io

# Set stdout to utf-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_1900_data():
    base_dir = os.path.join("data", "cinii", "v3_by_ndc_lang", "1900")
    if not os.path.exists(base_dir):
        print(f"Error: Directory {base_dir} not found.")
        return

    date_counter = Counter()
    publisher_counter = Counter()
    total_records = 0
    files_processed = 0

    print(f"Analyzing JSONL files in {base_dir}...")

    for file_path in glob.glob(os.path.join(base_dir, "*.jsonl")):
        files_processed += 1
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    total_records += 1
                    
                    # Analyze creation date
                    date_raw = record.get("display_creationdate", "MISSING")
                    date_counter[date_raw] += 1
                    
                    # Analyze publisher
                    pubs = record.get("display_publisher", [])
                    if isinstance(pubs, list):
                        for p in pubs:
                            publisher_counter[p] += 1
                    elif isinstance(pubs, str):
                        publisher_counter[pubs] += 1
                        
                except json.JSONDecodeError:
                    continue

    print("-" * 40)
    print(f"Total Records Analyzed: {total_records}")
    print(f"Files Processed: {files_processed}")
    print("-" * 40)
    
    print("\nTop 20 Raw Dates:")
    for date, count in date_counter.most_common(20):
        print(f"  {date}: {count} ({count/total_records*100:.1f}%)")
        
    print("\nTop 20 Publishers:")
    for pub, count in publisher_counter.most_common(20):
        print(f"  {pub}: {count}")

    # Interpretation recommendation
    print("\n--- INTERPRETATION ---")
    if date_counter["19--"] > total_records * 0.1:
        print("Note: High prevalence of '19--' indicates undated 20th-century records mapped to 1900.")

if __name__ == "__main__":
    analyze_1900_data()
