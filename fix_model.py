import pandas as pd
import joblib
import os
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

print("⚙️ Retraining Gradient Boosting Model for your environment...")

# 1. Load Data
data_path = 'data/processed/train_engineered.csv'
if not os.path.exists(data_path):
    print(f"❌ Error: {data_path} not found.")
    exit()

df = pd.read_csv(data_path)
X = df.drop('RUL', axis=1)
y = df['RUL']

# 2. Train Model (Fast training for compatibility)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = GradientBoostingRegressor(n_estimators=50, random_state=42) # Fast settings
model.fit(X_train, y_train)

# 3. Save Model
save_path = 'artifacts/best_GradientBoosting.pkl'
joblib.dump(model, save_path)
print(f"✅ Success! Saved compatible model to {save_path}")