import pandas as pd
import joblib


class PredictPipeline:

    def __init__(self):

        self.model_path = "artifacts/best_GradientBoosting.pkl"

    def predict(self, data_path):

        print("Loading model...")

        model = joblib.load(self.model_path)

        print("Loading data...")

        df = pd.read_csv(data_path)

        X = df.drop(columns=["RUL", "engine_id", "cycle"], errors="ignore")

        print("Making predictions...")

        predictions = model.predict(X)

        df["Predicted_RUL"] = predictions

        output_path = "artifacts/predictions.csv"

        df.to_csv(output_path, index=False)

        print(f"Predictions saved to {output_path}")

        return df


if __name__ == "__main__":

    pipeline = PredictPipeline()

    pipeline.predict("data/processed/test_engineered.csv")