import os
import requests
import json
import time

BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
YEAR_MIN, YEAR_MAX = 1850, 1920

LANG_MAP = {
    "jpn": "JP",
    "eng": "EN",
    "chi": "ZH",
    "ger": "DE",
    "fre": "FR",
    "rus": "RU",
    "ita": "IT",
    "spa": "ES",
    "kor": "KO"
}

NDC_LIST = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

def get_appid():
    path = "api_keys"
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if "cinii=" in line and not line.strip().startswith("#"):
                    return line.strip().split("=")[1]
    return None

def fetch_count(year_from, year_to, lang=None, ndc=None, appid=None):
    params = {
        "format": "json",
        "year_from": year_from,
        "year_to": year_to,
        "count": 0,
        "type": "0"
    }
    if lang: params["lang"] = lang
    if ndc: params["clas"] = f"NDC{ndc}*"
    if appid: params["appid"] = appid

    try:
        r = requests.get(BASE_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return int(data.get("@graph", [{}])[0].get("opensearch:totalResults", 0))
    except Exception as e:
        return None

def main():
    appid = get_appid()
    results = {
        "total": 0,
        "by_ndc": {},
        "by_lang": {}
    }

    print("Fetching global total...")
    results["total"] = fetch_count(YEAR_MIN, YEAR_MAX, appid=appid)
    time.sleep(1)

    print("Fetching totals by NDC...")
    for ndc in NDC_LIST:
        count = fetch_count(YEAR_MIN, YEAR_MAX, ndc=ndc, appid=appid)
        results["by_ndc"][ndc] = count
        print(f"  NDC {ndc}: {count}")
        time.sleep(1)

    print("Fetching totals by Language...")
    for l_code, l_short in LANG_MAP.items():
        count = fetch_count(YEAR_MIN, YEAR_MAX, lang=l_code, appid=appid)
        results["by_lang"][l_short] = count
        print(f"  {l_short}: {count}")
        time.sleep(1)

    with open("cinii_global_api_stats.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
