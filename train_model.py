import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import os

os.makedirs("model", exist_ok=True)

#Load data 
df = pd.read_csv("data/dataset.csv").dropna()

features = ["temp_max", "precipitation", "precip_7day", "precip_30day", 
            "temp_7day", "evapotranspiration"]
target = "drought_risk"

X = df[features]
y = df[target]

#Train/test split 
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

#Train model 
model = RandomForestClassifier(
    n_estimators=100,
    class_weight="balanced",  # handles the imbalance
    random_state=42
)
model.fit(X_train, y_train)

#Evaluate 
y_pred = model.predict(X_test)
print("=== Model Performance ===")
print(classification_report(y_test, y_pred, target_names=["No Drought", "Drought"]))

#Feature importance
print("=== Feature Importance ===")
for feat, imp in sorted(zip(features, model.feature_importances_), 
                         key=lambda x: x[1], reverse=True):
    print(f"  {feat}: {imp:.3f}")

#Save model
with open("model/drought_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\nModel saved to model/drought_model.pkl")