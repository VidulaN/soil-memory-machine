import requests

url = "https://kits.teleagriculture.org/api/kits/1001/ftTemp/measurements"

# Binary search - check page 5000, 10000 etc to find where 2020 starts
for page in [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000]:
    response = requests.get(url, params={"page": page})
    data = response.json().get("data", [])
    if data:
        print(f"Page {page}: {data[0]['created_at']} to {data[-1]['created_at']}")
    else:
        print(f"Page {page}: empty")