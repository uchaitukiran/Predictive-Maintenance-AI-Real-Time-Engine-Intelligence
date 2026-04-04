import sys
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import dill

# 1. Load the Raw Data
# Update this path to where your raw data is
raw_data_path = "data/processed/train_engine_data_clean.csv" 

try:
    df = pd.read_csv(raw_data_path)
    print(f"Data loaded successfully with shape: {df.shape}")
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

# 2. Feature Engineering (From Notebook Step 3 & 4)
# Drop low variance sensors identified in your notebook
drop_cols = ["sensor_1", "sensor_5", "sensor_6", "sensor_10", "sensor_16", "sensor_18", "sensor_19"]
# Also drop identifiers
ids = ["engine_id", "cycle"]

# Filter existing columns (in case some are already gone)
existing_cols_to_drop = [c for c in drop_cols if c in df.columns]
df = df.drop(columns=existing_cols_to_drop)

# Define Target (RUL) - Assuming you calculated RUL as per Notebook Step 1
# If your clean CSV doesn't have RUL, we calculate it here
if "RUL" not in df.columns:
    # Calculate RUL (Max cycle - current cycle) per engine
    if "engine_id" in df.columns and "cycle" in df.columns:
        max_cycle = df.groupby("engine_id")["cycle"].max().reset_index()
        max_cycle.columns = ["engine_id", "max_cycle"]
        df = df.merge(max_cycle, on="engine_id", how="left")
        df["RUL"] = df["max_cycle"] - df["cycle"]
        df.drop(columns=["max_cycle"], inplace=True)
        
        # Cap RUL at 125 (Notebook Step 2)
        df["RUL"] = df["RUL"].clip(upper=125)

# 3. Select Features (X) and Target (y)
# Input Features: All sensors + op_settings remaining
# Target: RUL
X = df.drop(columns=["RUL"] + [c for c in ids if c in df.columns])
y = df["RUL"]

print(f"Selected Features ({len(X.columns)}): {list(X.columns)}")

# 4. Preprocessing
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 5. Train Test Split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 6. Model Training
model = GradientBoostingRegressor(random_state=42)
model.fit(X_train, y_train)

# 7. Evaluation
preds = model.predict(X_test)
score = r2_score(y_test, preds)
print(f"Model R2 Score: {score:.4f}")

# 8. Save Artifacts
os.makedirs("artifacts", exist_ok=True)

# Save Preprocessor
with open("artifacts/preprocessor.pkl", "wb") as f:
    dill.dump(scaler, f)

# Save Model
with open("artifacts/model.pkl", "wb") as f:
    dill.dump(model, f)

print("✅ Model and Preprocessor saved to 'artifacts/' folder.")
print(f"Model expects {model.n_features_in_} features.")