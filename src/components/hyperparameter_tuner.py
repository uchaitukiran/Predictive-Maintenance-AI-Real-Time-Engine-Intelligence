import optuna
import pandas as pd
import numpy as np
import joblib
import os

from sklearn.metrics import mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor

from src.logger import logging


class HyperparameterTuner:

    def __init__(self):
        pass

    def objective(self, trial, X_train, y_train, X_test, y_test):

        params = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 300),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "max_depth": trial.suggest_int("max_depth", 2, 8),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 10)
        }

        model = GradientBoostingRegressor(**params)

        model.fit(X_train, y_train)

        preds = model.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test, preds))

        return rmse


    def tune_model(self, train_path, test_path):

        logging.info("Starting Hyperparameter Tuning")

        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)

        X_train = train_df.drop(columns=["RUL", "engine_id", "cycle"])
        y_train = train_df["RUL"]

        X_test = test_df.drop(columns=["RUL", "engine_id", "cycle"])
        y_test = test_df["RUL"]

        study = optuna.create_study(direction="minimize")

        study.optimize(
            lambda trial: self.objective(trial, X_train, y_train, X_test, y_test),
            n_trials=30
        )

        best_params = study.best_params

        logging.info(f"Best parameters: {best_params}")

        best_model = GradientBoostingRegressor(**best_params)

        best_model.fit(X_train, y_train)

        os.makedirs("artifacts", exist_ok=True)

        model_path = "artifacts/tuned_gradient_boosting.pkl"

        joblib.dump(best_model, model_path)

        logging.info(f"Tuned model saved at {model_path}")

        return best_params