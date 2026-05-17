import requests
import pandas as pd
import os
import time

BASE_URL = "https://kits.teleagriculture.org/api/kits"
KIT_ID = 1001
SENSORS = ["ftTemp", "ftSoilMoisture", "ftHumidity"]
MAX_PAGES = 200  # 6000 records per sensor — plenty for ML

def fetch_sensor(kit_id, sensor_name):
    url = f"{BASE_URL}/{kit_id}/{sensor_name}/measurements"
    all_data = []
    page = 1

    while page <= MAX_PAGES:
        for attempt in range(3):
            try:
                response = requests.get(url, params={"page": page}, timeout=10)
                break
            except Exception as e:
                print(f"  Retry {attempt+1} on page {page}: {e}")
                time.sleep(3)
        else:
            print(f"  Failed after 3 retries, stopping {sensor_name}")
            break

        if response.status_code != 200:
            break

        records = response.json().get("data", [])
        if not records:
            print(f"  {sensor_name} complete — {len(all_data)} total records")
            break

        for r in records:
            r["sensor"] = sensor_name

        all_data.extend(records)
        print(f"{sensor_name} — page {page} — {len(all_data)} total so far")
        page += 1
        time.sleep(0.1)

    df = pd.DataFrame(all_data)
    csv_path = f"data/{sensor_name}.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved {sensor_name} to {csv_path}")
    return df

def fetch_all():
    os.makedirs("data", exist_ok=True)
    frames = []
    for sensor in SENSORS:
        csv_path = f"data/{sensor}.csv"
        if os.path.exists(csv_path):
            print(f"Already have {sensor}, loading from cache...")
            df = pd.read_csv(csv_path)
        else:
            df = fetch_sensor(KIT_ID, sensor)
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv("data/raw_sensor_data.csv", index=False)
    print("\nDone. Saved to data/raw_sensor_data.csv")
    print("Columns:", combined.columns.tolist())
    print(combined.head())

if __name__ == "__main__":
    fetch_all()