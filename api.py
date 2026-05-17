from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle
import pandas as pd
import requests as req
from datetime import date, timedelta

app = Flask(__name__)
CORS(app)  # allow browser requests from the frontend

#Load model once at startup
with open("model/drought_model.pkl", "rb") as f:
    model = pickle.load(f)

FEATURES = ["temp_max", "precipitation", "precip_7day",
            "precip_30day", "temp_7day", "evapotranspiration"]

#Fetch climate data from Open-Meteo 
def fetch_climate(lat, lon, start_year=1990):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "precipitation_sum", "et0_fao_evapotranspiration"],
        "start_date": f"{start_year}-01-01",
        "end_date": "2024-12-31",
        "timezone": "auto"
    }
    r = req.get(url, params=params, timeout=30)
    daily = r.json()["daily"]

    df = pd.DataFrame({
        "date": pd.to_datetime(daily["time"]),
        "temp_max": daily["temperature_2m_max"],
        "precipitation": daily["precipitation_sum"],
        "evapotranspiration": daily["et0_fao_evapotranspiration"]
    })

    df["precip_7day"]  = df["precipitation"].rolling(7).mean()
    df["precip_30day"] = df["precipitation"].rolling(30).mean()
    df["temp_7day"]    = df["temp_max"].rolling(7).mean()
    df["evap_7day"]    = df["evapotranspiration"].rolling(7).mean()
    df["precip_14day"] = df["precipitation"].rolling(14).mean()
    df["evap_14day"]   = df["evapotranspiration"].rolling(14).mean()

    return df.dropna()

#Aggregate by year
def aggregate_by_year(df):
    df["year"] = df["date"].dt.year
    yearly = df.groupby("year").agg(
        temp_max=("temp_max", "mean"),
        precipitation=("precipitation", "sum"),
        evapotranspiration=("evapotranspiration", "mean"),
        precip_7day=("precip_7day", "mean"),
        precip_30day=("precip_30day", "mean"),
        temp_7day=("temp_7day", "mean")
    ).reset_index()
    return yearly

#Run ML model on each year 
def predict_years(yearly_df):
    X = yearly_df[FEATURES]
    preds = model.predict(X)
    probs = model.predict_proba(X)[:, 1]  # probability of drought
    yearly_df = yearly_df.copy()
    yearly_df["drought_predicted"] = preds
    yearly_df["drought_probability"] = (probs * 100).round(1)
    return yearly_df

#Forecast 2025-2027
def forecast(yearly_df):
    recent = yearly_df.tail(5)[FEATURES].mean()
    forecast_rows = []
    for y in [2025, 2026, 2027]:
        row = recent.copy()
        row["year"] = y
        forecast_rows.append(row)
    forecast_df = pd.DataFrame(forecast_rows)
    X = forecast_df[FEATURES]
    preds = model.predict(X)
    probs = model.predict_proba(X)[:, 1]
    forecast_df["drought_predicted"] = preds
    forecast_df["drought_probability"] = (probs * 100).round(1)
    return forecast_df

#Narrative
def generate_narrative(country, score, avg_temp, avg_precip, trend, prob):
    risk_word = "high" if prob >= 60 else "moderate" if prob >= 35 else "low"
    rain = (
        f"Annual precipitation is critically low at {round(avg_precip)}mm."
        if avg_precip < 200 else
        f"Rainfall is below average at {round(avg_precip)}mm per year."
        if avg_precip < 600 else
        f"Rainfall is relatively stable at {round(avg_precip)}mm annually."
    )
    temp = (
        f"Temperatures are extreme, averaging {avg_temp:.1f}°C, accelerating moisture loss from soil."
        if avg_temp > 35 else
        f"Temperatures are elevated at {avg_temp:.1f}°C, increasing evaporative stress on crops."
        if avg_temp > 28 else
        f"Temperatures average {avg_temp:.1f}°C — within a moderate range."
    )
    trend_sent = (
        "Drought conditions have worsened significantly over the historical record."
        if trend > 3 else
        "Conditions have improved, with declining drought pressure over time."
        if trend < -3 else
        "Drought patterns have remained broadly stable across the recorded period."
    )
    return f"{rain} {temp} {trend_sent} The ML model rates overall drought probability at {prob:.0f}% for {country}."

#API endpoint
@app.route("/predict", methods=["GET"])
def predict():
    lat  = request.args.get("lat",  type=float)
    lon  = request.args.get("lon",  type=float)
    name = request.args.get("name", type=str, default="this location")

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon required"}), 400

    try:
        df      = fetch_climate(lat, lon)
        yearly  = aggregate_by_year(df)
        results = predict_years(yearly)
        fcast   = forecast(results)

        # Current (2024) stats
        current = results[results["year"] == 2024].iloc[0]
        recent5 = results.tail(5)
        avg_temp   = float(recent5["temp_max"].mean())
        avg_precip = float(recent5["precipitation"].mean())
        early5     = results.head(5)
        trend      = float(recent5["drought_probability"].mean() - early5["drought_probability"].mean())
        current_prob = float(current["drought_probability"])

        # Build year-by-year output
        history = []
        for _, row in results.iterrows():
            history.append({
                "year":        int(row["year"]),
                "precip":      round(float(row["precipitation"])),
                "temp":        round(float(row["temp_max"]), 1),
                "drought_prob": round(float(row["drought_probability"]), 1),
                "drought":     int(row["drought_predicted"]),
                "forecast":    False
            })
        for _, row in fcast.iterrows():
            history.append({
                "year":        int(row["year"]),
                "precip":      round(float(row["precipitation"])),
                "temp":        round(float(row["temp_max"]), 1),
                "drought_prob": round(float(row["drought_probability"]), 1),
                "drought":     int(row["drought_predicted"]),
                "forecast":    True
            })

        return jsonify({
            "country":      name,
            "lat":          lat,
            "lon":          lon,
            "current_prob": current_prob,
            "avg_temp":     round(avg_temp, 1),
            "avg_precip":   round(avg_precip),
            "trend":        round(trend, 1),
            "narrative":    generate_narrative(name, current_prob, avg_temp, avg_precip, trend, current_prob),
            "history":      history
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "RandomForest drought classifier"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)