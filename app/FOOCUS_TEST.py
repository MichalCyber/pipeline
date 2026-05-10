import requests
import json

URL = "http://127.0.0.1:7865/run/predict"

payload = {
    "fn_index": 0,
    "data": [
        "AI cinematic still, ultra realistic photograph, East Asian woman, emotional expression, cinematic lighting",
        "",     # negative prompt
        1,      # image number
        "1024x1024",
        None,   # seed
        False, False, False, False
    ]
}

r = requests.post(URL, json=payload, timeout=300)

print("STATUS:", r.status_code)
print(json.dumps(r.json(), indent=2))
