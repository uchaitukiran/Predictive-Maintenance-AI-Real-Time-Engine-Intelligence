import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import os

app = FastAPI(title="Engine Health Monitoring API")

# ---------------------------------------------------------
# ✅ ULTIMATE CORS FIX
# ---------------------------------------------------------
# This explicitly allows your frontend (localhost:8000) to talk to backend (5000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# MODEL LOADING
# ---------------------------------------------------------
# Path logic: webapp/api -> webapp -> project_root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
MODEL_PATH = os.path.join(project_root, "artifacts", "best_GradientBoosting.pkl")

model = None
print(f"Looking for model at: {MODEL_PATH}")

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("✅ Model loaded successfully!")
    else:
        print("❌ CRITICAL: Model file not found.")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------
@app.get("/")
def home():
    return {"message": "API Running"}

@app.post("/predict")
def predict(data: dict):
    try:
        print("📥 Received data:", data)
        
        if model is None:
            print("⚠️ Model is None, returning dummy data.")
            return {"Predicted_RUL": 99.9, "state": "WARNING"}

        df = pd.DataFrame([data])
        
        # Match model columns
        if hasattr(model, 'feature_names_in_'):
            df = df.reindex(columns=model.feature_names_in_, fill_value=0)

        rul = float(model.predict(df)[0])
        
        if rul > 120: state = "GOOD"
        elif rul > 60: state = "WARNING"
        else: state = "CRITICAL"

        print(f"📤 Sending response -> RUL: {rul}, State: {state}")
        
        return {
            "Predicted_RUL": rul,
            "state": state
        }

    except Exception as e:
        print(f"❌ Prediction Error: {e}")
        return {"Predicted_RUL": 0, "state": "CRITICAL"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)