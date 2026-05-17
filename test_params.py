import requests

url = "https://kits.teleagriculture.org/api/kits/1001/ftTemp/measurements"

# Test different pagination styles
tests = [
    {"offset": 100},
    {"limit": 30, "offset": 100},
    {"start_date": "2023-01-01"},
    {"from": "2023-01-01"},
    {"date_from": "2023-01-01"},
    {"after": "2023-01-01"},
]

for params in tests:
    response = requests.get(url, params=params)
    data = response.json().get("data", [])
    if data:
        print(f"Params {params}: {data[0]['created_at']}")
    else:
        print(f"Params {params}: empty or no data key — {response.text[:100]}")