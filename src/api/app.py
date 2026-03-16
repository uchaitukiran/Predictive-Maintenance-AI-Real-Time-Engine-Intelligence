from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI(title="Engine Health Monitoring API")

MODEL_PATH = "artifacts/best_GradientBoosting.pkl"

print("Loading model...")
model = joblib.load(MODEL_PATH)


@app.get("/")
def home():
    return {"message": "Engine RUL Prediction API is running"}


@app.post("/predict")
def predict(data: dict):

    df = pd.DataFrame([data])

    # Remove columns that model doesn't use
    df = df.drop(columns=["engine_id", "cycle"], errors="ignore")

    prediction = model.predict(df)[0]

    return {"Predicted_RUL": float(prediction)}