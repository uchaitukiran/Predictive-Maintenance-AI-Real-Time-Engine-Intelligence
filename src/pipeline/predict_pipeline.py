import sys
import pandas as pd
import numpy as np
import dill
import os

# This maps the user inputs to the 14 sensors we kept
class CustomData:
    def __init__(self, 
                 # Operating Settings
                 op_setting_1: float,
                 op_setting_2: float,
                 op_setting_3: float,
                 # The 14 Selected Sensors (Notebooks Step 3)
                 sensor_2: float,
                 sensor_3: float,
                 sensor_4: float,
                 sensor_7: float,
                 sensor_8: float,
                 sensor_9: float,
                 sensor_11: float,
                 sensor_12: float,
                 sensor_13: float,
                 sensor_14: float,
                 sensor_15: float,
                 sensor_17: float,
                 sensor_20: float,
                 sensor_21: float
                 ):

        self.op_setting_1 = op_setting_1
        self.op_setting_2 = op_setting_2
        self.op_setting_3 = op_setting_3
        
        self.sensor_2 = sensor_2
        self.sensor_3 = sensor_3
        self.sensor_4 = sensor_4
        self.sensor_7 = sensor_7
        self.sensor_8 = sensor_8
        self.sensor_9 = sensor_9
        self.sensor_11 = sensor_11
        self.sensor_12 = sensor_12
        self.sensor_13 = sensor_13
        self.sensor_14 = sensor_14
        self.sensor_15 = sensor_15
        self.sensor_17 = sensor_17
        self.sensor_20 = sensor_20
        self.sensor_21 = sensor_21

    def get_data_as_data_frame(self):
        try:
            custom_data_input_dict = {
                "op_setting_1": [self.op_setting_1],
                "op_setting_2": [self.op_setting_2],
                "op_setting_3": [self.op_setting_3],
                "sensor_2": [self.sensor_2],
                "sensor_3": [self.sensor_3],
                "sensor_4": [self.sensor_4],
                "sensor_7": [self.sensor_7],
                "sensor_8": [self.sensor_8],
                "sensor_9": [self.sensor_9],
                "sensor_11": [self.sensor_11],
                "sensor_12": [self.sensor_12],
                "sensor_13": [self.sensor_13],
                "sensor_14": [self.sensor_14],
                "sensor_15": [self.sensor_15],
                "sensor_17": [self.sensor_17],
                "sensor_20": [self.sensor_20],
                "sensor_21": [self.sensor_21],
            }
            return pd.DataFrame(custom_data_input_dict)
        except Exception as e:
            raise Exception(f"Error creating dataframe: {e}")

class PredictPipeline:
    def __init__(self):
        pass

    def predict(self, features):
        try:
            model_path = os.path.join("artifacts", "model.pkl")
            preprocessor_path = os.path.join("artifacts", "preprocessor.pkl")

            # Load objects
            with open(preprocessor_path, 'rb') as f:
                preprocessor = dill.load(f)
            
            with open(model_path, 'rb') as f:
                model = dill.load(f)

            # Transform
            data_scaled = preprocessor.transform(features)

            # Predict
            preds = model.predict(data_scaled)
            return preds
        
        except Exception as e:
            raise Exception(f"Error in prediction pipeline: {e}")