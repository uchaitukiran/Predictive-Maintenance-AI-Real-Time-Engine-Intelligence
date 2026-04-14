import sys
import os
import pandas as pd
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.database.db import SessionLocal
from src.database.models import EngineSensorData

def ingest_data():
    db = SessionLocal()
    csv_path = 'data/processed/train_engineered.csv'
    
    print(f"⚙️ Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # --- SMART COLUMN MAPPING ---
    # This tries to find the right column names automatically
    col_map = {
        'op_setting_1': ['op_setting_1', 'setting1'],
        'op_setting_2': ['op_setting_2', 'setting2'],
        'op_setting_3': ['op_setting_3', 'setting3'],
        'sensor_2': ['sensor_2', 's2'],
        'sensor_3': ['sensor_3', 's3'],
        'sensor_4': ['sensor_4', 's4'],
        'sensor_7': ['sensor_7', 's7'],
        'sensor_8': ['sensor_8', 's8'],
        'sensor_9': ['sensor_9', 's9'],
        'sensor_11': ['sensor_11', 's11'],
        'sensor_12': ['sensor_12', 's12'],
        'sensor_13': ['sensor_13', 's13'],
        'sensor_14': ['sensor_14', 's14'],
        'sensor_15': ['sensor_15', 's15'],
        'sensor_17': ['sensor_17', 's17'],
        'sensor_20': ['sensor_20', 's20'],
        'sensor_21': ['sensor_21', 's21']
    }

    def get_col(target_name):
        # Find the column in df that matches target
        if target_name in df.columns: return target_name
        for variant in col_map.get(target_name, []):
            if variant in df.columns: return variant
        return None

    # Clear old data
    db.query(EngineSensorData).delete()
    db.commit()
    print("🗑️ Cleared old data.")

    print("🚀 Ingesting new data...")
    chunk_size = 1000
    # Reset index to ensure IDs start at 0 -> 1
    df = df.reset_index(drop=True)
    
    for i in tqdm(range(0, len(df), chunk_size)):
        chunk = df.iloc[i:i + chunk_size]
        records = []
        
        for idx, row in chunk.iterrows():
            # Helper to get value safely
            def val(target): 
                col = get_col(target)
                return row[col] if col else 0

            record = EngineSensorData(
                # Use 'id' from CSV if it exists, otherwise use loop index+1
                id=int(row['id']) if 'id' in row else int(idx + 1),
                op_setting_1=val('op_setting_1'),
                op_setting_2=val('op_setting_2'),
                op_setting_3=val('op_setting_3'),
                sensor_2=val('sensor_2'),
                sensor_3=val('sensor_3'),
                sensor_4=val('sensor_4'),
                sensor_7=val('sensor_7'),
                sensor_8=val('sensor_8'),
                sensor_9=val('sensor_9'),
                sensor_11=val('sensor_11'),
                sensor_12=val('sensor_12'),
                sensor_13=val('sensor_13'),
                sensor_14=val('sensor_14'),
                sensor_15=val('sensor_15'),
                sensor_17=val('sensor_17'),
                sensor_20=val('sensor_20'),
                sensor_21=val('sensor_21')
            )
            records.append(record)
        
        db.bulk_save_objects(records)
        db.commit()

    db.close()
    print("✅ Ingestion Complete.")

if __name__ == "__main__":
    ingest_data()