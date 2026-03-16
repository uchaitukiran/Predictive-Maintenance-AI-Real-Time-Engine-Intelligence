import pandas as pd
import matplotlib.pyplot as plt
import joblib
import os


class FeatureImportance:

    def generate(self):

        print("Loading best model...")

        model = joblib.load("artifacts/best_GradientBoosting.pkl")

        print("Loading dataset...")

        train_df = pd.read_csv("data/processed/train_engineered.csv")

        X = train_df.drop(columns=["RUL", "engine_id", "cycle"])

        print("Calculating feature importance...")

        importance = model.feature_importances_

        feature_importance = pd.DataFrame({
            "feature": X.columns,
            "importance": importance
        }).sort_values(by="importance", ascending=False)

        os.makedirs("artifacts", exist_ok=True)

        # Save CSV
        csv_path = "artifacts/feature_importance.csv"
        feature_importance.to_csv(csv_path, index=False)

        print(f"CSV saved at: {csv_path}")

        # Plot
        plt.figure(figsize=(10,6))
        plt.barh(feature_importance["feature"][:15], feature_importance["importance"][:15])
        plt.gca().invert_yaxis()
        plt.title("Top Feature Importance")

        plot_path = "artifacts/feature_importance.png"
        plt.savefig(plot_path)

        print(f"Plot saved at: {plot_path}")

        plt.show()