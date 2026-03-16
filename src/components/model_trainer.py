import os
import pandas as pd
import numpy as np
import joblib

from dataclasses import dataclass

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

from src.logger import logging


@dataclass
class ModelTrainerConfig:
    trained_model_dir: str = "artifacts"


class ModelTrainer:

    def __init__(self):
        self.config = ModelTrainerConfig()

    # ---------------------------
    # Model Evaluation
    # ---------------------------
    def evaluate_model(self, y_true, y_pred):

        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        return rmse, mae, r2


    # ---------------------------
    # All Models
    # ---------------------------
    def get_models(self):

        models = {

            "LinearRegression": LinearRegression(),

            "Ridge": Ridge(),

            "Lasso": Lasso(),

            "RandomForest": RandomForestRegressor(),

            "GradientBoosting": GradientBoostingRegressor(),

            "XGBoost": XGBRegressor(),

            "LightGBM": LGBMRegressor(),

            "CatBoost": CatBoostRegressor(verbose=0)

        }

        return models


    # ---------------------------
    # Training Function
    # ---------------------------
    def initiate_model_training(self, train_path, test_path):

        logging.info("Loading training and testing data")

        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)

        X_train = train_df.drop(columns=["RUL", "engine_id", "cycle"])
        y_train = train_df["RUL"]

        X_test = test_df.drop(columns=["RUL", "engine_id", "cycle"])
        y_test = test_df["RUL"]

        models = self.get_models()

        results = []

        best_model = None
        best_model_name = None
        best_rmse = float("inf")

        # create artifacts directory
        os.makedirs(self.config.trained_model_dir, exist_ok=True)

        for name, model in models.items():

            logging.info(f"Training {name}")
            print(f"Training {name}")

            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)

            rmse, mae, r2 = self.evaluate_model(y_test, y_pred)

            logging.info(
                f"{name} -> RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}"
            )

            # store results
            results.append({
                "Model": name,
                "RMSE": rmse,
                "MAE": mae,
                "R2": r2
            })

            # save each model
            model_path = os.path.join(
                self.config.trained_model_dir,
                f"{name}.pkl"
            )

            joblib.dump(model, model_path)

            logging.info(f"{name} saved at {model_path}")

            # track best model
            if rmse < best_rmse:
                best_rmse = rmse
                best_model = model
                best_model_name = name

        # save best model separately
        best_model_path = os.path.join(
            self.config.trained_model_dir,
            f"best_{best_model_name}.pkl"
        )

        joblib.dump(best_model, best_model_path)

        logging.info(f"Best model is {best_model_name}")
        logging.info(f"Best model saved at {best_model_path}")

        print(f"\nBest model: {best_model_name}")
        print(f"Saved at: {best_model_path}")

        # ---------------------------
        # Save results CSV
        # ---------------------------

        results_df = pd.DataFrame(results)

        results_csv_path = os.path.join(
            self.config.trained_model_dir,
            "model_results.csv"
        )

        results_df.to_csv(results_csv_path, index=False)

        logging.info(f"Model results saved at {results_csv_path}")

        print("\nModel Performance:\n")
        print(results_df)

        return results_df