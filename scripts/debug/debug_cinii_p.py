import requests
import json

BASE_URL = "https://ci.nii.ac.jp/books/opensearch/search"
params1 = {
    "format": "json",
    "year_from": 1852,
    "year_to": 1852,
    "p": 1,
    "count": 20,
    "type": "0",
    "sortorder": 1
}
params2 = {
    "format": "json",
    "year_from": 1852,
    "year_to": 1852,
    "p": 2,
    "count": 20,
    "type": "0",
    "sortorder": 1
}

r1 = requests.get(BASE_URL, params=params1)
r2 = requests.get(BASE_URL, params=params2)

items1 = r1.json().get("@graph", [{}])[0].get("items", [])
items2 = r2.json().get("@graph", [{}])[0].get("items", [])

ids1 = [item.get("@id") for item in items1]
ids2 = [item.get("@id") for item in items2]

print(f"Page 1 (p=1) IDs: {ids1}")
print(f"Page 2 (p=2) IDs: {ids2}")

overlap = set(ids1).intersection(set(ids2))
print(f"Overlap: {overlap}")
