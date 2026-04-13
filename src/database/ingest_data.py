import sys
import os
import pandas as pd
from tqdm import tqdm

# Setup Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.database.db import SessionLocal
from src.database.models import EngineSensorData

# Mapping CSV Names -> DB Names
# The CSV uses NASA names (s2, s3). The DB uses full names (sensor_2).
COLUMN_MAP = {
    's2': 'sensor_2',
    's3': 'sensor_3',
    's4': 'sensor_4',
    's7': 'sensor_7',
    's8': 'sensor_8',
    's9': 'sensor_9',
    's11': 'sensor_11',
    's12': 'sensor_12',
    's13': 'sensor_13',
    's14': 'sensor_14',
    's15': 'sensor_15',
    's17': 'sensor_17',
    's20': 'sensor_20',
    's21': 'sensor_21',
    'setting1': 'op_setting_1',
    'setting2': 'op_setting_2',
    'setting3': 'op_setting_3',
    'op_setting_1': 'op_setting_1', # Handle if already correct name
    'op_setting_2': 'op_setting_2',
    'op_setting_3': 'op_setting_3',
    'sensor_2': 'sensor_2' # Handle if already correct name
}

def ingest_data():
    db = SessionLocal()
    csv_path = 'data/processed/train_engineered.csv'
    
    print(f"⚙️ Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Rename columns based on map
    df.rename(columns=COLUMN_MAP, inplace=True)
    
    print(f"📊 Found {len(df)} rows.")

    # Clear old data
    db.query(EngineSensorData).delete()
    db.commit()

    print("🚀 Ingesting data into PostgreSQL...")
    
    # Use chunking for speed
    CHUNK_SIZE = 1000
    for i in tqdm(range(0, len(df), CHUNK_SIZE)):
        chunk = df.iloc[i:i + CHUNK_SIZE]
        records = []
        
        for _, row in chunk.iterrows():
            # Safe Get with 0 default
            def get_val(col_name):
                return row.get(col_name, 0)

            record = EngineSensorData(
                op_setting_1=get_val('op_setting_1'),
                op_setting_2=get_val('op_setting_2'),
                op_setting_3=get_val('op_setting_3'),
                sensor_2=get_val('sensor_2'),
                sensor_3=get_val('sensor_3'),
                sensor_4=get_val('sensor_4'),
                sensor_7=get_val('sensor_7'),
                sensor_8=get_val('sensor_8'),
                sensor_9=get_val('sensor_9'),
                sensor_11=get_val('sensor_11'),
                sensor_12=get_val('sensor_12'),
                sensor_13=get_val('sensor_13'),
                sensor_14=get_val('sensor_14'),
                sensor_15=get_val('sensor_15'),
                sensor_17=get_val('sensor_17'),
                sensor_20=get_val('sensor_20'),
                sensor_21=get_val('sensor_21')
            )
            records.append(record)
        
        db.bulk_save_objects(records)
        db.commit()

    db.close()
    print("✅ Ingestion Complete.")

if __name__ == "__main__":
    ingest_data()