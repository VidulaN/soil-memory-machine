import requests
import pandas as pd
import pickle
from narrative.generate import generate_narrative
from datetime import date, timedelta

# ── 1. Fetch recent climate data ──────────────────────────────────────────────
def get_recent_data():
    end = date.today() - timedelta(days=1)  # yesterday (archive lag)
    start = end - timedelta(days=60)        # 60 days back for rolling windows

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 6.14,
        "longitude": 1.22,
        "daily": ["temperature_2m_max", "precipitation_sum", 
                  "et0_fao_evapotranspiration", "precipitation_hours", 
                  "windspeed_10m_max"],
        "start_date": str(start),
        "end_date": str(end),
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

    df["precip_7day"]  = df["precipitation"].rolling(7).mean()
    df["precip_30day"] = df["precipitation"].rolling(30 ─────────────────────────────────
def predict(row):
    with open("model/drought_model.pkl", "rb") as f:
        model = pickle.load(f)

    features = ["temp_max", "precipitation", "precip_7day", 
                "precip_30day", "temp_7day", "evapotranspiration"]

    X = pd.DataFrame([row[features]])
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    return prediction, probabilities

# ── 3. Generate narrative ─────────────────────────────────────────────────────
def run():
    print("Fetching latest climate data for Togo...")
    row = get_recent_data()

    print(f"Latest date: {row['date'].date()}")
    print(f"Temp: {row['temp_max']}°C | Precip 30d: {row['precip_30day']:.2f}mm")

    prediction, probabilities = predict(row)

    features = {
        "precip_30day": row["precip_30day"],
        "precip_7day": row["precip_7day"],
        "temp_max": row["temp_max"],
        "temp_7day": row["temp_7day"],
        "evapotranspiration": row["evapotranspiration"],
        "precipitation": row["precipitation"]
    }

    narrative = generate_narrative(features, prediction, probabilities)

    print("\n── SOIL MEMORY MACHINE ──────────────────────────────")
    print(f"Date: {row['date'].date()}")
    print(f"Location: Togo (6.14°N, 1.22°E)")
    print("─────────────────────────────────────────────────────")
    print(narrative)
    print("─────────────────────────────────────────────────────")

if __name__ == "__main__":
    run()