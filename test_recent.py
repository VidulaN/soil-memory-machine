import requests

url = "https://kits.teleagriculture.org/api/kits/1001/ftTemp/measurements"
response = requests.get(url, params={"page": 1})
data = response.json().get("data", [])

print("First record:", data[0])
print("Last record:", data[-1])