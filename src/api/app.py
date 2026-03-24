from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd

app = FastAPI(title="Engine Health Monitoring API")

# ✅ CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "artifacts/best_GradientBoosting.pkl"

print("Loading model...")
model = joblib.load(MODEL_PATH)


@app.get("/")
def home():
    return {"message": "API Running"}


@app.post("/predict")
def predict(data: dict):

    try:
        print("Incoming data:", data)

        df = pd.DataFrame([data])

        # 👉 IMPORTANT: ensure columns match model
        expected_cols = model.feature_names_in_
        df = df.reindex(columns=expected_cols, fill_value=0)

        rul = float(model.predict(df)[0])

        # STATE LOGIC
        if rul > 120:
            state = "GOOD"
        elif rul > 60:
            state = "WARNING"
        else:
            state = "CRITICAL"

        return {
            "Predicted_RUL": rul,
            "state": state
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "error": str(e),
            "state": "CRITICAL"
        }