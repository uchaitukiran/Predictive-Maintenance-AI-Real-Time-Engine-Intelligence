import os
import sys
import pandas as pd
import numpy as np
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler
import joblib

from src.logger import logging
from src.exception import CustomException

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join('artifacts', "preprocessor.pkl")
    train_engineered_path: str = os.path.join('data', 'processed', "train_engineered.csv")
    test_engineered_path: str = os.path.join('data', 'processed', "test_engineered.csv")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def add_rul(self, df):
        rul = df.groupby('engine_id')['cycle'].max().reset_index()
        rul.columns = ['engine_id', 'max']
        df = df.merge(rul, on='engine_id', how='left')
        df['RUL'] = df['max'] - df['cycle']
        df.drop('max', axis=1, inplace=True)
        return df

    def initiate_data_transformation(self, train_path, test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info("Read train and test data completed")

            # 1. Add RUL
            train_df = self.add_rul(train_df)
            test_df = self.add_rul(test_df)

            # 2. Define Columns to Drop (Sensors with no variance + IDs)
            # IDs (engine_id, cycle) should NOT be used for prediction, so we drop them before scaling.
            drop_cols = [
                'engine_id', 'cycle', 
                'setting_1', 'setting_2', 'setting_3', 
                's_1', 's_5', 's_6', 's_10', 's_16', 's_18', 's_19'
            ]
            
            # Check existing columns
            cols_to_drop = [c for c in drop_cols if c in train_df.columns]

            # Save Target (RUL)
            y_train = train_df['RUL']
            y_test = test_df['RUL']

            # Drop columns
            train_features = train_df.drop(columns=cols_to_drop + ['RUL'], errors='ignore')
            test_features = test_df.drop(columns=cols_to_drop + ['RUL'], errors='ignore')

            # 3. Scaling (Fit only on features, NOT on IDs)
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(train_features)
            X_test_scaled = scaler.transform(test_features)

            # Save Scaler
            os.makedirs(os.path.dirname(self.data_transformation_config.preprocessor_obj_file_path), exist_ok=True)
            joblib.dump(scaler, self.data_transformation_config.preprocessor_obj_file_path)
            logging.info("Saved Scaler to artifacts/")

            # 4. Create Final DataFrames
            train_final = pd.DataFrame(X_train_scaled, columns=train_features.columns)
            train_final['RUL'] = y_train.values
            
            test_final = pd.DataFrame(X_test_scaled, columns=test_features.columns)
            test_final['RUL'] = y_test.values

            # Save to data/processed/
            train_final.to_csv(self.data_transformation_config.train_engineered_path, index=False)
            test_final.to_csv(self.data_transformation_config.test_engineered_path, index=False)

            logging.info(f"Transformation done. Saved to {self.data_transformation_config.train_engineered_path}")
            
            return (
                self.data_transformation_config.train_engineered_path,
                self.data_transformation_config.test_engineered_path
            )

        except Exception as e:
            raise CustomException(e, sys)