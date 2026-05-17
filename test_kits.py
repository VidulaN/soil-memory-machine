import requests

for kit_id in [1, 2, 3, 100, 101, 102, 1001, 1002, 1003, 2001]:
    url = f"https://kits.teleagriculture.org/api/kits/{kit_id}/ftTemp/measurements"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            print(f"Kit {kit_id}: {len(data)} records, first: {data[0]['created_at']}, last: {data[-1]['created_at']}")
        else:
            print(f"Kit {kit_id}: empty")
    else:
        print(f"Kit {kit_id}: status {response.status_code}")