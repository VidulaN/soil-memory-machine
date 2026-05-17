import requests

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 6.14,
    "longitude": 1.22,
    "daily": "temperature_2m_max,precipitation_sum,et0_fao_evapotranspiration",
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "timezone": "Africa/Abidjan"
}

response = requests.get(url, params=params)
data = response.json()

print("Status:", response.status_code)
print("Keys:", list(data.keys()))

if "daily" in data:
    print("Daily keys:", list(data["daily"].keys()))
    print("First 3 dates:", data["daily"]["time"][:3])
    print("First 3 temps:", data["daily"]["temperature_2m_max"][:3])
    print("First 3 precip:", data["daily"]["precipitation_sum"][:3])
    print("Total days:", len(data["daily"]["time"]))
else:
    print("No daily data — full response:")
    print(data)