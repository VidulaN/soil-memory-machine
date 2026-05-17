import requests
import pandas as pd
import os

os.makedirs("data", exist_ok=True)

print("Fetching Open-Meteo climate data...")

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 6.14,
    "longitude": 1.22,
    "daily": ["temperature_2m_max", "precipitation_sum", "et0_fao_evapotranspiration", 
              "precipitation_hours", "windspeed_10m_max"],
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "timezone": "Africa/Abidjan"
}

response = requests.get(url, params=params)
daily = response.json()["daily"]

df = pd.DataFrame({
    "date": pd.to_datetime(daily["time"]),
    "temp_max": daily["temperature_2m_max"],
    "precipitation": daily["precipitation_sum"],
    "evapotranspiration": daily["et0_fao_evapotranspiration"],
    "precip_hours": daily["precipitation_hours"],
    "windspeed": daily["windspeed_10m_max"]
})

# ── Features ──────────────────────────────────────────────────────────────────
df["precip_7day"]  = df["precipitation"].rolling(7).mean()
df["precip_30day"] = df["precipitation"].rolling(30).mean()
df["temp_7day"]    = df["temp_max"].rolling(7).mean()
df["evap_7day"]    = df["evapotranspiration"].rolling(7).mean()

# ── Label (independent) ───────────────────────────────────────────────────────
# Drought = prolonged low rainfall + high evaporation + low precip hours
# Using 14-day rolling window to create label independently of 30-day features
df["precip_14day"] = df["precipitation"].rolling(14).mean()
df["evap_14day"]   = df["evapotranspiration"].rolling(14).mean()

precip_low  = df["precip_14day"].quantile(0.25)
evap_high   = df["evap_14day"].quantile(0.75)

df["drought_risk"] = (
    (df["precip_14day"] < precip_low) &
    (df["evap_14day"] > evap_high)
).astype(int)

print(f"Drought days: {df['drought_risk'].sum()} out of {len(df)}")

df = df.dropna()
df.to_csv("data/dataset.csv", index=False)
print("Saved to data/dataset.csv")
print(df[["date", "temp_max", "precipitation", "precip_30day", "drought_risk"]].tail(10))