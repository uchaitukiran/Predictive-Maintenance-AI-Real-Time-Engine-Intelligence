import pandas as pd
import joblib
import os
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import dill

print("⚙️ Creating Model compatible with your App...")

# 1. Load Data
df = pd.read_csv('data/processed/train_engineered.csv')

# 2. Define the 17 columns your App uses
cols = [
    'op_setting_1', 'op_setting_2', 'op_setting_3',
    'sensor_2', 'sensor_3', 'sensor_4', 'sensor_7', 'sensor_8', 'sensor_9',
    'sensor_11', 'sensor_12', 'sensor_13', 'sensor_14', 'sensor_15',
    'sensor_17', 'sensor_20', 'sensor_21'
]

X = df[cols]
y = df['RUL']

# 3. Process
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# 4. Train
model = GradientBoostingRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# 5. Save
joblib.dump(model, 'artifacts/best_GradientBoosting.pkl')
with open('artifacts/preprocessor.pkl', 'wb') as f: dill.dump(scaler, f)

print("✅ Success! Model created with 17 features.")