import os
import json
import glob
import sys
import io
import time
import requests
import csv
import re

# Set stdout to utf-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "api_keys")
DATA_DIR = os.path.join(BASE_DIR, "data", "cinii", "v3_by_ndc_lang", "1900")
OUTPUT_CSV = os.path.join(BASE_DIR, "reports", "csv", "llm_pilot_comparison.csv")

def load_api_keys():
    keys = {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    keys[key.strip().lower()] = value.strip()
    except FileNotFoundError:
        print(f"Error: Config file not found at {CONFIG_FILE}")
    return keys

def query_llm(provider, api_key, title, creator):
    prompt = (
        f"Identify the original publication date for the book '{title}' by '{creator}'. "
        "If exact date is unknown, provide the most likely year. "
        "Strictly return a JSON object with this format: "
        "{\"date\": \"YYYY\", \"confidence\": \"High/Medium/Low\", \"reference\": \"Source or Explanation\"}. "
        "If strictly impossible to guess, use 'Unknown' for date."
    )
    
    messages = [
        {"role": "system", "content": "You are a bibliographic expert on Japanese literature (Meiji/Taisho era). Output only JSON."},
        {"role": "user", "content": prompt}
    ]

    if provider == "openai":
        url = "https://api.openai.com/v1/chat/completions"
        model = "gpt-4o"
    elif provider == "deepseek":
        url = "https://api.deepseek.com/chat/completions"
        model = "deepseek-chat"
    else:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            try:
                return json.loads(content)
            except:
                # Cleanup markdown if json mode fails or is not supported strictly
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
        else:
            return {"date": "Error", "confidence": "None", "reference": f"Status {response.status_code}"}
    except Exception as e:
        return {"date": "Error", "confidence": "None", "reference": str(e)}

def extract_year(date_str):
    """Simple helper to extract a 4-digit year from string."""
    m = re.search(r'\d{4}', str(date_str))
    return m.group(0) if m else ""

def run_pilot():
    keys = load_api_keys()
    gpt_key = keys.get("chatgpt") or keys.get("openai")
    ds_key = keys.get("deepseek")

    if not gpt_key or not ds_key:
        print("Error: Missing 'chatgpt' or 'deepseek' keys in config/api_keys")
        return

    print("Starting Multi-LLM Pilot (50 records)...")
    
    files = glob.glob(os.path.join(DATA_DIR, "*.jsonl"))
    records_processed = 0
    results = []

    for jsonl_file in files:
        if records_processed >= 50: break
        
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                if records_processed >= 50: break
                if not line.strip(): continue
                record = json.loads(line)
                
                date_raw = record.get("display_creationdate", "")
                # Filter for bad dates covering "1900", "19--", "190-"
                if date_raw == "1900" or "19-" in date_raw:
                    title = record.get("display_title", "Unknown")
                    creator = record.get("display_creator", "Unknown")
                    
                    print(f"[{records_processed+1}/50] {title}...")
                    
                    # Query GPT-4o
                    print("  GPT: ", end="", flush=True)
                    res_gpt = query_llm("openai", gpt_key, title, creator)
                    print(res_gpt.get("date"), end=" | ")
                    
                    # Query DeepSeek
                    print("DS: ", end="", flush=True)
                    res_ds = query_llm("deepseek", ds_key, title, creator)
                    print(res_ds.get("date"))
                    
                    # Compare
                    year_gpt = extract_year(res_gpt.get("date"))
                    year_ds = extract_year(res_ds.get("date"))
                    
                    match = (year_gpt == year_ds) and (len(year_gpt) == 4)
                    
                    results.append({
                        "title": title,
                        "creator": creator,
                        "original_date": date_raw,
                        "gpt_date": res_gpt.get("date"),
                        "gpt_conf": res_gpt.get("confidence"),
                        "ds_date": res_ds.get("date"),
                        "ds_conf": res_ds.get("confidence"),
                        "match": match,
                        "gpt_ref": res_gpt.get("reference"),
                        "ds_ref": res_ds.get("reference")
                    })
                    
                    records_processed += 1
                    time.sleep(0.5)

    # Save CSV
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    fieldnames = ["title", "creator", "original_date", "gpt_date", "gpt_conf", "ds_date", "ds_conf", "match", "gpt_ref", "ds_ref"]
    
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nCompleted. Results saved to {OUTPUT_CSV}")
    
    # Quick summary
    matches = sum(1 for r in results if r["match"])
    print(f"Total Matches (Consensus): {matches}/{records_processed} ({matches/records_processed*100:.1f}%)")

if __name__ == "__main__":
    run_pilot()
