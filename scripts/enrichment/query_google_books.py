import os
import json
import glob
import sys
import io
import time
import requests
import difflib
from urllib.parse import quote

# Set stdout to utf-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DATA_DIR = os.path.join("data", "cinii", "v3_by_ndc_lang")
TARGET_1900_DIR = os.path.join(BASE_DATA_DIR, "1900")
API_URL = "https://www.googleapis.com/books/v1/volumes"

# Rate limiting
REQUEST_DELAY = 1.0 # Seconds

def get_google_books_date(title, creator):
    query = f"intitle:{title}"
    if creator:
        query += f"+inauthor:{creator}"
        
    params = {
        "q": query,
        "maxResults": 3,
        "printType": "books",
        "langRestrict": "ja" # Optional restriction
    }
    
    try:
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                for item in data["items"]:
                    vol_info = item.get("volumeInfo", {})
                    pub_date = vol_info.get("publishedDate", "")
                    
                    # Check year
                    if len(pub_date) >= 4:
                        try:
                            year = int(pub_date[:4])
                            if 1850 <= year <= 1920 and year != 1900:
                                # Validation: check title similarity
                                g_title = vol_info.get("title", "")
                                ratio = difflib.SequenceMatcher(None, title, g_title).ratio()
                                if ratio > 0.7: # Threshold
                                    return str(year)
                        except ValueError:
                            continue
        elif response.status_code == 429:
            print("Rate limit reached. Sleeping...")
            time.sleep(10)
            
    except Exception as e:
        print(f"Error querying Google Books: {e}")
        
    return None

def process_enrichment():
    if not os.path.exists(TARGET_1900_DIR):
        print("1900 directory not found.")
        return

    print("Starting Google Books enrichment...")
    
    files = glob.glob(os.path.join(TARGET_1900_DIR, "*.jsonl"))
    total_processed = 0
    total_enriched = 0
    
    # SAMPLE RUN due to API limits
    MAX_RECORDS = 50 
    
    for jsonl_file in files:
        if total_processed >= MAX_RECORDS: break
        
        filename = os.path.basename(jsonl_file)
        print(f"Processing {filename}...")
        
        temp_file = jsonl_file + ".tmp"
        changes_in_file = 0
        
        with open(jsonl_file, "r", encoding="utf-8") as fin, \
             open(temp_file, "w", encoding="utf-8") as fout:
            
            for line in fin:
                if total_processed >= MAX_RECORDS:
                    fout.write(line)
                    continue

                if not line.strip(): continue
                record = json.loads(line)
                
                # Only process if not already enriched/valid
                date_raw = record.get("display_creationdate", "")
                if date_raw == "1900" or date_raw == "19--" or "190-" in date_raw:
                    
                    title = record.get("display_title", "")
                    creator = record.get("display_creator", "")
                    
                    if title:
                        print(f"  Querying: {title}...", end="", flush=True)
                        new_year = get_google_books_date(title, creator)
                        time.sleep(REQUEST_DELAY)
                        
                        if new_year:
                            print(f" FOUND: {new_year}")
                            record["display_creationdate"] = new_year
                            record["enrichment_source"] = "google_books_api"
                            changes_in_file += 1
                            total_enriched += 1
                        else:
                            print(" Not found.")
                    
                    total_processed += 1
                
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        # Replace file if changes made
        if changes_in_file > 0:
            os.replace(temp_file, jsonl_file)
            print(f"  Updated {changes_in_file} records in {filename}")
        else:
            os.remove(temp_file)

    print("-" * 40)
    print(f"Total Processed: {total_processed}")
    print(f"Total Enriched: {total_enriched}")
    print("-" * 40)

if __name__ == "__main__":
    process_enrichment()
