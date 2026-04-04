import os
import sys
import pandas as pd
import numpy as np
from dataclasses import dataclass
from src.logger import logging
from src.exception import CustomException

@dataclass
class DataIngestionConfig:
    # CHANGE: Save to data/processed/ NOT artifacts
    train_data_path: str = os.path.join('data', 'processed', "train.csv")
    test_data_path: str = os.path.join('data', 'processed', "test.csv")
    raw_data_path: str = os.path.join('data', 'processed', "raw.csv")

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Entered the data ingestion method")
        try:
            # 1. Define Column Names
            index_names = ['engine_id', 'cycle']
            setting_names = ['setting_1', 'setting_2', 'setting_3']
            sensor_names = ['s_{}'.format(i+1) for i in range(21)]
            col_names = index_names + setting_names + sensor_names

            # 2. Read Raw File (FIX PATH TO CMaps)
            raw_file_path = os.path.join('data', 'raw', 'CMaps', 'train_FD001.txt')
            
            if not os.path.exists(raw_file_path):
                raise FileNotFoundError(f"Raw data file not found at: {raw_file_path}")

            df = pd.read_csv(raw_file_path, sep=' ', header=None, names=col_names)
            df.dropna(axis=1, how='all', inplace=True)
            
            logging.info('Read the dataset as dataframe')
            
            # 3. Ensure folder exists
            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)
            df.to_csv(self.ingestion_config.raw_data_path, index=False, header=True)

            # 4. Train/Test Split (by Engine ID)
            logging.info("Train test split initiated")
            unique_engines = df['engine_id'].unique()
            # Use first 80 engines for train, rest for validation
            train_engines = unique_engines[:80] 
            test_engines = unique_engines[80:]

            train_df = df[df['engine_id'].isin(train_engines)]
            test_df = df[df['engine_id'].isin(test_engines)]

            train_df.to_csv(self.ingestion_config.train_data_path, index=False, header=True)
            test_df.to_csv(self.ingestion_config.test_data_path, index=False, header=True)

            logging.info(f"Ingestion completed. Files saved to data/processed/")

            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )

        except Exception as e:
            raise CustomException(e, sys)